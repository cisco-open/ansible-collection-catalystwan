#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
        module.module.log(variables_payload.__str__())  # TODO remove
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
