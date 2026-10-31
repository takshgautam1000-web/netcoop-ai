
from pydantic import BaseModel

from ingestion.organizer_adapter import adapt_organizer_telemetry
from ingestion.validator import validate_telemetry
from ingestion.evidence_builder import build_evidence


class PipelineResult(BaseModel):
    telemetry: dict
    is_valid: bool
    warnings: list[str]
    errors: list[str]
    evidence: dict


def process_organizer_input(raw_data: dict) -> PipelineResult:

    # Step 1: Convert organizer format into our canonical format
    adapter_result = adapt_organizer_telemetry(raw_data)

    telemetry = adapter_result.telemetry

    # Step 2: Validate the normalized telemetry
    validation_result = validate_telemetry(telemetry)

    # Step 3: Build structured evidence
    evidence_result = build_evidence(telemetry)

    return PipelineResult(
        telemetry=telemetry.model_dump(mode="json"),
        is_valid=validation_result.is_valid,
        warnings=(
            adapter_result.warnings
            + validation_result.warnings
        ),
        errors=validation_result.errors,
        evidence=evidence_result.model_dump(mode="json"),
    )
