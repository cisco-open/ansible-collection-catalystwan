#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: devices_wan_edges
short_description: Manages WAN Edge devices within vManage
version_added: "0.1.0"
description:
  - This module manages the WAN Edge devices in vManage.
  - It can sync devices from a smart account, upload a WAN Edge list, generate bootstrap configuration,
    or delete WAN Edge devices.
options:
  state:
    description:
      - The state of the WAN Edge devices.
    type: str
    choices: ["present", "absent"]
    default: "present"
  sync_devices_from_smart_account:
    description:
      - Whether to sync devices from the smart account.
    type: bool
    default: False
  username:
    description:
      - Username for the smart account.
    type: str
  password:
    description:
      - Password for the smart account.
    type: str
    no_log: True
  wan_edge_list:
    description:
      - Filepath to the WAN Edge list for uploading.
    type: str
  uuid:
    description:
      - UUIDs of the devices to manage or 'all' for all devices.
    type: raw
    default: "all"
    aliases: ["devices_ids"]
  generate_bootstrap_configuration:
    description:
      - Whether to generate bootstrap configuration for the devices.
    type: bool
    default: False
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - If 'state' is 'present', either 'sync_devices_from_smart_account' or 'wan_edge_list' must be defined.
  - If 'state' is 'absent', no additional parameters are needed apart from 'uuid'.
  - The 'sync_devices_from_smart_account' option requires 'username' and 'password'.

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication

"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: always
  type: str
  sample: "Sync Smart Account completed."
changed:
  description: Whether or not the state was changed.
  returned: always
  type: bool
  sample: true
response:
  description: Detailed response from the vManage API if applicable.
  returned: when API call is made
  type: dict
  sample: {"status": "success", "details": "Device added successfully."}
bootstrap_configuration:
  description: Bootstrap configuration details if generated.
  returned: when bootstrap configuration is generated
  type: list
  sample: [
    {
      "uuid": "1234-5678-9abc-def0",
      "bootstrap_config": "..."
    }
  ]
"""

EXAMPLES = r"""
# Example of using the module to sync devices from a smart account
- name: Sync devices from smart account
  cisco.catalystwan.devices_wan_edges:
    state: "present"
    sync_devices_from_smart_account: true
    username: "smartaccount_user"
    password: "smartaccount_password"  # pragma: allowlist secret

# Example of using the module to upload a WAN Edge list
- name: Upload WAN Edge list
  cisco.catalystwan.devices_wan_edges:
    state: "present"
    wan_edge_list: "/path/to/edge_list.csv"

# Example of using the module to delete WAN Edge devices by UUID
- name: Delete WAN Edge devices
  cisco.catalystwan.devices_wan_edges:
    state: "absent"
    uuid:
      - "1234-5678-9abc-def0"
      - "0987-6543-21dc-ba98"

# Example of using the module to generate bootstrap configuration for all devices
- name: Generate bootstrap configuration for all devices
  cisco.catalystwan.devices_wan_edges:
    generate_bootstrap_configuration: true
