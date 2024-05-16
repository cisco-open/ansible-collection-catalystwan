#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: software_upgrade
short_description: Manages the software upgrade process on devices.
version_added: "0.1.0"
description:
  - This module allows you to manage the software lifecycle on devices.
  - You can install, activate, set a default, or remove software images on devices.
options:
  state:
    description:
      - The desired state of the software image on the device(s).
    type: str
    choices: ['present', 'active', 'default', 'absent']
    default: 'present'
  image_version:
    description:
      - The version of the image to install/activate.
    type: str
  image_path:
    description:
      - The path to the image to install.
    type: str
  remote_server_name:
    description:
      - The name of the remote server where the image is located.
    type: str
  remote_image_filename:
    description:
      - The filename of the image on the remote server.
    type: str
  downgrade_check:
    description:
      - Whether to perform a downgrade check before installing the software.
    type: bool
    default: true
  wait_for_completed:
    description:
      - Whether to wait for the installation to complete before exiting.
    type: bool
    default: true
  wait_timeout_seconds:
    description:
      - The maximum time to wait for the software operation to complete.
    type: int
    default: 3600
  reboot:
    description:
      - Whether to reboot the device after installation.
    type: bool
    default: false
  sync:
    description:
      - Whether to synchronize the device after installation.
    type: bool
    default: true
  force:
    description:
      - Whether to force the removal of the software image.
    type: bool
    default: false
  filters:
    description:
      - A dictionary of filters to apply.
    type: dict
  devices:
    description:
      - A list of device identifiers to apply the software operation to.
    type: list
    elements: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - This module does not guarantee idempotency - certain operations like installation will always change device state.
  - Ensure the device's hardware is compatible with the software image before attempting an upgrade.
  - The module may require elevated privileges to perform software upgrades on network devices.
  - The 'sync' option is only applicable if the platform supports post-installation synchronization.

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

EXAMPLES = r"""
---
- name: Install a software image on devices by image version
  cisco.catalystwan.software_upgrade:
    state: present
    image_version: '19.2.1'
    devices:
      - 'device1'
      - 'device2'

- name: Activate a software image on devices
  cisco.catalystwan.software_upgrade:
    state: active
    image_version: '19.2.1'
    devices:
      - 'device1'
      - 'device2'
    wait_for_completed: true

- name: Remove a software image from devices
  cisco.catalystwan.software_upgrade:
    state: absent
    image_version: '18.4.5'
    devices:
      - 'device1'
      - 'device2'
    force: true

- name: Remove a software image from devices without performing a downgrade check
  cisco.catalystwan.software_upgrade:
    state: absent
    image_version: '18.4.5'
    devices:
      - 'device1'
      - 'device2'
    force: true
    downgrade_check: false

- name: Perform a software upgrade on devices with additional options
  cisco.catalystwan.software_upgrade:
    state: present
    image_version: '20.1.2'
    devices:
      - 'device1'
      - 'device2'
    wait_timeout_seconds: 7200
    sync: false
    filters:
      model: 'C9500'
      region: 'NA'
"""

RETURN = r"""
msg:
  description: A message describing the result of the operation.
  returned: always
  type: str
  sample: "Software upgrade initiated for device 100."

changed:
  description: A boolean indicating whether the module caused changes.
  returned: always
  type: bool

task_id:
  description: The ID of the task that was executed for the software upgrade.
  returned: when a task is started and wait_for_task is false
  type: str
  sample: "12345"

result:
  description: The result of the software upgrade task.
  returned: when wait_for_task is true
  type: dict
  contains:
    status:
      description: The final status of the upgrade task.
      type: str
      sample: "completed"
    details:
      description: Detailed information about the upgrade task.
      type: str
      sample: "Upgrade completed successfully."
    error:
      description: Error details if the upgrade failed.
      type: str
      sample: "Error during software upgrade."
"""


import traceback
from enum import Enum

from catalystwan.api.task_status_api import Task
from catalystwan.endpoints.configuration_device_inventory import DeviceDetailsResponse
from catalystwan.exceptions import EmptyVersionPayloadError, ImageNotInRepositoryError
from catalystwan.session import ManagerHTTPError, ManagerRequestException
from catalystwan.typed_list import DataSequence
from catalystwan.vmanage_auth import UnauthorizedAccessError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed  # type: ignore
from urllib3.exceptions import NewConnectionError, TimeoutError

from ..module_utils.filters import get_devices_details
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

INTERVAL_SECONDS = 30
TIMEOUT_SECONDS = 7200


class SoftwareState(str, Enum):
    PRESENT = "present"  # in vManage -> INSTALLED
    ACTIVE = "active"  # in vManage -> ACTIVATED
    ABSENT = "absent"  # in vManage -> REMOVED
    DEFAULT = "default"  # in vManage -> DEFAULT


