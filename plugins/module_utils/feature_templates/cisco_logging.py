cisco_logging_definition = {
    "cisco_logging": {
        "default": None,
        "options": {
            "enable": {"default": None, "required": False, "type": "str"},
            "ipv6_server": {
                "default": None,
                "elements": "dict",
                "options": {
                    "custom_profile": {"default": None, "required": False, "type": "str"},
                    "enable_tls": {"default": None, "required": False, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "priority": {"default": "information", "required": False, "type": "str"},
                    "profile": {"default": None, "required": False, "type": "str"},
                    "source_interface": {"default": None, "required": False, "type": "str"},
                    "vpn": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "rotate": {"default": None, "required": False, "type": "str"},
            "server": {
                "default": None,
                "elements": "dict",
                "options": {
                    "custom_profile": {"default": None, "required": False, "type": "str"},
                    "enable_tls": {"default": None, "required": False, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "priority": {"default": "information", "required": False, "type": "str"},
                    "profile": {"default": None, "required": False, "type": "str"},
                    "source_interface": {"default": None, "required": False, "type": "str"},
                    "vpn": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "size": {"default": None, "required": False, "type": "str"},
            "tls_profile": {
                "default": None,
                "elements": "dict",
                "options": {
                    "auth_type": {"default": None, "required": True, "type": "str"},
                    "ciphersuite_list": {"default": None, "elements": "str", "required": False, "type": "list"},
                    "profile": {"default": None, "required": True, "type": "str"},
                    "version": {"default": "TLSv1.1", "required": False, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
        },
        "required": False,
        "type": "dict",
    }
}
