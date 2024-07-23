#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: vmanage_feature_template
short_description: Manage feature templates for Cisco vManage SD-WAN
version_added: "0.2.0"
description:
  - This module can be used to create, modify, and delete feature templates in Cisco vManage SD-WAN.
  - The feature template configuration is defined via Python Pydantic models.
options:
  state:
    description:
      - Desired state for the template.
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
    required: false
  device_specific_variables:
    description:
      - Dictionary containing device specific variables names to be defined in template.
    type: dict
    required: false
  debug:
    description:
      - If to write payload of created template and response from vmanage as json to file.
      - Files will be written to C(CWD) as I("payload_{template.type}.json") and I("response_{template.type}.json").
    type: bool
    default: false
extends_documentation_fragment:
  - cisco.catalystwan.feature_template_aaa
  - cisco.catalystwan.feature_template_cisco_aaa
  - cisco.catalystwan.feature_template_cisco_banner
  - cisco.catalystwan.feature_template_cisco_bfd
  - cisco.catalystwan.feature_template_cisco_logging
  - cisco.catalystwan.feature_template_cisco_ntp
  - cisco.catalystwan.feature_template_cisco_omp
  - cisco.catalystwan.feature_template_cisco_ospf
  - cisco.catalystwan.feature_template_cisco_secure_internet_gateway
  - cisco.catalystwan.feature_template_cisco_snmp
  - cisco.catalystwan.feature_template_cisco_system
  - cisco.catalystwan.feature_template_cisco_vpn
  - cisco.catalystwan.feature_template_cisco_vpn_interface
  - cisco.catalystwan.feature_template_omp_vsmart
  - cisco.catalystwan.feature_template_security_vsmart
  - cisco.catalystwan.feature_template_system_vsmart
  - cisco.catalystwan.feature_template_vpn_vsmart_interface
  - cisco.catalystwan.feature_template_vpn_vsmart
  - cisco.catalystwan.device_models_feature_template
  - cisco.catalystwan.manager_authentication
author:
  - Arkadiusz Cichon (acichon@cisco.com)
