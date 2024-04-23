import yaml

yaml_data = """
options:
  cisco_aaa:
    description: Cisco AAA Feature Template configuration.
    type: dict
    suboptions:
      user:
        description:
        - List of user configurations
        required: false
        default: false
        type: list
        elements: dict
        suboptions:
          name:
            description:
            - The name of the user
            required: true
            default: null
            type: str
          password:
            description:
            - The password for the user
            required: false
            default: null
            type: str
          secret:
            description:
            - The secret for the user
            required: false
            default: null
            type: str
          privilege:
            description:
            - The privilege level for the user
            required: false
            default: null
            type: str
          pubkey_chain:
            description:
            - List of public keys for the user
            required: false
            default: []
            type: list
            elements: str
      authentication_group:
        description:
        - Whether to enable the authentication group
        required: false
        default: false
        type: bool
      accounting_group:
        description:
        - Whether to enable the accounting group
        required: false
        default: true
        type: bool
      radius:
        description:
        - List of Radius group configurations
        required: false
        default: null
        type: list
        elements: dict
        suboptions:
          group_name:
            description:
            - The name of the RADIUS group
            required: true
            default: null
            type: str
          vpn:
            description:
            - The VPN ID for the RADIUS group
            required: true
            default: null
            type: str
          source_interface:
            description:
            - The source interface for the RADIUS group
            required: true
            default: null
            type: str
          server:
            description:
            - The list of RADIUS servers for the group
            required: false
            default: []
            type: list
            elements: str
      domain_stripping:
        description:
        - The domain stripping configuration
        required: false
        default: null
        type: str
      port:
        description:
        - The port number for AAA
        required: false
        default: 1700
        type: str
      tacacs:
        description:
        - List of TACACS group configurations
        required: false
        default: null
        type: list
        elements: dict
        suboptions:
          group_name:
            description:
            - The name of the TACACS+ group
            required: true
            default: null
            type: str
          vpn:
            description:
            - The VPN ID for the TACACS+ group
            required: false
            default: 0
            type: str
          source_interface:
            description:
            - The source interface for the TACACS+ group
            required: false
            default: null
            type: str
          server:
            description:
            - The list of TACACS+ servers for the group
            required: false
            default: []
            type: list
            elements: str
      server_auth_order:
        description:
        - Authentication order to user access
        required: false
        default: local
        type: str
"""

# Function to parse YAML data and return the argument spec
def generate_arg_spec(yaml_data):
    # Load the YAML data
    data = yaml.safe_load(yaml_data)
    
    # Function to recursively parse the options
    def parse_options(options):
        arg_spec = {}
        for opt_name, opt_info in options.items():
            if 'type' in opt_info:
                # Basic fields
                arg_spec[opt_name] = {
                    'type': opt_info['type'],
                    'required': opt_info.get('required', False),
                    'default': opt_info.get('default', None)
                }
                
                # Special case for 'list' type
                if opt_info['type'] == 'list' and 'elements' in opt_info:
                    arg_spec[opt_name]['elements'] = opt_info['elements']
                
                # Recursively handle suboptions if present
                if 'suboptions' in opt_info:
                    arg_spec[opt_name]['options'] = parse_options(opt_info['suboptions'])
                
        return arg_spec
    
    # Get the top-level options and parse them
    options = data.get('options', {})
    return parse_options(options)

# Generate the argument spec
arg_spec = generate_arg_spec(yaml_data)

# Define the variable name
variable_name = "cisco_aaa_definition"

# Write the generated dictionary to a Python file
output_file = f"./plugins/module_args/cisco_aaa.py"
with open(output_file, 'w') as file:
    file.write(f"{variable_name} = ")
    # Use pformat to get a string representation of the dictionary
    from pprint import pformat
    file.write(pformat(arg_spec, indent=2, width=80))
    file.write("\n")

print(f"Argument spec saved to {output_file} under the variable {variable_name}")


# Printing the generated code in a Python syntax
import pprint
pprint.pprint(arg_spec)