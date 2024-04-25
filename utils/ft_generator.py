# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


import yaml

from enum import Enum
from typing import Type, Union, get_args, get_origin
from pathlib import Path, PurePath
from pprint import pformat
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from catalystwan.api.templates.models.supported import available_models
from catalystwan.utils.device_model import DeviceModel

PROJECT_ROOT_DIR = PurePath(Path.cwd())


def safe_issubclass(type_, class_):
    try:
        return issubclass(type_, class_)
    except TypeError:
        return False


def is_pydantic_model(type_):
    try:
        return issubclass(type_, BaseModel)
    except TypeError:
        return False


def field_to_ansible_option(field: FieldInfo):
    # # if field.description == "List of public keys for the user":
    # if field.description == "The identifier for the authentication key":
    #     from IPython import embed; embed()
    option = {
        "description": [field.description],
        "required": field.is_required(),
        "default": None,
        "type": "str",  # default type is str, will be overwritten as needed
    }
    if not field.is_required():
        if safe_issubclass(field.default, str) or safe_issubclass(field.default, str):
            option["default"] = field.default
        if safe_issubclass(type(field.default), Enum):
            option["default"] = field.default.value
        if safe_issubclass(type(field.default), list):
            option["default"] = field.default

    field_type = get_origin(field.annotation) or field.annotation
    args = get_args(field.annotation)
    subargs_base_types = [get_origin(annotation) for annotation in args]

    if field_type == bool:
        option["type"] = "bool"

    elif is_pydantic_model(field_type):
        option["type"] = "dict"
        option["suboptions"] = model_to_ansible_options(field_type)

    elif field_type == list or (field_type == Union and list in subargs_base_types):
        elements_type = next((arg for arg in args if arg is not None), None)
        if is_pydantic_model(elements_type):
            # from IPython import embed; embed()
            option["type"] = "list"
            option["elements"] = "dict"
            option["suboptions"] = model_to_ansible_options(elements_type)
        else:
            origin_type = get_origin(elements_type)
            if origin_type == list:
                user_class = get_args(elements_type)[0]
            else:
                user_class = None
            if is_pydantic_model(user_class):
                option["type"] = "list"
                option["elements"] = "dict"
                option["suboptions"] = model_to_ansible_options(user_class)
            else:
                option["type"] = "list"
                option["elements"] = "str"
    elif is_pydantic_model(field_type):
        option["type"] = "dict"
        option["suboptions"] = model_to_ansible_options(field_type)
    elif safe_issubclass(field_type, Enum):
        option["type"] = "str"
        option["choices"] = [item.value for item in field_type]
    elif field_type == Union and safe_issubclass(next((arg for arg in args if arg is not None), None), Enum):
        option["type"] = "str"
        option["choices"] = [item.value for item in args[0]]
    return option


def model_to_ansible_options(model: Type[BaseModel]):
    options = {}
    for field_name, field in model.model_fields.items():
        if field_name in [
            "template_name",
            "template_description",
            "device_models",
            "device_specific_variables",
        ]:
            continue
        options[field_name] = field_to_ansible_option(field)
    return options


def generate_ansible_docs(model: Type[BaseModel], model_name: str):
    if not hasattr(model, "_docs_description"):
        raise ValueError(f"Missing '_docs_description' documentation field for model {model_name}!")
    ansible_docs = {
        "options": {
            model_name: {
                "description": model._docs_description.default,
                "type": "dict",
                "suboptions": model_to_ansible_options(model),
            }
        }
    }
    return ansible_docs


# from catalystwan.api.templates.models.cisco_ntp_model import CiscoNTPModel

# available_models = {
#     "cisco_ntp": CiscoNTPModel,
# }


# Function to parse YAML data and return the argument spec
def generate_arg_spec(yaml_data):
    # Load the YAML data
    data = yaml.safe_load(yaml_data)

    # Function to recursively parse the options
    def parse_options(options):
        arg_spec = {}
        for opt_name, opt_info in options.items():
            if "type" in opt_info:
                # Basic fields
                # if opt_name == "key":
                #     from IPython import embed; embed()
                arg_spec[opt_name] = {
                    "type": opt_info["type"],
                    "required": opt_info.get("required", False),
                    "default": opt_info.get("default", None),
                }

                # Special case for 'list' type
                if opt_info["type"] == "list" and "elements" in opt_info:
                    arg_spec[opt_name]["elements"] = opt_info["elements"]

                # Recursively handle suboptions if present
                if "suboptions" in opt_info:
                    arg_spec[opt_name]["options"] = parse_options(opt_info["suboptions"])

        return arg_spec

    # Get the top-level options and parse them
    options = data.get("options", {})
    return parse_options(options)


for model_name, model_module in available_models.items():
    # Part for Ansible documentation
    ansible_docs = generate_ansible_docs(model_module, model_name)

    def to_nice_yaml(data):
        return yaml.dump(data, allow_unicode=True, default_flow_style=False, indent=4, sort_keys=False)

    template_dir = PROJECT_ROOT_DIR / "utils"
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    env.filters["to_nice_yaml"] = to_nice_yaml

    template_file = PurePath("ft_docs_template.j2")
    template = env.get_template(str(template_file))

    output = template.render(yaml_data=ansible_docs)

    filename = f"{PROJECT_ROOT_DIR}/plugins/doc_fragments/feature_template_{model_name}.py"
    with open(filename, "w") as f:
        f.write(output)

    print(f"File '{filename}' has been written successfully.")

    # Part for Ansible module arguments specification
    yaml_str = yaml.dump(ansible_docs, sort_keys=False)

    # Generate the argument spec
    arg_spec = generate_arg_spec(yaml_str)

    # Define the variable name
    variable_name = f"{model_name}_definition"

    # Write the generated dictionary to a Python file
    output_file = f"{PROJECT_ROOT_DIR}/plugins/module_utils/feature_templates/{model_name}.py"
    with open(output_file, "w") as file:
        file.write(f"{variable_name} = ")
        # Use pformat to get a string representation of the dictionary
        file.write(pformat(arg_spec, indent=2, width=80))
        file.write("\n")
    print(f"Argument spec saved to {output_file} under the variable {variable_name}")

    # Part for Ansible DeviceModel docs fragment
    # Load the template file
    template_file = "ft_device_model.j2"
    template = env.get_template(template_file)

    # Render the template with the DeviceModel enum
    output = template.render(DeviceModel=DeviceModel)

    # Write the output to a file
    file_name = f"{PROJECT_ROOT_DIR}/plugins/doc_fragments/device_models_feature_template.py"
    with open(file_name, "w") as f:
        f.write(output)
