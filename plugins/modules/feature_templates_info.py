#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: feature_templates_info
short_description: Get information about Feature Templates on vManage.
version_added: "0.2.0"
description:
  - This module allows you to get and filter Feature Templates from vManage.
options:
  filters:
    description:
      - A dictionary of filters used to select Feature Templates info.
    type: dict
    required: false
    suboptions:
      template_type:
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
          - The name of the Feature Template.
        required: false
        default: null
        type: str
      description:
        description:
          - Description of the Feature Template.
        required: false
        default: null
        type: str
      version:
        description:
          - Version of the Feature Template.
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
          - The definiton of Feature Template.
        required: false
        default: null
        type: str
      devices_attached:
        description:
          - Number of attached devices.
        required: false
        default: null
        type: int
      id:
        description:
          - Feature Template ID.
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
- name: Get all Non-Default Feature Templates available
  cisco.catalystwan.feature_templates_info:
    filters:
      factory_default: false
    manager_credentials:
      ...
    register: feature_templates
"""

RETURN = r"""
template_info:
  description: A list of dictionaries of templates info
  type: list
  returned: on success
  sample: |
    templates_info:
    - deviceType:
      - vedge-C8000V
      devicesAttached: 0
      factoryDefault: false
      lastUpdatedBy: example_user
      lastUpdatedOn: 111111111
      resourceGroup: example_groupo
      templateDefinition: null
      templateDescription: AAA Template with both TACACS+ and RADIUS servers
      templateId: xxxx-xxxx-xxxx-xxxx
      templateMinVersion: X.X.X.X
      templateName: example_name
      templateType: cedge_aaa
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

from catalystwan.api.template_api import FeatureTemplate
from catalystwan.models.templates import FeatureTemplateInformation
from catalystwan.typed_list import DataSequence
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

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    filters = module.params.get("filters")

    all_templates: DataSequence[FeatureTemplateInformation] = module.get_response_safely(
        module.session.api.templates.get, template=FeatureTemplate
    )

    if filters:
        filtered_templates = all_templates.filter(**filters)
        if filtered_templates:
            module.logger.info(f"All Feature Templates filtered with filters: {filters}:\n{filtered_templates}")
            result.msg = "Succesfully got all requested Feature Templates Info from vManage"
            result.templates_info = [template for template in filtered_templates]
        else:
            module.logger.warning(msg=f"Feature templates filtered with `{filters}` not present.")
            result.msg = f"Feature templates filtered with `{filters}` not present on vManage."
    else:
        result.msg = "Succesfully got all Feature Templates Info from vManage"
        result.templates_info = [template for template in all_templates]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
