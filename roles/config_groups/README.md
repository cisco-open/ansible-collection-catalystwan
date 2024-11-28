Ansible Role: config_groups
=========

This Ansible role facilitates the process of creating configuration groups, assigning them to devices and deployment of those.

Requirements
------------

- `cisco.catalystwan` collection installed.
- Access details for the Cisco Manager instance must be provided.

Role Variables
--------------

- `config_group_name`: Name of config group to create.
- `config_group_description`: Description of config group to create.
- `system_profiles`: System profiles config YAML.
- `transport_profiles`: Transport profiles config YAML.
- `service_profiles`: Service profiles config YAML.
- `deployed_edge_instances`: List of deployed edge instances as created by `cisco.sdwan_deployment.aws_edges` and `cisco.sdwan_deployment.azure_edges` roles.

Dependencies
------------

There are no external role dependencies. Only `cisco.catalystwan` collection is required.

Example Playbook
----------------

```yaml
- name: Create and deploy config groups
  hosts: localhost
  import_role:
    name: config_groups
  vars:
    service_profiles:
    - description: ansible-generated Service Profile
      name: ansible-generated_LAN
      parcels:
      - config:
          data:
            enableSdra:
              optionType: global
              value: false
            ipv4Route: []
            name:
              optionType: global
              value: SERVICE
            vpnId:
              optionType: global
              value: 10
          description: LAN VPN
          name: Service_Network
        sub_parcels:
        - config:
            data:
              advanced:
                arpTimeout:
                  optionType: default
                  value: 1200
                icmpRedirectDisable:
                  optionType: default
                  value: true
                ipDirectedBroadcast:
                  optionType: default
                  value: false
                ipMtu:
                  optionType: default
                  value: 1500
                loadInterval:
                  optionType: default
                  value: 30
              description:
                optionType: default
              interfaceName:
                optionType: variable
                value: '{{ ''{{vpn_10_if_0}}'' }}'
              intfIpAddress:
                static:
                  staticIpV4AddressPrimary:
                    ipAddress:
                      optionType: variable
                      value: '{{ ''{{vpn_10_if_0_static_ipaddr}}'' }}'
                    subnetMask:
                      optionType: variable
                      value: '{{ ''{{vpn_10_if_0_static_subnet}}'' }}'
              nat:
                optionType: default
                value: false
              shutdown:
                optionType: global
                value: false
            description: LAN Interface
            name: VPN_Service_10_Interface
          type: ethernet
        type: vpn
    system_profiles:
    - description: ansible-generated Basic Profile
      name: ansible-generated_Basic
      parcels:
      - config:
          data:
            login:
              optionType: default
              value: ''
            motd:
              optionType: default
              value: ''
          description: Banner Description
          name: Banner
        type: banner
      - config:
          data:
            adminTechOnFailure:
              optionType: default
              value: true
            affinityGroupNumber:
              optionType: default
            affinityGroupPreference:
              optionType: default
            affinityPerVrf:
            - affinityGroupNumber:
                optionType: default
              vrfRange:
                optionType: default
            affinityPreferenceAuto:
              optionType: default
              value: false
            clock:
              timezone:
                optionType: default
                value: UTC
            consoleBaudRate:
              optionType: default
              value: '9600'
            controlSessionPps:
              optionType: default
              value: 300
            controllerGroupList:
              optionType: default
            description:
              optionType: default
            deviceGroups:
              optionType: default
            gpsLocation:
              latitude:
                optionType: default
              longitude:
                optionType: default
            idleTimeout:
              optionType: default
            location:
              optionType: default
            maxOmpSessions:
              optionType: default
            multiTenant:
              optionType: default
              value: false
            onDemand:
              onDemandEnable:
                optionType: default
                value: false
              onDemandIdleTimeout:
                optionType: default
                value: 10
            overlayId:
              optionType: default
              value: 1
            portHop:
              optionType: default
              value: true
            portOffset:
              optionType: default
              value: 0
            siteType:
              optionType: default
            trackDefaultGateway:
              optionType: default
              value: true
            trackInterfaceTag:
              optionType: default
            trackTransport:
              optionType: default
              value: true
          description: Basic Setting Description
          name: Basic
        type: basic
      - config:
          data:
            defaultDscp:
              optionType: default
              value: 48
            multiplier:
              optionType: default
              value: 6
            pollInterval:
              optionType: default
              value: 600000
          description: BFD Description
          name: BFD
        type: bfd
      - config:
          data:
            advertiseIpv4:
              bgp:
                optionType: default
                value: false
              connected:
                optionType: default
                value: true
              eigrp:
                optionType: default
                value: false
              isis:
                optionType: default
                value: false
              lisp:
                optionType: default
                value: false
              ospf:
                optionType: default
                value: false
              ospfv3:
                optionType: default
                value: false
              static:
                optionType: default
                value: true
            advertiseIpv6:
              bgp:
                optionType: default
                value: false
              connected:
                optionType: default
                value: false
              eigrp:
                optionType: default
                value: false
              isis:
                optionType: default
                value: false
              lisp:
                optionType: default
                value: false
              ospf:
                optionType: default
                value: false
              static:
                optionType: default
                value: false
            advertisementInterval:
              optionType: default
              value: 1
            ecmpLimit:
              optionType: default
              value: 4
            eorTimer:
              optionType: default
              value: 300
            gracefulRestart:
              optionType: default
              value: true
            gracefulRestartTimer:
              optionType: default
              value: 43200
            holdtime:
              optionType: default
              value: 60
            ignoreRegionPathLength:
              optionType: default
              value: false
            ompAdminDistanceIpv4:
              optionType: default
              value: 251
            ompAdminDistanceIpv6:
              optionType: default
              value: 251
            overlayAs:
              optionType: default
            sendPathLimit:
              optionType: default
              value: 4
            shutdown:
              optionType: default
              value: false
            siteTypesForTransportGateway:
              optionType: default
            transportGateway:
              optionType: default
          description: OMP Description
          name: OMP
        type: omp
      - config:
          data:
            disk:
              file:
                diskFileRotate:
                  optionType: default
                  value: 10
                diskFileSize:
                  optionType: default
                  value: 10
          description: Logging Description
          name: Logging
        type: logging
      - config:
          data:
            server:
            - key:
                optionType: default
              name:
                optionType: global
                value: time.google.com
              prefer:
                optionType: default
                value: false
              sourceInterface:
                optionType: default
              version:
                optionType: default
                value: 4
              vpn:
                optionType: default
                value: 0
          description: NTP Description
          name: NTP
        type: ntp
      - config:
          data:
            services_global:
              services_ip:
                globalOtherSettingsConsoleLogging:
                  optionType: default
                  value: true
                globalOtherSettingsIPSourceRoute:
                  optionType: default
                  value: false
                globalOtherSettingsIgnoreBootp:
                  optionType: default
                  value: true
                globalOtherSettingsSnmpIfindexPersist:
                  optionType: default
                  value: true
                globalOtherSettingsTcpKeepalivesIn:
                  optionType: default
                  value: true
                globalOtherSettingsTcpKeepalivesOut:
                  optionType: default
                  value: true
                globalOtherSettingsTcpSmallServers:
                  optionType: default
                  value: false
                globalOtherSettingsUdpSmallServers:
                  optionType: default
                  value: false
                globalOtherSettingsVtyLineLogging:
                  optionType: default
                  value: false
                globalSettingsHttpAuthentication:
                  optionType: default
                globalSettingsNat64TcpTimeout:
                  optionType: default
                  value: 3600
                globalSettingsNat64UdpTimeout:
                  optionType: default
                  value: 300
                globalSettingsSSHVersion:
                  optionType: default
                servicesGlobalServicesIpArpProxy:
                  optionType: default
                  value: false
                servicesGlobalServicesIpCdp:
                  optionType: default
                  value: true
                servicesGlobalServicesIpDomainLookup:
                  optionType: default
                  value: false
                servicesGlobalServicesIpFtpPassive:
                  optionType: default
                  value: false
                servicesGlobalServicesIpHttpServer:
                  optionType: default
                  value: false
                servicesGlobalServicesIpHttpsServer:
                  optionType: default
                  value: false
                servicesGlobalServicesIpLineVty:
                  optionType: default
                  value: false
                servicesGlobalServicesIpLldp:
                  optionType: default
                  value: true
                servicesGlobalServicesIpRcmd:
                  optionType: default
                  value: false
                servicesGlobalServicesIpSourceIntrf:
                  optionType: default
          description: Global Description
          name: Global
        type: global
      - config:
          data:
            accountingGroup:
              optionType: default
              value: false
            authenticationGroup:
              optionType: default
              value: false
            authorizationConfigCommands:
              optionType: default
              value: false
            authorizationConsole:
              optionType: default
              value: false
            serverAuthOrder:
              optionType: global
              value:
              - local
            user:
            - name:
                optionType: global
                value: admin
              password:
                optionType: variable
                value: '{{ ''{{admin_password}}'' }}'
              privilege:
                optionType: default
                value: '15'
          description: AAA Profile Feature Description
          name: AAA
        type: aaa
      - config:
          data:
            role:
              optionType: global
              value: edge-router
          description: Multi Region Fabric Description
          name: MRF
        type: mrf
    transport_profiles:
    - description: ansible-generated Transport Profile
      name: ansible-generated_WAN
      parcels:
      - config:
          data:
            enhanceEcmpKeying:
              optionType: global
              value: true
            ipv4Route: []
            vpnId:
              optionType: default
              value: 0
          description: SDWAN Transport Wan Vpn Feature config
          name: VPN0
        sub_parcels:
        - config:
            data:
              advanced:
                arpTimeout:
                  optionType: default
                  value: 1200
                icmpRedirectDisable:
                  optionType: default
                  value: true
                ipDirectedBroadcast:
                  optionType: default
                  value: false
                ipMtu:
                  optionType: default
                  value: 1500
                loadInterval:
                  optionType: default
                  value: 30
              allowService:
                all:
                  optionType: default
                  value: false
                bfd:
                  optionType: default
                  value: false
                bgp:
                  optionType: default
                  value: false
                dhcp:
                  optionType: default
                  value: true
                dns:
                  optionType: default
                  value: true
                https:
                  optionType: default
                  value: true
                icmp:
                  optionType: default
                  value: true
                netconf:
                  optionType: default
                  value: false
                ntp:
                  optionType: default
                  value: true
                ospf:
                  optionType: default
                  value: false
                snmp:
                  optionType: default
                  value: false
                ssh:
                  optionType: default
                  value: true
                stun:
                  optionType: default
                  value: false
              autoDetectBandwidth:
                optionType: default
                value: false
              blockNonSourceIp:
                optionType: default
                value: false
              description:
                optionType: global
                value: WAN VPN 0 Interface
              encapsulation:
              - encap:
                  optionType: global
                  value: ipsec
                preference:
                  optionType: default
                weight:
                  optionType: default
                  value: 1
              interfaceName:
                optionType: variable
                value: '{{ ''{{vpn_0_transport_if}}'' }}'
              intfIpAddress:
                dynamic:
                  dynamicDhcpDistance:
                    optionType: default
                    value: 1
              multiRegionFabric:
                coreRegion:
                  optionType: default
                  value: core-shared
                enableCoreRegion:
                  optionType: default
                  value: false
                enableSecondaryRegion:
                  optionType: default
                  value: false
                secondaryRegion:
                  optionType: default
                  value: secondary-shared
              nat:
                optionType: default
                value: false
              shutdown:
                optionType: global
                value: false
              tunnel:
                border:
                  optionType: default
                  value: false
                clearDontFragment:
                  optionType: default
                  value: false
                color:
                  optionType: global
                  value: mpls
                ctsSgtPropagation:
                  optionType: default
                  value: false
                excludeControllerGroupList:
                  optionType: default
                group:
                  optionType: default
                lowBandwidthLink:
                  optionType: default
                  value: false
                maxControlConnections:
                  optionType: default
                networkBroadcast:
                  optionType: default
                  value: false
                perTunnelQos:
                  optionType: default
                  value: false
                portHop:
                  optionType: default
                  value: true
                restrict:
                  optionType: default
                  value: false
                tunnelTcpMss:
                  optionType: default
                vBondAsStunServer:
                  optionType: default
                  value: false
                vManageConnectionPreference:
                  optionType: default
                  value: 5
              tunnelInterface:
                optionType: global
                value: true
            description: WAN VPN 0 Feature
            name: TRANSPORT
          type: ethernet
        type: vpn
    settable_variables:
      service:
        interface_names:
        - vpn_10_if_0
        static_ip_addresses:
        - vpn_10_if_0_static_ipaddr
        static_subnets:
        - vpn_10_if_0_static_subnet
      transport:
        interface_names:
        - vpn_0_transport_if
```

## License

"GPL-3.0-only"

## Author Information

This role was created by Przemyslaw Susko <sprzemys@cisco.com>
