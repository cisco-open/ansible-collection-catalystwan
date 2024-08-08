# Ansible Collection - cisco.catalystwan

## Overview

Reusable Ansible modules and roles that will help to automate Cisco
SD-WAN management (post bringup operations, day0, day1).

All modules are based on [catalystwan](https://github.com/cisco-open/cisco-catalyst-wan-sdk).

Collection available on Ansible Galaxy: [cisco.catalystwan](https://galaxy.ansible.com/ui/repo/published/cisco/catalystwan/)

## Table of Contents

- [Roadmap](#roadmap)
- [Requirements](#requirements)
- [Installing this collection](#installing-this-collection)
- [Using this collection](#using-this-collection)
- [Contributing](#contributing)
- [Useful links and Getting Started](#useful-links-and-getting-started)
- [License](#license)

---

## Roadmap

Support for the following workflows in vManage client and as Ansible modules:

- Detect API server readiness:
  - [x] in vManage-client?
  - [x] in cisco.catalystwan module

- Device onboarding (virtual and physical devices):
  - [x] in vManage-client?
  - [x] in cisco.catalystwan module

- Device health checks:
  - control/orchestrator connections check, and devices system health check
    - [x] in vManage-client?
    - [x] in cisco.catalystwan module
  - BFD and OMP checks (BFD needs at least 2 edge devices to talk to each other)
    - [x] in vManage-client?
    - [x] in cisco.catalystwan module

- Day 0 template attachment
  - [x] in vManage-client?
  - [x] in cisco.catalystwan module

- Onboarding via PNP (Smart account sync & certificates sync)
  - [x] in vManage-client?
  - [x] in cisco.catalystwan module

- Software upgrades
  - [x] in vManage-client?
  - [x] in cisco.catalystwan module

- Day 1 configuration(Edit)
  - [x] in vManage-client?
  - [ ] in cisco.catalystwan module

---

## Requirements

Currently development of the tool was set with:

- Python = 3.10.0
- Ansible = 2.16.6
- catalystwan = "^0.33.6post0"

## Installing this collection

In order to use collection, add these lines to `requirements.yml` file in your ansible directory:

```yaml
---
collections:
- name: git@github.com:cisco-open/ansible-collection-catalystwan.git
  type: git
  version: main
```

And run command:

```bash
ansible-galaxy collection install -r requirements.yml
```

### Python dependencies

The python module dependencies are not installed by ansible-galaxy. They can be manually installed using pip:

```bash
pip install -r requirements.txt
```

### Important ansible.cfg

It is important that your playbook execution will recognize this option from `ansible.cfg`:

```cfg
[defaults]
stdout_callback = debug
```

as it is highly recommended when debugging your module code.

If you want to test the modules already in your playbook, use `stdout_callback = yaml`.

### Credentials

Use `manager_authentication` module argument, to provide authentication credentials to your Manager:

```yml
- name: Get list of Edge devices
  cisco.catalystwan.devices_info:
    device_category: vedges
    manager_authentication:
      url: "x.x.x.x"
      username: "xxx"
      password: "xxx"
  register: edge_devices
```

See [Providing credentials to catalystwan Ansible modules](./plugins/README.md#providing-credentials-to-catalystwan-ansible-modules) for more information.

---

## Using this collection

To run the modules againts specific machines, you have to include your playbook to act on localhost:

```yaml
- name: Example playbook
  hosts: localhost
```

And then you can use the module:

```yaml
  tasks:
    - name: Get all active sessions
      cisco.catalystwan.active_sessions_info:
        manager_authentication:
          url: "x.x.x.x"
          username: "xxx"
          password: "xxx"
      register: active_sessions

```

### Logging

All of the modules will produce 2 log files: `ansible_catalystwan_module.log` and `ansible_catalystwan.log`.
Currently base dir destination of these log files will be current working directory of playbooks.

### Quick usage with example playbooks from .dev_dir

All of the modules are currently developed and tested with help of .dev_dir playbooks.
These playbooks offer initial config, onboarding and health checks.
If you want to run example playbook, supply your variables in `.dev_dir/dev_vars.yml`
and execute playbooks from `.dev_dir/` directory.

### Feature Templates

Feature Templates operations (`add` and `delete`) are supported via `cisco.catalystwan.feature_templates` module.

Available models are dependent on Catalystwan SDK, and they can be seen [here](https://github.com/cisco-open/cisco-catalyst-wan-sdk/blob/main/catalystwan/api/templates/models/supported.py).

For more information about adding new models see [Feature Templates generation](./plugins/README.md#feature-templates).

---

## Useful links and Getting Started

### Python

- [Download Python](https://www.python.org/downloads/)
- [Getting Started with Python](https://docs.python.org/3/using/index.html)

### Ansible

- [Install Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Getting Started with Ansible](https://docs.ansible.com/ansible/latest/user_guide/intro_getting_started.html)

- [Developing Modules General](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- [Developing Modules Best Practices](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_best_practices.html)
- [Ansible module architecture](https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html)

### Ansible Galaxy

Ansible Galaxy provides pre-packaged units of work known as roles, and it can be used to share and use content with Ansible.

- [Using Ansible Galaxy](https://galaxy.ansible.com/docs/)

### Cisco SD-WAN

- [Cisco SD-WAN Overview](https://www.cisco.com/c/en/us/solutions/enterprise-networks/sd-wan/index.html)
- [Cisco SD-WAN Documentation](https://www.cisco.com/c/en/us/support/routers/sd-wan/products-installation-and-configuration-guides-list.html)

---

## License

See [LICENSE](./LICENSE) file.

## Contributing

See [Contributing](./docs/CONTRIBUTING.md) file.

## Code of Conduct

See [Code of Conduct](./docs/CODE_OF_CONDUCT.md) file.

## Releasing, Versioning and Deprecation

This collection follows Semantic Versioning. More details on versioning can be found in [Understanding collection versioning](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_distributing.html#understanding-collection-versioning).

New minor and major releases as well as deprecations will follow new releases and deprecations of the Cisco Catalystwan SDK, a Python SDK, which this project relies on.
