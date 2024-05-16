#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: health_checks
short_description: Performs health checks on network devices managed by vManage
version_added: "0.1.0"
description:
  - This module performs various health checks on devices managed by vManage.
  - Available health chesk are choosen by C(check_type)
options:
  check_type:
    description:
      - The type of health check to perform.
    type: str
    choices: ["all", "control_connections", "orchestrator_connections", "device_system_status", "bfd", "omp"]
    default: "all"
  filters:
    description:
      - A dictionary of filters used to select devices for module action.
    type: dict
author:
  - Arkadiusz Cichon (acichon@cisco.com)
extends_documentation_fragment:
  - cisco.catalystwan.manager_authentication
"""

RETURN = r"""
msg:
  description: Message summarizing the health check outcome.
  returned: on failure
  type: str
  sample: "Not all health checks passed. See details."
success:
  description: Whether all health checks have passed successfully.
  returned: always
  type: bool
  sample: true
data:
  description: Detailed health check data.
  returned: always
  type: list
  sample:
    {"cpu_state": "normal", "mem_state": "normal", "memUsage": 75, "status": "normal", "reachability": "reachable"}
health_check_msg:
  description: Descriptive messages about each health check performed.
  returned: always
  type: list
  sample: ["All control connections are in state 'up' for vEdge 1.2.3.4"]
changed:
  description: Indicates if any changes were made by the module.
  returned: always
  type: bool
  sample: false
"""

EXAMPLES = r"""
# Example of using the module to run all health checks on all devices
- name: Run all health checks on all devices
  cisco.catalystwan.health_checks:
    check_type: "all"

# Example of using the module to check control connections on a specific device
- name: Check control connections on a specific device
  cisco.catalystwan.health_checks:
    check_type: "control_connections"
    device_uuid: "1.2.3.4"

# Example of using the module to check orchestrator connections on a specific device
- name: Check orchestrator connections on a specific device
  cisco.catalystwan.health_checks:
    check_type: "orchestrator_connections"
    device_uuid: "1.2.3.4"
