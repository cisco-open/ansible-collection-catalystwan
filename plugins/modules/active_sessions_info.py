#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: active_sessions_info
short_description: Retrieves information about active sessions
version_added: "0.1.0"
description:
  - This module retrieves information about active sessions from a vManage instance.
  - Each session includes details such as UUID, source IP, remote host, username, and more.
options:
  manager_credentials:
    description:
      - Credentials to authenticate with the vManage instance.
    required: true
    type: dict
    aliases: [ manager_authentication ]
    suboptions:
      url:
        description:
          - URL of the vManage instance.
        required: true
        type: str
      username:
        description:
          - Username for authentication with vManage.
        required: true
        type: str
      password:
        description:
          - Password for authentication with vManage.
        required: true
        type: str
        no_log: true
      port:
        description:
          - Port number to use for connecting to vManage.
        required: false
        type: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)
"""

EXAMPLES = r"""
# Retrieve information about all active sessions with explicitly provided vManage credentials
- name: Get active sessions with explicit credentials
  active_sessions_info:
    manager_credentials:
      url: "https://vmanage.example.com"
      username: "admin"
      password: "securepassword123"  # pragma: allowlist secret
      port: "8443"
"""

RETURN = r"""
active_sessions:
  description: A list of active sessions.
  returned: success
  type: list
  elements: dict
  sample: |
    [
        {
            "uuid": "abcdef1234567890",  # pragma: allowlist secret
            "source_ip": "192.0.2.1",
            "remote_host": "host.example.com",
            "raw_username": "admin",
            "raw_id": "admin-123",
            "tenant_domain": "example.com",
            "user_group": "admins",
            "user_mode": "active",
            "create_date_time": "2021-01-01T12:34:56Z",
            "tenant_id": "tenant123",
            "last_accessed_time": "2021-01-01T15:34:56Z"
        }
    ]
changed:
  description: Indicates whether any changes were made. Always returns False for this module.
  returned: success
  type: bool
  sample: False
"""


from typing import List, Optional

from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    active_sessions: Optional[List] = Field(default=[])


def run_module():
    module = AnsibleCatalystwanModule()
    result = ExtendedModuleResult()

    active_sessions = module.get_response_safely(
        module.session.endpoints.administration_user_and_group.get_active_sessions
    )

    if not active_sessions:
        module.exit_json(**result.model_dump(mode="json"))

    for ses in active_sessions:
        result.active_sessions.append(ses.model_dump(mode="json"))

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
