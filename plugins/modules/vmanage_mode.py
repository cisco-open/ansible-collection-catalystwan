#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: vmanage_mode
short_description: Manage vManage modes on Cisco devices.
version_added: "0.1.0"
description:
  - This module allows you to set vManage modes on Cisco devices.
  - Currently, it supports setting devices to 'present' state only.
  - The module will attach a CLI template to the device(s) based on its hostname.
options:
  state:
    description:
      - The state of vManage mode to enforce on the specified devices.
    type: str
    choices: ["present"]
    default: "present"
  hostnames:
    description:
      - A list of hostnames of devices to which the vManage mode will be applied.
    type: list
    elements: str
    required: true
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
  - The module does not support idempotence. If a template with the specified name exists, it will be reattached.
  - This module is in development and may not support all possible configurations and scenarios.
"""

EXAMPLES = r"""
- name: Attach default CLI template to the specified devices
  cisco.catalystwan.vmanage_mode:
    state: present
    hostnames:
      - device1
      - device2
"""

RETURN = r"""
attached_templates:
  description: A dictionary of attached templates with the key as template name and value as device hostname.
  type: dict
  returned: on success
  sample: |
    {
      "Default_device1": "device1",
      "Default_device2": "device2"
    }
msg:
  description: Messages that indicate actions taken or any errors that have occurred.
  type: str
  returned: always
  sample: "Successfully attached template: Default_device1 to device: device1"
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
  sample: true
"""

import traceback
from typing import Dict, Literal, Optional, get_args

from catalystwan.api.template_api import CLITemplate
from catalystwan.session import ManagerHTTPError
from catalystwan.utils.personality import Personality
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

State = Literal["present"]


class ExtendedModuleResult(ModuleResult):
    attached_templates: Optional[Dict] = Field(default={})


def run_module():
    module_args = dict(
        state=dict(
            type="str",
            choices=list(get_args(State)),
            default="present",
        ),
        hostnames=dict(type="list", elements="str", default=[]),
    )
    result = ExtendedModuleResult()
    module = AnsibleCatalystwanModule(argument_spec=module_args)

    try:
        devices = module.session.api.devices.get(rediscover=False)
        for hostname in module.params["hostnames"]:
            device = devices.filter(hostname=hostname).single_or_default()
            if device is None:
                module.fail_json(msg=f"Device with hostname `{hostname}` does not exits.")

    except ManagerHTTPError as ex:
        module.fail_json(msg=f"Could not fetch list of devices: {str(ex)}", exception=traceback.format_exc())

    for hostname in module.params["hostnames"]:
        device = devices.filter(hostname=hostname).single_or_default()
        try:
            template_name = f"Default-{hostname}"
            device_model = device.model
            if device.personality is Personality.VBOND:
                device_model = "vedge-cloud"

            cli_template = CLITemplate(
                template_name=template_name,
                template_description="Created for setting vManage mode.",
                device_model=device_model,
            )

            # Currently if template with that name exists, we are going to attach it once again to the device.
            existing_template = module.session.api.templates.get(cli_template).filter(name=template_name)
            if not existing_template:
                cli_template.load_running(module.session, device)
                module.session.api.templates.create(cli_template)
            else:
                result.msg += (
                    f"Template: {template_name} exists on : {device.hostname}. Trying to attach it to the device.\n"
                )
            module.session.api.templates.attach(template_name, device)

            result.changed = True
            result.attached_templates.update({template_name: device.hostname})
            result.msg += f"Successfully attached template: {template_name} to device: {device.hostname}\n"

        except ManagerHTTPError as ex:
            module.fail_json(
                msg=f"{result.msg} Could not change vManage mode: {str(ex.info)}", exception=traceback.format_exc()
            )

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
