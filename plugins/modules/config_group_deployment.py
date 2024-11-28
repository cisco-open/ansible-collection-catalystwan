#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: config_group_deployment
short_description: Description
version_added: "0.3.1"
description: Module for deployment of config groups.
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
response:
  description: Detailed response from the vManage API if applicable.
  returned: when API call is made
  type: dict
changed:
  description: Whether or not the state was changed.
  returned: always
  type: bool
  sample: true
"""

EXAMPLES = r"""
- name: "Deploy config group"
  cisco.catalystwan.config_group_deployment:
    config_group_id: c90cdc29-fbc7-470a-80ad-6c81beb35848
    edge_device_variables:
      - admin_password: password
        hostname: cedge-1
        pseudo_commit_timer: 300
        site_id: '1001'
        system_ip: 192.168.101.1
        uuid: XXX-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX1
        vpn_0_transport_if: GigabitEthernet1
        vpn_10_if_0: GigabitEthernet2
        vpn_10_if_0_static_ipaddr: 10.0.0.1
        vpn_10_if_0_static_subnet: 255.255.255.0
      - admin_password: Cisco#!@#@ViptelaxDD
        hostname: sprzemys-cedge-2
        pseudo_commit_timer: 300
        site_id: '1002'
        system_ip: 192.168.102.1
        uuid: XXX-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX2
        vpn_0_transport_if: GigabitEthernet1
        vpn_10_if_0: GigabitEthernet2
        vpn_10_if_0_static_ipaddr: 10.0.0.2
        vpn_10_if_0_static_subnet: 255.255.255.0
"""

import traceback

from catalystwan.endpoints.configuration_group import DeviceVariables, VariableData

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def normalize_variables(variables: dict):
    return_variables = {}
    key_map = {"hostname": "host_name"}

    for key, value in variables.items():
        new_key = key_map.get(key, key)
        if new_key == "site_id" and isinstance(value, str):
            value = int(value)
        return_variables[new_key] = value

    return return_variables


def normalize_variables_list(variables: list):
    return_variables = []
    for v in variables:
        return_variables.append(normalize_variables(v))
    return return_variables


def generate_payload_for_device(module: AnsibleCatalystwanModule, source: dict, device_ids: list):
    try:
        variables = []
        for key, value in source.items():
            if key == "uuid":
                continue
            variables.append(VariableData(name=key, value=value))

        device_ids.append(source["uuid"])
        return DeviceVariables(device_id=source["uuid"], variables=variables)
    except Exception as exception:
        module.fail_json(msg=f"Unknown exception: {exception}", exception=traceback.format_exc())


def run_module():
    module_args = dict(
        config_group_id=dict(type=str, required=True),
        edge_device_variables=dict(type=list, required=True),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ModuleResult()

    config_group_id = module.params.get("config_group_id")
    edge_device_variables = normalize_variables_list(module.params.get("edge_device_variables"))

    device_ids = []
    variables_payload = []
    for device in edge_device_variables:
        variables_payload.append(generate_payload_for_device(module, device, device_ids))

    try:
        module.session.api.config_group.associate(config_group_id, device_ids)
        module.session.api.config_group.update_variables(config_group_id, "sdwan", variables_payload)
        response = module.session.api.config_group.deploy(config_group_id, device_ids)
        result.response = response
        result.changed = True
        module.exit_json(**result.model_dump(mode="json"))
    except Exception as exception:
        module.fail_json(msg=f"Unknown exception: {exception}", exception=traceback.format_exc())


def main():
    run_module()


if __name__ == "__main__":
    main()
