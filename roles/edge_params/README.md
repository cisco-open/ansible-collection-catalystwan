# Ansible Role: edge_params

The `edge_params` Ansible extends deployment facts for cEdge devices with additional parameters required by other roles. 

## Role Description

The `edge_params` role extends deployment facts for cEdge devices with the following parameters:
- `uuid`
- `system_ip`
- `site_id`

## Requirements

- The `cisco.catalystwan` collection installed.
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
- name: Read deployed cEdge parameters
  hosts: localhost
  gather_facts: false
  vars:
    vmanage_instances:
      - mgmt_public_ip: '192.0.2.1'
        admin_username: 'admin'
        admin_password: 'password'
  roles:
    - cisco.catalystwan.edge_params
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Przemyslaw Susko <sprzemys@cisco.com>
