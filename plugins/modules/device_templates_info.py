#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: Device_templates_info
short_description: Get information about Device Templates on vManage.
version_added: "0.1.0"
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
      template_type:
        description:
          - The type of template, eg. "system-vsmart
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

from typing import Dict, Optional

from catalystwan.api.template_api import DeviceTemplate
from catalystwan.dataclasses import DeviceTemplateInfo
from catalystwan.typed_list import DataSequence
from catalystwan.utils.creation_tools import asdict
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


def run_module():
    module_args = dict(
        filters=dict(type="dict", default=None, required=False),
    )
    result = ExtendedModuleResult()
    result.state = None
    result.response = None

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    filters = module.params.get("filters")

    all_templates: DataSequence[DeviceTemplateInfo] = module.get_response_safely(
        module.session.api.templates.get, template=DeviceTemplate
    )

    if filters:
        filtered_templates = all_templates.filter(**filters)
        if filtered_templates:
            module.logger.info(f"All Device Templates filtered with filters: {filters}:\n{filtered_templates}")
            result.msg = "Succesfully got all requested Device Templates Info from vManage"
            result.templates_info = [asdict(template) for template in filtered_templates]
        else:
            module.logger.warning(msg=f"Device templates filtered with `{filters}` not present.")
            result.msg = f"Device templates filtered with `{filters}` not present on vManage."
    else:
        result.msg = "Succesfully got all Device Templates Info from vManage"
        result.templates_info = [asdict(template) for template in all_templates]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
