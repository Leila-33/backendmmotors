from dataclasses import dataclass, field


@dataclass
class InspectionResult:

    engine_score: int
    brakes_score: int
    tires_score: int
    electronics_score: int

    safety_score: int
    overall_score: int

    failures: list[str] = field(
        default_factory=list
    )

    recommended_repairs: list[str] = field(
        default_factory=list
    )