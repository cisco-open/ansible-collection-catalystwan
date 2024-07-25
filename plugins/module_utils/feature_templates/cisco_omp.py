cisco_omp_definition = {
    "cisco_omp": {
        "default": None,
        "options": {
            "advertise": {
                "default": None,
                "elements": "dict",
                "options": {
                    "protocol": {"default": None, "required": True, "type": "str"},
                    "route": {"default": None, "required": False, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "advertisement_interval": {"default": None, "required": False, "type": "int"},
            "auto_translate": {"default": False, "required": False, "type": "bool"},
            "ecmp_limit": {"default": None, "required": False, "type": "int"},
            "eor_timer": {"default": None, "required": False, "type": "int"},
            "graceful_restart": {"default": True, "required": False, "type": "bool"},
            "graceful_restart_timer": {"default": None, "required": False, "type": "int"},
            "holdtime": {"default": None, "required": False, "type": "int"},
            "ignore_region_path_length": {"default": False, "required": False, "type": "bool"},
            "ipv6_advertise": {
                "default": None,
                "elements": "dict",
                "options": {"protocol": {"default": None, "required": True, "type": "str"}},
                "required": False,
                "type": "list",
            },
            "omp_admin_distance_ipv4": {"default": None, "required": False, "type": "int"},
            "omp_admin_distance_ipv6": {"default": None, "required": False, "type": "int"},
            "overlay_as": {"default": None, "required": False, "type": "int"},
            "send_path_limit": {"default": None, "required": False, "type": "int"},
            "shutdown": {"default": None, "required": False, "type": "bool"},
            "site_types": {"default": None, "elements": "str", "required": False, "type": "list"},
            "transport_gateway": {"default": None, "required": False, "type": "str"},
        },
        "required": False,
        "type": "dict",
    }
}
