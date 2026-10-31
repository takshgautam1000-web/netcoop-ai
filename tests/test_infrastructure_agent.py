
from protocol.schemas import AgentMessage, MessageType, MessageStatus
from agents.infrastructure_agent import handle


def test_infrastructure_agent_returns_findings():
    message = AgentMessage(
        message_id="MSG_101",
        correlation_id="CORR_101",
        incident_id="INC_101",
        sender="orchestrator",
        receiver="infrastructure_agent",
        message_type=MessageType.TASK,
        payload={
            "telemetry": {
                "timestamp": "2026-10-31T10:00:00Z",
                "device_id": "SW_CAMPUS_1",
                "metrics": {
                    "cpu_percent": 99.9,
                    "queue_drops": 8000,
                    "interface_errors": 250,
                    "latency_ms": 700,
                },
                "status": "Critical",
            }
        },
    )

    response = handle(message)

    assert response.message_type == MessageType.FINDING
    assert response.sender == "infrastructure_agent"
    assert response.correlation_id == "CORR_101"

    metrics_found = {
        item["metric"]
        for item in response.payload["findings"]
    }

    assert metrics_found == {
        "cpu_percent",
        "queue_drops",
        "interface_errors",
    }


def test_infrastructure_agent_reports_missing_metrics():
    message = AgentMessage(
        message_id="MSG_102",
        correlation_id="CORR_102",
        incident_id="INC_102",
        sender="orchestrator",
        receiver="infrastructure_agent",
        message_type=MessageType.TASK,
        payload={
            "telemetry": {
                "timestamp": "2026-10-31T10:00:00Z",
                "device_id": "SW_CAMPUS_2",
                "metrics": {
                    "cpu_percent": 50,
                },
            }
        },
    )

    response = handle(message)

    assert response.status == MessageStatus.PARTIAL
    assert "queue_drops" in response.payload["missing_metrics"]
    assert "interface_errors" in response.payload["missing_metrics"]


def test_infrastructure_agent_rejects_wrong_message_type():
    message = AgentMessage(
        message_id="MSG_103",
        correlation_id="CORR_103",
        incident_id="INC_103",
        sender="orchestrator",
        receiver="infrastructure_agent",
        message_type=MessageType.RESPONSE,
        payload={},
    )

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