"""

import traceback
from enum import Enum
from typing import List, Optional

from catalystwan.endpoints.configuration_device_inventory import (
    DeviceDetailsResponse,
    SerialFilePayload,
    SmartAccountSyncParams,
)
from pydantic import Field

from ..module_utils.filters import get_target_device
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class State(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"


class ExtendedModuleResult(ModuleResult):
    bootstrap_configuration: Optional[List] = Field(default=[])


def generate_bootstrap_configuration(module: AnsibleCatalystwanModule, result: ExtendedModuleResult):
    def _gen_bootstrap_cfg_with_uuid(module: AnsibleCatalystwanModule, result: ExtendedModuleResult, device_uuid: str):
        module.send_request_safely(
            result=result,
            action_name="Generate bootstrap configuration",
            send_func=module.session.api.config_device_inventory_api.generate_bootstrap_cfg,
            device_uuid=device_uuid,
            response_key="bootstrap_cfg",
        )
        module.logger.info(f"Bootstrap cfg: {result.response['bootstrap_cfg']}")
        result.bootstrap_configuration.append(result.response["bootstrap_cfg"])
        result.msg += f"Generated bootstrap configuration for device with uuid: {device_uuid}"

    devices_uuid = module.params.get("uuid")
    if isinstance(devices_uuid, str):
        devices_uuid = [devices_uuid]  # if devices_uuid is a string, turn it into a list

    if "all" in devices_uuid:  # if 'all' is in the list, generate bootstrap cfg for all devices
        all_edge_devices = get_target_device(module=module, device_category="vedges", all_from_category=True)
        if not all_edge_devices:
            result.msg += "No Edge devices present on Manager!"
        else:
            for device in all_edge_devices:
                _gen_bootstrap_cfg_with_uuid(module, result, device.uuid)
    else:  # otherwise, generate bootstrap cfg for all specified device
        for device_uuid in devices_uuid:
            _gen_bootstrap_cfg_with_uuid(module, result, device_uuid)


def add_edge_devices(module: AnsibleCatalystwanModule, result: ExtendedModuleResult):
    if module.params.get("sync_devices_from_smart_account"):
        payload = SmartAccountSyncParams(**module.params_without_none_values)

        module.execute_action_safely(
            result=result,
            action_name="Sync Smart Account",
            send_func=module.session.endpoints.configuration_device_inventory.sync_devices_from_smart_account,
            payload=payload,
            success_msg="Sync Smart Account completed.",
            failure_msg="Couldn't Sync Smart Account, task failed or task has reached timeout.",
        )

    if module.params.get("wan_edge_list"):
        image_path = module.params.get("wan_edge_list")

        try:
            payload = SerialFilePayload(image_path=image_path)
        except FileNotFoundError as ex:
            module.fail_json(
                msg=f"No file found under provided filepath: {image_path}. {ex}", exception=traceback.format_exc()
            )

        module.send_request_safely(
            result=result,
            action_name="Upload WAN Edges list",
            send_func=module.session.endpoints.configuration_device_inventory.upload_wan_edge_list,
            payload=payload,
            response_key="upload_wan_edge_list",
        )

        result.changed = True
        result.msg = "Upload WAN Edges list completed."


def delete_devices(module: AnsibleCatalystwanModule, result: ExtendedModuleResult):
    devices_uuid = module.params.get("uuid")

    if isinstance(devices_uuid, str):
        devices_uuid = [devices_uuid]  # if devices_uuid is a string, turn it into a list

    if "all" in devices_uuid:
        # if 'all' is in the list, delete all devices
        all_edge_devices = module.session.endpoints.configuration_device_inventory.get_device_details(
            device_category="vedges"
        )
        for device in all_edge_devices:
            delete_device(device, module, result)
    else:
        # otherwise, delete each specified device
        for device_uuid in devices_uuid:
            device = module.session.endpoints.configuration_device_inventory.get_device_details(uuid=device_uuid)
            if device:
                delete_device(device, module, result)
            else:
                result.msg += f"Device with uuid: {device_uuid} not present in WAN Edge devices list."


def delete_device(device: DeviceDetailsResponse, module: AnsibleCatalystwanModule, result: ExtendedModuleResult):
    module.send_request_safely(
        result=result,
        action_name="Device Inventory: Delete Device",
        send_func=module.session.endpoints.configuration_device_inventory.delete_device,
        uuid=device.uuid,
        response_key="delete_device",
    )
    if "status" in result.response.delete_device.model_dump(mode="json").keys():
        if result.response.status != "success":
            module.fail_json(msg=f"Couldn't upload WAN Edge list: response.status is: {result.response.status}")
    result.changed = True
    result.msg += f"Successfully deleted WAN Edge device with uuid: {device.uuid}\n"


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=[State.PRESENT, State.ABSENT],
            default=State.PRESENT.value,
        ),
        sync_devices_from_smart_account=dict(
            type=bool,
            default=False,
        ),
        username=dict(type=str),
        password=dict(type=str, no_log=True),
        wan_edge_list=dict(type=str),  # for Upload WAN Edge List
        uuid=dict(type="raw", default="all", aliases=["devices_ids"]),
        # uuid is the ID of the device/devices to delete, or 'all' to delete all devices
        generate_bootstrap_configuration=dict(type=bool, default=False),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    # Add check to verify that if state is in provided parameters
    # then one of the options, sync or list must be defined.
    # And if state value is absent no additional parameters apart from device_id should be present

    if module.params.get("sync_devices_from_smart_account") and module.params.get("wan_edge_list"):
        module.fail_json(msg="Please provide only one option: `sync_devices_from_smart_account` or `wan_edge_list`.")

    # Check if state is present and required parameters are not set
    if module.params.get("sync_devices_from_smart_account") and (
        not module.params["username"] and not module.params["password"]  # noqa: W503
    ):
        module.fail_json(msg="'username' and 'password' are required when 'sync_devices_from_smart_account' requested")

    if module.params.get("state") == "present":
        add_edge_devices(module, result)

    if module.params.get("state") == "absent":
        delete_devices(module, result)

    if module.params.get("generate_bootstrap_configuration"):
        generate_bootstrap_configuration(module, result)

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
