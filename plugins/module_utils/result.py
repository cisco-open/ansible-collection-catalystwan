# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Dict, Final, Optional

from pydantic import BaseModel, ConfigDict, Field

ALLOW: Final[str] = "allow"


class ModuleResult(BaseModel):
    model_config = ConfigDict(extra=ALLOW)

    response: Optional[Dict] = Field(default={})  # for responses from Manager after running action
    state: Optional[Dict] = Field(default={})  # for current state when no changes applied
    changed: bool = Field(default=False)
    msg: Optional[str] = Field(default="")
