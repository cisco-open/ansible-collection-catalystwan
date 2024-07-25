cisco_bfd_definition = {
    "cisco_bfd": {
        "default": None,
        "options": {
            "color": {
                "default": None,
                "elements": "dict",
                "options": {
                    "color": {"default": None, "required": True, "type": "str"},
                    "dscp": {"default": None, "required": False, "type": "int"},
                    "hello_interval": {"default": None, "required": False, "type": "int"},
                    "multiplier": {"default": None, "required": False, "type": "int"},
                    "pmtu_discovery": {"default": True, "required": False, "type": "bool"},
                },
                "required": False,
                "type": "list",
            },
            "default_dscp": {"default": None, "required": False, "type": "int"},
            "multiplier": {"default": None, "required": False, "type": "int"},
            "poll_interval": {"default": None, "required": False, "type": "int"},
        },
        "required": False,
        "type": "dict",
    }
}
