
from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)
from agents.fault_correlation_agent import handle


def make_message(payload, message_type=MessageType.TASK):
    return AgentMessage(
        message_id="msg-001",
        correlation_id="corr-001",
        incident_id="incident-001",
        sender="orchestrator",
        receiver="fault_correlation_agent",
        message_type=message_type,
        payload=payload,
    )


def test_combines_agent_findings():
    findings = [
        {
            "agent": "performance_agent",
            "evidence": [
                {"metric": "latency_ms", "value": 250},
            ],
            "missing_data": [],
        },
        {
            "agent": "infrastructure_agent",
            "evidence": [
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_data": [],
        },
    ]

    response = handle(make_message({"agent_findings": findings}))

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.COMPLETED

    diagnosis = response.payload["diagnosis"]

    assert len(diagnosis["all_evidence"]) == 2
    assert len(diagnosis["ranked_hypotheses"]) > 0


def test_insufficient_evidence():
    findings = [
        {
            "agent": "service_health_agent",
            "evidence": [],
            "missing_data": ["DNS health measurements"],
        }
    ]

    response = handle(make_message({"agent_findings": findings}))

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.PARTIAL

    assert (
        response.payload["diagnosis"]["diagnosis_status"]
        == "insufficient_evidence"
    )


def test_wrong_message_type():
    message = make_message(
        {"agent_findings": []},
        MessageType.RESPONSE,
    )

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED


def test_missing_agent_findings():
    response = handle(make_message({}))

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
