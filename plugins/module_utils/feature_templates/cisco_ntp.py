cisco_ntp_definition = {
    "cisco_ntp": {
        "default": None,
        "options": {
            "authentication": {
                "default": None,
                "elements": "dict",
                "options": {
                    "md5": {"default": None, "required": True, "type": "str"},
                    "number": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "enable": {"default": None, "required": False, "type": "str"},
            "server": {
                "default": [],
                "elements": "dict",
                "options": {
                    "key": {"default": None, "required": False, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "prefer": {"default": None, "required": False, "type": "str"},
                    "source_interface": {"default": None, "required": False, "type": "str"},
                    "version": {"default": None, "required": False, "type": "str"},
                    "vpn": {"default": None, "required": False, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "source": {"default": None, "required": False, "type": "str"},
            "stratum": {"default": None, "required": False, "type": "str"},
            "trusted": {"default": None, "elements": "str", "required": False, "type": "list"},
        },
        "required": False,
        "type": "dict",
    }
}
