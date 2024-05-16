#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: devices_controllers
short_description: Manages devices within vManage
version_added: "0.1.0"
description:
  - This module can be used to add or invalidate controller devices in vManage.
  - It supports the creation of a new device with a generated CSR and specifies the device personality.
  - When invalidating, it requires either the UUID or device IP to identify the device.
options:
  state:
    description:
      - Desired state of the device.
    type: str
    choices: ["present", "invalidated"]
    default: "present"
  username:
    description:
      - Username for the device being managed.
    type: str
  password:
    description:
      - Password for the device being managed.
    type: str
    no_log: True
  personality:
    description:
      - Personality of the device. Choices are 'vSmart', 'vBond', or 'vManage'.
    type: str
    choices: ["vSmart", "vBond", "vManage"]
  generate_csr:
    description:
      - Whether to generate a CSR (Certificate Signing Request) for the device.
    type: bool
    default: True
  port:
    description:
      - Port used by the device.
    type: str
  protocol:
    description:
      - Protocol used by the device. Choices are 'DTLS' or 'TLS'.
    type: str
    choices: ["DTLS", "TLS"]
  device_ip:
    description:
      - Transport IP address of the device.
    type: str
  uuid:
    description:
      - UUID of the device.
    type: str
  hostname:
    description:
      - Hostname of the device.
    type: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)
notes:
  - "Only vSmart, vBond, and vManage device personalities are currently supported."
  - "The 'state' option 'invalidated' will delete the device configuration in vManage."
  - "For 'present' state, 'username', 'password', 'personality', and 'device_ip' are required."
  - "For 'invalidated' state, either 'uuid' or 'device_ip' is required."
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: always
  type: str
  sample: "Added new device: 192.168.1.1, personality: vSmart"
response:
  description: Detailed response from the vManage API if applicable.
  returned: when API call is made
  type: dict
  sample: {"status": "success", "details": "Device added successfully."}
changed:
  description: Whether or not the state was changed.
  returned: always
  type: bool
  sample: true
"""

EXAMPLES = r"""
# Example of using the module to add a new device
- name: Add new device
  cisco.catalystwan.devices_controllers:
    username: "admin"
    password: "admin"  # pragma: allowlist secret
    personality: "vSmart"
    device_ip: "192.168.1.1"
    state: "present"

# Example of using the module to invalidate an existing device using UUID
- name: Invalidate device using UUID
  cisco.catalystwan.devices_controllers:
    uuid: "1234-5678-9abc-def0"
    state: "invalidated"
"""

from catalystwan.endpoints.configuration_device_inventory import DeviceCreationPayload
from catalystwan.utils.personality import Personality

from ..module_utils.filters import get_target_device
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def run_module():
    module_args = dict(
        state=dict(
            type=str,
            choices=["present", "invalidated"],
            default="present",
        ),
        username=dict(type=str),
        password=dict(type=str, no_log=True),
        personality=dict(type=str, choices=[Personality.VSMART, Personality.VBOND, Personality.VMANAGE]),
        generate_csr=dict(type=bool, default=True),
        port=dict(type=str),
        protocol=dict(type=str, choices=["DTLS", "TLS"]),
        device_ip=dict(type=str),  # Add hint that unlike in GUI it has to be transport ip
        uuid=dict(type=str),
        hostname=dict(type="str"),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ModuleResult()

    # Check if state is present and required parameters are not set
    if module.params["state"] == "present" and (
        not module.params["username"]
        and not module.params["password"]  # noqa: W503
        and not module.params["personality"]  # noqa: W503
        and not module.params["device_ip"]  # noqa: W503
    ):
        module.fail_json(msg="username, password, personality and device_ip are required when state is 'present'")

    if module.params["state"] == "invalidated" and not (module.params["uuid"] or module.params["device_ip"]):
        module.fail_json(msg="uuid or device_ip is required when state is 'invalidated'")

    target_device_details = get_target_device(module=module, device_category="controllers")

    if module.params.get("state") == "present":
        # report OK and changed=False If device is present
        if target_device_details:
            result.msg = (
                f"Device with device_ip='{target_device_details.device_ip}' already present in the devices list."
            )
            module.exit_json(**result.model_dump(mode="json"))

        payload = DeviceCreationPayload(**module.params_without_none_values)

        # Configuration - Device Inventory - Create new device
        module.send_request_safely(
            result=result,
            action_name="Device Inventory: Create Device",
            send_func=module.session.endpoints.configuration_device_inventory.create_device,
            payload=payload,
            response_key="create_device",
        )
        result.changed = True
        result.msg = f"Added new device: {payload.device_ip}, personality: {payload.personality}\n"

    if module.params["state"] == "invalidated":
        # report OK and changed=False If device not present
        if not target_device_details:
            result.msg = "Device not present in the devices list."
            module.exit_json(**result.model_dump(mode="json"))

        module.send_request_safely(
            result=result,
            action_name="Certificate Management Device: Delete Configuration",
            send_func=module.session.endpoints.certificate_management_device.delete_configuration,
            uuid=target_device_details.uuid,
            response_key="invalidate_device",
        )
        result.changed = True
        result.msg = f"Invalidated device with uuid: {target_device_details.uuid}"

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
