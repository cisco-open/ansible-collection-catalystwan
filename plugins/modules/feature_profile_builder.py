#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: feature_profile_builder
short_description: Description
version_added: "0.3.1"
description: Module for building feature profile data based on parcel templates.
author:
  - Przemyslaw Susko (sprzemys@cisco.com)
"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: on failure
  type: str
system_profiles:
  description: Generated system feature profiles.
  returned: on success
  type: str
transport_profiles:
  description: Generated transport feature profiles.
  returned: on success
  type: str
service_profiles:
  description: Generated service feature profiles.
  returned: on success
  type: str
settable_variables:
  description: A list of settable variables for created feature profiles grouped by profile type, i.e.:
    settable_variables:
      service:
        interface_names:
        - vpn_10_if_0
        static_ip_addresses:
        - vpn_10_if_0_static_ipaddr
        static_subnets:
        - vpn_10_if_0_static_subnet
      transport:
        interface_names:
        - vpn_0_transport_if
  returned: on success
  type: str
"""

EXAMPLES = r"""
- name: "Generate config group data from template"
  cisco.catalystwan.feature_profile_builder:
    templates_path: "/path/to/parcel/templates"
    system_profiles:
      - name: System
        description: Description
        parcels:
          - template: banner
          - template: basic
    transport_profiles:
      - name: Transport
        description: Description
        parcels:
          wan_vpn_parcel:
            template: vpn
            config:
              name: OverridenName
            sub_parcels:
              - wan_interface_ethernet_parcel_1:
                template: ethernet
                config:
                    data:
                      interfaceName:
                        optionType: default
    service_profiles:
      - name: Service
        description: Description
        parcels:
        - template: vpn
          sub_parcels:
            - template: ethernet
"""

import os
from copy import copy
from dataclasses import asdict, dataclass
from typing import Optional

import yaml
from ansible.module_utils.basic import AnsibleModule


class TemplateCache:
    def __init__(self, module: AnsibleModule, templates_dir: os.path):
        self.module = module
        self.dir = templates_dir
        self.cache = {}

    def get(self, template):
        if template not in self.cache:
            file_path = os.path.join(self.dir, template)
            try:
                with open(file_path, "r") as file:
                    self.cache[template] = yaml.safe_load(file)
            except FileNotFoundError:
                self.module.fail_json(msg=f"File not found {file_path}")
            except IOError as e:
                self.module.fail_json(msg=f"Error reading file {file_path}: {e}")
        return copy(self.cache[template])


@dataclass
class SettableVars:
    @dataclass
    class Vars:
        interface_names: set[str]
        static_ip_addresses: Optional[set[str]]
        static_subnets: Optional[set[str]]

    transport: Vars
    service: Vars

    @classmethod
    def init(cls):
        return cls(transport=SettableVars.Vars(set(), None, None), service=SettableVars.Vars(set(), set(), set()))

    def sort(self):
        def _sort_vars(_vars: SettableVars.Vars):
            _vars.interface_names = sorted(_vars.interface_names)
            if _vars.static_ip_addresses:
                _vars.static_ip_addresses = sorted(_vars.static_ip_addresses)
            if _vars.static_subnets:
                _vars.static_subnets = sorted(_vars.static_subnets)

        _sort_vars(self.transport)
        _sort_vars(self.service)
        return self


SETTABLE_VARS = SettableVars.init()


def get_settable_vars_for_profile(profile_type: str) -> SettableVars.Vars:
    if profile_type == "transport":
        return SETTABLE_VARS.transport
    if profile_type == "service":
        return SETTABLE_VARS.service


def update_template(template, config: dict):
    for key, value in config.items():
        if key in template:
            if isinstance(value, dict) and isinstance(template[key], dict):
                update_template(template[key], value)
            else:
                if isinstance(value, str) and value.startswith("{"):
                    value = "{{ '" + value + "' }}"
                template[key] = value


def append_settable_vars(config: dict, profile_type: str):
    def _helper(_key, _value, _match):
        try:
            if _key == _match and isinstance(_value, dict) and _value["optionType"] == "variable":
                return _value["value"].strip("{ ' }")
        except ValueError:
            return None

    _settable_vars = get_settable_vars_for_profile(profile_type)
    for key, value in config.items():
        if_name = _helper(key, value, "interfaceName")
        if if_name:
            _settable_vars.interface_names.add(if_name)
            continue

        ip_addr = _helper(key, value, "ipAddress")
        if ip_addr and (_settable_vars.static_ip_addresses is not None):
            _settable_vars.static_ip_addresses.add(ip_addr)
            continue

        subnet = _helper(key, value, "subnetMask")
        if subnet and (_settable_vars.static_subnets is not None):
            _settable_vars.static_subnets.add(subnet)
            continue

        if isinstance(value, dict):
            append_settable_vars(value, profile_type)


def generate_parcel(module: AnsibleModule, cache: TemplateCache, profile_type: str, source: dict):
    if "template" not in source:
        module.fail_json(f"Template type not provided for {profile_type} type parcel")

    template = cache.get(f"{profile_type}_parcels/{source['template']}.yml")
    if "config" in source:
        update_template(template["config"], source["config"])
    append_settable_vars(template["config"], profile_type)

    sub_parcels = []
    if source["template"] == "vpn" and "sub_parcels" in source and len(source["sub_parcels"]):
        for parcel in source["sub_parcels"]:
            sub_parcels.append(generate_parcel(module, cache, profile_type, parcel))

    generated = {"type": source["template"], "config": template["config"]}
    if len(sub_parcels):
        generated.update({"sub_parcels": sub_parcels})

    return generated


def generate_profiles(module: AnsibleModule, cache: TemplateCache, profile_type: str, source_profiles: dict):
    generated_profiles = []
    for profile in source_profiles:
        parcels = []
        for parcel in profile["parcels"]:
            parcels.append(generate_parcel(module, cache, profile_type, parcel))
        generated_profiles.append({"name": profile["name"], "description": profile["description"], "parcels": parcels})
    return generated_profiles


def run_module():
    module_args = dict(
        templates_path=dict(type="str", required=True),
        system_profiles=dict(type="list"),
        transport_profiles=dict(type="list"),
        service_profiles=dict(type="list"),
    )

    result = dict(changed=True, data={})

    module = AnsibleModule(argument_spec=module_args)

    templates_path = module.params["templates_path"]
    system_profiles = module.params["system_profiles"]
    transport_profiles = module.params["transport_profiles"]
    service_profiles = module.params["service_profiles"]

    cache = TemplateCache(module, templates_path)
    generated_system_profiles = generate_profiles(module, cache, "system", system_profiles)
    generated_transport_profiles = generate_profiles(module, cache, "transport", transport_profiles)
    generated_service_profiles = generate_profiles(module, cache, "service", service_profiles)

    result["data"].update({"system_profiles": generated_system_profiles})
    result["data"].update({"transport_profiles": generated_transport_profiles})
    result["data"].update({"service_profiles": generated_service_profiles})
    result["data"].update(
        {
            "settable_variables": asdict(
                SETTABLE_VARS.sort(), dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
            )
        }
    )
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
