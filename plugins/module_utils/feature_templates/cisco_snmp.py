cisco_snmp_definition = {
    "cisco_snmp": {
        "default": None,
        "options": {
            "community": {
                "default": None,
                "elements": "dict",
                "options": {
                    "authorization": {"default": None, "required": True, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "view": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "contact": {"default": None, "required": False, "type": "str"},
            "group": {
                "default": None,
                "elements": "dict",
                "options": {
                    "name": {"default": None, "required": True, "type": "str"},
                    "security_level": {"default": None, "required": True, "type": "str"},
                    "view": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "location": {"default": None, "required": False, "type": "str"},
            "shutdown": {"default": True, "required": False, "type": "bool"},
            "target": {
                "default": None,
                "elements": "dict",
                "options": {
                    "community_name": {"default": None, "required": False, "type": "str"},
                    "ip": {"default": None, "required": True, "type": "str"},
                    "port": {"default": None, "required": True, "type": "int"},
                    "source_interface": {"default": None, "required": False, "type": "str"},
                    "user": {"default": None, "required": False, "type": "str"},
                    "vpn_id": {"default": None, "required": True, "type": "int"},
                },
                "required": False,
                "type": "list",
            },
            "user": {
                "default": None,
                "elements": "dict",
                "options": {
                    "auth": {"default": None, "required": False, "type": "str"},
                    "auth_password": {"default": None, "required": False, "type": "str"},
                    "group": {"default": None, "required": True, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "priv": {"default": None, "required": False, "type": "str"},
                    "priv_password": {"default": None, "required": False, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "view": {
                "default": None,
                "elements": "dict",
                "options": {
                    "name": {"default": None, "required": True, "type": "str"},
                    "oid": {
                        "default": None,
                        "elements": "dict",
                        "options": {
                            "exclude": {"default": None, "required": False, "type": "bool"},
                            "id": {"default": None, "required": True, "type": "str"},
                        },
                        "required": False,
                        "type": "list",
                    },
                },
                "required": False,
                "type": "list",
            },
        },
        "required": False,
        "type": "dict",
    }
}
