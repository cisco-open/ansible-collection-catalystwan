#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: software_repository_info
short_description: Get information about Software Repository
version_added: "0.1.0"
description:
  - This module fetches information about software repositories managed by vManage.
  - It can retrieve details about remote servers or software images from the repository.
options:
  category:
    description:
      - The category of information to retrieve.
    type: str
    required: True
    choices: ["remote_servers", "software_images"]
  filters:
    description:
      - Optional filters used to refine the results.
    type: dict
    default: None
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
remote_servers:
  description: The list of remote server information if the category is 'remote_servers'.
  returned: when 'remote_servers' is selected
  type: list
  sample: [{"name": "Server1", "address": "192.168.1.10", "type": "vManage"}]
software_images:
  description: The list of software image details if the category is 'software_images'.
  returned: when 'software_images' is selected
  type: list
  sample: [{"name": "vEdge", "version": "20.3.2", "imageFile": "vedge-20.3.2.img"}]
"""

EXAMPLES = r"""
# Example of using the module to retrieve remote server information
- name: Get remote server information
  cisco.catalystwan.software_repository_info:
    category: "remote_servers"

# Example of using the module to retrieve software image information with filters
- name: Get filtered software image information
  cisco.catalystwan.software_repository_info:
    category: "software_images"
    filters:
      version: "20.3.2"
"""

from typing import Any, List, Optional, Union

from catalystwan.endpoints.configuration.software_actions import RemoteServerInfo, SoftwareImageDetails
from catalystwan.typed_list import DataSequence
from pydantic import Field

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    remote_servers: Optional[List] = Field(default=[])
    software_images: Optional[List] = Field(default=[])


def run_module():
    module_args = dict(
        category=dict(
            type=str,
            required=True,
            choices=["remote_servers", "software_images"],
        ),
        filters=dict(type=dict, default=None),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
    )
    result = ExtendedModuleResult()
    category = module.params.get("category")

    if category == "remote_servers":
        remote_servers: Union[DataSequence[RemoteServerInfo], Any] = module.get_response_safely(
            module.session.endpoints.configuration_software_actions.get_list_of_remote_servers
        )
        module.logger.info(f"get_list_of_remote_servers response: {remote_servers}")

        module.logger.debug(f"Filter: {module.params.get('filters')}")
        if module.params.get("filters"):
            filtered_remote_servers: Union[DataSequence[RemoteServerInfo], Any] = remote_servers.filter(
                **module.params.get("filters")
            )
            module.logger.debug(f"All filtered_remote_servers: {filtered_remote_servers}")
            result.remote_servers = [server.model_dump(mode="json") for server in filtered_remote_servers]
        else:
            result.remote_servers = [server.model_dump(mode="json") for server in remote_servers]

    if category == "software_images":
        all_images: Union[DataSequence[SoftwareImageDetails], Any] = module.get_response_safely(
            module.session.endpoints.configuration_software_actions.get_list_of_all_images
        )
        module.logger.info(f"get_list_of_all_images response: {all_images}")

        module.logger.debug(f"Filter: {module.params.get('filters')}")
        if module.params.get("filters"):
            filtered_all_images: Union[DataSequence[SoftwareImageDetails], Any] = all_images.filter(
                **module.params.get("filters")
            )
            module.logger.debug(f"All filtered_all_images: {filtered_all_images}")
            result.software_images = [server.model_dump(mode="json") for server in filtered_all_images]
        else:
            result.software_images = [server.model_dump(mode="json") for server in all_images]

    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
