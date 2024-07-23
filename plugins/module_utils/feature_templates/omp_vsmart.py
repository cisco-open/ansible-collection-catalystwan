omp_vsmart_definition = {
    "omp_vsmart": {
        "default": None,
        "options": {
            "advertisement_interval": {"default": None, "required": False, "type": "int"},
            "affinity_group_preference": {"default": False, "required": False, "type": "bool"},
            "discard_rejected": {"default": None, "required": False, "type": "bool"},
            "eor_timer": {"default": None, "required": False, "type": "int"},
            "graceful_restart": {"default": None, "required": False, "type": "bool"},
            "graceful_restart_timer": {"default": None, "required": False, "type": "int"},
            "holdtime": {"default": None, "required": False, "type": "int"},
            "send_backup_paths": {"default": None, "required": False, "type": "bool"},
            "send_path_limit": {"default": None, "required": False, "type": "int"},
            "shutdown": {"default": None, "required": False, "type": "bool"},
            "tloc_color": {"default": False, "required": False, "type": "bool"},
        },
        "required": False,
        "type": "dict",
    }
}
