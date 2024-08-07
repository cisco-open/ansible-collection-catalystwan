#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# This file is autogenerated by `utils/feature_template_docs_generator.py`


from __future__ import annotations


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    cisco_system:
        description: Cisco System configuration settings for SD-WAN devices.
        type: dict
        suboptions:
            timezone:
                description:
                - The timezone setting for the system.
                required: false
                default: null
                type: str
                choices:
                - Europe/Andorra
                - Asia/Dubai
                - Asia/Kabul
                - America/Antigua
                - America/Anguilla
                - Europe/Tirane
                - Asia/Yerevan
                - Africa/Luanda
                - Antarctica/McMurdo
                - Antarctica/Rothera
                - Antarctica/Palmer
                - Antarctica/Mawson
                - Antarctica/Davis
                - Antarctica/Casey
                - Antarctica/Vostok
                - Antarctica/DumontDUrville
                - Antarctica/Syowa
                - America/Argentina/Buenos_Aires
                - America/Argentina/Cordoba
                - America/Argentina/Salta
                - America/Argentina/Jujuy
                - America/Argentina/Tucuman
                - America/Argentina/Catamarca
                - America/Argentina/La_Rioja
                - America/Argentina/San_Juan
                - America/Argentina/Mendoza
                - America/Argentina/San_Luis
                - America/Argentina/Rio_Gallegos
                - America/Argentina/Ushuaia
                - Pacific/Pago_Pago
                - Europe/Vienna
                - Australia/Lord_Howe
                - Antarctica/Macquarie
                - Australia/Hobart
                - Australia/Currie
                - Australia/Melbourne
                - Australia/Sydney
                - Australia/Broken_Hill
                - Australia/Brisbane
                - Australia/Lindeman
                - Australia/Adelaide
                - Australia/Darwin
                - Australia/Perth
                - Australia/Eucla
                - America/Aruba
                - Europe/Mariehamn
                - Asia/Baku
                - Europe/Sarajevo
                - America/Barbados
                - Asia/Dhaka
                - Europe/Brussels
                - Africa/Ouagadougou
                - Europe/Sofia
                - Asia/Bahrain
                - Africa/Bujumbura
                - Africa/Porto-Novo
                - America/St_Barthelemy
                - Atlantic/Bermuda
                - Asia/Brunei
                - America/La_Paz
                - America/Kralendijk
                - America/Noronha
                - America/Belem
                - America/Fortaleza
                - America/Recife
                - America/Araguaina
                - America/Maceio
                - America/Bahia
                - America/Sao_Paulo
                - America/Campo_Grande
                - America/Cuiaba
                - America/Santarem
                - America/Porto_Velho
                - America/Boa_Vista
                - America/Manaus
                - America/Eirunepe
                - America/Rio_Branco
                - America/Nassau
                - Asia/Thimphu
                - Africa/Gaborone
                - Europe/Minsk
                - America/Belize
                - America/St_Johns
                - America/Halifax
                - America/Glace_Bay
                - America/Moncton
                - America/Goose_Bay
                - America/Blanc-Sablon
                - America/Toronto
                - America/Nipigon
                - America/Thunder_Bay
                - America/Iqaluit
                - America/Pangnirtung
                - America/Resolute
                - America/Atikokan
                - America/Rankin_Inlet
                - America/Winnipeg
                - America/Rainy_River
                - America/Regina
                - America/Swift_Current
                - America/Edmonton
                - America/Cambridge_Bay
                - America/Yellowknife
                - America/Inuvik
                - America/Creston
                - America/Dawson_Creek
                - America/Vancouver
                - America/Whitehorse
                - America/Dawson
                - Indian/Cocos
                - Africa/Kinshasa
                - Africa/Lubumbashi
                - Africa/Bangui
                - Africa/Brazzaville
                - Europe/Zurich
                - Africa/Abidjan
                - Pacific/Rarotonga
                - America/Santiago
                - Pacific/Easter
                - Africa/Douala
                - Asia/Shanghai
                - Asia/Harbin
                - Asia/Chongqing
                - Asia/Urumqi
                - Asia/Kashgar
                - America/Bogota
                - America/Costa_Rica
                - America/Havana
                - Atlantic/Cape_Verde
                - America/Curacao
                - Indian/Christmas
                - Asia/Nicosia
                - Europe/Prague
                - Europe/Berlin
                - Europe/Busingen
                - Africa/Djibouti
                - Europe/Copenhagen
                - America/Dominica
                - America/Santo_Domingo
                - Africa/Algiers
                - America/Guayaquil
                - Pacific/Galapagos
                - Europe/Tallinn
                - Africa/Cairo
                - Africa/El_Aaiun
                - Africa/Asmara
                - Europe/Madrid
                - Africa/Ceuta
                - Atlantic/Canary
                - Africa/Addis_Ababa
                - Europe/Helsinki
                - Pacific/Fiji
                - Atlantic/Stanley
                - Pacific/Chuuk
                - Pacific/Pohnpei
                - Pacific/Kosrae
                - Atlantic/Faroe
                - Europe/Paris
                - Africa/Libreville
                - Europe/London
                - America/Grenada
                - Asia/Tbilisi
                - America/Cayenne
                - Europe/Guernsey
                - Africa/Accra
                - Europe/Gibraltar
                - America/Godthab
                - America/Danmarkshavn
                - America/Scoresbysund
                - America/Thule
                - Africa/Banjul
                - Africa/Conakry
                - America/Guadeloupe
                - Africa/Malabo
                - Europe/Athens
                - Atlantic/South_Georgia
                - America/Guatemala
                - Pacific/Guam
                - Africa/Bissau
                - America/Guyana
                - Asia/Hong_Kong
                - America/Tegucigalpa
                - Europe/Zagreb
                - America/Port-au-Prince
                - Europe/Budapest
                - Asia/Jakarta
                - Asia/Pontianak
                - Asia/Makassar
                - Asia/Jayapura
                - Europe/Dublin
                - Asia/Jerusalem
                - Europe/Isle_of_Man
                - Asia/Kolkata
                - Indian/Chagos
                - Asia/Baghdad
                - Asia/Tehran
                - Atlantic/Reykjavik
                - Europe/Rome
                - Europe/Jersey
                - America/Jamaica
                - Asia/Amman
                - Asia/Tokyo
                - Africa/Nairobi
                - Asia/Bishkek
                - Asia/Phnom_Penh
                - Pacific/Tarawa
                - Pacific/Enderbury
                - Pacific/Kiritimati
                - Indian/Comoro
                - America/St_Kitts
                - Asia/Pyongyang
                - Asia/Seoul
                - Asia/Kuwait
                - America/Cayman
                - Asia/Almaty
                - Asia/Qyzylorda
                - Asia/Aqtobe
                - Asia/Aqtau
                - Asia/Oral
                - Asia/Vientiane
                - Asia/Beirut
                - America/St_Lucia
                - Europe/Vaduz
                - Asia/Colombo
                - Africa/Monrovia
                - Africa/Maseru
                - Europe/Vilnius
                - Europe/Luxembourg
                - Europe/Riga
                - Africa/Tripoli
                - Africa/Casablanca
                - Europe/Monaco
                - Europe/Chisinau
                - Europe/Podgorica
                - America/Marigot
                - Indian/Antananarivo
                - Pacific/Majuro
                - Pacific/Kwajalein
                - Europe/Skopje
                - Africa/Bamako
                - Asia/Rangoon
                - Asia/Ulaanbaatar
                - Asia/Hovd
                - Asia/Choibalsan
                - Asia/Macau
                - Pacific/Saipan
                - America/Martinique
                - Africa/Nouakchott
                - America/Montserrat
                - Europe/Malta
                - Indian/Mauritius
                - Indian/Maldives
                - Africa/Blantyre
                - America/Mexico_City
                - America/Cancun
                - America/Merida
                - America/Monterrey
                - America/Matamoros
                - America/Mazatlan
                - America/Chihuahua
                - America/Ojinaga
                - America/Hermosillo
                - America/Tijuana
                - America/Santa_Isabel
                - America/Bahia_Banderas
                - Asia/Kuala_Lumpur
                - Asia/Kuching
                - Africa/Maputo
                - Africa/Windhoek
                - Pacific/Noumea
                - Africa/Niamey
                - Pacific/Norfolk
                - Africa/Lagos
                - America/Managua
                - Europe/Amsterdam
                - Europe/Oslo
                - Asia/Kathmandu
                - Pacific/Nauru
                - Pacific/Niue
                - Pacific/Auckland
                - Pacific/Chatham
                - Asia/Muscat
                - America/Panama
                - America/Lima
                - Pacific/Tahiti
                - Pacific/Marquesas
                - Pacific/Gambier
                - Pacific/Port_Moresby
                - Asia/Manila
                - Asia/Karachi
                - Europe/Warsaw
                - America/Miquelon
                - Pacific/Pitcairn
                - America/Puerto_Rico
                - Asia/Gaza
                - Asia/Hebron
                - Europe/Lisbon
                - Atlantic/Madeira
                - Atlantic/Azores
                - Pacific/Palau
                - America/Asuncion
                - Asia/Qatar
                - Indian/Reunion
                - Europe/Bucharest
                - Europe/Belgrade
                - Europe/Kaliningrad
                - Europe/Moscow
                - Europe/Volgograd
                - Europe/Samara
                - Asia/Yekaterinburg
                - Asia/Omsk
                - Asia/Novosibirsk
                - Asia/Novokuznetsk
                - Asia/Krasnoyarsk
                - Asia/Irkutsk
                - Asia/Yakutsk
                - Asia/Khandyga
                - Asia/Vladivostok
                - Asia/Sakhalin
                - Asia/Ust-Nera
                - Asia/Magadan
                - Asia/Kamchatka
                - Asia/Anadyr
                - Africa/Kigali
                - Asia/Riyadh
                - Pacific/Guadalcanal
                - Indian/Mahe
                - Africa/Khartoum
                - Europe/Stockholm
                - Asia/Singapore
                - Atlantic/St_Helena
                - Europe/Ljubljana
                - Arctic/Longyearbyen
                - Europe/Bratislava
                - Africa/Freetown
                - Europe/San_Marino
                - Africa/Dakar
                - Africa/Mogadishu
                - America/Paramaribo
                - Africa/Juba
                - Africa/Sao_Tome
                - America/El_Salvador
                - America/Lower_Princes
                - Asia/Damascus
                - Africa/Mbabane
                - America/Grand_Turk
                - Africa/Ndjamena
                - Indian/Kerguelen
                - Africa/Lome
                - Asia/Bangkok
                - Asia/Dushanbe
                - Pacific/Fakaofo
                - Asia/Dili
                - Asia/Ashgabat
                - Africa/Tunis
                - Pacific/Tongatapu
                - Europe/Istanbul
                - America/Port_of_Spain
                - Pacific/Funafuti
                - Asia/Taipei
                - Africa/Dar_es_Salaam
                - Europe/Kiev
                - Europe/Uzhgorod
                - Europe/Zaporozhye
                - Europe/Simferopol
                - Africa/Kampala
                - Pacific/Johnston
                - Pacific/Midway
                - Pacific/Wake
                - America/New_York
                - America/Detroit
                - America/Kentucky/Louisville
                - America/Kentucky/Monticello
                - America/Indiana/Indianapolis
                - America/Indiana/Vincennes
                - America/Indiana/Winamac
                - America/Indiana/Marengo
                - America/Indiana/Petersburg
                - America/Indiana/Vevay
                - America/Chicago
                - America/Indiana/Tell_City
                - America/Indiana/Knox
                - America/Menominee
                - America/North_Dakota/Center
                - America/North_Dakota/New_Salem
                - America/North_Dakota/Beulah
                - America/Denver
                - America/Boise
                - America/Phoenix
                - America/Los_Angeles
                - America/Anchorage
                - America/Juneau
                - America/Sitka
                - America/Yakutat
                - America/Nome
                - America/Adak
                - America/Metlakatla
                - Pacific/Honolulu
                - America/Montevideo
                - Asia/Samarkand
                - Asia/Tashkent
                - Europe/Vatican
                - America/St_Vincent
                - America/Caracas
                - America/Tortola
                - America/St_Thomas
                - Asia/Ho_Chi_Minh
                - Pacific/Efate
                - Pacific/Wallis
                - Pacific/Apia
                - Asia/Aden
                - Indian/Mayotte
                - Africa/Johannesburg
                - Africa/Lusaka
                - Africa/Harare
                - UTC
            description:
                description:
                - Set a text description of the device
                required: false
                default: null
                type: str
            hostname:
                description:
                - The hostname for the device.
                required: false
                type: raw
                suboptions:
                    name:
                        default: system_host_name
                        required: true
                        type: str
                        description: Device Specific Variables name
            location:
                description:
                - The physical location of the device.
                required: false
                default: null
                type: str
            latitude:
                description:
                - The latitude coordinate for the device's location.
                required: false
                default: null
                type: str
            longitude:
                description:
                - The longitude coordinate for the device's location.
                required: false
                default: null
                type: str
            range:
                description:
                - The range for geo-fencing feature.
                required: false
                default: null
                type: int
            enable_fencing:
                description:
                - Enable or disable geo-fencing.
                required: false
                default: null
                type: bool
            mobile_number:
                description:
                - List of mobile numbers for SMS notifications.
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    number:
                        description:
                        - The mobile phone number used for notification or security
                            purposes.
                        required: true
                        default: null
                        type: str
            enable_sms:
                description:
                - Enable or disable SMS notifications.
                required: false
                default: false
                type: bool
            device_groups:
                description:
                - List of device groups the device belongs to.
                required: false
                default: null
                type: list
                elements: str
            controller_group_list:
                description:
                - List of controller groups the device is associated with.
                required: false
                default: null
                type: list
                elements: int
            system_ip:
                description:
                - The system IP address of the device.
                required: false
                type: raw
                suboptions:
                    name:
                        default: system_system_ip
                        required: true
                        type: str
                        description: Device Specific Variables name
            overlay_id:
                description:
                - The overlay ID of the device.
                required: false
                default: null
                type: int
            site_id:
                description:
                - The site ID of the device.
                required: false
                default: system_site_id
                type: int
            site_type:
                description:
                - The site type classification for the device.
                required: false
                default: null
                type: list
                elements: str
                choices:
                - type-1
                - type-2
                - type-3
                - cloud
                - branch
                - br
                - spoke
            port_offset:
                description:
                - The port offset for the device.
                required: false
                default: null
                type: int
            port_hop:
                description:
                - Enable or disable port hopping.
                required: false
                default: null
                type: bool
            control_session_pps:
                description:
                - Control session packets per second setting.
                required: false
                default: null
                type: int
            track_transport:
                description:
                - Enable or disable transport tracking.
                required: false
                default: null
                type: bool
            track_interface_tag:
                description:
                - The tag of the interface to be tracked.
                required: false
                default: null
                type: int
            console_baud_rate:
                description:
                - The console baud rate setting for the device.
                required: false
                default: null
                type: str
                choices:
                - '1200'
                - '2400'
                - '4800'
                - '9600'
                - '19200'
                - '38400'
                - '57600'
                - '115200'
            max_omp_sessions:
                description:
                - The maximum number of OMP (Overlay Management Protocol) sessions.
                required: false
                default: null
                type: int
            multi_tenant:
                description:
                - Enable or disable multi-tenant support.
                required: false
                default: null
                type: bool
            track_default_gateway:
                description:
                - Enable or disable default gateway tracking.
                required: false
                default: null
                type: bool
            admin_tech_on_failure:
                description:
                - Enable or disable automatic generation of admin technical details
                    on failure.
                required: false
                default: null
                type: bool
            enable_tunnel:
                description:
                - Enable or disable tunnel functionality.
                required: false
                default: null
                type: bool
            idle_timeout:
                description:
                - The idle timeout setting for tunnels.
                required: false
                default: null
                type: int
            on_demand_idle_timeout_min:
                description:
                - The minimum idle timeout for on-demand tunnels.
                required: false
                default: null
                type: int
            tracker:
                description:
                - List of tracker configurations.
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    name:
                        description:
                        - Name for the Tracker
                        required: true
                        default: null
                        type: str
                    endpoint_ip:
                        description:
                        - The IP address of the endpoint to track.
                        required: false
                        default: null
                        type: str
                    endpoint_ip_transport_port:
                        description:
                        - The transport port of the endpoint IP address.
                        required: false
                        default: null
                        type: str
                    protocol:
                        description:
                        - The protocol used for the tracker (TCP or UDP).
                        required: false
                        default: null
                        type: str
                        choices:
                        - tcp
                        - udp
                    port:
                        description:
                        - The port number used for the tracker.
                        required: false
                        default: null
                        type: int
                    endpoint_dns_name:
                        description:
                        - The DNS name of the endpoint to track.
                        required: false
                        default: null
                        type: str
                    endpoint_api_url:
                        description:
                        - The API URL of the endpoint to track.
                        required: false
                        default: null
                        type: str
                    elements:
                        description:
                        - A list of elements to track.
                        required: false
                        default: null
                        type: list
                        elements: str
                    boolean:
                        description:
                        - The boolean condition to use when evaluating multiple elements.
                        required: false
                        default: or
                        type: str
                        choices:
                        - or
                        - and
                    threshold:
                        description:
                        - The threshold for triggering the tracker.
                        required: false
                        default: null
                        type: int
                    interval:
                        description:
                        - The interval at which the tracker checks the elements.
                        required: false
                        default: null
                        type: int
                    multiplier:
                        description:
                        - The multiplier used for determining the loss threshold.
                        required: false
                        default: null
                        type: int
                    type:
                        description:
                        - The type of tracker (interface or static route).
                        required: false
                        default: interface
                        type: str
                        choices:
                        - interface
                        - static-route
            object_track:
                description:
                - List of object tracking configurations.
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    object_number:
                        description:
                        - The tracking object number.
                        required: true
                        default: null
                        type: int
                    interface:
                        description:
                        - The name of the interface to track.
                        required: true
                        default: null
                        type: str
                    sig:
                        description:
                        - The signature associated with the tracking object.
                        required: true
                        default: null
                        type: str
                    ip:
                        description:
                        - The IP address used for tracking.
                        required: true
                        default: null
                        type: str
                    mask:
                        description:
                        - The subnet mask associated with the IP address for tracking.
                        required: false
                        default: 0.0.0.0
                        type: str
                    vpn:
                        description:
                        - The VPN instance associated with the tracking object.
                        required: true
                        default: null
                        type: int
                    object:
                        description:
                        - A list of objects related to the tracking.
                        required: true
                        default: null
                        type: list
                        elements: dict
                        suboptions:
                            number:
                                description:
                                - The unique identifier for the object.
                                required: true
                                default: null
                                type: int
                    boolean:
                        description:
                        - The boolean condition to use when evaluating multiple objects.
                        required: true
                        default: null
                        type: str
                        choices:
                        - or
                        - and
            region_id:
                description:
                - The region ID of the device.
                required: false
                default: null
                type: int
            secondary_region:
                description:
                - The secondary region ID of the device.
                required: false
                default: null
                type: int
            role:
                description:
                - The role of the device in the network.
                required: false
                default: null
                type: str
                choices:
                - edge-router
                - border-router
            affinity_group_number:
                description:
                - The affinity group number for VRF binding.
                required: false
                default: null
                type: int
            preference:
                description:
                - List of affinity group preferences.
                required: false
                default: null
                type: list
                elements: int
            preference_auto:
                description:
                - Enable or disable automatic preference setting for affinity groups.
                required: false
                default: null
                type: bool
            affinity_per_vrf:
                description:
                - List of affinity configurations per VRF.
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    affinity_group_number:
                        description:
                        - The affinity group number for VRF binding.
                        required: false
                        default: null
                        type: int
                    vrf_range:
                        description:
                        - The range of VRFs associated with the affinity group.
                        required: false
                        default: null
                        type: str
            transport_gateway:
                description:
                - Enable or disable the transport gateway feature.
                required: false
                default: null
                type: bool
            enable_mrf_migration:
                description:
                - Enable Multicast Routing Framework (MRF) migration settings.
                required: false
                default: null
                type: str
                choices:
                - enabled
                - enabled-from-bgp-core
            migration_bgp_community:
                description:
                - BGP community value for MRF migration.
                required: false
                default: null
                type: int
            enable_management_region:
                description:
                - Enable or disable management region configuration.
                required: false
                default: null
                type: bool
            vrf:
                description:
                - List of VRF configurations.
                required: false
                default: null
                type: list
                elements: dict
                suboptions:
                    vrf_id:
                        description:
                        - The VRF (VPN Routing and Forwarding) instance ID.
                        required: true
                        default: null
                        type: int
                    gateway_preference:
                        description:
                        - List of affinity group preferences for VRF
                        required: false
                        default: null
                        type: list
                        elements: int
            management_gateway:
                description:
                - Enable or disable the management gateway feature.
                required: false
                default: null
                type: bool
            epfr:
                description:
                - Edge Policy-based Framework Routing (EPFR) setting.
                required: false
                default: null
                type: str
                choices:
                - disabled
                - aggressive
                - moderate
                - conservative
    """
