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
  - This module supports backup of running-config from devices. Available for all or filtered devices.
options:
  device_category:
    description:
      - Category of devices to retrieve information for.
    type: str
    choices: ["controllers", "vedges", "all"]
    default: all
  details:
    description:
      - This argument triggers the module to collect device details info.
    type: bool
    default: true
  filters:
    description:
      - Dictionary of filter key-value pairs to apply on the device details.
    type: dict
    default: None
  backup:
    description:
      - This argument triggers the module to back up the filtered device's current running-config.
        Without specified backup_options, it saves to the playbook's root "backup" folder
        or the role's root if within an Ansible role. The folder is created if it doesn't exist.
    type: bool
    default: false
  backup_dir_path:
    description:
      - Directory to store the backup. It's created if missing. Defaults to a 'backup' folder in the current directory.
    type: path
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - The C(filters) option allows for specifying filtering criteria such as device model, status, etc.
  - The C(backup) option doesn't allow to specify backup file path, it only allows to specify directory
    Backup files are always stored in format of f"{base_filename}_{timestamp}

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

from datetime import datetime
from pathlib import Path, PurePath
from pydantic import Field
from typing import List, Optional

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
            choices=["controllers", "vedges", "all"],
            default="all",
        ),
        details=dict(type=bool, default=True),
        filters=dict(type=dict, default=None),
        backup=dict(type=bool, default=False),
        backup_dir_path=dict(type="path", default=PurePath(Path.cwd() / "backup")),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    details = module.params.get("details")
    filters = module.params.get("filters")
    backup = module.params.get("backup")
    backup_dir_path: Path = Path(module.params.get("backup_dir_path"))

    devices = get_target_device(module, device_category=module.params.get("device_category"), all_from_category=True)

    if not devices:
        module.exit_json(**result.model_dump(mode="json"))

    if details:
        if filters:
            filtered_devices: DataSequence[DeviceDetailsResponse] = devices.filter(**filters)
            if filtered_devices:
                module.logger.debug(f"All filtered_devices: {filtered_devices}")
                result.devices = [dev.model_dump(mode="json") for dev in filtered_devices]
            else:
                result.msg = f"No devices found based on filters: {filters}"
        else:
            result.devices = [dev.model_dump(mode="json") for dev in devices]

    if backup:
        module.logger.info(f"{backup_dir_path}")
        try:
            backup_dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as ex:
            module.fail_json(msg=f"Cannot create or find directory: {backup_dir_path}, exception: {ex.strerror}")

        if filters:
            devices = module.get_response_safely(module.session.api.devices.get).filter(**filters)
        else:
            devices = module.get_response_safely(module.session.api.devices.get)

        if devices:
            for device in devices:
                rcfg = module.get_response_safely(module.session.api.templates.load_running, device=device)
                timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M")
                rcfg.save_as(f"{backup_dir_path}/{device.hostname}_{timestamp}")
                result.msg = (
                    f"Succesfully saved running configuration to file: {backup_dir_path}/{device.hostname}_{timestamp}"
                )
        else:
            result.msg = f"No devices found based on filters: {filters}"

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
