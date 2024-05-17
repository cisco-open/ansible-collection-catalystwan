# Ansible Role: administration_settings

This Ansible role is designed to manage the initial configuration of Cisco Manager devices and administration settings.
NOTE: Role must be used on localhost - API requests to Manager are done from local machine.

## Role Description

Key tasks:

- inform the user to manually verify that their PnP Portal Controller Profile is up to date with the vBond and organization name, pausing execution until the user confirms
- verifying variables
- setting iinitial configuration via administration settings

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vbond_transport_public_ip`: The public IP of the vBond transport.
- `organization_name`: The name of the organization.
- `validator_port`: The port used by the validator.
- `pnp_username`: The username for the PnP service account.
- `pnp_password`: The password for the PnP service account.
- `vmanage_instances`: A list of vManage instances, each containing management IP, admin username, and admin password.

Example of `vmanage_instances`:

```yaml
vmanage_instances:
  - hostname: 'vmanage01'
    system_ip: '192.0.2.10'
    mgmt_public_ip: '198.51.100.10'
    admin_username: 'admin'
    admin_password: 'password'
```

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: localhost
  gather_facts: no
  roles:
    - role: cisco.catalystwan.activate_edges
      vars:
        vbond_transport_public_ip: '203.0.113.100'
        organization_name: 'MyOrganization'
        validator_port: '12345'
        pnp_username: 'pnp_user'
        pnp_password: 'pnp_pass'
        vmanage_instances:
          - hostname: 'vmanage01'
            system_ip: '192.0.2.10'
            mgmt_public_ip: '198.51.100.10'
            admin_username: 'admin'
            admin_password: 'password'
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
