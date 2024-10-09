#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: cluster_management
short_description: Cluster configuration for vManage devices
version_added: "0.2.1"
description: This module can be used to add or edit existing controller devices to cluster configuration.
options:
  wait_until_configured_seconds:
    description:
      - How much time (in seconds) to wait for the device to connect to cluster post configuration.
    type: int
    default: 0
  vmanage_id:
    description:
      - Optional ID of vManage to edit. Don't set when adding new vManage instances to cluster.
    type: str
  device_ip:
    description:
      - Added/edited device IP address.
    type: str
  username:
    description:
      - Username for the device being managed.
    type: str
  password:
    description:
      - Password for the device being managed.
    type: str
    no_log: True
  gen_csr:
    description:
      - Whether to generate a CSR (Certificate Signing Request) for the device.
    type: bool
  persona:
    description:
      - Persona of the device. Choices are 'COMPUTE_AND_DATA', 'COMPUTE', or 'DATA'.
    type: str
    choices: ["COMPUTE_AND_DATA", "COMPUTE", "DATA"]
  services:
    description:
      - A dict containing the services of cluster device,
        such as Cisco Software-Defined Application Visibility and Control.
    type: dict
author:
  - Przemyslaw Susko (sprzemys@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: always
  type: str
  sample: "Successfully updated requested vManage configuration."
response:
  description: Detailed response from the vManage API if applicable.
  returned: when API call is made
  type: dict
  sample: {"edit_vmanage": "successMessage": "Edit Node operation performed. The operation may take some time and
    may cause application-server to restart in between"}
changed:
  description: Whether or not the state was changed.
  returned: always
  type: bool
  sample: true
"""

EXAMPLES = r"""
# Example of using the module to edit parameters of vManage added to cluster
- name: "Edit vManage"
  cisco.catalystwan.cluster_management:
    wait_until_configured_seconds: 300
    vmanage_id: "0"
    device_ip: "1.1.1.1"
    username: "username"
    password: "password"  # pragma: allowlist secret
    persona: "COMPUTE_AND_DATA"
    services:
      sd-avc:
        server: false

# Example of using the module to add a new vManage to cluster
- name: "Add vManage to cluster"
  cisco.catalystwan.cluster_management:
    wait_until_configured_seconds: 300
    device_ip: "2.2.2.2"
    username: "username"
    password: "password"  # pragma: allowlist secret
    gen_csr: false
    persona: "DATA"
    services:
      sd-avc:
        server: false
"""

import time
from typing import Optional

from catalystwan.endpoints.cluster_management import VManageSetup
from catalystwan.exceptions import ManagerRequestException

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def get_connected_devices(module, device_ip):
    result = ModuleResult()
    module.send_request_safely(
        result,
        action_name=f"Get connected devices for {device_ip}",
        send_func=module.session.endpoints.cluster_management.get_connected_devices,
        vmanageIP=device_ip,
        response_key="connected_devices",
        fail_on_exception=False,
    )
    try:
        return result.response["connected_devices"]
    except KeyError:
        return None


def wait_for_connected_devices(module, device_ip, timeout) -> Optional[str]:
    start = time.time()
    while True:
        try:
            connected_devices = get_connected_devices(module, device_ip)
            if connected_devices:
                return None
            if (time.time() - start) > timeout:
                return f"reached timeout of {timeout}s"
            time.sleep(1)
        except ManagerRequestException:
            time.sleep(1)
            continue
    return "unknown exception occurred"


def run_module():
    module_args = dict(
        wait_until_configured_seconds=dict(type="int", default=0),
        vmanage_id=dict(type=str),
        device_ip=dict(type=str, required=True),
        username=dict(type=str, required=True),
        password=dict(type=str, no_log=True, required=True),
        gen_csr=dict(type=bool, aliases=["genCSR"]),
        persona=dict(type=str, choices=["COMPUTE_AND_DATA", "COMPUTE", "DATA"], required=True),
        services=dict(
            type="dict",
            options=dict(
                sd_avc=dict(
                    type="dict",
                    aliases=["sd-avc"],
                    options=dict(
                        server=dict(type="bool"),
                    ),
                ),
            ),
        ),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args, session_reconnect_retries=180)
    result = ModuleResult()

    vmanage_id = module.params.get("vmanage_id")
    device_ip = module.params.get("device_ip")

    connected_devices = get_connected_devices(module, device_ip)
    if connected_devices:
        result.changed = False
        result.msg = f"Device {device_ip} already configured"
        module.exit_json(**result.model_dump(mode="json"))

    payload = VManageSetup(
        vmanage_id=vmanage_id,
        device_ip=device_ip,
        username=module.params.get("username"),
        password=module.params.get("password"),
        persona=module.params.get("persona"),
        services=module.params.get("services"),
    )

    if vmanage_id:
        module.send_request_safely(
            result,
            action_name="Cluster Management: Edit vManage",
            send_func=module.session.endpoints.cluster_management.edit_vmanage,
            payload=payload,
            response_key="edit_vmanage",
        )
    else:
        module.session.request_timeout = 60
        module.send_request_safely(
            result,
            action_name="Cluster Management: Add vManage",
            send_func=module.session.endpoints.cluster_management.add_vmanage,
            payload=payload,
            response_key="add_vmanage",
            num_retries=30,
            retry_interval_seconds=10,
        )

    if result.changed:
        wait_until_configured_seconds = module.params.get("wait_until_configured_seconds")
        if wait_until_configured_seconds:
            error_msg = wait_for_connected_devices(module, device_ip, wait_until_configured_seconds)
            if error_msg:
                module.fail_json(msg=f"Error during vManage configuration: {error_msg}")
        result.msg = "Successfully updated requested vManage configuration."
    else:
        result.msg = "No changes to vManage configuration applied."

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
