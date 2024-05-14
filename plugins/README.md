# Modules notes

## Recommended reading

[Developing Modules General](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)

[Developing Modules Best Practices](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_best_practices.html)

[Ansible module architecture](https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html)

---

## Mapping between REST API endpoints and Ansible modules DEPRECATED

Recommended convention:

* Ansible Modules do not map 1:1 API endpoints.

Justification:

* Modules should not require that a user know all the underlying options of an API/tool to be used.
* APIs are nested structures that couldn't be reflected in Modules structure
  Instead we will use roles to gather Modules into Workflows

## Gathering information about state of SD-WAN from vManage

Recommended convention:

* Name your modues `*_info` - and not `*_facts`.

Justification:

* Currently we are not operating on vManages like they are host (we do not specify them in inventory).
  Therefore we don't want to fetch information about the system and store it in `ansible_facts` - our goal
  is to fetch and if necessary reuse.

---

## Return values from modules

First thing to know is that we will use api endpoints that will return Data Models and:

* We are not focusing on HTTP requests parts like response code etc.
* We are here only to deal with data in nice Ansible wrapper

Recommended conventions:

* Modules will output JSON only
* Optional: incorporate wrapper that will be useful between DataModels and JSON objects

Justification:

* Modules must output valid JSON only (required by `exit_json()` method from `AnsibleModule`)
* Return values must be useful for other modules/tasks/roles/playbooks

Proposed common Return Values:

1. `changed`  # handled by AnsibleModule
2. `failed`  # handled by AnsibleModule
3. `invocation`:
    1. Can include `endpoint` and `payload`
    2. payload only if it is safe!
4. `response`
   1. what was returned by endpoint (vmgnclient model as dict/JSON)
5. `instances/interfaces/devices/certificates/templates` etc. Anything that will be useful in next task/module

---

## Feature Templates contribution

Module [feature_templaes](../plugins/modules/feature_templates.py) provide option to add Feature Templates.
This module is highly relaying on existing models of Feature Templates in Catalystwan SDK. If there is a missing
template that you want to use, you can contribute, and first add that model in Catalystwan SDK (important node: available_models dictionary is still used to determine which templates are supported)

When required model is already there, you can reuse [script for generating documentation and module args](../utils/ft_generator.py) (simply by running it as python script). If your model was correctly added in Catalystwan SDK, script should create 2 files:

* first one in `plugins/doc_fragments/` directory with .yml extension -> this one contains all documentation for that template in Ansible module

* second one in `plugins/module_utils/feature_templates` directory with .py extension -> this one contains all module args that can be reuse later in Ansible module

With these 2 files, you can extend `feature_templates` module by using `extends_documentation_fragment` fragment in DOCUMENTATION block, and also by using `module_args` dictionary extended by unpacked dictionary coming from `plugins/module_utils/feature_templates` file.

---

## Providing credentials to catalystwan Ansible modules

There are 3 ways to provide information to module about vManage you want to work with.
Also, the order they are presented is the order of precedence.

### 1. Module (task) common parameters

```yml
- name: Add vbond device
  cisco.catalystwan.devices:
    manager_authentication:
      url:  Y.Y.Y.Y
      username: admin
      password: 123456789
    ...
```

### #FIXME 2. Env variables (`VMANAGE_URL`, `VMANAGE_USERNAME`, `VMANAGE_PASSWORD`)

Mostly useful if you connect to ST vManage instance.

### #FIXME 3. Dedicated yaml credentials file indicated by setting env variable - `VMANAGE_CREDS_PATH`

Mostly useful if you connect to ST vManage instance.

```yml
vmanage_url: "XXX:10100"
vmanage_username: "XXX"
vmanage_password: "XXX"
```

Then export path to `vmanage_creds.yml` file:

```bash
export VMANAGE_CREDS_PATH="YOURPATH/vmanage_creds.yml"
```
