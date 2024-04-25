omp_vsmart_definition = {
    "omp_vsmart": {
        "default": None,
        "options": {
            "advertisement_interval": {"default": None, "required": False, "type": "str"},
            "affinity_group_preference": {"default": None, "required": False, "type": "str"},
            "discard_rejected": {"default": None, "required": False, "type": "str"},
            "eor_timer": {"default": None, "required": False, "type": "str"},
            "graceful_restart": {"default": None, "required": False, "type": "str"},
            "graceful_restart_timer": {"default": None, "required": False, "type": "str"},
            "holdtime": {"default": None, "required": False, "type": "str"},
            "send_backup_paths": {"default": None, "required": False, "type": "str"},
            "send_path_limit": {"default": None, "required": False, "type": "str"},
            "shutdown": {"default": None, "required": False, "type": "str"},
        },
        "required": False,
        "type": "dict",
    }
}
