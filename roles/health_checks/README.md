# Ansible Role: health_checks

This Ansible role performs health checks on Cisco vManage devices.

## Role Description

The `health_checks` role runs a series of health checks to ensure that the Cisco SD-WAN environment is operating as expected. It checks the state of various connections and sessions to validate their status:

- control connections
- orchestrator connections
- BFD sessions
- OMP sessions

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vmanage_instances`: List of vManage instances containing management IP, admin username, and admin password.

Example:

```yaml
vmanage_instances:
  - mgmt_public_ip: '192.0.2.1'
    admin_username: 'admin'
    admin_password: 'password'
```

## Example Playbook

Including an example of how to use your role (for instance, with variables passed in as parameters):

```yaml
- hosts: localhost
  gather_facts: no
  tasks:
    - name: Run health_checks
      import_role:
        name: health_checks
      vars:
        vmanage_instances:
          - mgmt_public_ip: '192.0.2.1'
            admin_username: 'admin'
            admin_password: 'password'
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
