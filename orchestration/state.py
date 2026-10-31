
from typing import Annotated, Any, TypedDict
import operator


class NetcoopState(TypedDict, total=False):

    # Incident information
    incident_id: str

    # Input data
    raw_telemetry: dict[str, Any]
    normalized_telemetry: dict[str, Any]

    # Validation and evidence
    validation_result: dict[str, Any]
    evidence: dict[str, Any]

    # Information collected from agents
    agent_findings: Annotated[list[dict[str, Any]], operator.add]
    agent_errors: Annotated[list[dict[str, Any]], operator.add]

    # Additional investigation data
    topology: dict[str, Any]
    affected_devices: list[str]
    service_health: dict[str, Any]

    # Diagnosis and recommendations
    diagnosis: dict[str, Any]
    recommendations: list[dict[str, Any]]

    # Final output
    report: dict[str, Any]
    workflow_status: str
