#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: device_templates_recovery
short_description: Backup and restore Device Templates
version_added: "0.2.0"
description:
  - This module allows you to backup and restore Device Templates.
  - With 0(mode=backup), it exports Device Templates (with Feature Templates and Policies)
    and store them to tar archive.
  - With 0(mode=restore), it extracts the templates from a tar archive, loads the JSON data for device,
    feature, and policy templates, and then processes them to create or update the templates.
    Templates will be extracted to Path(Path.cwd() / "templates") location.
  - If 0(backup_dir_path) already exists, it will be removed and new empty director will be created.
options:
  mode:
    description:
      - Desired recovery operation.
    type: str
    choices: ["backup", "restore"]
    default: "backup"
  backup_dir_path:
    description:
      - With 0(mode=backup), directory to store the backup. It's created if missing.
        Defaults to a 'default_templates' folder in the current directory.
      - With 0(mode=restore), directory containing the tar archive of templates.
    type: path
  filters:
    description:
      - A dictionary of filters used to select Device Templates to backup.
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
        default: false
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
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from pathlib import Path, PurePath

from catalystwan.session import ManagerHTTPError
from catalystwan.workflows import backup_restore_device_templates

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def run_module():
    module_args = dict(
        mode=dict(
            type=str,
            choices=list(["backup", "restore"]),
            default="backup",
        ),
        filters=dict(type="dict", default={"factory_default": False}, required=False),
        backup_dir_path=dict(type="path", default=PurePath(Path.cwd() / "backup")),
    )
    result = ModuleResult()

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    filters = module.params.get("filters")
    backup_dir_path: Path = Path(module.params.get("backup_dir_path"))

    if module.params.get("mode") == "backup":
        try:
            backup_restore_device_templates.export_templates(
                session=module.session,
                templates_directory=backup_dir_path,
                filters=filters,
                force_existing_dir_removal=True,
            )
        except ManagerHTTPError as ex:
            module.fail_json(msg=f"Could not perform Backup of Device Templates.\nManager error: {ex.info}")
        result.changed = True
        result.msg += f"Successfully exported and archived Device Templates to directory: {backup_dir_path}"
        result.msg += "See catalystwan log file for more details."

    if module.params.get("mode") == "restore":
        try:
            backup_restore_device_templates.import_templates(
                session=module.session, templates_directory=backup_dir_path
            )
        except ManagerHTTPError as ex:
            module.fail_json(msg=f"Could not perform Import of Device Templates.\nManager error: {ex.info}")
        result.changed = True
        result.msg += f"Successfully imported Device Templates to Manager from directory: {backup_dir_path}"
        result.msg += "See catalystwan log file for more details."

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
