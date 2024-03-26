#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: devices_info
short_description: Retrieves information about devices within vManage
version_added: "0.1.0"
description:
  - This module retrieves details about devices in vManage.
  - It can filter the retrieved device information based on specified criteria.
options:
  device_category:
    description:
      - Category of devices to retrieve information for.
    type: str
    choices: ["controllers", "vedges"]
  filters:
    description:
      - Dictionary of filter key-value pairs to apply on the device details.
    type: dict
    default: None
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - The 'filters' option allows for specifying filtering criteria such as device model, status, etc.

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication

"""

RETURN = r"""
devices:
  description: A list of devices with their details based on the applied filters.
  returned: success
  type: list
  sample: |
    [
      {
        "host-name": "vmanage",
        "device-type": "controller",
        "system-ip": "192.168.1.1",
        "uuid": "1234-5678-9abc-def0",
        "status": "active"
      },
      {
        "host-name": "vsmart",
        "device-type": "controller",
        "system-ip": "192.168.1.2",
        "uuid": "0987-6543-21dc-ba98",
        "status": "active"
      }
    ]
"""

EXAMPLES = r"""
# Example of using the module to retrieve all controller devices information
- name: Get controllers devices information
  cisco.catalystwan.devices_info:
    device_category: "controllers"

# Example of using the module to retrieve all vedges devices information with filters
- name: Get vedges devices information with filters
  cisco.catalystwan.devices_info:
    device_category: "vedges"
    filters:
      model: "vedge-1000"
      status: "active"
"""

from typing import List, Optional
from pydantic import Field

from ..module_utils.filters import get_target_device
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

from catalystwan.endpoints.configuration_device_inventory import DeviceDetailsResponse
from catalystwan.typed_list import DataSequence


class ExtendedModuleResult(ModuleResult):
    devices: Optional[List] = Field(default=[])


def run_module():
    module_args = dict(
        device_category=dict(
            type=str,
            choices=["controllers", "vedges"],
        ),
        filters=dict(type=dict, default=None),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    devices = get_target_device(module, device_category=module.params.get("device_category"), all_from_category=True)

    if not devices:
        module.exit_json(**result.model_dump(mode="json"))

    if module.params.get("filters"):
        filtered_devices: DataSequence[DeviceDetailsResponse] = devices.filter(**module.params.get("filters"))
        module.logger.debug(f"All filtered_devices: {filtered_devices}")
        result.devices = [dev.model_dump(mode="json") for dev in filtered_devices]
    else:
        result.devices = [dev.model_dump(mode="json") for dev in devices]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
