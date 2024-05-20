# Ansible Role: onboarding_controllers

This Ansible role facilitates the onboarding process for Cisco SD-WAN controllers, including vManage, vSmart, and vBond devices. It handles certificate signing requests (CSRs) generation, controller additions, and validation of the device onboarding status.

## Role Description

The `onboarding_controllers` role performs the following tasks:

1. Verifies that all required variables for the role are set.
2. Generates CSRs for vManage devices.
3. Adds vSmart devices and registers the result of the addition.
4. Adds vBond devices and registers the result of the addition.
5. Waits until all controller devices are discoverable via system IP.
6. Waits until the certificate install status is "Installed" on all controllers.

## Requirements

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

## Dependencies

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

## Role Variables

Variables expected by this role:

- `vmanage_instances`: A list of vManage instances containing management IP, admin username, and admin password.
- `vsmart_instances`: A list of vSmart instances containing necessary details for onboarding.
- `vbond_instances`: A list of vBond instances containing necessary details for onboarding.

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
  tasks:
    - name: Run onboarding_controllers
      import_role:
        name: onboarding_controllers
      vars:
        vmanage_instances:
          - hostname: 'vmanage01'
            system_ip: '192.0.2.10'
            mgmt_public_ip: '198.51.100.10'
            admin_username: 'admin'
            admin_password: 'password'
        vsmart_instances:
          - hostname: 'vsmart01'
            system_ip: '192.0.2.20'
            transport_public_ip: '203.0.113.10'
            admin_username: 'admin'
            admin_password: 'password'
        vbond_instances:
          - hostname: 'vbond01'
            system_ip: '192.0.2.30'
            transport_public_ip: '203.0.113.20'
            admin_username: 'admin'
            admin_password: 'password'
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Arkadiusz Cichon <acichon@cisco.com>
