#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: XXX

short_description: XXX

description: XXX

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool

author:
    - Your Name (@yourGitHubHandle)
"""

EXAMPLES = r"""
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
"""
import traceback
from typing import Any, Dict, Optional

from catalystwan.session import create_manager_session
from catalystwan.vmanage_auth import UnauthorizedAccessError
from pydantic import Field
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_fixed  # type: ignore
from urllib3.exceptions import NewConnectionError, TimeoutError

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    is_server_ready: Optional[str] = Field(default="")


def run_module():
    module_args = dict(
        timeout_seconds=dict(type=int),
        sleep_seconds=dict(type=int),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    timeout_seconds = module.params.get("timeout_seconds")
    sleep_seconds = module.params.get("sleep_seconds")

    result = ExtendedModuleResult()
    module.logger.warning(f"{module.module._name} is deprecated! Please use role: cisco.catalystwan.api_ready")

    @retry(
        wait=wait_fixed(sleep_seconds),
        stop=(stop_after_delay(timeout_seconds)),
        retry=retry_if_exception_type((NewConnectionError, TimeoutError, ConnectionError, UnauthorizedAccessError)),
        reraise=True,
    )
    def get_server_ready_response(module: AnsibleCatalystwanModule, result: ExtendedModuleResult) -> Dict[str, Any]:
        module.logger.debug(
            f"Trying to establish API connection with vManage, retry: {get_server_ready_response.retry.statistics}"
        )
        module._session = create_manager_session(
            url=module.params.get("manager_credentials").get("url"),
            username=module.params.get("manager_credentials").get("username"),
            password=module.params.get("manager_credentials").get("password"),
            port=module.params.get("manager_credentials").get("port"),
        )
        response = module.session.endpoints.client.server_ready()
        result.is_server_ready = response.is_server_ready
        module.exit_json(**result.model_dump(mode="json"))

    try:
        get_server_ready_response(module=module, result=result)
    except (NewConnectionError, TimeoutError, ConnectionError) as ex:
        module.fail_json(msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc())
    except UnauthorizedAccessError as ex:
        module.fail_json(msg=f"Could not access API server: {str(ex)}", exception=traceback.format_exc())


def main():
    # raise DeprecationWarning(f"{__name__} is deprecated! Plase use role: cisco.catalystwan.api_ready")
    run_module()


if __name__ == "__main__":
    main()
