#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: cli_templates
short_description: Manage CLI templates in Cisco SDWAN
version_added: "0.2.0"
description:
  - This module allows you to create or delete CLI templates in Cisco SDWAN.
options:
  state:
    description:
      - Whether the CLI template should be present or absent on the Cisco SDWAN.
    required: false
    type: str
    choices: ["present", "absent"]
    default: "present"
  template_name:
    description:
      - The name of the CLI template.
    required: true
    type: str
  template_description:
    description:
      - The description of the CLI template.
    required: false
    type: str
    default: None
  config_file:
    description:
      - The path to the configuration file that contains the CLI template content.
    required: false
    type: str
    aliases: ["running_config_file_path"]
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.device_models_device_template
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
"""

EXAMPLES = r"""
- name: Using configuration from file, ensure a CLI template is present on vManage
  cisco.catalystwan.cli_templates:
    state: present
    template_name: "MyTemplate"
    template_description: "This is a CLI template for device configuration"
    device_model: "ISR4451"
    config_file: "/path/to/config_file.txt"
    manager_credentials: ...

- name: Remove a CLI template from vManage
  cisco.catalystwan.cli_templates:
    state: absent
    template_name: "MyTemplate"
    manager_credentials: ...
"""

RETURN = r"""
msg:
  description: A message describing the result of the operation.
  returned: always
  type: str
  sample: "Created template MyTemplate: MyTemplate. Template id: abc123"
changed:
  description: A boolean flag indicating if any changes were made.
  returned: always
  type: bool
  sample: true
template_id:
  description: The ID of the template that was created or modified.
  returned: when a template is created
  type: str
  sample: "abc123"
"""

from typing import Literal, Optional, get_args

from catalystwan.api.template_api import CLITemplate
from catalystwan.models.common import DeviceModel
from catalystwan.models.templates import DeviceTemplateInformation
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

State = Literal["present", "absent"]


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=list(get_args(State)),
            default="present",
        ),
        template_name=dict(type="str", required=True),
        template_description=dict(type="str", default=None),
        device_model=dict(type="str", aliases=["device_type"], choices=list(get_args(DeviceModel)), default=None),
        config_file=dict(type="str", aliases=["running_config_file_path"]),
    )
    result = ModuleResult()

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_if=[
            (
                "state",
                "present",
                (
                    "template_name",
                    "template_description",
                    "device_model",
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

    all_templates: DataSequence[DeviceTemplateInformation] = module.get_response_safely(
        module.session.api.templates.get, template=CLITemplate
    )
    target_template: Optional[DeviceTemplateInformation] = all_templates.filter(name=template_name)

    if module.params.get("state") == "present":
        # Code for checking if template name exists already
        if target_template:
            module.logger.debug(f"Detected existing template:\n{target_template}\n")
            result.msg = (
                f"Template with name {template_name} already present on vManage, skipping create template operation."
            )
        else:
            cli_template = CLITemplate(
                template_name=template_name,
                template_description=module.params.get("template_description"),
                device_model=module.params.get("device_model"),
            )
            cli_template.load_from_file(file=module.params.get("config_file"))

            module.logger.debug(f"Prepared template for sending to vManage, template configuration:\n{cli_template}\n")
            try:
                template_id: str = module.session.api.templates.create(
                    template=cli_template, debug=module.params.get("debug")
                )
            except ManagerHTTPError as ex:
                module.fail_json(
                    msg=f"Could not perform create CLI Template {template_name}.\nManager error: {ex.info}"
                )
            result.changed = True
            result.msg += f"Created template {template_name}: {cli_template.template_name}. Template id: {template_id}"

    if module.params.get("state") == "absent":
        if target_template:
            module.send_request_safely(
                result,
                action_name="Delete Template",
                send_func=module.session.api.templates.delete,
                template=CLITemplate,
                name=template_name,
            )
            result.changed = True
            result.msg = f"Deleted template {template_name}"
        else:
            module.logger.debug(f"Template '{target_template}' not presend in list of Templates on vManage.")
            result.msg = (
                f"Template {template_name} not presend in list of CLI Templates on vManage. "
                "skipping delete template operation."
            )

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
