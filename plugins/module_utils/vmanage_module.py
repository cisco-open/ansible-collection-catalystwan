# Copyright 2024 Cisco Systems, Inc. and its affiliates#
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


import logging
import time
import traceback
from typing import Any, Callable, Dict, Protocol, TypeVar

import urllib3
from ansible.module_utils.basic import AnsibleModule, env_fallback, missing_required_lib
from urllib3.exceptions import NewConnectionError, TimeoutError

from ..module_utils.logger_config import configure_logger
from ..module_utils.result import ModuleResult

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Suggested by
# https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_best_practices.html#importing-and-using-shared-code
LIB_IMP_ERR = None
try:
    from catalystwan.api.task_status_api import Task
    from catalystwan.session import ManagerHTTPError, ManagerRequestException, ManagerSession, create_manager_session
    from catalystwan.typed_list import DataSequence
    from catalystwan.vmanage_auth import UnauthorizedAccessError

    HAS_LIB = True
except:  # noqa: E722
    HAS_LIB = False
    LIB_IMP_ERR = traceback.format_exc()


ReturnType = TypeVar("ReturnType")


class GetDataFunc(Protocol[ReturnType]):
    def __call__(self, **kwargs: Any) -> ReturnType:
        ...


class AnsibleCatalystwanModule:
    """Common code for ansible modules that use catalystwan.

    Args:
        argument_spec (dict): Dictionary containing arguments specific to the module.
        supports_check_mode (bool, optional): Check mode of module. Defaults to False.

    Note: supports_check_mode is currently not supported for AnsibleCatalystwanModule

    """

    common_args = dict(
        manager_credentials=dict(
            type="dict",
            required=True,
            aliases=["manager_authentication"],
            options=dict(
                url=dict(type="str", required=True, fallback=(env_fallback, ["VMANAGE_URL"])),
                username=dict(type="str", required=True, fallback=(env_fallback, ["VMANAGE_USERNAME"])),
                password=dict(type="str", required=True, fallback=(env_fallback, ["VMANAGE_PASSWORD"]), no_log=True),
                port=dict(type="str", required=False, fallback=(env_fallback, ["VMANAGE_PORT"])),
            ),
        )
    )

    def __init__(self, argument_spec=None, supports_check_mode=False, session_reconnect_retries=0, **kwargs):
        self.argument_spec = argument_spec
        if self.argument_spec is None:
            self.argument_spec = dict()
        self.session_reconnect_retries = session_reconnect_retries

        self.argument_spec.update(self.common_args)
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=supports_check_mode, **kwargs)
        self.logger = configure_logger(name="ansible_catalystwan_module", loglevel=logging.DEBUG)
        self._vmanage_logger = configure_logger(name="ansible_catalystwan", loglevel=logging.DEBUG)

        if not HAS_LIB:
            self.module.fail_json(msg=missing_required_lib("catalystwan"), exception=LIB_IMP_ERR)

        self._session = None

    def exit_json(self, **kwargs):
        self.module.exit_json(**kwargs)

    def fail_json(self, msg: str, **kwargs):
        self.module.fail_json(msg, **kwargs)

    @property
    def params(self) -> Dict:
        return self.module.params

    @property
    def params_without_none_values(self) -> Dict:
        """
        When passing values to catalystwan endpoints, we don't want to modify state by providing any None values.
        """

        def strip_none_values(value):
            if isinstance(value, dict):
                return {k: strip_none_values(v) for k, v in value.items() if v is not None}
            else:
                return value

        return strip_none_values(self.params)

    @staticmethod
    def get_exception_string(exception) -> str:
        if hasattr(exception, "message"):
            return exception.message
        else:
            return repr(exception)

    @property
    def session(self) -> ManagerSession:
        if self._session is None:
            reconnect_times = self.session_reconnect_retries
            manager_url = self.module.params["manager_credentials"]["url"]
            while True:
                try:
                    self._session = create_manager_session(
                        url=manager_url,
                        username=self.module.params["manager_credentials"]["username"],
                        password=self.module.params["manager_credentials"]["password"],
                        port=self.module.params["manager_credentials"]["port"],
                        logger=self._vmanage_logger,
                    )
                    break
                # Avoid catchall exceptions, they are not very useful unless the underlying API
                # gives very good error messages pertaining the attempted action.
                except (
                    NewConnectionError,
                    ConnectionError,
                    ManagerRequestException,
                    TimeoutError,
                    UnauthorizedAccessError,
                ) as exception:
                    if reconnect_times:
                        reconnect_times = reconnect_times - 1
                        time.sleep(1)
                        continue
                    else:
                        self.module.fail_json(
                            msg=f"Cannot establish session with Manager: {manager_url}, "
                            f"exception: {self.get_exception_string(exception)}",
                            exception=traceback.format_exc(),
                        )

                except Exception as exception:
                    self.module.fail_json(msg=f"Unknown exception: {exception}", exception=traceback.format_exc())

        return self._session

    def get_response_safely(self, get_data_func: GetDataFunc[ReturnType], **kwargs: Any) -> ReturnType:
        """
        Wrapper around get endpoints, that handles ManagerHTTPError exceptions.

        Used to simplify getting safe data for manager, that is not intented to be returned directly to user, but
        that will be used internally for verification of state or for operations.
        """
        try:
            data = get_data_func(**kwargs)
            return data

        except ManagerHTTPError as ex:
            self.fail_json(
                msg=f"Could not call '{get_data_func}' endpoint.\nManager error: {ex.info}",
                exception=traceback.format_exc(),
            )

    def send_request_safely(
        self,
        result: ModuleResult,
        action_name: str,
        send_func: Callable,
        response_key: str = None,
        fail_on_exception: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Simplify process of sending requests to Manager safely. Handle all kind of requests.
        """
        try:
            response = send_func(**kwargs)

            if response_key and response is not None:
                if isinstance(response, DataSequence) and len(response):
                    try:
                        result.response[f"{response_key}"] = [element.model_dump(mode="json") for element in response]
                    except AttributeError:  # handle pydantic v1 models
                        result.response[f"{response_key}"] = [element.dict() for element in response]
                else:
                    result.response[f"{response_key}"] = response
            result.changed = True

        except ManagerHTTPError as ex:
            if fail_on_exception:
                self.fail_json(
                    msg=f"Could not perform '{action_name}' action.\nManager error: {ex.info}",
                    exception=traceback.format_exc(),
                )

    def execute_action_safely(
        self,
        result: ModuleResult,
        action_name: str,
        send_func: Callable,
        success_msg: str,
        failure_msg: str,
        payload: Any = None,
        wait_for_completed: bool = True,
    ):
        """
        Simplify process of sending requests to Manager, that are considered as tasks (return task id).
        """
        try:
            if payload is None:
                response = send_func()
            else:
                response = send_func(payload=payload)

            task_id = response.process_id if hasattr(response, "process_id") else response.id
            task = Task(self.session, task_id)

            if wait_for_completed:
                task_result = task.wait_for_completed()

                if task_result.result:
                    result.changed = True
                    result.response = [task.dict() for task in task_result.sub_tasks_data]
                    result.msg += success_msg

                else:
                    result.changed = False
                    result.msg = failure_msg
                    self.fail_json(**result.model_dump(mode="json"))
            else:
                result.changed = True
                result.response = f"Action '{action_name}' started, skipping waiting for task result"

        except ManagerHTTPError as ex:
            self.fail_json(
                msg=f"Could not perform '{action_name}' action.\nManager error: {str(ex)} {ex.info}",
                exception=traceback.format_exc(),
            )
