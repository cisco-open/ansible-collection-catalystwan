Ansible Role: feature_profile_builder
=========

This Ansible role generates feature profile configuration in YAML format, which can be used as input to `cisco.catalystwan.config_groups` role.

Requirements
------------

- `cisco.catalystwan` collection installed.

Role Variables
--------------

- `results_path`: The file path where generated config will be stored.
- `system_profiles`: A list of templated config for system profiles as such:
```yaml
system_profile:
  name: Name
  description: Description
  parcels: <A list of parcels config>
```
- `transport_profiles`: A list of templated config for transport profiles as such:
```yaml
transport_profile:
  name: Name
  description: Description
  parcels: <A list of parcels config>
```
- `service_profiles`: A list of templated config for service profiles as such:
```yaml
service_profiles:
  name: Name
  description: Description
  parcels: <A list of parcels config>
```

A parcel config is as such:
```yaml
template: template_name
config:
  parameter_to_override_1: value_to_override_1
  parameter_to_override_2: value_to_override_2
  parameter_to_override_3: value_to_override_3
sub_parcels: <A list of parcels config>
```
Where
- `template_name` matches a given parcel template name in the context of the feature profile type as defined [here](./templates).
- `config` is an optional field that you can use to override the values for specific parameters from the parcel template.
- `sub_parcels` is an optional field that can be set for a transport or service VPN parcel and represents a list of sub-parcels related to it.

Dependencies
------------

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

Example Playbook
----------------

```yaml
- name: Generate feature profile data
  hosts: localhost
  import_role:
    name: feature_profile_builder
  vars:
    system_profiles: 
      - name: System
        description: Description
        parcels:
          - template: banner
          - template: basic
    transport_profiles:
      - name: Transport
        description: Description
        parcels:
          wan_vpn_parcel:
            template: vpn
            config:
              name: OverridenName
            sub_parcels:
              - wan_interface_ethernet_parcel_1:
                template: ethernet
                config:
                    data:
                      interfaceName:
                        optionType: default
    service_profiles:
      - name: Service
        description: Description
        parcels:
        - template: vpn
          sub_parcels:
            - template: ethernet
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Przemyslaw Susko <sprzemys@cisco.com>
