import inspect

from pydantic import BaseModel
from enum import Enum
from typing import get_type_hints, List, Optional

# Import the Pydantic models (assuming they are defined in the same file or are accessible from the script)
from catalystwan.api.templates.models.cisco_aaa_model import CiscoAAAModel

# Your Pydantic models should be defined here (as provided in your example)

# Function to convert a Pydantic model to YAML documentation
def model_to_yaml_docs(model_class, depth=0, is_suboption=False):
    indent = '  ' * depth
    # type_hints = get_type_hints(model_class)

    # Begin the options block
    docs = f"{indent}options:\n" if not is_suboption else ""

    for field_name, field_type in model_class.__annotations__.items():
        default_value = getattr(model_class, field_name, None)
        is_required = default_value is None and not issubclass(field_type, (Optional, List))
        is_list = issubclass(field_type, List)
        field_info = model_class.__fields__[field_name]

        # Skip if excluded
        if field_info.field_info.exclude:
            continue

        description = field_info.field_info.description
        docs += f"{indent}- name: {field_name}\n"
        docs += f"{indent}  description: {description}\n"
        docs += f"{indent}  type: {'list' if is_list else 'dict' if issubclass(field_type, BaseModel) else 'str'}\n"
        
        if is_required:
            docs += f"{indent}  required: True\n"
        else:
            docs += f"{indent}  required: False\n"
            if default_value is not None and not is_list:
                docs += f"{indent}  default: {default_value}\n"

        if issubclass(field_type, BaseModel):
            docs += f"{indent}  suboptions:\n"
            docs += model_to_yaml_docs(field_type, depth=depth + 2, is_suboption=True)
        elif is_list:
            element_type = next(iter(field_type.__args__), None)
            if issubclass(element_type, BaseModel):
                docs += f"{indent}  elements: dict\n"
                docs += f"{indent}  suboptions:\n"
                docs += model_to_yaml_docs(element_type, depth=depth + 2, is_suboption=True)
            elif issubclass(element_type, (str, int, Enum)):
                docs += f"{indent}  elements: {'str' if issubclass(element_type, (str, Enum)) else 'int'}\n"

        if issubclass(field_type, Enum):
            choices = [e.value for e in field_type]
            docs += f"{indent}  choices: {choices}\n"

    return docs

# Generate the YAML documentation for the CiscoAAAModel
yaml_docs = model_to_yaml_docs(CiscoAAAModel, depth=1)
print(yaml_docs)
