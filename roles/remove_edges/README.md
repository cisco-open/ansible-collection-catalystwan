# Ansible Role: remove_edges

This Ansible role is responsible for removing all Edge devices (vEdges) from a Cisco SD-WAN environment managed by Cisco vManage.

## Role Description

The `remove_edges` role executes a sequence of tasks that:

1. Verifies the necessary role-specific variables are set.
2. Retrieves the list of all Edge devices in the Cisco SD-WAN environment.
3. Invalidates Edge devices certificates before deletion.
4. Sends updates to controllers to propagate the changes.
5. Removes all Edge devices from the vManage inventory.

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
- hosts: localhost
  gather_facts: no
  tasks:
    - name: Run remove_edges
      import_role:
        name: remove_edges
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