"""


from typing import Dict, Final, Literal, Optional, get_args

from catalystwan.api.template_api import FeatureTemplate
from catalystwan.api.templates.device_variable import DeviceVariable
from catalystwan.api.templates.models.supported import available_models
from catalystwan.models.common import DeviceModel
from catalystwan.models.templates import FeatureTemplateInformation
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence
from pydantic import BaseModel, ConfigDict, Field

from ..module_utils.feature_templates.aaa import aaa_definition
from ..module_utils.feature_templates.cisco_aaa import cisco_aaa_definition
from ..module_utils.feature_templates.cisco_banner import cisco_banner_definition
from ..module_utils.feature_templates.cisco_bfd import cisco_bfd_definition
from ..module_utils.feature_templates.cisco_logging import cisco_logging_definition
from ..module_utils.feature_templates.cisco_ntp import cisco_ntp_definition
from ..module_utils.feature_templates.cisco_omp import cisco_omp_definition
from ..module_utils.feature_templates.cisco_ospf import cisco_ospf_definition
from ..module_utils.feature_templates.cisco_secure_internet_gateway import cisco_secure_internet_gateway_definition
from ..module_utils.feature_templates.cisco_snmp import cisco_snmp_definition
from ..module_utils.feature_templates.cisco_system import cisco_system_definition
from ..module_utils.feature_templates.cisco_vpn import cisco_vpn_definition
from ..module_utils.feature_templates.cisco_vpn_interface import cisco_vpn_interface_definition
from ..module_utils.feature_templates.omp_vsmart import omp_vsmart_definition
from ..module_utils.feature_templates.security_vsmart import security_vsmart_definition
from ..module_utils.feature_templates.system_vsmart import system_vsmart_definition
from ..module_utils.feature_templates.vpn_vsmart import vpn_vsmart_definition
from ..module_utils.feature_templates.vpn_vsmart_interface import vpn_vsmart_interface_definition
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

ALLOW: Final[str] = "allow"


class Values(BaseModel):
    model_config = ConfigDict(extra=ALLOW, populate_by_name=True)


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


State = Literal["present", "modified", "absent"]


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=list(get_args(State)),
            default="present",
        ),
        template_name=dict(type="str", required=True),
        template_description=dict(type="str", default=None),
        device_models=dict(type="list", choices=list(get_args(DeviceModel)), default=[]),
        debug=dict(type="bool", default=False),
        device_specific_variables=dict(type="raw", default={}),
        # device=dict(type="str", default=None),  # For this we need to think how to pass devices
        **aaa_definition,
        **cisco_aaa_definition,
        **cisco_banner_definition,
        **cisco_bfd_definition,
        **cisco_logging_definition,
        **cisco_ntp_definition,
        **cisco_omp_definition,
        **cisco_ospf_definition,
        **cisco_secure_internet_gateway_definition,
        **cisco_snmp_definition,
        **cisco_system_definition,
        **cisco_vpn_interface_definition,
        **cisco_vpn_definition,
        **omp_vsmart_definition,
        **security_vsmart_definition,
        **system_vsmart_definition,
        **vpn_vsmart_definition,
        **vpn_vsmart_interface_definition,
    )

    result = ExtendedModuleResult()

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_if=[
            (
                "state",
                "present",
                (
                    "template_name",
                    "template_description",
                    "device_models",
                ),
            ),
            (
                "modified",
                "modified",
                (
                    "template_name",
                    "template_description",
                    "device_models",
                ),
            ),
            (
                "state",
                "absent",
                ("template_name",),
            ),
        ],
    )
    # Verify if we are dealing with one or more templates
    template_name = module.params.get("template_name")
    device_specific_variables: Dict = module.params.get("device_specific_variables")
    module.logger.info(f"Module input: \n{module.params}\n")

    all_templates: DataSequence[FeatureTemplateInformation] = module.get_response_safely(
        module.session.api.templates.get, template=FeatureTemplate
    )
    target_template: Optional[FeatureTemplateInformation] = all_templates.filter(name=template_name)

    if module.params.get("state") == "present":
        # Code for checking if template name exists already
        if target_template:
            module.logger.debug(f"Detected existing template:\n{target_template}\n")
            result.msg = (
                f"Template with name {template_name} already present on vManage, skipping create template operation."
            )
        else:
            for model_name, model_module in available_models.items():
                if model_name in module.params.keys():
                    if module.params[model_name] is not None:
                        module.logger.debug(f"Template input:\n{module.params_without_none_values[model_name]}\n")
                        # Perform action with template

                        configuration: Dict = module.params_without_none_values[model_name]

                        # Check if any device_specific_variables defined and use them in template
                        if device_specific_variables:
                            _dsv = Values()
                            for key, value in device_specific_variables.items():
                                dev_value = DeviceVariable(name=value)
                                setattr(_dsv, key, dev_value)

                            for field, value in configuration.items():
                                if value == "device_specific_variable":
                                    configuration[field] = _dsv.model_extra[field]

                        template = model_module(
                            template_name=template_name,
                            template_description=module.params.get("template_description"),
                            device_models=module.params.get("device_models"),
                            **configuration,
                        )

                        module.logger.debug(
                            f"Prepared template for sending to vManage, template configuration:\n{template}\n"
                        )
                        try:
                            module.session.api.templates.create(template=template, debug=module.params.get("debug"))
                        except ManagerHTTPError as ex:
                            module.fail_json(
                                msg=f"Could not perform add Feature Template {template_name}.\nManager error: {ex.info}"
                            )
                        result.changed = True
                        result.msg += f"Created template {model_name}: {template}"

    if module.params.get("state") == "absent":
        if target_template:
            module.send_request_safely(
                result,
                action_name="Delete Template",
                send_func=module.session.api.templates.delete,
                template=FeatureTemplate,
                name=template_name,
            )
            result.changed = True
            result.msg = f"Deleted template {template_name}"
        else:
            module.logger.debug(f"Template '{target_template}' not presend in list of Feature Templates on vManage.")
            result.msg = (
                f"Template {template_name} not presend in list of Feature Templates on vManage, "
                "skipping delete template operation."
            )

    if module.params.get("state") == "modified":
        module.fail_json(msg="Module parameter 'modified' not implemented yet!")

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
