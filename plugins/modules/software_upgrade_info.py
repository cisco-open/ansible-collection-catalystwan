#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: software_upgrade_info

short_description: Gathers information about software upgrades on devices managed by vManage

version_added: "0.1.0"

description:
  - This module can be used to retrieve information about software upgrades on devices managed by vManage.
  - It allows for fetching a list of installed devices with the option to filter based on specific criteria.

options:
  device_type:
    description:
      - Type of device to fetch software upgrade information for.
    type: str
    required: False
    choices: ['vedge', 'controller', 'vmanage']
    default: 'controller'
  filters:
    description:
      - Optional filters to apply on the list of installed devices.
    type: dict
    default: None
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

EXAMPLES = r"""
# Example of getting software upgrade information for all controller devices
- name: Get software upgrade info for controllers
  cisco.catalystwan.software_upgrade_info:
    device_type: controller

# Example of getting software upgrade information for vEdge devices with specific filters
- name: Get software upgrade info for vEdge devices with filters
  cisco.catalystwan.software_upgrade_info:
    device_type: vedge
    filters:
      version: "20.3.2"
      status: "installed"

# Example of getting software upgrade information for vManage without any filters
- name: Get software upgrade info for vManage
  cisco.catalystwan.software_upgrade_info:
    device_type: vmanage
"""

RETURN = r"""
installed_devices:
  description: List of installed devices with software upgrade information.
  returned: always
  type: list
  elements: dict
  contains:
    deviceModel:
      description: The model of the device.
      type: str
      returned: when device is present
      sample: "vEdge 1000"
    deviceType:
      description: The type of the device.
      type: str
      returned: when device is present
      sample: "controller"
    version:
      description: The software version installed on the device.
      type: str
      returned: when device is present
      sample: "20.3.2"
    status:
      description: The status of the software on the device.
      type: str
      returned: when device is present
      sample: "installed"
    # Other fields returned by the InstalledDeviceData model_dump method
"""

from typing import List, Optional

from catalystwan.endpoints.configuration_device_actions import InstalledDeviceData
from catalystwan.typed_list import DataSequence
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    installed_devices: Optional[List] = Field(default=[])


def run_module():
    module_args = dict(
        device_type=dict(type=str, required=False, choices=["vedge", "controller", "vmanage"], default="controller"),
        filters=dict(type=dict, default=None),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
    )
    result = ExtendedModuleResult()
    device_type = module.params.get("device_type")

    installed_devices_info: DataSequence[InstalledDeviceData] = module.get_response_safely(
        module.session.endpoints.configuration_device_actions.get_list_of_installed_devices,
        device_type=device_type,
    )
    module.logger.info(f"get_list_of_installed_devices response: {installed_devices_info}")
    module.logger.debug(f"Filter: {module.params.get('filters')}")

    if module.params.get("filters"):
        filtered_installed_devices_info: DataSequence[InstalledDeviceData] = installed_devices_info.filter(
            **module.params.get("filters")
        )
        module.logger.debug(f"All filtered_remote_servers: {filtered_installed_devices_info}")
        result.installed_devices = [server.model_dump(mode="json") for server in filtered_installed_devices_info]
    else:
        result.installed_devices = [server.model_dump(mode="json") for server in installed_devices_info]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
