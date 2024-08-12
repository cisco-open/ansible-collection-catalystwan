#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: administration_settings
version_added: "0.1.0"
short_description: Manages administration settings on a vManage instance
description:
  - Manages various administration settings on a vManage instance, including
    validator (vBond), certificates, smart account credentials, PnP Connect Sync,
    and organization settings.
  - More settings can be enhanced by reusing
    https://github.com/cisco-open/cisco-catalyst-wan-sdk/blob/main/catalystwan/api/administration.py
options:
  certificates:
    description: Configuration for controller certificate authorization.
    type: dict
    aliases: [cca, controller_certificate_authorization]
    suboptions:
      certificate_signing:
        description: Defines the certificate signing authority.
        type: str
        choices: ["cisco", "manual", "enterprise"]
        default: "cisco"
      email:
        description: Email address to use for the certificate.
        type: str
      first_name:
        description: First name to use for the certificate.
        type: str
      last_name:
        description: Last name to use for the certificate.
        type: str
      retrieve_interval:
        description: Defines the interval to retrieve certificates in minutes.
        type: str
        choices: ["1", "2", "3", ..., "60"]
        default: "5"
      validity_period:
        description: Defines the validity period for the certificate.
        type: str
        choices: ["1Y", "2Y"]
        default: "1Y"
  enterprise_root_ca:
    description: Configuration for enterprise root certificate.
    type: str
    aliases: [enterprise_root_certificate]
  org:
    description: Name of the organization.
    type: str
    aliases: [organization]
  pnp_connect_sync:
    description: Configures the PnP Connect Sync mode.
    type: str
    choices: ["on", "off"]
    default: "off"
    aliases: [pnp_connect_sync_mode]
  smart_account_credentials:
    description: Smart Account credentials for authentication.
    type: dict
    aliases: [smart_account]
    suboptions:
      password:
        description: Password for Smart Account.
        type: str
        required: true
        no_log: true
      username:
        description: Username for Smart Account.
        type: str
        required: true
  validator:
    description: Configuration for vBond validator.
    type: dict
    aliases: [vbond]
    suboptions:
      domain_ip:
        description: Domain IP of the vBond validator.
        type: str
      port:
        description: Port number for the vBond validator.
        type: int
  software_install_timeout:
    description: Configuration for upgrades timeout.
    type: dict
    suboptions:
      download_timeout:
        description: Download Timeout in minutes, should be in range 60-360.
        type: str
      activate_timeout:
        description: Activate Timeout in minutes, should be in range 30-180.
        type: str
      control_pps:
        description: Control PPS, should be in range 300-65535.
        type: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

EXAMPLES = r"""
# Example of using the module to configure vBond validator
- name: Configure vBond validator
  cisco.catalystwan.administration_settings:
    validator:
      domain_ip: "192.0.2.1"
      port: "12346"
    manager_credentials:
      url: "https://vmanage.example.com"
      username: "admin"
      password: "securepassword123"  # pragma: allowlist secret
      port: "8443"

# Example of using the module to configure certificates
- name: Configure certificates
  cisco.catalystwan.administration_settings:
    certificates:
      certificate_signing: "cisco"
      validity_period: "2Y"
      retrieve_interval: 10
      first_name: "John"
      last_name: "Doe"
      email: "john.doe@example.com"
    manager_credentials: ...

# Example of using the module to configure the certificate used for enterprise signing
- name: Configure enterprise root CA
  cisco.catalystwan.administration_settings:
    enterprise_root_ca: "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"
    manager_credentials: ...

# Example of using the module to configure Smart Account credentials
- name: Configure Smart Account credentials
  cisco.catalystwan.administration_settings:
    smart_account_credentials:
      username: "smartuser"
      password: "smartpass"  # pragma: allowlist secret
    manager_credentials: ...

# Example of using the module to configure PnP Connect Sync
- name: Configure PnP Connect Sync
  cisco.catalystwan.administration_settings:
    pnp_connect_sync: "ON"
    manager_credentials: ...

# Example of using the module to configure the organization name
- name: Configure organization name
  cisco.catalystwan.administration_settings:
    org: "ExampleOrganization"
    manager_credentials: ...
"""

