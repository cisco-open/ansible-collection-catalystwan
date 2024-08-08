#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: Device_templates_info
short_description: Get information about Device Templates on vManage.
version_added: "0.2.0"
description:
  - This module allows you to get Device Templates Info from vManage.
  - Device Templates can be filtered by Device Templates Info key:values.
options:
  filters:
    description:
      - A dictionary of filters used to select Device Templates info.
    type: dict
    required: false
    suboptions:
      config_type:
        description:
          - The type of template, file == cli, template == feature
        required: false
        default: null
        type: str
      device_type:
        description:
          - The device type of the template
        required: false
        default: null
        type: list
        elements: str
      name:
        description:
          - The name of the Device Template.
        required: false
        default: null
        type: str
      description:
        description:
          - Description of the Device Template.
        required: false
        default: null
        type: str
      version:
        description:
          - Version of the Device Template.
        required: false
        default: null
        type: str
      factory_default:
        description:
          - If template is Factory Default template.
        required: false
        default: null
        type: bool
      template_definiton:
        description:
          - The definiton of Device Template.
        required: false
        default: null
        type: str
      devices_attached:
        description:
          - Number of attached devices.
        required: false
        default: null
        type: int
      draft_mode:
        description:
          - The draft mode of template.
        required: false
        default: null
        type: str
      device_role:
        description:
          - The device role.
        required: false
        default: null
        type: str
      id:
        description:
          - Device Template ID.
        required: false
        default: null
        type: str
      last_updated_on:
        description:
          - Last Updated on value.
        required: false
        default: null
        type: int
      last_updated_by:
        description:
          - Last Updated by value.
        required: false
        default: null
        type: str
      resource_group:
        description:
          - Resource Group value.
        required: false
        default: null
        type: str
  backup:
    description:
      - This argument triggers the module to back up the filtered Device Templates.
        Device Template backup is dumped json payload with template definition.
        Without specified backup_dir_path, it saves to the playbook's root "backup" folder
        or the role's root if within an Ansible role. The folder is created if it doesn't exist.
    type: bool
    default: false
  backup_dir_path:
    description:
      - Directory to store the backup. It's created if missing. Defaults to a 'backup' folder in the current directory.
    type: path
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
"""

EXAMPLES = r"""
- name: Get all Non-Default Device Templates available
  cisco.catalystwan.device_templates_info:
    filters:
      factory_default: false
    manager_credentials:
      ...
    register: device_templates
"""

RETURN = r"""
template_info:
  description: A list of dictionaries of templates info
  type: list
  returned: on success
  sample: |
    templates_info:
    - configType: template
      deviceRole: sdwan-edge
      deviceType: vedge-C8000V
      devicesAttached: 0
      draftMode: Disabled
      factoryDefault: false
      lastUpdatedBy: example_admin
      lastUpdatedOn: 1715270833776
      resourceGroup: global
      templateAttached: 11
      templateClass: cedge
      templateDescription: xd
      templateId: xxx-xxx-xxx
      templateName: xd
msg:
  description: Messages that indicate actions taken or any errors that have occurred.
  type: str
  returned: always
  sample: "Successfully fetched information about template: trial-template"
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
  sample: false
"""

import json
import traceback
from pathlib import Path, PurePath
from typing import Dict, List, Optional

from catalystwan.api.template_api import DeviceTemplate
from catalystwan.models.templates import DeviceTemplateInformation
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence
from pydantic import BaseModel, Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class BackupPathModel(BaseModel):
    hostname: str
    filename: str
    backup_path: str


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})
    backup_paths: Optional[List[BackupPathModel]] = Field(default=[])


def run_module():
    module_args = dict(
        filters=dict(type="dict", default=None, required=False),
        backup=dict(type=bool, default=False),
        backup_dir_path=dict(type="path", default=PurePath(Path.cwd() / "backup")),
    )
    result = ExtendedModuleResult()

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    filters = module.params.get("filters")
    filtered_templates = DataSequence(DeviceTemplateInformation)

    all_templates: DataSequence[DeviceTemplateInformation] = module.get_response_safely(
        module.session.api.templates.get, template=DeviceTemplate
    )

    if filters:
        filtered_templates = all_templates.filter(**filters)
        if filtered_templates:
            module.logger.info(f"All Device Templates filtered with filters: {filters}:\n{filtered_templates}")
            result.msg = "Succesfully got all requested Device Templates Info from vManage"
            result.templates_info = [template for template in filtered_templates]
        else:
            module.logger.warning(msg=f"Device templates filtered with `{filters}` not present.")
            result.msg = f"Device templates filtered with `{filters}` not present on vManage."
    else:
        result.msg = "Succesfully got all Device Templates Info from vManage"
        result.templates_info = [template for template in all_templates]

    if module.params.get("backup"):
        backup_dir_path: Path = Path(module.params.get("backup_dir_path"))
        module.logger.info(f"{backup_dir_path}")
        try:
            backup_dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as ex:
            module.fail_json(msg=f"Cannot create or find directory: {backup_dir_path}, exception: {ex.strerror}")

        templates_to_backup = filtered_templates if filtered_templates else all_templates
        if templates_to_backup:
            for template in templates_to_backup:
                try:
                    template_payload = module.session.get(f"dataservice/template/device/object/{template.id}").json()
                except ManagerHTTPError as ex:
                    module.fail_json(
                        msg=(
                            f"Could not call get DeviceTemplate payload for template with name: {template.name}. "
                            f"\nManager error: {ex.info}"
                        ),
                        exception=traceback.format_exc(),
                    )
                filename = f"{template.name}.json"
                backup_path = f"{backup_dir_path}/{filename}"
                with open(backup_path, "w", encoding="utf-8") as file:
                    json.dump(template_payload, file, ensure_ascii=False, indent=4)
                result.backup_paths.append(
                    BackupPathModel(hostname=template.name, backup_path=backup_path, filename=filename)
                )
                result.msg = f"Succesfully saved Device Template payload to file: {backup_path}"
        else:
            module.module.warn(f"No Device Templates found based on filters: {filters}")

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
