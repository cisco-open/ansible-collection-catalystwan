#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: feature_templates_info
short_description: Get information about Feature Templates on vManage.
version_added: "0.1.0"
description:
  - This module allows you to get and filter Feature Templates from vManage.
options:
  filters:
    description:
      - A dictionary of filters used to select devices for module action.
    type: dict
    required: false
    # suboptions:
    #   description:
    #   - The login banner text displayed before authentication
    #   required: false
    #   default: null
    #   type: str
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
notes:
  - Ensure that the provided credentials have sufficient permissions to manage templates and devices in vManage.
"""

EXAMPLES = r"""
- name: Attach default CLI template to the specified devices
  cisco.catalystwan.feature_templates_info:
    filters:
      name: "trial-template"
"""

RETURN = r"""
template_info:
  description: A dictionary of templates with the key as template name and value as device hostname.
  type: dict
  returned: on success
  sample: |
    {
      "Default_device1": "device1",
      "Default_device2": "device2"
    }
msg:
  description: Messages that indicate actions taken or any errors that have occurred.
  type: str
  returned: always
  sample: "Successfully fetched information about template: trial-template"
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
  sample: false
"""
from typing import Optional, Dict
from pydantic import Field

from catalystwan.api.template_api import FeatureTemplate
from catalystwan.dataclasses import FeatureTemplateInfo
from catalystwan.typed_list import DataSequence
from catalystwan.utils.creation_tools import asdict

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    templates_info: Optional[Dict] = Field(default={})


def run_module():
    module_args = dict(
        filters=dict(type="dict", default=None, required=False),
    )
    result = ExtendedModuleResult()
    result.state = None
    result.response = None

    module = AnsibleCatalystwanModule(argument_spec=module_args)

    filters = module.params.get('filters')

    all_templates: DataSequence[FeatureTemplateInfo] = module.get_response_safely(module.session.api.templates.get, template=FeatureTemplate)

    if filters:
        filtered_templates = all_templates.filter(**filters)
        if filtered_templates:
            module.logger.info(f"All Feature Templates filtered with filters: {filters}:\n{filtered_templates}")
            result.msg = "Succesfully got all requested Feature Templates Info from vManage"
            result.templates_info = [asdict(template) for template in filtered_templates]
        else:
            module.logger.warning(msg=f"Feature templates filtered with `{filters}` not present.")
            result.msg = f"Feature templates filtered with `{filters}` not present on vManage."
    else:
        result.msg = "Succesfully got all Feature Templates Info from vManage"
        result.templates_info = [asdict(template) for template in all_templates]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
