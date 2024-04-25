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
            "contact": {"default": None, "required": True, "type": "str"},
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
            "location": {"default": None, "required": True, "type": "str"},
            "shutdown": {"default": None, "required": False, "type": "str"},
            "target": {
                "default": None,
                "elements": "dict",
                "options": {
                    "community_name": {"default": None, "required": True, "type": "str"},
                    "ip": {"default": None, "required": True, "type": "str"},
                    "port": {"default": None, "required": True, "type": "str"},
                    "source_interface": {"default": None, "required": True, "type": "str"},
                    "user": {"default": None, "required": True, "type": "str"},
                    "vpn_id": {"default": None, "required": True, "type": "str"},
                },
                "required": False,
                "type": "list",
            },
            "user": {
                "default": None,
                "elements": "dict",
                "options": {
                    "auth": {"default": None, "required": True, "type": "str"},
                    "auth_password": {"default": None, "required": True, "type": "str"},
                    "group": {"default": None, "required": True, "type": "str"},
                    "name": {"default": None, "required": True, "type": "str"},
                    "priv": {"default": None, "required": True, "type": "str"},
                    "priv_password": {"default": None, "required": True, "type": "str"},
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
                            "exclude": {"default": None, "required": True, "type": "str"},
                            "id": {"default": None, "required": True, "type": "str"},
                        },
                        "required": True,
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
