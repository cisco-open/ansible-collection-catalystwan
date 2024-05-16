#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: users
short_description: Manage users in vManage.
version_added: "0.1.0"
description:
  - This module allows you to manage users within Cisco vManage.
  - You can create, update, reset, or delete user accounts, as well as retrieve all user accounts.
options:
  get_all:
    description:
      - Retrieve information about all users.
    type: bool
    required: false
    default: false
  mode:
    description:
      - The operation mode for the user management.
    type: str
    choices: ['create', 'update', 'reset', 'delete']
    required: false
  username:
    description:
      - The username of the user to be managed.
    type: str
    required: false
  password:
    description:
      - The password for the user. Required when creating or resetting a user.
    type: str
    required: false
  description:
    description:
      - A description for the user.
    type: str
    required: false
  group:
    description:
      - The list of groups to which the user belongs.
    type: list
    elements: str
    required: false
    default: []
notes:
  - Ensure that the provided credentials have sufficient permissions to manage users in vManage.
  - Passwords should be handled carefully, consider using Ansible Vault for sensitive data.
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

EXAMPLES = r"""
---
- name: Retrieve all users from vManage
  cisco.catalystwan.users:
    get_all: true

- name: Create a new user in vManage
  cisco.catalystwan.users:
    mode: create
    username: 'johndoe'
    password: 'securepassword'  # pragma: allowlist secret
    description: 'John Doe user'
    group:
      - 'admin'

- name: Delete a user from vManage
  cisco.catalystwan.users:
    mode: delete
    username: 'janedoe'
"""

RETURN = r"""
---
users:
  description: The list of user information, returned when 'get_all' is used.
  type: list
  elements: dict
  returned: when 'get_all' is true
  sample: |
    [
      {
        "username": "johndoe",
        "description": "John Doe user",
        "group": ["admin"]
      },
      {
        "username": "janedoe",
        "description": "Jane Doe user",
        "group": ["read-only"]
      }
    ]
msg:
  description: Message about the action performed.
  type: str
  returned: on change
  sample: "Create new user: johndoe"
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
  sample: true
"""
import traceback
from typing import List, Optional

from catalystwan.endpoints.administration_user_and_group import User
from catalystwan.session import ManagerHTTPError
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    users: Optional[List] = Field(default=[])


def run_module():
    module_args = dict(
        get_all=dict(type=bool, required=False, default=False),
        mode=dict(type=str, required=False, choices=["create", "delete"], default=None),
        username=dict(type=str, required=False, default=False),
        password=dict(type=str, required=False, default=False),
        description=dict(type=str, required=False, default=False),
        group=dict(type=list, required=False, default=[]),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    try:
        if module.params.get("get_all"):
            all_users = module.session.api.users.get()
            result.users = [user.model_dump(mode="json") for user in all_users]

        if module.params.get("mode") == "create":
            new_user = User(**module.params)
            module.session.api.users.create(new_user)

            result.changed = True
            result.msg = f"Create new user: {new_user}"

        if module.params.get("mode") == "delete":
            module.session.api.users.delete(module.params["username"])
            result.changed = True
            result.msg = f'Delete user: {module.params["username"]}'

    except ManagerHTTPError as ex:
        module.fail_json(
            msg=f"Could not perform users action.\nManager error: {str(ex)} {ex.info}",
            exception=traceback.format_exc(),
        )

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
