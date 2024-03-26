#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations


class ModuleDocFragment(object):
    # Plugin options for AWS credentials
    DOCUMENTATION = r"""
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
notes:
  - manager_authentication argument is required for all modules invocation.
    To keep all examples of usage of modules clean and easy to read examples are not including that argument.
"""
