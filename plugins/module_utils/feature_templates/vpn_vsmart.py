vpn_vsmart_definition = {
    "vpn_vsmart": {
        "default": None,
        "options": {
            "dns": {
                "default": None,
                "elements": "dict",
                "options": {
                    "dns_addr": {"default": None, "required": False, "type": "str"},
                    "role": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "host": {
                "default": None,
                "elements": "dict",
                "options": {
                    "hostname": {"default": None, "required": True, "type": "str"},
                    "ip": {"default": None, "elements": "str", "required": True, "type": "list"},
                },
                "required": False,
                "type": "list",
            },
            "name": {"default": None, "required": False, "type": "str"},
            "route_v4": {
                "default": None,
                "elements": "dict",
                "options": {
                    "distance": {"default": None, "required": False, "type": "int"},
                    "next_hop": {
                        "default": None,
                        "elements": "dict",
                        "options": {
                            "address": {"default": None, "required": False, "type": "str"},
                            "distance": {"default": None, "required": False, "type": "int"},
                        },
                        "required": False,
                        "type": "list",
                    },
                    "null0": {"default": None, "required": False, "type": "bool"},
                    "prefix": {"default": None, "required": False, "type": "str"},
                    "route_interface": {
                        "default": None,
                        "options": {
                            "interface_name": {"default": None, "required": True, "type": "str"},
                            "interface_next_hop": {
                                "default": None,
                                "elements": "dict",
                                "options": {
                                    "address": {"default": None, "required": False, "type": "str"},
                                    "distance": {"default": None, "required": False, "type": "int"},
                                },
                                "required": False,
                                "type": "list",
                            },
                        },
                        "required": False,
                        "type": "dict",
                    },
                    "vpn": {"default": None, "required": False, "type": "int"},
                },
                "required": False,
                "type": "list",
            },
            "route_v6": {
                "default": None,
                "elements": "dict",
                "options": {
                    "distance": {"default": None, "required": False, "type": "int"},
                    "next_hop": {
                        "default": None,
                        "elements": "dict",
                        "options": {
                            "address": {"default": None, "required": True, "type": "str"},
                            "distance": {"default": None, "required": False, "type": "int"},
                        },
                        "required": False,
                        "type": "list",
                    },
                    "null0": {"default": None, "required": False, "type": "bool"},
                    "prefix": {"default": None, "required": True, "type": "str"},
                    "vpn": {"default": None, "required": False, "type": "int"},
                },
                "required": False,
                "type": "list",
            },
            "vpn_id": {"default": None, "required": True, "type": "str"},
        },
        "required": False,
        "type": "dict",
    }
}
