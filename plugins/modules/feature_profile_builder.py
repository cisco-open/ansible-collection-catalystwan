#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

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
        return self.cache[template]


def update_template(template, config):
    for key, value in config.items():
        if key in template:
            if isinstance(value, dict) and isinstance(template[key], dict):
                update_template(template[key], value)
            else:
                template[key] = value


def generate_parcel(module: AnsibleModule, cache: TemplateCache, profile_type: str, source: dict):
    if "template" not in source:
        module.fail_json(f"Template type not provided for {profile_type} type parcel")

    template = cache.get(f"{profile_type}_parcels/{source['template']}.yml")
    if "config" in source:
        update_template(template["config"], source["config"])

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
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
