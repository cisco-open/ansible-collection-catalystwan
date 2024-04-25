#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# This file is autogenerated by `utils/feature_template_docs_generator.py`


from __future__ import annotations


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    omp_vsmart:
        description: Overlay Management Protocol (OMP) settings for vSmart controller
        type: dict
        suboptions:
            graceful_restart:
                description:
                - Enable or disable graceful restart for the OMP session
                required: false
                default: null
                type: str
            send_path_limit:
                description:
                - The maximum number of paths that can be sent to a TLOC
                required: false
                default: null
                type: str
            send_backup_paths:
                description:
                - Enable or disable sending additional backup paths
                required: false
                default: null
                type: str
            discard_rejected:
                description:
                - Discard routes that are rejected by policy instead of marking them
                    as rejected
                required: false
                default: null
                type: str
            shutdown:
                description:
                - Enable or disable the shutdown of the OMP session
                required: false
                default: null
                type: str
            graceful_restart_timer:
                description:
                - The time interval for graceful restart of OMP sessions
                required: false
                default: null
                type: str
            eor_timer:
                description:
                - The End of Routes (EOR) timer value
                required: false
                default: null
                type: str
            holdtime:
                description:
                - The hold time interval for OMP sessions
                required: false
                default: null
                type: str
            affinity_group_preference:
                description:
                - Prefer routes from the same affinity group
                required: false
                default: null
                type: str
            advertisement_interval:
                description:
                - Interval between sending OMP route advertisements
                required: false
                default: null
                type: str
    """
