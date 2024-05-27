#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: alarms
version_added: "0.1.0"
short_description: Information about alarms in vManage
description:
  - This module can be used to retrieve alarm information from vManage.
  - It allows filtering to retrieve only critical alarms, marking all alarms as viewed
  - Optionally supports logging the alarms to a file.
  - Can be used to mark all the alarms as viewed
options:
  from_time:
    description:
      - Starting epoch time in hours for alarms query.
      - If not provided, the module will retrieve alarms from the beginning of time.
    type: int
    required: False
    default: None
  mark_all_as_viewed:
    description:
      - Whether to mark all the alarms as viewed.
    type: bool
    required: False
    default: False
  only_critical:
    description:
      - Whether to retrieve only alarms with CRITICAL severity.
    type: bool
    required: False
    default: False
  log_file:
    description:
      - Path to a file where the alarms will be logged in JSON format.
      - If not provided, alarms will not be logged to a file.
    type: str
    required: False
    default: None
author:
  - Arkadiusz Cichon (acichon@cisco.com)

extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""


RETURN = r"""
alarms:
  description: List of alarms with details.
  returned: always
  type: list
  elements: dict
  sample: [
      {
        "alarm_id": "12345",
        "severity": "CRITICAL",
        "entry_time": 1616582130000,
        "details": "Interface ge0/1 on device XYZ went down."
      }
  ]
number_of_alarms:
  description: The total number of alarms retrieved.
  returned: always
  type: int
  sample: 10
changed:
  description:
    - Indicates whether any changes were made.
    - In this case, always false since this module is for information retrieval only.
  returned: always
  type: bool
  default: False
"""

EXAMPLES = r"""
# Example of using the module to retrieve all alarms
- name: Retrieve all alarms
  cisco.catalystwan.alarms:
    from_time: 16

# Example of using the module to retrieve only critical alarms
- name: Retrieve only critical alarms
  cisco.catalystwan.alarms:
    only_critical: true

# Example of using the module to mark all alarms as viewed
- name: Mark all alarms as viewed
  cisco.catalystwan.alarms:
    mark_all_as_viewed: true

# Example of using the module to log alarms to a file
- name: Log alarms to a file
  cisco.catalystwan.alarms:
    log_file: "/path/to/alarms.log"
"""

import json
import traceback
from typing import List, Optional

from catalystwan.session import ManagerHTTPError
from catalystwan.utils.alarm_status import Severity
from catalystwan.utils.creation_tools import asdict
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    alarms: Optional[List] = Field(default=[])
    number_of_alarms: Optional[List] = Field(default=[])


def run_module():
    module_args = dict(
        from_time=dict(type=int, required=False, default=None),
        mark_all_as_viewed=dict(type=bool, required=False, default=False),
        only_critical=dict(type=bool, required=False, default=False),
        log_file=dict(type=str, required=False, default=None),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    try:
        if module.params.get("only_critical"):
            alarms = module.session.api.alarms.get(from_time=module.params["from_time"]).filter(
                severity=Severity.CRITICAL
            )
        else:
            alarms = module.session.api.alarms.get(from_time=module.params["from_time"])

        if module.params.get("mark_all_as_viewed"):
            module.session.api.alarms.mark_all_as_viewed()

    except ManagerHTTPError as ex:
        module.fail_json(
            msg=f"Could not perform alarms action. Manager error: {str(ex)} {ex.info}",
            exception=traceback.format_exc(),
        )

    alarms_dict = [asdict(alarm) for alarm in alarms]
    for alarm in alarms_dict:
        if type(alarm["severity"]) is Severity:
            alarm["severity"] = alarm["severity"].value
    result.alarms = [alarm for alarm in alarms_dict]

    result.changed = False
    result.number_of_alarms = len(alarms_dict)

    if module.params.get("log_file"):
        with open(module.params["log_file"], "w") as outfile:
            outfile.write(json.dumps(result.alarms, indent=4))

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
