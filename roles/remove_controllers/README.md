# Ansible Role: remove_controllers

This Ansible role is designed to remove all discoverable Cisco SD-WAN controllers, including vManage, vSmart, and vBond devices, from the Cisco vManage inventory.

## Role Description

The `remove_controllers` role executes the following tasks:

1. Verifies that all required variables for the role are set.
2. Gathers information about all controllers currently recognized in the Cisco vManage inventory.
3. Removes all discoverable controllers by setting their state to invalidated.

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.


## Role Variables

Variables expected by this role:

- `vmanage_instances`: A list of vManage instances containing management IP, admin username, and admin password.

Example of `vmanage_instances`:

```yaml
vmanage_instances:
  - mgmt_public_ip: '192.0.2.1'
    admin_username: 'admin'
    admin_password: 'password'
```

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: all
  gather_facts: localhost
  tasks:
    - name: Run remove_controllers
      import_role:
        name: remove_controllers
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
