#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from catalystwan.utils.device_model import DeviceModel

import pkgutil
import importlib

def import_all_classes_from_library(library_name):
    imported_classes = {}

    # Find the library's location and iterate through its modules
    library_path = importlib.import_module(library_name).__path__
    for _, module_name, _ in pkgutil.iter_modules(library_path):
        # Import the module
        module = importlib.import_module(f'{library_name}.{module_name}')

        # Iterate through the module's attributes and import classes
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type):  # Check if it is a class
                imported_classes[attribute_name] = attribute

    return imported_classes

# Usage example:
# Let's say you want to import all classes from a library called 'external_library'
all_classes = import_all_classes_from_library('catalystwan.api.templates.models')
all_device_models = [device_model.value for device_model in DeviceModel]

DOCUMENTATION = r"""
---
module: vmanage_feature_template

short_description: Manage feature templates for Cisco vManage SD-WAN

version_added: "1.0.0"

description:
  - This module can be used to create, modify, and delete feature templates in Cisco vManage SD-WAN.
  - The feature template configuration is defined via Python Pydantic models.

options:
  template_name:
    description:
      - The name for the Feature Template.
    type: str
    required: true
  template_description:
    description:
      - Description for the Feature Template.
    type: str
    required: true
  device_models:
      description:
          - The model of the device.
      required: true
      type: list
      default: []
      elements: str
      choices:
        - "vmanage"
        - "vedge-cloud"
        - "vsmart"
extends_documentation_fragment:
  - cisco.catalystwan.feature_template_cisco_aaa
  - cisco.catalystwan.feature_template_cisco_banner
author:
  - Arkadiusz Cichon (acichon@cisco.com)
"""

from typing import Optional, Dict
from pydantic import Field

from catalystwan.api.template_api import FeatureTemplate
from catalystwan.dataclasses import FeatureTemplateInfo
from catalystwan.typed_list import DataSequence
from catalystwan.utils.creation_tools import asdict
from catalystwan.utils.device_model import DeviceModel
from catalystwan.api.templates.models.supported import available_models

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule
from ..module_utils.feature_templates_definitions.cisco_aaa import cisco_aaa_definition


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


def run_module():
    module_args = dict(
        template_name=dict(type="str", default=None, required=True),
        template_description=dict(type="str", default=None, required=True),
        device_models=dict(
            type="list",
            required=True,
            choices=[device_model.value for device_model in DeviceModel]),
        **cisco_aaa_definition,
        debug=dict(type="bool", default=False),  # if to dump templates payload
    )
    result = ExtendedModuleResult()
    result.state = None
    result.response = None

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    # Code for checking if template name exists already, if yes, do we need some force method or we just inform user and exit?

    for model_name, model_module in available_models.items():
        if model_name in module.params.keys():
            # Perform action with template
            template = model_module(
                template_name=module.params.get("template_name"),
                template_description=module.params.get("template_description"),
                device_models=module.params.get("device_models"),
                **module.params_without_none_values[model_name])

            module.logger.info(f"Prepared template for sending to vManage: \n{template}\n")
            
            module.session.api.templates.create(template=template, debug=module.params.get("debug")
            result.changed = True
            result.msg = f"Created template model for {model_name}: {template}"

    # all_templates: DataSequence[FeatureTemplateInfo] = module.get_response_safely(module.session.api.templates.get, template=FeatureTemplate)

    # if filters:
    #     filtered_templates = all_templates.filter(**filters)
    #     if filtered_templates:
    #         module.logger.info(f"All Feature Templates filtered with filters: {filters}:\n{filtered_templates}")
    #         result.msg = "Succesfully got all requested Feature Templates Info from vManage"
    #         result.templates_info = [asdict(template) for template in filtered_templates]
    #     else:
    #         module.logger.warning(msg=f"Feature templates filtered with `{filters}` not present.")
    #         result.msg = f"Feature templates filtered with `{filters}` not present on vManage."
    # else:
    #     result.msg = "Succesfully got all Feature Templates Info from vManage"
    #     result.templates_info = [asdict(template) for template in all_templates]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
