from dataclasses import dataclass

from modules.options.domain.entities.option import Option


@dataclass
class GetActiveOptionsResult:

    options: list[Option]