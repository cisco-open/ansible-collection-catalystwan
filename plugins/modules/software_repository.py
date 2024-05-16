#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: software_repository
short_description: Manages software repositories and remote servers
version_added: "0.1.0"

description:
  - This module can be used to manage software repositories and remote servers.
  - It provides capabilities to add, update, or remove remote servers
  - It provides capabilities to upload or delete software images in the repository.

options:
  remote_server:
    description:
      - Defines the remote server configuration and state.
    type: dict
    suboptions:
      state:
        description:
          - Desired state of the remote server.
        type: str
        choices: [ 'present', 'absent' ]
        default: 'present'
      remote_server_id:
        description:
          - Unique identifier of the remote server.
        type: str
        aliases: [ 'id' ]
      remote_server_name:
        description:
          - Name of the remote server.
        type: str
        aliases: [ 'name' ]
      remote_server_url:
        description:
          - URL of the remote server.
        type: str
        aliases: [ 'url' ]
      remote_server_protocol:
        description:
          - Protocol used by the remote server.
        type: str
        choices: [ 'ftp', 'http', 'https', 'scp', 'sftp', 'tftp' ]  # Add actual protocols from RemoteServerProtocol
        default: 'ftp'
        aliases: [ 'protocol' ]
      remote_server_port:
        description:
          - Port number used by the remote server.
        type: int
        default: 21
        aliases: [ 'port' ]
      remote_server_vpn:
        description:
          - VPN ID used by the remote server.
        type: int
        choices: range(0, 65528)
        aliases: [ 'vpn' ]
      remote_server_user:
        description:
          - Username to authenticate to the remote server.
        type: str
        aliases: [ 'user' ]
      remote_server_password:
        description:
          - Password to authenticate to the remote server.
        type: str
        no_log: true
        aliases: [ 'password' ]
      image_location_prefix:
        description:
          - Prefix location for image storage.
        type: str
        default: '/'

  software:
    description:
      - Defines the software image configuration and state.
    type: dict
    suboptions:
      state:
        description:
          - Desired state of the software image.
        type: str
        choices: [ 'present', 'absent' ]
        default: 'present'
      software_id:
        description:
          - Unique identifier of the software image.
        type: str
        aliases: [ 'id' ]
      image_path:
        description:
          - Local path to the software image.
        type: str
        aliases: [ 'image_local_path' ]
      remote_server_name:
        description:
          - Name of the remote server where the image is located.
        type: str
        aliases: [ 'server_name' ]
      remote_filename:
        description:
          - Filename of the software image on the remote server.
        type: str
        aliases: [ 'filename' ]

author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
remote_server_info:
  description: Information about the remote server that was processed.
  returned: when a remote server is configured
  type: dict
  contains:
    id:
      description: Unique identifier of the remote server.
      type: str
      returned: success
      sample: "12345"
    name:
      description: Name of the remote server.
      type: str
      returned: success
      sample: "MyRemoteServer"
    url:
      description: URL of the remote server.
      type: str
      returned: success
      sample: "ftp://example.com"
    protocol:
      description: Protocol used by the remote server.
      type: str
      returned: success
      sample: "ftp"
    port:
      description: Port number used by the remote server.
      type: int
      returned: success
      sample: 21
    vpn:
      description: VPN ID used by the remote server.
      type: int
      returned: success
      sample: 10
    user:
      description: Username to authenticate to the remote server.
      type: str
      returned: success
      sample: "admin"

software_info:
  description: Information about the software image that was processed.
  returned: when a software image is configured
  type: dict
  contains:
    id:
      description: Unique identifier of the software image.
      type: str
      returned: success
      sample: "abcd1234"
    image_path:
      description: Local path to the software image.
      type: str
      returned: success
      sample: "/tmp/myimage.img"
    server_name:
      description: Name of the remote server where the image is located.
      type: str
      returned: success
      sample: "MyRemoteServer"
    filename:
      description: Filename of the software image on the remote server.
      type: str
      returned: success
      sample: "myimage.img"
"""

EXAMPLES = r"""
# Example to ensure remote server is present
- name: Ensure remote server is present
  cisco.catalystwan.software_repository:
    remote_server:
      state: present
      remote_server_name: "MyRemoteServer"
      remote_server_url: "ftp://example.com"
      remote_server_vpn: 10
      remote_server_user: "admin"
      remote_server_password: "password"  # pragma: allowlist secret

# Example to remove remote server by ID
- name: Remove remote server
  cisco.catalystwan.software_repository:
    remote_server:
      state: absent
      remote_server_id: "12345"

# Example to upload a software image to the manager
- name: Upload software image to the manager
  cisco.catalystwan.software_repository:
    software:
      state: present
      image_path: "/tmp/myimage.img"
      remote_server_name: "MyRemoteServer"
      remote_filename: "myimage.img"

# Example to remove a software image from the repository
- name: Remove software image from the repository
  cisco.catalystwan.software_repository:
    software:
      state: absent
      software_id: "abcd1234"
      remote_server_name: "MyRemoteServer"
