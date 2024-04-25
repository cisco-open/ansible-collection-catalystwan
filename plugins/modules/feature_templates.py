#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: vmanage_feature_template

short_description: Manage feature templates for Cisco vManage SD-WAN

version_added: "1.0.0"

description:
  - This module can be used to create, modify, and delete feature templates in Cisco vManage SD-WAN.
  - The feature template configuration is defined via Python Pydantic models.

options:
  state:
    description:
      - Desired state of for the template.
      - 0(state=present) is equivalent of create template in GUI
    type: str
    choices: ["absent", "present", "modified"]
    default: "present"
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
  debug:
    description:
      - If to write payload of created template and response from vmanage as json to file.
      - Files will be written to C(CWD) as I("payload_{template.type}.json") and I("response_{template.type}.json").
    type: bool
    default: false
extends_documentation_fragment:
  - cisco.catalystwan.feature_template_cisco_aaa
  - cisco.catalystwan.feature_template_cisco_banner
  - cisco.catalystwan.feature_template_cisco_bfd
  - cisco.catalystwan.feature_template_cisco_logging
  - cisco.catalystwan.feature_template_cisco_ntp
  - cisco.catalystwan.device_models_feature_template
author:
  - Arkadiusz Cichon (acichon@cisco.com)
"""


from enum import Enum
from pydantic import Field
from typing import Optional, Dict

from catalystwan.api.template_api import FeatureTemplate
from catalystwan.dataclasses import FeatureTemplateInfo
from catalystwan.typed_list import DataSequence
from catalystwan.utils.device_model import DeviceModel
from catalystwan.api.templates.models.supported import available_models

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule
from ..module_utils.feature_templates.cisco_aaa import cisco_aaa_definition
from ..module_utils.feature_templates.cisco_banner import cisco_banner_definition
from ..module_utils.feature_templates.cisco_bfd import cisco_bfd_definition
from ..module_utils.feature_templates.cisco_logging import cisco_logging_definition
from ..module_utils.feature_templates.cisco_ntp import cisco_ntp_definition


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


class State(str, Enum):
    PRESENT = "present"
    MODIFIED = "modified"
    ABSENT = "absent"


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=[State.PRESENT, State.ABSENT, State.MODIFIED],
            default=State.PRESENT.value,
        ),
        template_name=dict(type="str", required=True),
        template_description=dict(type="str", default=None),
        device_models=dict(type="list", choices=[device_model.value for device_model in DeviceModel]),
        debug=dict(type="bool", default=False),
        device=dict(type="str", default=None),  # For this we need to think how to pass devices
        **cisco_aaa_definition,
        **cisco_banner_definition,
        **cisco_bfd_definition,
        **cisco_logging_definition,
        **cisco_ntp_definition,
    )

    result = ExtendedModuleResult()
    result.state = None
    result.response = None

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_if=[
            (
                "state",
                State.PRESENT.value,
                (
                    "template_name",
                    "template_description",
                    "device_models",
                ),
                True,
            ),
            (
                "modified",
                State.MODIFIED.value,
                (
                    "template_name",
                    "template_description",
                    "device_models",
                ),
                True,
            ),
            ("state", State.ABSENT.value, ("template_name",), True),
        ],
    )
    # Verify if we are dealing with one or more templates
    template_name = module.params.get("template_name")
    module.logger.info(f"Module input: \n{module.params}\n")

    all_templates: DataSequence[FeatureTemplateInfo] = module.get_response_safely(
        module.session.api.templates.get, template=FeatureTemplate
    )
    target_template = all_templates.filter(name=template_name)

    # Code for checking if template name exists already
    # if yes, do we need some force method or we just inform user and exit?
    if module.params.get("state") == "present":
        if target_template:
            module.logger.debug(f"Detected existing template:\n{target_template}\n")
            result.msg = (
                f"Template with name {template_name} already present on vManage," "skipping create template operation."
            )
        else:
            for model_name, model_module in available_models.items():
                if model_name in module.params.keys() and module.params[model_name] is not None:
                    module.logger.debug(f"Template input:\n{module.params_without_none_values[model_name]}\n")
                    # Perform action with template
                    template = model_module(
                        template_name=template_name,
                        template_description=module.params.get("template_description"),
                        device_models=module.params.get("device_models"),
                        **module.params_without_none_values[model_name],
                    )

                    module.logger.debug(
                        f"Prepared template for sending to vManage, template configuration:\n{template}\n"
                    )

                    module.session.api.templates.create(template=template, debug=module.params.get("debug"))
                    result.changed = True
                    result.msg += f"Created template {model_name}: {template}"

    if module.params.get("state") == "absent":
        module.session.api.templates.delete(template=FeatureTemplate, name=template_name)
        result.changed = True
        result.msg = f"Deleted template {template_name}"

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
