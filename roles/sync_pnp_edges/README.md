# Ansible Role: sync_pnp_edges

This Ansible role is designed to automate the process of synchronizing WAN Edge devices with Cisco's Plug and Play (PnP) portal and generating bootstrap configurations for Cisco SD-WAN devices. It also provides the capability to upload a custom WAN Edge list and to generate a file with edge deployment configurations.

## Role Description

The `sync_pnp_edges` role performs the following tasks:

1. Verifies that required variables for the role are present.
2. Informs the user that devices must be defined in the PnP Portal before synchronization can occur.
3. Optionally uploads a WAN Edge list if a path to the list is provided.
4. Synchronizes devices with the Smart Account if no WAN Edge list is provided by the user.
5. Generates bootstrap configurations for all devices in the Smart Account.
6. Initializes an empty dictionary to store generated data for edge instances.
7. Generates entries for the edge instances based on the bootstrap configurations.
8. Creates a file containing the edge deployment configuration data.

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vmanage_instances`: List of vManage instances containing management IP, admin username, and admin password.
- `wan_edge_list_path`: Optional path to the custom WAN Edge list.
- `pnp_username`: Username for the PnP Portal.
- `pnp_password`: Password for the PnP Portal.
- `organization_name`: Name of the organization to prefix to the hostname of the edge devices.
- `deployment_edges_config`: Path where the edge deployment configuration file will be stored.

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: all
  gather_facts: no
  tasks:
    - name: Synchronize WAN Edges and Generate Configurations
      import_role:
        name: sync_pnp_edges
      vars:
        vmanage_instances:
          - mgmt_public_ip: '192.0.2.1'
            admin_username: 'admin'
            admin_password: 'password'
        wan_edge_list_path: '/path/to/custom/wan_edge_list.csv'
        pnp_username: 'pnp_user'
        pnp_password: 'pnp_pass'
        organization_name: 'myorg'
        deployment_edges_config: '/path/to/deployment_edges_config.yml'
```

## Known Limitations

- The role assumes that the PnP Portal has been configured and that devices are already registered.
- The role does not cover the registration of new devices to the PnP Portal.

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
