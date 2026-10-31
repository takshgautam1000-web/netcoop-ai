
from uuid import uuid4

from agents.recommendation_agent import handle
from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)


def make_task(diagnosis):
    return AgentMessage(
        message_id=str(uuid4()),
        correlation_id="test-incident",
        incident_id="test-incident",
        sender="fault_correlation_agent",
        receiver="recommendation_agent",
        message_type=MessageType.TASK,
        payload={"diagnosis": diagnosis},
    )


def test_hardware_fault_recommendations():
    message = make_task({
        "primary_hypothesis": {
            "hypothesis": "interface_or_hardware_fault",
            "score": 3,
            "supporting_evidence": [
                {"metric": "interface_errors", "value": 250}
            ],
        }
    })

    response = handle(message)

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.COMPLETED
    assert len(response.payload["recommended_actions"]) > 0


def test_insufficient_evidence_recommendations():
    message = make_task({
        "primary_hypothesis": None
    })

    response = handle(message)

    assert response.status == MessageStatus.PARTIAL
    assert "additional telemetry" in (
        response.payload["recommended_actions"][0]["action"]
    )


def test_invalid_diagnosis():
    message = make_task(None)

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