@retry(
    wait=wait_fixed(INTERVAL_SECONDS),
    stop=stop_after_attempt(int(TIMEOUT_SECONDS / INTERVAL_SECONDS)),
    retry=retry_if_exception_type((ManagerRequestException, UnauthorizedAccessError)),
    reraise=True,
)
def wait_for_task_data(module: AnsibleCatalystwanModule, result: ModuleResult, task: Task):
    task.session.login()
    task_data = task.wait_for_completed(timeout_seconds=module.params.get("wait_timeout_seconds"))
    if not task_data.result:
        result.msg = [data.activity for data in task_data.sub_tasks_data]
        result.response = task_data.json()
        module.fail_json(**result.model_dump(mode="json"))
    module.logger.info(f"Task data after task completed: {task_data.dict()}")


def run_module():
    module_args = dict(
        state=dict(
            type="str",
            choices=[SoftwareState.PRESENT, SoftwareState.ACTIVE, SoftwareState.DEFAULT, SoftwareState.ABSENT],
            default=SoftwareState.PRESENT.value,
        ),
        image_version=dict(type="str", default=None),
        image_path=dict(type="str", default=None),
        remote_server_name=dict(type="str", default=None),
        remote_image_filename=dict(type="str", default=None),
        downgrade_check=dict(type="bool", default=True),
        wait_for_completed=dict(type="bool", default=True),  # If task has to wait for installation finish
        wait_timeout_seconds=dict(
            type="int", default=7200
        ),  # 3600 is because vManage reports: 'configuration-dbStatus it may take up to 40 mins or longer'
        reboot=dict(type="bool", default=False),
        sync=dict(type="bool", default=True),
        force=dict(type="bool", default=False),  # Only for REMOVE
        filters=dict(type="dict"),
        devices=dict(type="list", elements="str", default=[]),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_one_of=[
            ("image_version", "image_path", "remote_image_filename", "remote_server_name"),
            ("filters", "devices"),
        ],
        required_if=[
            (
                "state",
                SoftwareState.PRESENT.value,
                (
                    "image_version",
                    "image_path",
                    ("remote_server_name", "remote_image_filename"),
                ),
                True,
            ),
            (
                "state",
                SoftwareState.ACTIVE.value,
                (
                    "image_version",
                    "image_path",
                ),
                True,
            ),
            ("state", SoftwareState.ABSENT.value, ("image_version",), True),
        ],
    )
    result = ModuleResult()

    # ---------------------------------#
    # STEP 1 - verify module arguments #
    # ---------------------------------#
    # Done with required_one_of and required_if

    # ----------------------------------------------------------------#
    # STEP 2 - verify if any action required or state is changed = OK #
    # ----------------------------------------------------------------#
    # Prepare devices list
    devices: DataSequence[DeviceDetailsResponse] = get_devices_details(module=module)
    expected_state = module.params["state"]

    # ----------------------------------#
    # STEP 3 - perform required actions #
    # ----------------------------------#

    if not devices:
        result.msg = f"Empty devices list based on filter: {module.params.get('filters')}"
        module.exit_json(**result.model_dump(mode="json"))

    if expected_state == SoftwareState.PRESENT:
        try:
            # Install software
            # NOTE We do not check if `Requested SW version already installed`, we always perform installation.
            # Checking inside of the task is too complex to perform (at least till we don't have it in API)

            # That means we are failing badly because sometimes install or activate is not possible.
            install_task = module.session.api.software.install(
                devices=devices,
                image=module.params.get("image_path"),
                image_version=module.params.get("image_version"),
                downgrade_check=module.params.get("downgrade_check"),
                sync=module.params.get("sync"),
                reboot=module.params.get("reboot"),
                remote_server_name=module.params.get("remote_server_name"),
                remote_image_filename=module.params.get("remote_image_filename"),
            )

            if (
                module.params.get("wait_for_completed")
                and module.params.get("reboot")  # noqa: W503
                and all([True for device in devices if device.personality == "vmanage"])  # noqa: W503
            ):
                try:
                    module.session.restart_imminent(restart_timeout_override=module.params.get("wait_timeout_seconds"))
                    wait_for_task_data(module=module, result=result, task=install_task)
                    result.msg += f"Installation task finished, id: {install_task.task_id}"
                except (ManagerRequestException, TimeoutError, ConnectionError) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )

            # Check action status
            elif module.params.get("wait_for_completed"):
                try:
                    wait_for_task_data(module=module, result=result, task=install_task)
                    result.msg += f"Installation task finished, id: {install_task.task_id}"
                except (
                    ManagerRequestException,
                    NewConnectionError,
                    TimeoutError,
                    ConnectionError,
                    UnauthorizedAccessError,
                ) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )
            else:
                result.msg += f"Installation task scheduled, id: {install_task.task_id}"

            result.changed = True
            module.exit_json(**result.model_dump(mode="json"))

        except EmptyVersionPayloadError:
            module.fail_json(
                msg="Requested software version not found in repository software versions for that device.",
                exception=traceback.format_exc(),
            )

        except ManagerHTTPError as ex:
            module.fail_json(
                msg=f"Could not get expected state: '{expected_state}' with upgrade operation: {ex.info}",
                exception=traceback.format_exc(),
            )

        except ValueError as ex:
            module.fail_json(
                msg=f"Could not perform requested upgrade operation, see details: {ex}",
                exception=traceback.format_exc(),
            )

        except ImageNotInRepositoryError as ex:
            module.fail_json(
                msg=f"Could not find requested image, see details: {ex}",
                exception=traceback.format_exc(),
            )

    elif expected_state == SoftwareState.ACTIVE:
        try:
            # Activate software
            activate_task = module.session.api.software.activate(
                devices=devices,
                image=module.params.get("image_path"),
                version_to_activate=module.params.get("image_version"),
            )

            if module.params.get("wait_for_completed") and all(
                [True for device in devices if device.personality == "vmanage"]
            ):
                try:
                    module.session.restart_imminent(restart_timeout_override=module.params.get("wait_timeout_seconds"))
                    wait_for_task_data(module=module, result=result, task=activate_task)
                    result.msg += f"Activation task finished, id: {activate_task.task_id}"
                except (ManagerRequestException, UnauthorizedAccessError) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )

            elif module.params.get("wait_for_completed"):
                try:
                    wait_for_task_data(module=module, result=result, task=activate_task)
                    result.msg += f"Activation task finished, id: {activate_task.task_id}"
                except (ManagerRequestException, UnauthorizedAccessError) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )

            else:
                result.msg += f"Activation task scheduled, id: {activate_task.task_id}"

            result.changed = True
            module.exit_json(**result.model_dump(mode="json"))

        except EmptyVersionPayloadError:
            module.fail_json(
                msg="Cannot create payload for activate operation with provided software image or version."
            )

        except ManagerHTTPError as ex:
            module.fail_json(
                msg=f"Could not get expected state: '{expected_state}' with activate operation: {ex.info}",
                exception=traceback.format_exc(),
            )

        except ValueError as ex:
            module.fail_json(
                msg=f"Could not perform requested upgrade operation, see details: {ex}",
                exception=traceback.format_exc(),
            )

        except ImageNotInRepositoryError as ex:
            module.fail_json(
                msg=f"Could not find requested image, see details: {ex}",
                exception=traceback.format_exc(),
            )

    elif expected_state == SoftwareState.DEFAULT:
        try:
            # Set default software version
            requested_version = module.params.get("image_version")
            if requested_version == "current":
                set_default_partition_task = module.session.api.partition.set_default_partition(
                    devices=devices,
                )
            else:
                set_default_partition_task = module.session.api.partition.set_default_partition(
                    devices=devices,
                    partition=requested_version,
                )

            # Check action status
            if module.params.get("wait_for_completed"):
                try:
                    wait_for_task_data(module=module, result=result, task=set_default_partition_task)
                    result.msg += f"Set Default task finished, id: {set_default_partition_task.task_id}"
                except (
                    ManagerRequestException,
                    NewConnectionError,
                    TimeoutError,
                    ConnectionError,
                    UnauthorizedAccessError,
                ) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )
            else:
                result.msg += f"Set Default task scheduled, id: {set_default_partition_task.task_id}"

            result.changed = True
            module.exit_json(**result.model_dump(mode="json"))

        except EmptyVersionPayloadError:
            module.fail_json(
                msg="Requested software version not found in software versions for that device."
                "If you want to set current version as default version, "
                "provide image_version parameter or set it as 'current'"
            )

        except ManagerHTTPError as ex:
            module.fail_json(
                msg=f"Could not get expected state: '{expected_state}' with Default operation: {ex.info}",
                exception=traceback.format_exc(),
            )

    elif expected_state == SoftwareState.ABSENT:
        try:
            # These are just for logging
            if module.params.get("image_version"):
                payload_devices = module.session.api.partition.device_version.get_device_available(
                    module.params.get("image_version"), devices
                )
                module.logger.info(f"get_device_available: {payload_devices}")
            else:
                payload_devices = module.session.api.partition.device_version.get_devices_available_versions(devices)
                module.logger.info(f"get_devices_available_versions: {payload_devices}")

            remove_partition_task = module.session.api.partition.remove_partition(
                devices=devices,
                partition=module.params.get("image_version"),
                force=module.params.get("force"),
            )

            # Check action status
            if module.params.get("wait_for_completed"):
                try:
                    wait_for_task_data(module=module, result=result, task=remove_partition_task)
                    result.msg += f"Remove partition task finished, id: {remove_partition_task.task_id}"
                except (
                    ManagerRequestException,
                    NewConnectionError,
                    TimeoutError,
                    ConnectionError,
                    UnauthorizedAccessError,
                ) as ex:
                    module.fail_json(
                        msg=f"Timed out waiting for API server: {str(ex)}", exception=traceback.format_exc()
                    )

            else:
                result.msg += f"Remove partition task scheduled, id: {remove_partition_task.task_id}"

            result.changed = True
            module.exit_json(**result.model_dump(mode="json"))

        except EmptyVersionPayloadError:
            module.exit_json(
                msg="Cannot find requested software version in versions available to remove from that device. "
                "No effect of `Delete Available Software` action."
            )

        except ManagerHTTPError as ex:
            module.fail_json(
                msg=f"Could not get expected state: '{expected_state}' with remove partition operation: {ex.info}",
                exception=traceback.format_exc(),
            )

    # ----------------------------------#
    # STEP 4 - update and return result #
    # ----------------------------------#
    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
