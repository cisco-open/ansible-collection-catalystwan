#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: devices_certificates
short_description: Manages certificates for devices within vManage
version_added: "0.1.0"
description:
  - This module manages the certificates for devices in vManage.
  - It can generate a Certificate Signing Request (CSR), send configuration to controllers,
    send configuration to vBond, invalidate certificates, and change the validity of the device list.
options:
  generate_csr:
    description:
      - Whether to generate a CSR for the device.
    type: bool
    default: False
  send_to_controllers:
    description:
      - Whether to send the device list to controllers.
    type: bool
    default: False
    aliases: [ "save_vedge_list" ]
  send_to_vbond:
    description:
      - Whether to send the device list to vBond.
    type: bool
    default: False
    aliases: [ "save_vsmart_list" ]
  invalidate:
    description:
      - Whether to invalidate the device's certificates.
    type: bool
    default: False
  change_vedge_list_validity:
    description:
      - Details for changing the validity of the device list.
    type: dict
    aliases: [ "change_validity" ]
    suboptions:
      chasis_number:
        description:
          - Chassis number of the device.
        type: str
        required: True
      serial_number:
        description:
          - Serial number of the device.
        type: str
      validity:
        description:
          - Desired validity state for the device.
        type: str
        choices: [ "valid", "invalid" ]
        required: True
  device_ip:
    description:
      - Target device IP address.
    type: str
    aliases: [ "target_ip" ]
  uuid:
    description:
      - UUID of the device.
    type: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - Actions are mutually exclusive and only one action can be performed at a time.
  - At least one of the action options must be provided.
  - The 'invalidate' option requires either 'device_ip' or 'uuid' to identify the device.

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: always
  type: str
  sample: "Certificate CSR generated for device with IP: 192.168.1.1"
changed:
  description: Whether or not the state was changed.
  returned: always
  type: bool
  sample: true
response:
  description: Detailed response from the vManage API if applicable.
  returned: when API call is made
  type: dict
  sample: {"status": "success", "details": "CSR generated successfully."}
"""

EXAMPLES = r"""
# Example of using the module to generate a CSR for a device
- name: Generate CSR for device
  cisco.catalystwan.devices_certificates:
    device_ip: "192.168.1.1"
    generate_csr: true

# Example of using the module to invalidate a device's certificates
- name: Invalidate device certificates
  cisco.catalystwan.devices_certificates:
    uuid: "1234-5678-9abc-def0"
    invalidate: true

# Example of using the module to change the validity of a device in the list
- name: Change validity of device in the list
  cisco.catalystwan.devices_certificates:
    change_vedge_list_validity:
      chasis_number: "123456"
      validity: "invalid"
"""

from catalystwan.endpoints.certificate_management_device import TargetDevice, Validity, VedgeListValidityPayload

from ..module_utils.filters import get_target_device
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def run_module():
    module_args = dict(
        generate_csr=dict(type=bool, default=False),
        send_to_controllers=dict(type=bool, default=False, aliases=["save_vedge_list"]),
        send_to_vbond=dict(type=bool, default=False, aliases=["save_vsmart_list"]),
        invalidate=dict(type=bool, default=False),
        change_vedge_list_validity=dict(
            type=dict,
            aliases=["change_validity"],
            options=dict(
                chasis_number=dict(type="str", required=True),
                serial_number=dict(type="str"),
                validity=dict(type=str, choices=[Validity.VALID, Validity.INVALID], required=True),
            ),
        ),
        device_ip=dict(type=str, aliases=["target_ip"]),
        uuid=dict(type=str),
        wait_for_completed=dict(type="bool", default=True),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ("invalidate", "generate_csr"),
            ("invalidate", "send_to_controllers"),
            ("invalidate", "send_to_vbond"),
            ("invalidate", "change_vedge_list_validity"),
        ],
        required_one_of=[
            ("invalidate", "generate_csr", "send_to_controllers", "send_to_vbond", "change_vedge_list_validity")
        ],
    )
    result = ModuleResult()

    invalidate_device = False

    # ---------------------------------#
    # STEP 1 - verify module arguments #
    # ---------------------------------#
    # Handled by mutually_exclusive and required_one_of

    # ----------------------------------------------------------------#
    # STEP 2 - verify if any action required or state is changed = OK #
    # ----------------------------------------------------------------#
    if module.params.get("invalidate"):
        target_device_details = get_target_device(module=module)
        # report OK and changed=False If device not present
        if not target_device_details:
            result.msg = "Device not present in the devices list."
            result.changed = False
            module.exit_json(**result.model_dump(mode="json"))
        invalidate_device = True

    # ----------------------------------#
    # STEP 3 - perform required actions #
    # ----------------------------------#
    if invalidate_device:
        module.send_request_safely(
            result,
            action_name="Invalidate device",
            send_func=module.session.endpoints.certificate_management_device.delete_configuration,
            uuid=target_device_details.uuid,
            response_key="invalidate_device",
        )

    if module.params.get("generate_csr"):
        # Verify if we have to regenerate
        # Add force argument to the module to handle forced regenerate
        target_device_details = get_target_device(module=module, device_category="controllers")
        if target_device_details.cert_install_status == "Installed":
            result.msg = "Device already has certificate installed."
            result.changed = False
            module.exit_json(**result.model_dump(mode="json"))

        payload = TargetDevice(deviceIP=module.params.get("device_ip"))
        module.send_request_safely(
            result=result,
            action_name="Generate CSR for vManage",
            send_func=module.session.endpoints.certificate_management_device.generate_csr,
            payload=payload,
            response_key="generate_csr",
        )

    if module.params.get("send_to_controllers"):
        module.execute_action_safely(
            result,
            action_name="send to controllers",
            send_func=module.session.endpoints.certificate_management_device.send_to_controllers,
            success_msg="Send to controllers completed.\n",
            failure_msg="Couldn't send to controllers, task failed or task has reached timeout.",
            wait_for_completed=module.params.get("wait_for_completed"),
        )

    if module.params.get("send_to_vbond"):
        module.execute_action_safely(
            result,
            action_name="Send to vBond",
            send_func=module.session.endpoints.certificate_management_device.send_to_vbond,
            success_msg="Send to vBond (Save vSmart List) completed.\n",
            failure_msg="Couldn't send to vBond (Save vSmart List), task failed or task has reached timeout.",
            wait_for_completed=module.params.get("wait_for_completed"),
        )

    if module.params.get("change_vedge_list_validity"):
        payload = [VedgeListValidityPayload(**module.params.get("change_vedge_list_validity"))]
        module.execute_action_safely(
            result,
            action_name="Change edge list validity",
            send_func=module.session.endpoints.certificate_management_device.change_vedge_list_validity,
            success_msg="Invalidate devices completed.\n",
            failure_msg="Couldn't Invalidate devices, task failed or task has reached timeout.",
            payload=payload,
            wait_for_completed=module.params.get("wait_for_completed"),
        )

    # ----------------------------------#
    # STEP 4 - update and return result #
    # ----------------------------------#
    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
