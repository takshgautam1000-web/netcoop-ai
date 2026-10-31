
from uuid import uuid4

from pydantic import ValidationError

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)
from diagnosis.correlation_engine import correlate_findings


def handle(message: AgentMessage) -> AgentMessage:

    def make_response(message_type, payload, status):
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="fault_correlation_agent",
            receiver="orchestrator",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    # Accept only TASK messages
    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Fault Correlation Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    try:
        agent_findings = message.payload["agent_findings"]

        if not isinstance(agent_findings, list):
            raise ValueError("agent_findings must be a list.")

        # Run the correlation engine
        result = correlate_findings(agent_findings)

        # Determine response status
        if result["diagnosis_status"] == "insufficient_evidence":
            status = MessageStatus.PARTIAL
        else:
            status = MessageStatus.COMPLETED

        return make_response(
            MessageType.FINDING,
            {
                "agent": "fault_correlation_agent",
                "diagnosis": result,
                "root_cause_determined": False,
                "score_type": "heuristic_points",
            },
            status,
        )

    except (KeyError, TypeError, ValueError, ValidationError) as error:
        return make_response(
            MessageType.ERROR,
            {"error": str(error)},
            MessageStatus.FAILED,
        )
