import pytest

from modules.inspections.domain.entities.inspection import Inspection
from modules.reconditionings.application.results.admin.reconditioning_analysis_result import (
    ReconditioningAnalysisResult,
)
from modules.reconditionings.domain.exceptions import InvalidRepairConfiguration
from modules.reconditionings.application.services.perform_reconditioning_analysis import (
    perform_reconditioning_analysis,
)
from modules.inspections.domain.enums import InspectionStatus


def make_inspection(recommended_repairs=None):
    return Inspection(
        id="inspection-123",
        vehicle_id="vehicle-123",
        status=InspectionStatus.COMPLETED,
        recommended_repairs=recommended_repairs,
    )


def test_perform_reconditioning_analysis_with_multiple_repairs():
    inspection = make_inspection(
        [
            "ENGINE_DIAG",
            "BRAKES_REPLACE",
            "TIRES_REPLACE",
        ]
    )

    result = perform_reconditioning_analysis(inspection)

    assert isinstance(result, ReconditioningAnalysisResult)
    assert result.tasks == [
        "ENGINE_DIAG",
        "BRAKES_REPLACE",
        "TIRES_REPLACE",
    ]
    assert result.cost == 1600
    assert result.duration_days == 4


def test_perform_reconditioning_analysis_with_one_repair():
    inspection = make_inspection(["ELECTRONICS_DIAG"])

    result = perform_reconditioning_analysis(inspection)

    assert isinstance(result, ReconditioningAnalysisResult)
    assert result.tasks == ["ELECTRONICS_DIAG"]
    assert result.cost == 250
    assert result.duration_days == 1


def test_perform_reconditioning_analysis_without_repairs():
    inspection = make_inspection([])

    result = perform_reconditioning_analysis(inspection)

    assert isinstance(result, ReconditioningAnalysisResult)
    assert result.tasks == ["NO_REPAIR_NEEDED"]
    assert result.cost == 0
    assert result.duration_days == 1


def test_perform_reconditioning_analysis_with_none_repairs():
    inspection = make_inspection(None)

    result = perform_reconditioning_analysis(inspection)

    assert isinstance(result, ReconditioningAnalysisResult)
    assert result.tasks == ["NO_REPAIR_NEEDED"]
    assert result.cost == 0
    assert result.duration_days == 1


def test_perform_reconditioning_analysis_rejects_unknown_repair():
    inspection = make_inspection(["UNKNOWN_REPAIR"])

    with pytest.raises(
        InvalidRepairConfiguration,
        match="UNKNOWN_REPAIR",
    ):
        perform_reconditioning_analysis(inspection)