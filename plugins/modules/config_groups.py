#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: config_groups
short_description: Description
version_added: "0.3.1"
description: Module for configuration of config groups.
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
id:
  description: ID of created config group.
  returned: on success
  type: bool
  sample: c90cdc29-fbc7-470a-80ad-6c81beb35848
"""

EXAMPLES = r"""
- name: "Create config group"
  cisco.catalystwan.config_groups:
    name: NAME
    description: DESCRIPTION
    system_profiles:
      - name: "{{ config_group_name }}_Basic"
        description: "{{ config_group_name }} Basic Profile"
        parcels:
          - type: banner
            config:
            name: Banner
            description: Banner Description
"""

import traceback

from catalystwan.models.configuration.feature_profile.common import FeatureProfileCreationPayload
from catalystwan.models.configuration.feature_profile.sdwan.service import (
    InterfaceEthernetParcel as ServiceInterfaceEthernetParcel,
)
from catalystwan.models.configuration.feature_profile.sdwan.service import LanVpnParcel
from catalystwan.models.configuration.feature_profile.sdwan.system import (
    AAAParcel,
    BannerParcel,
    BasicParcel,
    BFDParcel,
    GlobalParcel,
    LoggingParcel,
    MRFParcel,
    NtpParcel,
    OMPParcel,
)
from catalystwan.models.configuration.feature_profile.sdwan.transport import (
    InterfaceEthernetParcel as TransportInterfaceEthernetParcel,
)
from catalystwan.models.configuration.feature_profile.sdwan.transport import TransportVpnParcel

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule

system_parcel_type_mapping = {
    "banner": BannerParcel,
    "basic": BasicParcel,
    "bfd": BFDParcel,
    "omp": OMPParcel,
    "logging": LoggingParcel,
    "ntp": NtpParcel,
    "global": GlobalParcel,
    "aaa": AAAParcel,
    "mrf": MRFParcel,
}

transport_parcel_type_mapping = {
    "vpn": TransportVpnParcel,
    "ethernet": TransportInterfaceEthernetParcel,
}

service_parcel_type_mapping = {
    "vpn": LanVpnParcel,
    "ethernet": ServiceInterfaceEthernetParcel,
}


def create_parcel(module, parcel, profile_type):
    if "config" not in parcel:
        module.fail_json(msg="{} parcel lacks config".format(parcel["type"]))

    parcel_type = parcel["type"]
    if profile_type == "system":
        parcel_class = system_parcel_type_mapping.get(parcel_type)
    elif profile_type == "transport":
        parcel_class = transport_parcel_type_mapping.get(parcel_type)
    elif profile_type == "service":
        parcel_class = service_parcel_type_mapping.get(parcel_type)
    else:
        raise ValueError(f"Unknown profile type {profile_type}")

    if parcel_class:
        try:
            return parcel_class(**parcel["config"])
        except Exception as ex:
            module.fail_json(
                "Failed to parse {} type parcel for {} profile. Exception: {}".format(parcel["type"], profile_type, ex)
            )
    else:
        module.fail_json(msg=f"Unknown parcel type: {parcel_type}")


def builder_add_parcel_vpn(builder, module, parcel, profile_type):
    vpn_tag = builder.add_parcel_vpn(create_parcel(module, parcel, profile_type))
    if "sub_parcels" in parcel:
        for sub_parcel in parcel["sub_parcels"]:
            if profile_type == "transport":
                builder.add_vpn_subparcel(vpn_tag, create_parcel(module, sub_parcel, profile_type))
            elif profile_type == "service":
                builder.add_parcel_vpn_subparcel(vpn_tag, create_parcel(module, sub_parcel, profile_type))


def create_profile(module, profile, profile_type):
    if "name" not in profile:
        module.fail_json(msg=f"{profile_type} profile lacks name")
    if "parcels" not in profile:
        module.fail_json(msg="{} profile {} lacks parcels".format(profile_type, profile["name"]))

    builder = module.session.api.builders.feature_profiles.create_builder(profile_type)
    builder.add_profile_name_and_description(
        FeatureProfileCreationPayload(
            name=profile["name"], description=profile["description"] if "description" in profile else ""
        )
    )
    for parcel in profile["parcels"]:
        if "type" not in parcel:
            module.fail_json(msg="parcel for profile {} lacks type".format(profile["name"]))

        if parcel["type"] == "vpn":
            builder_add_parcel_vpn(builder, module, parcel, profile_type)
        else:
            builder.add_parcel(create_parcel(module, parcel, profile_type))

    build_report = builder.build()
    if len(build_report.failed_parcels) > 0:
        module.fail_json(
            msg="Failed to create {} parcels for profile {}."
            "Build report: {}".format(len(build_report.failed_parcels), profile["name"], build_report)
        )

    return build_report.profile_uuid


def run_module():
    module_args = dict(
        name=dict(type=str, required=True),
        description=dict(type=str),
        system_profiles=dict(type=list),
        transport_profiles=dict(type=list),
        service_profiles=dict(type=list),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ModuleResult()
    profile_ids = []

    name = module.params.get("name")
    description = module.params.get("description")
    system_profiles = module.params.get("system_profiles")
    transport_profiles = module.params.get("transport_profiles")
    service_profiles = module.params.get("service_profiles")

    for profile in system_profiles:
        profile_ids.append(create_profile(module, profile, "system"))
    for profile in transport_profiles:
        profile_ids.append(create_profile(module, profile, "transport"))
    for profile in service_profiles:
        profile_ids.append(create_profile(module, profile, "service"))

    try:
        response = module.session.api.config_group.create(name, description, "sdwan", profile_ids)
        result.response = response
        result.changed = True
        result.id = response.id

        module.exit_json(**result.model_dump(mode="json"))
    except Exception as exception:
        module.fail_json(msg=f"Unknown exception: {exception}", exception=traceback.format_exc())


def main():
    run_module()


if __name__ == "__main__":
    main()
