Ansible Role: cluster
=========

This Ansible role facilitates the process of adding and editing controllers to the cluster for Cisco SD-WAN vManage devices.

Requirements
------------

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

Role Variables
--------------
- `vmanage_instances`: A list of vManage instances containing management IP, admin username, and admin password. May also include vManage persona and services configuration for cluster usage.
- `default_services`: A list of services for cluster usage, such as `sd-avc`.

Dependencies
------------

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

Example Playbook
----------------

```yaml
- name: Edit vManage cluster IP address
  hosts: localhost
  import_role:
    name: cluster
  vars:
    vmanage_instances:
    - admin_password: password
      admin_username: user
      cluster_private_ip: 10.0.3.4
      hostname: vManage1
      mgmt_public_ip: 170.170.170.10
      persona: COMPUTE_AND_DATA
      cluster_services:
        sd-avc:
          server: true
    - admin_password: password
      admin_username: user
      cluster_private_ip: 10.0.3.5
      hostname: vManage2
      mgmt_public_ip: 170.170.170.20
      persona: COMPUTE_AND_DATA
    default_services:
      sd-avc:
        server: false
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Przemyslaw Susko <sprzemys@cisco.com>
