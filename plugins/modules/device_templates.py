#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: Device_templates
short_description: Manage Device Templates on vManage.
version_added: "0.2.0"
description:
  - This module allows you to create, delete, attach and detach Device Templates
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
    default: null
  template_description:
    description:
      - Description for the Feature Template.
    type: str
    default: null
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
    required: false
    default: null
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - The name of the template
        required: true
        type: str
      subtemplates:
        description:
          - List of names of the subtemplates to be attached to General template
        required: false
        default: null
        type: list
        elements: str
  timeout_seconds:
    description:
      - The timeout in seconds for attaching the template. Default is 300.
    type: int
  hostname:
    description:
      - Hostname of the device to attach template. Available only for 0(state=attached).
    type: str
  device_specific_vars:
    description:
      - For parameters in a feature template that you configure as device-specific,
        when you attach a device template to a device, Cisco vManage prompts you for the values to use
        for these parameters.
    type: raw
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.device_models_device_template
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
"""

EXAMPLES = r"""
- name: Ensure a device template is present on vManage
  cisco.catalystwan.device_templates:
    state: present
    template_name: "MyDeviceTemplate"
    template_description: "This is a device template for device configuration"
    device_type: "ISR4451"
    device_role: "sdwan-edge"
    general_templates:
      - "Template1"
      - "Template2"
    manager_credentials: ...

- name: Attach a device template to a device with a specific hostname
  cisco.catalystwan.device_templates:
    state: attached
    template_name: "MyDeviceTemplate"
    hostname: "device-hostname"
    timeout_seconds: 600
    manager_credentials: ...

- name: Remove a device template from vManage
  cisco.catalystwan.device_templates:
    state: absent
    template_name: "MyDeviceTemplate"
    manager_credentials: ...

- name: Detach device - change configuration mode to CLI
  cisco.catalystwan.device_templates:
    state: detached
    hostname: "device-hostname"
    manager_credentials: ...
"""

RETURN = r"""
msg:
  description: A message describing the result of the operation.
  returned: always
  type: str
  sample: "Created template MyDeviceTemplate: MyDeviceTemplate"

changed:
  description: A boolean flag indicating if any changes were made.
  returned: always
  type: bool
  sample: true
"""

from typing import Literal, Optional, get_args

from catalystwan.api.template_api import DeviceTemplate, GeneralTemplate
from catalystwan.dataclasses import Device
from catalystwan.exceptions import TemplateNotFoundError
from catalystwan.models.common import DeviceModel
from catalystwan.models.templates import DeviceTemplateInformation
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

State = Literal["present", "absent", "attached", "detached"]


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=list(get_args(State)),
            default="present",
        ),
        template_name=dict(type="str", default=None),
        template_description=dict(type="str", default=None),
        device_type=dict(type="str", aliases=["device_model"], choices=list(get_args(DeviceModel)), default=None),
        device_role=dict(type="str", choices=["sdwan-edge", "service-node"], default="sdwan-edge"),
        general_templates=dict(
            type="list",
            elements="dict",
            options=dict(
                name=dict(type="str", required=True),
                subtemplates=dict(type="list", elements="str", default=[]),
            ),
            default=[],
        ),
        timeout_seconds=dict(type="int", default=300),
        hostname=dict(type="str"),
        device_specific_vars=dict(type="list", elements="dict"),
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
                    "device_type",
                ),
            ),
            (
                "state",
                "absent",
                ("template_name",),
            ),
            (
                "state",
                "attached",
                (
                    "template_name",
                    "hostname",
                ),
            ),
            (
                "state",
                "detached",
                ("hostname",),
            ),
        ],
    )

    template_name = module.params.get("template_name")

    all_templates: DataSequence[DeviceTemplateInformation] = module.get_response_safely(
        module.session.api.templates.get, template=DeviceTemplate
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
            general_templates = []
            for template in module.params.get("general_templates"):
                sub_templates = [GeneralTemplate(name=sub) for sub in template.get("subtemplates", [])]
                general_templates.append(GeneralTemplate(name=template["name"], subTemplates=sub_templates))

            device_template = DeviceTemplate(
                template_name=template_name,
                template_description=module.params.get("template_description"),
                device_type=module.params.get("device_type"),
                device_role=module.params.get("device_role"),
                general_templates=general_templates,
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

    if module.params.get("state") == "attached":
        hostname = module.params.get("hostname")
        device: DataSequence[Device] = (
            module.get_response_safely(module.session.api.devices.get).filter(hostname=hostname).single_or_default()
        )

        if not device:
            module.fail_json(f"No devices with hostname found, hostname provided: {hostname}")
        try:
            response = None
            if module.params.get("device_specific_vars"):
                device_specific_vars = {k: v for d in module.params.get("device_specific_vars") for k, v in d.items()}
                response = module.session.api.templates.attach(
                    name=template_name,
                    device=device,
                    device_specific_vars=device_specific_vars,
                    timeout_seconds=module.params.get("timeout_seconds"),
                )
            else:
                response = module.session.api.templates.attach(
                    name=template_name,
                    device=device,
                    timeout_seconds=module.params.get("timeout_seconds"),
                )
            if not response:
                module.fail_json(f"Failed to attach device template: {template_name}")
            result.changed = True
            result.msg = f"Attached template {template_name} to device: {hostname}"
        except ManagerHTTPError as ex:
            module.fail_json(msg=f"Could not perform attach Template {template_name}.\nManager error: {ex.info}")
        except TemplateNotFoundError as ex:
            module.fail_json(msg=f"Template with name: {template_name} doesn't exist. \nOriginal error: {ex}")
        except TypeError as ex:
            module.fail_json(msg=f"{ex}")

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

    if module.params.get("state") == "detached":
        hostname = module.params.get("hostname")
        device: DataSequence[Device] = (
            module.get_response_safely(module.session.api.devices.get).filter(hostname=hostname).single_or_default()
        )
        if not device:
            module.fail_json(f"No devices with hostname found, hostname provided: {hostname}")
        module.send_request_safely(
            result,
            action_name="Detach Template",
            send_func=module.session.api.templates.deatach,
            device=device,
        )
        result.changed = True
        result.msg = "Changed configuration mode to CLI"

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
