
from uuid import uuid4

from pydantic import ValidationError

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
    TelemetrySnapshot,
)
from ingestion.evidence_builder import build_evidence


INFRASTRUCTURE_METRICS = {
    "cpu_percent",
    "queue_drops",
    "interface_errors",
}


def handle(message: AgentMessage) -> AgentMessage:
    """Analyze infrastructure-related telemetry and return findings."""

    def make_response(
        message_type: MessageType,
        payload: dict,
        status: MessageStatus,
    ) -> AgentMessage:
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="infrastructure_agent",
            receiver="fault_correlation_agent",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Infrastructure Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    try:
        telemetry = TelemetrySnapshot.model_validate(
            message.payload["telemetry"]
        )

        report = build_evidence(telemetry)

        findings = [
            item.model_dump(mode="json")
            for item in report.evidence
            if item.metric in INFRASTRUCTURE_METRICS
        ]

        missing_metrics = [
            metric
            for metric in report.missing_metrics
            if metric in INFRASTRUCTURE_METRICS
        ]

        status = (
            MessageStatus.PARTIAL
            if missing_metrics
            else MessageStatus.COMPLETED
        )

        return make_response(
            MessageType.FINDING,
            {
                "agent": "infrastructure_agent",
                "findings": findings,
                "missing_metrics": missing_metrics,
                "reported_device_status": telemetry.status,
                "root_cause_determined": False,
            },
            status,
        )

    except (KeyError, ValidationError, ValueError) as error:
        return make_response(
            MessageType.ERROR,
            {"error": str(error)},
            MessageStatus.FAILED,
        )
