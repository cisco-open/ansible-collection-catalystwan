#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: server_info
short_description: Retrieves server information categories from vManage
version_added: "0.1.0"
description:
  - This module fetches different types of information about a server managed by vManage.
  - The information that can be retrieved includes server general info, server readiness, and about info.
options:
  information_category:
    description:
      - The category of information to retrieve from the server.
    type: str
    choices: ["server_info", "server_ready", "about_info"]
    default: "server_info"
author:
  - Arkadiusz Cichon (acichon@cisco.com)

notes:
  - The module does not make any changes on the server, it only retrieves information.

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
changed:
  description: Indicates if any changes were made by the module.
  returned: always
  type: bool
  sample: false
response:
  description: The detailed server information based on the selected category.
  returned: success
  type: dict
  sample: {"version": "20.3.1", "buildNumber": "12345", "ready": true}
msg:
  description: Failure message if the information could not be retrieved.
  returned: failure
  type: str
  sample: "Could not get requested server info: <error message>"
"""

EXAMPLES = r"""
# Example of using the module to retrieve server general information
- name: Get server general information
  cisco.catalystwan.server_info:
    information_category: "server_info"

# Example of using the module to check if the server is ready
- name: Check if server is ready
  cisco.catalystwan.server_info:
    information_category: "server_ready"

# Example of using the module to get 'about' information of the server
- name: Get server 'about' information
  cisco.catalystwan.server_info:
    information_category: "about_info"
"""

from enum import Enum

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class InformationCategory(str, Enum):
    SERVER_INFO = "server_info"
    SERVER_READY = "server_ready"
    ABOUT_INFO = "about_info"


def run_module():
    module_args = dict(
        information_category=dict(
            type=str,
            choices=[InformationCategory.SERVER_INFO, InformationCategory.SERVER_READY, InformationCategory.ABOUT_INFO],
            default=InformationCategory.SERVER_INFO.value,
        ),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ModuleResult()

    if module.params["information_category"] == InformationCategory.SERVER_INFO:
        response = module.get_response_safely(module.session.endpoints.client.server)

    elif module.params["information_category"] == InformationCategory.SERVER_READY:
        response = module.get_response_safely(module.session.endpoints.client.server_ready)

    elif module.params["information_category"] == InformationCategory.ABOUT_INFO:
        response = module.get_response_safely(module.session.endpoints.client.about)

    result.response = response.dict()

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