RETURN = r"""
msg:
  description: Message detailing the outcome of the operation.
  returned: always
  type: str
  sample: "Successfully updated requested administration settings."
response:
  description: Detailed response for each section of administration settings that has been touched.
    Includes current state when no changes were applied.
  returned: always
  type: complex
  contains:
    org:
      description: Organization settings.
      returned: when org is provided
      type: dict
      sample: {"name": "ExampleOrganization"}
    validator:
      description: vBond validator settings.
      returned: when validator is provided
      type: dict
      sample: {"domain_ip": "192.0.2.1", "port": "12346"}
    certificates:
      description: Controller certificate authorization settings.
      returned: when certificates are provided
      type: dict
      sample: {
        "certificate_signing": "cisco",
        "validity_period": "2Y",
        "retrieve_interval": "10",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
      }
    smart_account_credentials:
      description: Smart Account credentials settings.
      returned: when smart_account_credentials are provided
      type: dict
      sample: {"username": "smartuser"}
    pnp_connect_sync:
      description: PnP Connect Sync mode settings.
      returned: when pnp_connect_sync is provided
      type: str
      sample: "ON"
"""

from typing import get_args

from catalystwan.endpoints.configuration_settings import (
    Certificate,
    Device,
    EnterpriseRootCA,
    OnOffMode,
    Organization,
    PnPConnectSync,
    SmartAccountCredentials,
    SoftwareInstallTimeout,
)

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def run_module():
    module_args = dict(
        validator=dict(
            type="dict",
            aliases=["vbond"],
            options=dict(
                domain_ip=dict(type="str"),
                port=dict(type="str"),
            ),
        ),
        certificates=dict(
            type="dict",
            aliases=["cca", "controler_certificate_authorization"],
            options=dict(
                certificate_signing=dict(
                    type="str",
                    choices=["cisco", "manual", "enterprise"],
                    default="cisco",
                ),
                validity_period=dict(type="str", choices=["1Y", "2Y"], default="1Y"),
                retrieve_interval=dict(
                    type="str",
                    choices=[str(i) for i in range(1, 61)],
                    default="5",
                ),
                first_name=dict(type="str"),
                last_name=dict(type="str"),
                email=dict(type="str"),
            ),
        ),
        enterprise_root_ca=dict(type="str", aliases=["enterprise_root_certificate"]),
        smart_account_credentials=dict(
            type="dict",
            aliases=["smart_account"],
            options=dict(
                username=dict(type="str", required=True),
                password=dict(type="str", required=True, no_log=True),
            ),
        ),
        pnp_connect_sync=dict(
            type="str",
            choices=list(get_args(OnOffMode)),
            default="off",
            aliases=["pnp_connect_sync_mode"],
        ),
        org=dict(type="str", aliases=["organization"]),
        software_install_timeout=dict(
            type="dict",
            options=dict(
                download_timeout=dict(type="str"),
                activate_timeout=dict(type="str"),
                control_pps=dict(type="str"),
            ),
        ),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_one_of=[
            (
                "org",
                "certificates",
                "enterprise_root_ca",
                "smart_account_credentials",
                "pnp_connect_sync",
                "validator",
                "software_install_timeout",
            )
        ],
    )
    result = ModuleResult()

    modify_vbond = False
    modify_org = False
    modify_certificates = False
    modify_enterprise_root_ca = False
    modify_smart_account_credentials = False
    modify_pnp_sync = False
    modify_software_install_timeout = False
    vbond_device_data, vbond_payload = None, None
    organization_data, org_payload = None, None
    smart_account_payload = None
    certificates_data, certificates_payload = None, None
    enterprise_ca_payload = None
    pnp_sync_payload, pnp_sync_data = None, None
    software_install_timeout_payload, software_install_timeout_data = None, None

    # ---------------------------------#
    # STEP 1 - verify module arguments #
    # ---------------------------------#
    # Handled by required and required_one_of

    # ----------------------------------------------------------------#
    # STEP 2 - verify if any action required or state is changed = OK #
    # ----------------------------------------------------------------#
    if module.params.get("validator"):
        vbond_payload = Device(**module.params_without_none_values.get("validator"))
        vbond_device_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_devices
        ).single_or_default()
        modify_vbond = True if vbond_device_data != vbond_payload else False

    if module.params.get("org"):
        org_payload = Organization(**module.params_without_none_values)
        organization_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_organizations
        ).single_or_default()
        modify_org = True if organization_data.org != org_payload.org else False

    if module.params.get("certificates"):
        certificates_payload = Certificate(**module.params_without_none_values.get("certificates"))
        certificates_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_certificates
        ).single_or_default()
        modify_certificates = True if certificates_data != certificates_payload else False

    if module.params.get("enterprise_root_ca"):
        enterprise_ca_payload = EnterpriseRootCA(
            enterprise_root_ca=module.params_without_none_values.get("enterprise_root_ca")
        )
        enterprise_ca_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_enterprise_root_ca
        ).single_or_default()
        modify_enterprise_root_ca = True if enterprise_ca_data != enterprise_ca_payload else False

    if module.params.get("smart_account_credentials"):
        # Always edit smart account credentials if username and password provided
        # We do it because get_smart_account_credentials do not return password content so we cannot compare states
        smart_account_payload = SmartAccountCredentials(
            **module.params_without_none_values.get("smart_account_credentials")
        )
        modify_smart_account_credentials = True

    if module.params.get("pnp_connect_sync"):
        pnp_sync_payload = PnPConnectSync(mode=module.params_without_none_values.get("pnp_connect_sync"))
        pnp_sync_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_pnp_connect_sync
        ).single_or_default()
        modify_pnp_sync = True if pnp_sync_data.mode != pnp_sync_payload.mode else False

    if module.params.get("software_install_timeout"):
        software_install_timeout_payload = SoftwareInstallTimeout(
            **module.params_without_none_values.get("software_install_timeout")
        )
        software_install_timeout_data = module.get_response_safely(
            module.session.endpoints.configuration_settings.get_software_install_timeout
        ).single_or_default()
        modify_software_install_timeout = (
            True if software_install_timeout_data != software_install_timeout_payload else False
        )

    # ----------------------------------#
    # STEP 3 - perform required actions #
    # ----------------------------------#
    if modify_org:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Organizations",
            send_func=module.session.endpoints.configuration_settings.edit_organizations,
            payload=org_payload,
            response_key="org",
        )

    if modify_vbond:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Validator",
            send_func=module.session.endpoints.configuration_settings.edit_devices,
            payload=vbond_payload,
            response_key="validator",
        )

    if modify_certificates:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Controller Cerfificate Authorization",
            send_func=module.session.endpoints.configuration_settings.edit_certificates,
            payload=certificates_payload,
            response_key="certificates",
        )

    if modify_enterprise_root_ca:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Enterprise Root CA",
            send_func=module.session.endpoints.configuration_settings.edit_enterprise_root_ca,
            payload=enterprise_ca_payload,
            response_key="enterprise_root_ca",
        )

    if modify_smart_account_credentials:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Smart Account Credentials",
            send_func=module.session.endpoints.configuration_settings.edit_smart_account_credentials,
            payload=smart_account_payload,
        )

    if modify_pnp_sync:
        module.send_request_safely(
            result,
            action_name="Administration Settings: PnP Connect Sync",
            send_func=module.session.endpoints.configuration_settings.edit_pnp_connect_sync,
            payload=pnp_sync_payload,
            response_key="pnp_sync",
        )

    if modify_software_install_timeout:
        module.send_request_safely(
            result,
            action_name="Administration Settings: Software Install Timeout",
            send_func=module.session.endpoints.configuration_settings.edit_software_install_timeout,
            payload=software_install_timeout_payload,
            response_key="software_install_timeout",
        )

    # ----------------------------------#
    # STEP 4 - update and return result #
    # ----------------------------------#
    if result.changed:
        result.msg = "Successfully updated requested administration settings."
    else:
        result.msg = "No changes to administration settings applied."

    if organization_data and not modify_org:
        result.state["org"] = organization_data.dict()
    if vbond_device_data and not modify_vbond:
        result.state["validator"] = vbond_device_data.dict()
    if certificates_data and not modify_certificates:
        result.state["certificates"] = certificates_data.dict()
    if pnp_sync_data and not modify_pnp_sync:
        result.state["pnp_sync"] = pnp_sync_data.dict()
    if software_install_timeout_data and not modify_software_install_timeout:
        result.state["software_install_timeout"] = pnp_sync_data.dict()

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
