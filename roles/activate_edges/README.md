# Ansible Role: activate_edges

This Ansible role is designed to manage the activation process of Cisco Catalyst WAN Edge devices.
NOTE: Role must be used on localhost - API requests to Manager are done from local machine.

## Role Description

The `activate_edges` role ensure that Edge devices are properly synchronized and activated in the network.
It includes:

- verifying variables
- retrieving the list of Edge devices
- syncing them with controllers
- waiting until the devices are reachable and have completed the OTP (One-Time Password) phase
- ensuring that certificates are installed, and the devices are reachable

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role, example:

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
  roles:
    - role: cisco.catalystwan.activate_edges
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
