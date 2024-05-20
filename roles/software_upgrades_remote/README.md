# Ansible Role: software_upgrades_remote

This Ansible role is designed to perform software upgrades on Cisco SD-WAN devices using a remote server. It covers the entire workflow for upgrading vManage, vBond, vSmar devices using software images stored on a remote server configured with SCP.

## Role Description

The `software_upgrades_remote` role performs the following tasks:

1. Verifies that required variables for the role are present.
2. Informs the user to ensure the FTP server is correctly configured for remote server upgrades.
3. Configures the remote server within Cisco vManage.
4. Retrieves and validates the list of remote server repositories.
5. Uploads software images from the remote server to the Cisco vManage software repository.
6. Filters and asserts the presence of required software images in the vManage software repository.
7. Executes software upgrade operations on vManage, vBond, and vSmart controllers.
8. Sets the default software version on the controllers.
9. Cleans up available software images from the controllers if desired.
10. Verifies that the activated version is set as the current and default version.

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vmanage_instances`: List of vManage instances containing management IP, admin username, and admin password.
- `remote_server_name`: Name of the remote server to be used.
- `remote_server_url`: URL of the remote server.
- `remote_server_user`: Username for the remote server.
- `remote_server_password`: Password for the remote server.
- `remote_server_image_location_prefix`: Prefix for the image location on the remote server.
- `vmanage_remote_software_filename`: Software image filename for vManage.
- `viptela_remote_software_filename`: Software image filename for vBond and vSmart.
- `cedge_remote_software_filename`: Software image filename for cEdge.
- `controller_software_version_to_activate`: Version of the software to activate on controllers.
- `edge_software_version_to_activate`: Version of the software to activate on cEdge devices.
- `remove_available_software_from_device`: Boolean indicating whether to remove software from the device post-upgrade.

## Example Playbook

Including an example of how to use your role (with variables passed in as parameters):

```yaml
- hosts: localhost
  gather_facts: no
  tasks:
    - name: Run software_upgrades_remote
      import_role:
        name: software_upgrades_remote
      vars:
        vmanage_instances:
          - mgmt_public_ip: '192.0.2.1'
            admin_username: 'admin'
            admin_password: 'password'
        remote_server_name: 'my_remote_server'
        remote_server_url: 'scp://my.remote.server'
        remote_server_user: 'remote_user'
        remote_server_password: 'remote_password'
        remote_server_image_location_prefix: '/images'
        vmanage_remote_software_filename: 'viptela-vmanage-genericx86-64.zip'
        viptela_remote_software_filename: 'viptela-edge-genericx86-64.zip'
        cedge_remote_software_filename: 'c8000v-universalk9.17.XX.XX.X.XXX_V17_XX_X.SSA.bin'
        controller_software_version_to_activate: '20.3.1'
        edge_software_version_to_activate: '20.3.1'
        remove_available_software_from_device: true
```

## Known Limitations

- The role assumes that controllers are <20.13 version.
- Upgrades of cEdges from Remote Server are currently not included

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
