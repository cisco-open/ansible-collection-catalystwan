#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from enum import Enum
import yaml

from catalystwan.utils.device_model import DeviceModel


enum_values_str = ', '.join(f'\"{model.value}\"' for model in DeviceModel)


with_list = f"[{enum_values_str}]"

DOCUMENTATION = rf"""
    options:
    device_model:
        description:
        - Type of device for which to create the template.
        type: str
        required: true
        choices: {with_list}
    """

with open('plugins/doc_fragments/device_models.yml', 'w') as file:
    file.write(DOCUMENTATION)


values = yaml.safe_load(with_list)

class ModuleDocFragment(object):
    DOCUMENTATION = rf"""
    options:
        device_models:
            description:
            - Type of device for which to create the template.
            type: str
            required: true
            choices: {with_list}
    """