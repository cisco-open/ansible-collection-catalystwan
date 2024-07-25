cisco_ntp_definition = {
    "cisco_ntp": {
        "default": None,
        "options": {
            "authentication": {
                "default": None,
                "elements": "dict",
                "options": {
                    "md5": {"default": None, "required": True, "type": "str"},
                    "number": {"default": None, "required": True, "type": "int"},
                },
                "required": False,
                "type": "list",
            },
            "enable": {"default": None, "required": False, "type": "bool"},
            "server": {
                "default": [],
                "elements": "dict",
                "options": {
                    "key": {"default": None, "required": False, "type": "int"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "prefer": {"default": None, "required": False, "type": "bool"},
                    "source_interface": {"default": None, "required": False, "type": "str"},
                    "version": {"default": None, "required": False, "type": "int"},
                    "vpn": {"default": None, "required": False, "type": "int"},
                },
                "required": False,
                "type": "list",
            },
            "source": {"default": None, "required": False, "type": "str"},
            "stratum": {"default": None, "required": False, "type": "int"},
            "trusted": {"default": None, "elements": "int", "required": False, "type": "list"},
        },
        "required": False,
        "type": "dict",
    }
}
