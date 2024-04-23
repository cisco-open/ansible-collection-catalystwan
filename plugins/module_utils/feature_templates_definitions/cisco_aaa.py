cisco_aaa_definition = { 'cisco_aaa': { 'default': None,
                 'options': { 'accounting_group': { 'default': True,
                                                    'required': False,
                                                    'type': 'bool'},
                              'authentication_group': { 'default': False,
                                                        'required': False,
                                                        'type': 'bool'},
                              'domain_stripping': { 'default': None,
                                                    'required': False,
                                                    'type': 'str'},
                              'port': { 'default': 1700,
                                        'required': False,
                                        'type': 'str'},
                              'radius': { 'default': None,
                                          'elements': 'dict',
                                          'options': { 'group_name': { 'default': None,
                                                                       'required': True,
                                                                       'type': 'str'},
                                                       'server': { 'default': [ ],
                                                                   'elements': 'str',
                                                                   'required': False,
                                                                   'type': 'list'},
                                                       'source_interface': { 'default': None,
                                                                             'required': True,
                                                                             'type': 'str'},
                                                       'vpn': { 'default': None,
                                                                'required': True,
                                                                'type': 'str'}},
                                          'required': False,
                                          'type': 'list'},
                              'server_auth_order': { 'default': 'local',
                                                     'required': False,
                                                     'type': 'str'},
                              'tacacs': { 'default': None,
                                          'elements': 'dict',
                                          'options': { 'group_name': { 'default': None,
                                                                       'required': True,
                                                                       'type': 'str'},
                                                       'server': { 'default': [ ],
                                                                   'elements': 'str',
                                                                   'required': False,
                                                                   'type': 'list'},
                                                       'source_interface': { 'default': None,
                                                                             'required': False,
                                                                             'type': 'str'},
                                                       'vpn': { 'default': 0,
                                                                'required': False,
                                                                'type': 'str'}},
                                          'required': False,
                                          'type': 'list'},
                              'user': { 'default': False,
                                        'elements': 'dict',
                                        'options': { 'name': { 'default': None,
                                                               'required': True,
                                                               'type': 'str'},
                                                     'password': { 'default': None,
                                                                   'required': False,
                                                                   'type': 'str'},
                                                     'privilege': { 'default': None,
                                                                    'required': False,
                                                                    'type': 'str'},
                                                     'pubkey_chain': { 'default': [ ],
                                                                       'elements': 'str',
                                                                       'required': False,
                                                                       'type': 'list'},
                                                     'secret': { 'default': None,
                                                                 'required': False,
                                                                 'type': 'str'}},
                                        'required': False,
                                        'type': 'list'}},
                 'required': False,
                 'type': 'dict'}}
