#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: Device_templates
short_description: Manage Device Templates on vManage.
version_added: "0.1.1"
description:
  - This module allows you to create, delete, attach and detach Device Templates
  - Device Templates can be filtered by Device Templates Info key:values.
options:
  state:
    description:
      - Desired state for the template.
      - 0(state=present) is equivalent of create template in GUI
    type: str
    choices: ["absent", "present", "attached", "detached"]
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
  device_role:
    description:
      - The device role. Applicable to all devices except 'vManage' and 'vSmart'
    required: false
    default: null
    type: str
    choices: ["service-node", "sdwan-edge"]
  general_templates:
    description:
      - List of names of Feature Templates to be included in Device Template
      type: list
      elements: str
      required: false
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.device_models_device_template
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

from typing import Dict, Literal, Optional, get_args

from catalystwan.api.template_api import DeviceTemplate
from catalystwan.dataclasses import DeviceTemplateInfo
from catalystwan.models.common import DeviceModel
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

State = Literal["present", "absent"]


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=list(get_args(State)),
            default="present",
        ),
        template_name=dict(type="str", required=True),
        template_description=dict(type="str", default=None),
        device_type=dict(type="str", choices=list(get_args(DeviceModel)), default=None),
        device_role=dict(type="str", choices=["sdwan-edge", "service-node"], default=None),
        general_templates=dict(type="list", elements="str", default=[]),
    )
    result = ExtendedModuleResult()
    result.state = None
    result.response = None

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_if=[
            (
                "state",
                "present",
                (
                    "template_name",
                    "template_description",
                    "device_type",
                ),
            ),
            (
                "state",
                "absent",
                ("template_name",),
            ),
        ],
    )

    template_name = module.params.get("template_name")

    all_templates: DataSequence[DeviceTemplateInfo] = module.get_response_safely(
        module.session.api.templates.get, template=DeviceTemplate
    )
    target_template: DeviceTemplateInfo = all_templates.filter(name=template_name)

    if module.params.get("state") == "present":
        # Code for checking if template name exists already
        if target_template:
            module.logger.debug(f"Detected existing template:\n{target_template}\n")
            result.msg = (
                f"Template with name {template_name} already present on vManage, skipping create template operation."
            )
        else:
            device_template = DeviceTemplate(
                template_name=template_name,
                template_description=module.params.get("template_description"),
                device_type=module.params.get("device_type"),
                device_role=module.params.get("device_role"),
                general_templates=module.params.get("general_templates"),
            )

            module.logger.debug(
                f"Prepared template for sending to vManage, template configuration:\n{device_template}\n"
            )
            try:
                module.session.api.templates.create(template=device_template, debug=module.params.get("debug"))
            except ManagerHTTPError as ex:
                module.fail_json(
                    msg=f"Could not perform add Feature Template {template_name}.\nManager error: {ex.info}"
                )
            result.changed = True
            result.msg += f"Created template {template_name}: {device_template}"

        # Way to attach the template, to be implemented
        # response = provider_session.api.templates.attach(
        #     name=name,
        #     template=device_template,
        #     device=device,
        #     device_specific_vars={
        #         "//system/site-id": mt_edge.get_site_id(),
        #         "//system/host-name": mt_edge.name,
        #         "//system/system-ip": mt_edge.get_system_ip_no_mask(),
        #     },
        # )

    if module.params.get("state") == "absent":
        if target_template:
            module.send_request_safely(
                result,
                action_name="Delete Template",
                send_func=module.session.api.templates.delete,
                template=DeviceTemplate,
                name=template_name,
            )
            result.changed = True
            result.msg = f"Deleted template {template_name}"
        else:
            module.logger.debug(f"Template '{target_template}' not presend in list of Device Templates on vManage.")
            result.msg = (
                f"Template {template_name} not presend in list of Device Templates on vManage. "
                "skipping delete template operation."
            )

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
