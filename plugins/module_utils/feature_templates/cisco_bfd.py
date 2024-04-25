cisco_bfd_definition = {
    "cisco_bfd": {
        "default": None,
        "options": {
            "color": {
                "default": None,
                "elements": "dict",
                "options": {
                    "color": {"default": None, "required": True, "type": "str"},
                    "dscp": {"default": None, "required": False, "type": "str"},
                    "hello_interval": {"default": None, "required": False, "type": "str"},
                    "multiplier": {"default": None, "required": False, "type": "str"},
                    "pmtu_discovery": {"default": None, "required": False, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "default_dscp": {"default": None, "required": False, "type": "str"},
            "multiplier": {"default": None, "required": False, "type": "str"},
            "poll_interval": {"default": None, "required": False, "type": "str"},
        },
        "required": False,
        "type": "dict",
    }
}
