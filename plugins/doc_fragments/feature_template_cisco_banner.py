# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
    cisco_banner:
      description:
        - This module allows you to configure the login and message of the day (MOTD) banners on Cisco devices.
      required: false
      type: dict
      suboptions:
        login_banner:
          description:
            - The text to be set as the login banner. If set to None, the login banner will be removed.
          type: str
          required: false
        motd_banner:
          description:
            - The text to be set as the MOTD banner. If set to None, the MOTD banner will be removed.
          type: str
          required: false
  '''
