from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class InspectionResult:
    engine_score: int
    brakes_score: int
    tires_score: int
    electronics_score: int
    safety_score: int

    failures: List[str] = field(default_factory=list)
    recommended_repairs: List[str] = field(default_factory=list)