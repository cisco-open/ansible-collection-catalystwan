#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# This file is autogenerated by `utils/feature_template_docs_generator.py`


from __future__ import annotations


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    cisco_logging:
        description: Cisco Logging Feature Template configuration
        type: dict
        suboptions:
            enable:
                description:
                - Whether logging to disk is enabled
                required: false
                default: null
                type: str
            size:
                description:
                - The maximum file size for the log file
                required: false
                default: null
                type: str
            rotate:
                description:
                - The number of log files to maintain before rotating
                required: false
                default: null
                type: str
            tls_profile:
                description:
                - List of TLS profiles configurations
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    profile:
                        description:
                        - The name of the TLS profile
                        required: true
                        default: null
                        type: str
                    version:
                        description:
                        - The TLS version
                        required: false
                        default: TLSv1.1
                        type: str
                        choices:
                        - TLSv1.1
                        - TLSv1.2
                    auth_type:
                        description:
                        - The authentication type for the TLS connection
                        required: true
                        default: null
                        type: str
                        choices:
                        - Server
                        - Mutual
                    ciphersuite_list:
                        description:
                        - The list of ciphersuites for the TLS connection
                        required: false
                        default: null
                        type: list
                        elements: str
            server:
                description:
                - List of server configurations for logging
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    name:
                        description:
                        - The name of the server
                        required: true
                        default: null
                        type: str
                    vpn:
                        description:
                        - The VPN ID for the server
                        required: true
                        default: null
                        type: str
                    source_interface:
                        description:
                        - The source interface for the server
                        required: false
                        default: null
                        type: str
                    priority:
                        description:
                        - The priority level for logging messages
                        required: false
                        default: information
                        type: str
                        choices:
                        - information
                        - debugging
                        - notice
                        - warn
                        - error
                        - critical
                        - alert
                        - emergency
                    enable_tls:
                        description:
                        - Whether to enable TLS encryption
                        required: false
                        default: null
                        type: str
                    custom_profile:
                        description:
                        - Whether to use a custom TLS profile
                        required: false
                        default: null
                        type: str
                    profile:
                        description:
                        - The custom TLS profile to use
                        required: false
                        default: null
                        type: str
            ipv6_server:
                description:
                - List of IPv6 server configurations for logging
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    name:
                        description:
                        - The name of the IPv6 server
                        required: true
                        default: null
                        type: str
                    vpn:
                        description:
                        - The VPN ID for the IPv6 server
                        required: true
                        default: null
                        type: str
                    source_interface:
                        description:
                        - The source interface for the IPv6 server
                        required: false
                        default: null
                        type: str
                    priority:
                        description:
                        - The priority level for logging messages to the IPv6 server
                        required: false
                        default: information
                        type: str
                        choices:
                        - information
                        - debugging
                        - notice
                        - warn
                        - error
                        - critical
                        - alert
                        - emergency
                    enable_tls:
                        description:
                        - Whether to enable TLS encryption for the IPv6 server
                        required: false
                        default: null
                        type: str
                    custom_profile:
                        description:
                        - Whether to use a custom TLS profile for the IPv6 server
                        required: false
                        default: null
                        type: str
                    profile:
                        description:
                        - The custom TLS profile to use for the IPv6 server
                        required: false
                        default: null
                        type: str
    """