"""

from enum import Enum
from typing import List, Optional

from catalystwan.dataclasses import Personality
from catalystwan.endpoints.configuration_device_inventory import DeviceDetailsResponse
from catalystwan.typed_list import DataSequence
from catalystwan.utils.creation_tools import asdict
from pydantic import Field

from ..module_utils.filters import get_devices_details
from ..module_utils.result import ModuleResult
from ..module_utils.vmanage_module import AnsibleCatalystwanModule


class ExtendedModuleResult(ModuleResult):
    health_summary: Optional[List] = Field(default=[])


class HealthCheckTypes(str, Enum):
    CONTROL_CONNECTIONS = "control_connections"
    ORCHERSTRATOR_CONNECTIONS = "orchestrator_connections"
    DEVICE_SYSTEM_STATUS = "device_system_status"
    BFD = "bfd"
    OMP = "omp"


def control_connections_have_state_up(
    result: ExtendedModuleResult, module: AnsibleCatalystwanModule, devices: DataSequence[DeviceDetailsResponse]
):
    EXCECTED_STATE = "up"
    control_connections_health = []
    result.response[f"{HealthCheckTypes.CONTROL_CONNECTIONS.value}"] = {}

    devices_list = [dev for dev in devices if dev.personality != Personality.VBOND]

    for dev in devices_list:
        # if device not reachable report problem but move with other devices to have all reported
        if dev.reachability != "reachable":
            control_connections_health.append(False)
            result.health_summary.append(
                f"Device {dev.personality}: {dev.uuid} - not reachable. Cannot verify control connections state.",
            )
            continue

        connections = module.get_response_safely(
            module.session.api.device_state.get_device_control_connections_info, device_id=dev.system_ip
        )
        module.logger.debug(f"control connections for {dev.uuid}: {[asdict(con) for con in connections]}")
        result.response[f"{HealthCheckTypes.CONTROL_CONNECTIONS.value}"][dev.uuid] = [
            asdict(connection) for connection in connections
        ]

        for connection in connections:
            if connection.state == EXCECTED_STATE:
                control_connections_health.append(True)
                result.health_summary.append(
                    f'Control connection state "{EXCECTED_STATE}" for {dev.personality} {dev.uuid}. '
                    f"peer-type: {connection.peerType}, system-ip: {connection.systemIp}"
                )
            else:
                control_connections_health.append(False)
                result.health_summary.append(
                    f'Wrong state "{connection.state}" for {dev.personality} {dev.uuid}. '
                    f"peer-type: {connection.peerType}, system-ip: {connection.systemIp}"
                )

    if not control_connections_health:
        result.msg = "No Control connections present!"
        module.fail_json(**result.model_dump(mode="json"))

    if not all(control_connections_health):
        result.msg = (
            "Not all health checks for control connections passed. "
            "See result.health_summary for list of all control connections state."
        )
        module.fail_json(**result.model_dump(mode="json"))

    result.msg = "All required health checks have been completed successfully"
    module.exit_json(**result.model_dump(mode="json"))


def orchestrator_connections_have_state_up(
    result: ExtendedModuleResult, module: AnsibleCatalystwanModule, devices: DataSequence[DeviceDetailsResponse]
):
    EXCECTED_STATE = "up"
    orchestrator_connections_health = []
    result.response[f"{HealthCheckTypes.ORCHERSTRATOR_CONNECTIONS.value}"] = {}

    vbonds = [dev for dev in devices if dev.personality == Personality.VBOND]
    for dev in vbonds:
        # if device not reachable report problem but move with other devices to have all reported
        if dev.reachability != "reachable":
            orchestrator_connections_health.append(False)
            result.health_summary.append(
                f"Device {dev.personality}: {dev.uuid} - not reachable. Cannot verify orchestrator connections state.",
            )
            continue

        connections = module.get_response_safely(
            module.session.api.device_state.get_device_orchestrator_connections_info, device_id=dev.system_ip
        )
        module.logger.debug(f"orchestrator connections for {dev.uuid}: {[asdict(con) for con in connections]}")
        result.response[f"{HealthCheckTypes.ORCHERSTRATOR_CONNECTIONS.value}"][dev.uuid] = [
            asdict(connection) for connection in connections
        ]

        for connection in connections:
            if connection.state == EXCECTED_STATE:
                orchestrator_connections_health.append(True)
                result.health_summary.append(
                    f'Orchestrator connection state "{EXCECTED_STATE}" for {dev.personality} {dev.uuid}. '
                    f"peer-type: {connection.peerType}, system-ip: {connection.systemIp}"
                )
            else:
                orchestrator_connections_health.append(False)
                result.health_summary.append(
                    f'Wrong state "{connection.state}" for {dev.personality} {dev.uuid}. '
                    f"peer-type: {connection.peerType}, system-ip: {connection.systemIp}"
                )

    if not orchestrator_connections_health:
        result.msg = "No Orchestractor connections present!"
        module.fail_json(**result.model_dump(mode="json"))

    if not all(orchestrator_connections_health):
        result.msg = (
            "Not all health checks for orchestrator connections passed. "
            "See result.health_summary for list of all orchestrator connections state."
        )
        module.fail_json(**result.model_dump(mode="json"))

    result.msg = "All required health checks have been completed successfully"
    module.exit_json(**result.model_dump(mode="json"))


def system_status_is_healthy(
    result: ExtendedModuleResult, module: AnsibleCatalystwanModule, devices: DataSequence[DeviceDetailsResponse]
):
    CPU_STATE = "normal"
    MEM_STATE = "normal"
    MEM_USAGE_THRESHOLD = 90
    DEVICE_STATUS = "normal"
    DEVICE_REACHABILITY = "reachable"

    system_status_is_healthy = []
    result.response[f"{HealthCheckTypes.DEVICE_SYSTEM_STATUS.value}"] = {}

    for dev in devices:
        # if devbice not reachable report problem but move with other devices to have all reported
        if dev.reachability != "reachable":
            system_status_is_healthy.append(False)
            result.health_summary.append(
                f"Device {dev.personality}: {dev.uuid} - not reachable. Cannot verify system status health.",
            )
            continue
        system_status = module.get_response_safely(
            module.session.api.device_state.get_system_status, device_id=dev.system_ip
        )
        if not system_status:
            module.session.api.devices.get(rediscover=True)
            system_status = module.session.api.device_state.get_system_status(dev.system_ip)

        module.logger.info(f"System status for {dev.uuid}: {asdict(system_status)}")
        result.response[f"{HealthCheckTypes.DEVICE_SYSTEM_STATUS.value}"][dev.uuid] = asdict(system_status)

        if isinstance(system_status.cpu_state, str) and system_status.cpu_state == CPU_STATE:
            system_status_is_healthy.append(True)
            result.health_summary.append(
                f'Expected cpu_state: "{CPU_STATE}" for {dev.personality} {dev.uuid}',
            )
        else:
            system_status_is_healthy.append(False)
            result.health_summary.append(f'Wrong cpu_state: "{system_status.cpu_state}" for {dev.uuid} has occurred')

        if isinstance(system_status.mem_state, str) and system_status.mem_state == MEM_STATE:
            system_status_is_healthy.append(True)
            result.health_summary.append(
                f'Expected mem_state: "{CPU_STATE}" for {dev.personality} {dev.uuid}',
            )
        else:
            system_status_is_healthy.append(False)
            result.health_summary.append(f'Wrong mem_state: "{system_status.mem_state}" for {dev.uuid} has occurred')

        if isinstance(system_status.memUsage, (int, float)) and system_status.memUsage < MEM_USAGE_THRESHOLD:
            system_status_is_healthy.append(True)
            result.health_summary.append(
                f'Expected memUsage: "{CPU_STATE}" for {dev.personality} {dev.uuid}',
            )
        else:
            system_status_is_healthy.append(False)
            result.health_summary.append(f'Wrong memUsage: "{system_status.memUsage}" for {dev.uuid} has occurred')

        if isinstance(system_status.status, str) and system_status.status == DEVICE_STATUS:
            system_status_is_healthy.append(True)
            result.health_summary.append(
                f'Expected device_status: "{DEVICE_STATUS}" for {dev.personality} {dev.uuid}',
            )
        else:
            system_status_is_healthy.append(False)
            result.health_summary.append(f'Wrong device_status: "{system_status.status}" for {dev.uuid} has occurred')

        if (
            isinstance(system_status.reachability.value, str)
            and system_status.reachability.value == DEVICE_REACHABILITY  # noqa: W503
        ):
            system_status_is_healthy.append(True)
            result.health_summary.append(
                f'Expected DEVICE_REACHABILITY status: "{DEVICE_REACHABILITY}" for {dev.personality} {dev.uuid}',
            )
        else:
            system_status_is_healthy.append(False)
            result.health_summary.append(
                f'Wrong DEVICE_REACHABILITY: "{system_status.reachability}" for {dev.uuid} has occurred'
            )

    if not system_status_is_healthy:
        result.msg = "Cannot evaluate system status health!"
        module.fail_json(**result.model_dump(mode="json"))

    if not all(system_status_is_healthy):
        result.msg = (
            "Not all health checks for system status passed. "
            "See result.health_summary for list of all system statuses."
        )
        module.fail_json(**result.model_dump(mode="json"))

    result.msg = "All required health checks have been completed successfully"
    module.exit_json(**result.model_dump(mode="json"))


def bfd_sessions_health(
    result: ExtendedModuleResult, module: AnsibleCatalystwanModule, devices: DataSequence[DeviceDetailsResponse]
):
    EXCECTED_STATE = "up"
    bfd_sessions_health = []
    result.response[f"{HealthCheckTypes.BFD.value}"] = {}

    for dev in devices:
        # if devbice not reachable report problem but move with other devices to have all reported
        if dev.reachability != "reachable":
            bfd_sessions_health.append(False)
            result.health_summary.append(
                f"Device {dev.personality}: {dev.uuid} - not reachable. Cannot verify BFD sessions state.",
            )
            continue

        bfd_sessions = module.get_response_safely(
            module.session.api.device_state.get_bfd_sessions, device_id=dev.system_ip
        )
        module.logger.info(f"BFD sessions for {dev.uuid}: {[asdict(ses) for ses in bfd_sessions]}")
        result.response[f"{HealthCheckTypes.BFD.value}"][dev.uuid] = [
            asdict(bfd_session) for bfd_session in bfd_sessions
        ]

        for bfd_session in bfd_sessions:
            if bfd_session.state == EXCECTED_STATE:
                bfd_sessions_health.append(True)
                result.health_summary.append(
                    f'BFD sessions state "{EXCECTED_STATE}" for {dev.personality} {dev.uuid} '
                    f"dst-ip: {bfd_session.destinationPublicIp}, src-ip: {bfd_session.sourceIp}"
                )
            else:
                bfd_sessions_health.append(False)
                result.health_summary.append(
                    f'Wrong state "{bfd_session.state}" for {dev.uuid}'
                    f"dst-ip: {bfd_session.destinationPublicIp}, src-ip: {bfd_session.sourceIp}"
                )

    if not bfd_sessions_health:
        result.msg = "No BFD sessions present!"
        module.fail_json(**result.model_dump(mode="json"))

    if not all(bfd_sessions_health):
        result.msg = (
            "Not all health checks for BFD sessions passed. "
            "See result.health_summary for list of all BFD sessions state."
        )
        module.fail_json(**result.model_dump(mode="json"))

    result.msg = "All required health checks have been completed successfully"
    module.exit_json(**result.model_dump(mode="json"))


def omp_sessions_health(
    result: ExtendedModuleResult, module: AnsibleCatalystwanModule, devices: DataSequence[DeviceDetailsResponse]
):
    EXCECTED_STATE = ["up", "UP"]
    omp_sessions_health = []
    result.response[f"{HealthCheckTypes.OMP.value}"] = {}

    for dev in devices:
        # if device not reachable report problem but move with other devices to have all reported
        if dev.reachability != "reachable":
            omp_sessions_health.append(False)
            result.health_summary.append(
                f"Device {dev.personality}: {dev.uuid} - not reachable. Cannot verify OMP sessions state.",
            )
            continue

        omp_sessions = module.get_response_safely(module.session.api.omp.get_omp_summary, device_id=dev.system_ip)
        module.logger.info(f"OMP summary data: {[asdict(ses) for ses in omp_sessions]}")
        result.response[f"{HealthCheckTypes.OMP.value}"][dev.uuid] = [
            asdict(omp_session) for omp_session in omp_sessions
        ]

        for omp_session in omp_sessions:
            if omp_session.oper_state in EXCECTED_STATE:
                omp_sessions_health.append(True)
                result.health_summary.append(
                    f'OMP sessions state "{EXCECTED_STATE[0]}" for {dev.personality} {dev.uuid}'
                )
            else:
                omp_sessions_health.append(False)
                result.health_summary.append(f'Wrong state "{omp_session.oper_state}" for {dev.uuid}')

    if not omp_sessions_health:
        result.msg = "No OMP sessions present!"
        module.fail_json(**result.model_dump(mode="json"))

    if not all(omp_sessions_health):
        result.msg = (
            "Not all health checks for OMP sessions passed. "
            "See result.health_summary for list of all OMP sessions state."
        )
        module.fail_json(**result.model_dump(mode="json"))

    result.msg = "All required health checks have been completed successfully"
    module.exit_json(**result.model_dump(mode="json"))


def run_module():
    module_args = dict(
        check_type=dict(
            type=str,
            choices=[check_type for check_type in HealthCheckTypes],
            required=True,
        ),
        filters=dict(type="dict", default=None),
    )

    module = AnsibleCatalystwanModule(argument_spec=module_args)
    result = ExtendedModuleResult()

    devices: DataSequence[DeviceDetailsResponse] = get_devices_details(module=module)
    module.logger.debug(f"Devices to test: {[dev.host_name for dev in devices]}")
    if not devices:
        result.msg = f"Empty devices list based on filter: {module.params.get('filters')}"
        module.exit_json(**result.model_dump(mode="json"))

    if module.params["check_type"] == HealthCheckTypes.CONTROL_CONNECTIONS:
        control_connections_have_state_up(result, module, devices)
    if module.params["check_type"] == HealthCheckTypes.ORCHERSTRATOR_CONNECTIONS:
        orchestrator_connections_have_state_up(result, module, devices)
    if module.params["check_type"] == HealthCheckTypes.DEVICE_SYSTEM_STATUS:
        system_status_is_healthy(result, module, devices)
    if module.params["check_type"] == HealthCheckTypes.BFD:
        bfd_sessions_health(result, module, devices)
    if module.params["check_type"] == HealthCheckTypes.OMP:
        omp_sessions_health(result, module, devices)


def main():
    run_module()


if __name__ == "__main__":
    main()
