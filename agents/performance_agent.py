
from uuid import uuid4

from pydantic import ValidationError

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
    TelemetrySnapshot,
)
from ingestion.evidence_builder import build_evidence


PERFORMANCE_METRICS = {
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "link_utilization_percent",
}


def handle(message: AgentMessage) -> AgentMessage:
    """
    Receive a telemetry task, analyze performance metrics,
    and return structured findings to the Fault Correlation Agent.
    """

    def make_response(
        message_type: MessageType,
        payload: dict,
        status: MessageStatus,
    ) -> AgentMessage:
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="performance_agent",
            receiver="fault_correlation_agent",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Performance Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    try:
        # Convert incoming telemetry dictionary into our schema.
        telemetry = TelemetrySnapshot.model_validate(
            message.payload["telemetry"]
        )

        # Generate structured evidence.
        report = build_evidence(telemetry)

        # Keep only network performance observations.
        findings = [
            item.model_dump(mode="json")
            for item in report.evidence
            if item.metric in PERFORMANCE_METRICS
        ]

        missing_metrics = [
            metric
            for metric in report.missing_metrics
            if metric in PERFORMANCE_METRICS
        ]

        status = (
            MessageStatus.PARTIAL
            if missing_metrics
            else MessageStatus.COMPLETED
        )

        return make_response(
            MessageType.FINDING,
            {
                "agent": "performance_agent",
                "findings": findings,
                "missing_metrics": missing_metrics,
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