"""

from enum import Enum
from pathlib import Path
from uuid import UUID

from catalystwan.endpoints.configuration.software_actions import (
    RemoteServer,
    RemoteServerInfo,
    RemoteServerProtocol,
    SoftwareImageDetails,
    SoftwareRemoteServer,
)
from catalystwan.typed_list import DataSequence
from catalystwan.utils.upgrades_helper import SoftwarePackageUploadPayload

from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class State(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"


def check_version_id_exists_in_repository(version_id: UUID, all_images: DataSequence[SoftwareImageDetails]):
    for image_details in all_images:
        if version_id == image_details.version_id:
            return True
    return False


def run_module():
    module_args = dict(
        remote_server=dict(
            type="dict",
            options=dict(
                state=dict(type="str", choices=[State.PRESENT, State.ABSENT], default=State.PRESENT.value),
                remote_server_id=dict(type="str", aliases=["id"]),
                remote_server_name=dict(type="str", aliases=["name"]),
                remote_server_url=dict(type="str", aliases=["url"]),
                remote_server_protocol=dict(
                    type="str",
                    choices=[choice for choice in RemoteServerProtocol],
                    default=RemoteServerProtocol.FTP.value,
                    aliases=["protocol"],
                ),
                remote_server_port=dict(type="int", default=21, aliases=["port"]),
                remote_server_vpn=dict(type="int", choices=range(0, 65528), aliases=["vpn"]),
                remote_server_user=dict(type="str", aliases=["user"]),
                remote_server_password=dict(type="str", aliases=["password"], no_log=True),
                image_location_prefix=dict(type="str", default="/"),
            ),
            required_if=[
                (
                    "state",
                    State.PRESENT.value,
                    (
                        "remote_server_name",
                        "remote_server_url",
                        "remote_server_vpn",
                        "remote_server_user",
                        "remote_server_password",
                    ),
                ),
                ("state", State.ABSENT.value, ("remote_server_id",), False),
            ],
            mutually_exclusive=[("remote_server_name", "id")],
        ),
        software=dict(
            type="dict",
            options=dict(
                state=dict(type="str", choices=[State.PRESENT, State.ABSENT], default=State.PRESENT.value),
                software_id=dict(type="str", aliases=["id"]),
                image_path=dict(type="str", aliases=["image_local_path"]),
                remote_server_name=dict(type="str", aliases=["server_name"]),
                remote_filename=dict(type="str", aliases=["filename"]),
            ),
            required_if=[
                ("state", State.PRESENT.value, ("image_path", "remote_server_name"), True),
                ("state", State.ABSENT.value, ("software_id",), True),
            ],
            mutually_exclusive=[("image_path", "remote_server_name")],
        ),
    )

    module = AnsibleCatalystwanModule(
        argument_spec=module_args,
        required_one_of=[
            ("remote_server", "software"),
        ],
    )
    result = ModuleResult()

    add_new_remote_server = False
    update_remote_server = False
    remove_remote_server = False
    upload_software_to_manager = False
    upload_software_from_remote_server = False
    delete_software_from_software_repository = False
    software_payload = None

    # ---------------------------------#
    # STEP 1 - verify module arguments #
    # ---------------------------------#
    # if remote_server_id is provided, filename must also be provided
    if module.params.get("software"):
        if (module.params["software"]["remote_server_name"] and not module.params["software"]["remote_filename"]) or (
            not module.params["software"]["remote_server_name"] and module.params["software"]["remote_filename"]
        ):
            module.fail_json(
                msg="Both arguments (remote_filename and remote_server_name) are required for upload from Remote Server"
            )

        if module.params["software"]["image_path"] and not Path(module.params["software"]["image_path"]).is_file():
            module.fail_json(
                msg=f'Cannot find file with provided path: {module.params["software"]["image_path"]}. '
                "Please verify your path variable and try again."
            )

    # ----------------------------------------------------------------#
    # STEP 2 - verify if any action required or state is changed = OK #
    # ----------------------------------------------------------------#

    if module.params.get("remote_server"):
        remote_servers = module.get_response_safely(
            module.session.endpoints.configuration_software_actions.get_list_of_remote_servers
        )
        module.logger.info(f"get_list_of_remote_servers response: {remote_servers}")

        if module.params["remote_server"]["state"] == State.PRESENT.value:
            existing_server: RemoteServerInfo = remote_servers.filter(
                remote_server_name=module.params["remote_server"]["remote_server_name"]
            ).single_or_default()

            if not existing_server:
                add_new_remote_server = True
            else:
                # NOTE We always update remote server if exists because it can have different password
                # and we cannot check that remotely
                existing_remote_server_id = existing_server.remote_server_id
                update_remote_server = True

        if module.params["remote_server"]["state"] == State.ABSENT.value:
            remote_server_id = module.params["remote_server"]["id"]
            existing_server: RemoteServerInfo = remote_servers.filter(remote_server_id=remote_server_id)
            if existing_server:
                remove_remote_server = True
            else:
                result.response[
                    "remove_remote_server"
                ] = f"Server with UUID: {remote_server_id} not present in Remote Servers List"

    if module.params.get("software"):
        image_path = module.params["software"].get("image_path")
        remote_server_id = module.params["software"].get("remote_server_id")
        remote_server_name = module.params["software"].get("remote_server_name")
        remote_filename = module.params["software"].get("filename")
        software_id = module.params["software"].get("software_id")
        software_state = module.params["software"]["state"]

        all_images: DataSequence[SoftwareImageDetails] = module.get_response_safely(
            module.session.endpoints.configuration_software_actions.get_list_of_all_images
        )
        module.logger.info(f"get_list_of_all_images response: {all_images}")

        if software_state == State.PRESENT.value and image_path:
            version_in_available_files = module.get_response_safely(
                module.session.api.repository.get_image_version, software_image=image_path
            )
            module.logger.info(f"get_image_version response for image_path: {image_path}: {version_in_available_files}")

            if not version_in_available_files:
                software_payload = SoftwarePackageUploadPayload(image_path=image_path)
                upload_software_to_manager = True
            else:
                result.msg = (
                    f"Image {image_path} already present in repository available files repository under version:\n"
                    f"{version_in_available_files}, skipping upload."
                )

        elif (
            software_state == State.PRESENT.value
            and remote_filename  # noqa: W503
            and (remote_server_id or remote_server_name)  # noqa: W503
        ):
            remote_servers = module.get_response_safely(
                module.session.endpoints.configuration_software_actions.get_list_of_remote_servers
            )
            module.logger.info(f"remote_servers response: {remote_servers}")
            target_remote_server: SoftwareRemoteServer = remote_servers.filter(
                remote_server_name=remote_server_name
            ).single_or_default()
            if not target_remote_server:
                module.fail_json(
                    msg=f"Cannot find requested remote_server_name: {remote_server_name} "
                    "in list of configured Remote Servers."
                )
            # NOTE PROBLEM WITH REMOTE SERVER
            # We can provide almost any path, and it can be dummy, image doesn't have to exists in this path.
            # May lead to way to many problems IMO
            image_in_repository = module.get_response_safely(
                module.session.api.repository.get_remote_image,
                remote_image_filename=remote_filename,
                remote_server_name=remote_server_name,
            )
            module.logger.info(
                f"get_remote_image response for remote_filename: {remote_filename}: {image_in_repository}"
            )

            if not image_in_repository:
                software_payload = SoftwareRemoteServer(
                    filename=remote_filename, remote_server_id=target_remote_server.remote_server_id
                )
                upload_software_from_remote_server = True
            else:
                result.msg = (
                    f"Image {remote_filename} already present in repository available files repository under version:\n"
                    f"{image_in_repository.available_files}, skipping upload."
                )

        if module.params["software"]["state"] == State.ABSENT.value and software_id:
            # NOTE We only can remove by software_id -> therefore it is on user side to find proper software_id
            if check_version_id_exists_in_repository(software_id, all_images):
                delete_software_from_software_repository = True
                remove_software_id = software_id
            else:
                result.msg = f"Requested image: {software_id} not present in software images on Manager."

    # ----------------------------------#
    # STEP 3 - perform required actions #
    # ----------------------------------#
    if add_new_remote_server:
        payload = RemoteServer(**module.params_without_none_values.get("remote_server"))
        module.send_request_safely(
            result,
            action_name="Add New Remote Server",
            send_func=module.session.endpoints.configuration_software_actions.add_new_remote_server,
            payload=payload,
            response_key="add_remote_server",
        )

    if update_remote_server:
        payload = RemoteServer(**module.params_without_none_values.get("remote_server"))
        module.send_request_safely(
            result,
            action_name="Update Remote Server",
            send_func=module.session.endpoints.configuration_software_actions.update_remote_server,
            payload=payload,
            id=existing_remote_server_id,
            response_key="update_remote_server",
        )

    if remove_remote_server:
        module.send_request_safely(
            result,
            action_name="Remove Remote Server",
            send_func=module.session.endpoints.configuration_software_actions.remove_remote_server,
            id=remote_server_id,
            response_key="remove_remote_server",
        )

    if upload_software_to_manager:
        module.send_request_safely(
            result,
            action_name="Upload Software To Manager",
            send_func=module.session.endpoints.configuration_device_software_update.upload_software_to_manager,
            payload=software_payload,
            response_key="upload_software_to_manager",
        )

    if upload_software_from_remote_server:
        module.send_request_safely(
            result,
            action_name="Upload Software From Remote Server",
            send_func=module.session.endpoints.configuration_software_actions.upload_software_from_remote_server,
            payload=software_payload,
            response_key="upload_software",
        )

    if delete_software_from_software_repository:
        module.send_request_safely(
            result,
            action_name="Delete Software From Manager",
            send_func=module.session.endpoints.configuration_software_actions.delete_software_from_software_repository,
            version_id=remove_software_id,
            response_key="delete_software",
        )

    # ----------------------------------#
    # STEP 4 - update and return result #
    # ----------------------------------#
    module.exit_json(**result.model_dump(mode="json"))


def main():
    run_module()


if __name__ == "__main__":
    main()
