from dataclasses import dataclass
from typing import Optional

from modules.core.enums import OptionType

@dataclass
class Option:
    id: str
    name: str
    type: OptionType
    price: Optional[float] = None
    is_active: bool = True