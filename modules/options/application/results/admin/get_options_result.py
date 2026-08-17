# modules/options/application/results/get_options_result.py

from dataclasses import dataclass
from modules.options.domain.entities.option import Option


@dataclass
class GetOptionsResult:
    options: list[Option]