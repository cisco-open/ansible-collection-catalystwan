#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  cisco_aaa:
    description: Cisco AAA Feature Template configuration.
    type: dict
    suboptions:
      user:
        description:
        - List of user configurations
        required: false
        default: false
        type: list
        elements: dict
        suboptions:
          name:
            description:
            - The name of the user
            required: true
            default: null
            type: str
          password:
            description:
            - The password for the user
            required: false
            default: null
            type: str
          secret:
            description:
            - The secret for the user
            required: false
            default: null
            type: str
          privilege:
            description:
            - The privilege level for the user
            required: false
            default: null
            type: str
          pubkey_chain:
            description:
            - List of public keys for the user
            required: false
            default: []
            type: list
            elements: str
      authentication_group:
        description:
        - Whether to enable the authentication group
        required: false
        default: false
        type: bool
      accounting_group:
        description:
        - Whether to enable the accounting group
        required: false
        default: true
        type: bool
      radius:
        description:
        - List of Radius group configurations
        required: false
        default: null
        type: list
        elements: dict
        suboptions:
          group_name:
            description:
            - The name of the RADIUS group
            required: true
            default: null
            type: str
          vpn:
            description:
            - The VPN ID for the RADIUS group
            required: true
            default: null
            type: str
          source_interface:
            description:
            - The source interface for the RADIUS group
            required: true
            default: null
            type: str
          server:
            description:
            - The list of RADIUS servers for the group
            required: false
            default: []
            type: list
            elements: str
      domain_stripping:
        description:
        - The domain stripping configuration
        required: false
        default: null
        type: str
      port:
        description:
        - The port number for AAA
        required: false
        default: 1700
        type: str
      tacacs:
        description:
        - List of TACACS group configurations
        required: false
        default: null
        type: list
        elements: dict
        suboptions:
          group_name:
            description:
            - The name of the TACACS+ group
            required: true
            default: null
            type: str
          vpn:
            description:
            - The VPN ID for the TACACS+ group
            required: false
            default: 0
            type: str
          source_interface:
            description:
            - The source interface for the TACACS+ group
            required: false
            default: null
            type: str
          server:
            description:
            - The list of TACACS+ servers for the group
            required: false
            default: []
            type: list
            elements: str
      server_auth_order:
        description:
        - Authentication order to user access
        required: false
        default: local
        type: str
    '''
