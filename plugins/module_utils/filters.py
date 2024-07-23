# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import traceback

from catalystwan.endpoints.configuration_device_inventory import DeviceDetailsResponse
from catalystwan.session import ManagerHTTPError
from catalystwan.typed_list import DataSequence

from ..module_utils.vmanage_module import AnsibleCatalystwanModule


def get_target_device(
    module: AnsibleCatalystwanModule,
    device_category="all",
    all_from_category: bool = False,
) -> DataSequence[DeviceDetailsResponse]:
    """
    Fetch list off all devices based on category, filer by either device_ip, hostname or uuid.
    Returns always single device
    """
    target_device = None
    try:
        controllers = module.session.endpoints.configuration_device_inventory.get_device_details(
            device_category="controllers"
        )
        vedges = module.session.endpoints.configuration_device_inventory.get_device_details(device_category="vedges")
        all_devices = controllers + vedges

        if device_category == "all":
            devices = all_devices
        elif device_category == "controllers":
            devices = controllers
        elif device_category == "vedges":
            devices = vedges
    except ManagerHTTPError as ex:
        module.fail_json(
            msg=f"Could not perform get_device_details action: {str(ex)}", exception=traceback.format_exc()
        )

    module.logger.info(f"Device Category: {device_category} \nAll devices response: {devices}")
    if module.params.get("device_ip"):
        target_device = devices.filter(device_ip=module.params["device_ip"]).single_or_default()
    if module.params.get("hostname"):
        target_device = devices.filter(host_name=module.params["hostname"]).single_or_default()
    if module.params.get("uuid"):
        target_device = devices.filter(uuid=module.params["uuid"]).single_or_default()
    if all_from_category:
        target_device = devices
    if target_device:
        module.logger.info(f"Detected device: {target_device}")
    return target_device


def get_devices_details(
    module: AnsibleCatalystwanModule,
) -> DataSequence[DeviceDetailsResponse]:
    """
    Returns DataSequence of DeviceDetailsResponse.
    They can be filtered based on provided filter.
    Or based on UUID we can have list of Devices.
    """
    devices = DataSequence(DeviceDetailsResponse)

    filters = module.params.get("filters")
    devices_uuid = module.params.get("devices")

    try:
        controllers = module.session.endpoints.configuration_device_inventory.get_device_details(
            device_category="controllers"
        )
        vedges = module.session.endpoints.configuration_device_inventory.get_device_details(device_category="vedges")
        all_devices = controllers + vedges

    except ManagerHTTPError as ex:
        module.fail_json(msg=f"Could not get devices details : {str(ex)}", exception=traceback.format_exc())

    if filters:
        filtered_devices = all_devices.filter(**filters)
        if filtered_devices is None:
            module.logger.warning(msg=f"Device filtered with `{filters}` does not exits.")
        module.logger.info(f"All devices filtered with filters: {filters}:\n{filtered_devices}")
        return filtered_devices

    if devices_uuid:
        if isinstance(devices_uuid, str):
            devices_uuid = [devices_uuid]  # if devices_uuid is a string, turn it into a list

        for uuid in devices_uuid:
            device = all_devices.filter(uuid=uuid).single_or_default()
            if device is None:
                module.logger.warning(msg=f"Device with uuid `{uuid}` does not exits.")
            else:
                devices.append(device)
            module.logger.info(f"All devices filtered with UUID: {devices}")
        return devices

    else:
        return all_devices
