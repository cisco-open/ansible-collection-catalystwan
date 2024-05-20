# Ansible Role: api_ready

This Ansible role is designed to verify Manager API server readiness.
NOTE: Role must be used on localhost - API requests to Manager are done from local machine.

## Role Description

Key tasks:

- verifying variables
- check that API server is ready

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Example of `vmanage_instances`:

```yaml
vmanage_instances:
    - mgmt_public_ip: '198.51.100.10'
      admin_username: 'admin'
      admin_password: 'password'
```

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: localhost
  gather_facts: no
  roles:
    - role: cisco.catalystwan.api_ready
      vars:
        vmanage_instances:
          - mgmt_public_ip: '198.51.100.10'
            admin_username: 'admin'
            admin_password: 'password'
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
