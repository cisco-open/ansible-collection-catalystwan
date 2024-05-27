# Ansible Role: vmanage_mode

This Ansible role is designed to configure the operational mode of Cisco SD-WAN devices within a vManage environment. It can be used to set the mode for both controller (vSmart, vBond, vManage) and Edge (vEdge, cEdge) devices.

## Role Description

The `vmanage_mode` role performs the following tasks:

1. Verifies that the required variables for the role are present.
2. Sets the vManage mode for all controller devices including vSmart, vBond, and vManage instances.
3. Optionally sets the vManage mode for all Edge devices if `edge_instances` are defined.

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vmanage_instances`: List of vManage instances containing management IP, admin username, and admin password.
- `vsmart_instances`: List of vSmart controller instances with hostnames.
- `vbond_instances`: List of vBond controller instances with hostnames.
- `edge_instances`: Optional list of Edge device instances with hostnames.

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: all
  gather_facts: no
  tasks:
    - name: Configure vManage Mode for Controllers and Edges
      import_role:
        name: vmanage_mode
      vars:
        vmanage_instances:
          - mgmt_public_ip: '192.0.2.1'
            admin_username: 'admin'
            admin_password: 'password'
        vsmart_instances:
          - hostname: 'vsmart01'
        vbond_instances:
          - hostname: 'vbond01'
        edge_instances:
          - hostname: 'vedge01'
```

## Known Limitations

- The role assumes that the vManage, vSmart, vBond, and Edge devices are already registered and accessible within the vManage environment.
- The role does not cover initial device registration or provisioning in vManage.

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
