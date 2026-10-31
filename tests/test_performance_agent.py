
from protocol.schemas import AgentMessage, MessageType, MessageStatus
from agents.performance_agent import handle


def test_performance_agent_returns_findings():
    message = AgentMessage(
        message_id="MSG_001",
        correlation_id="CORR_001",
        incident_id="INC_001",
        sender="orchestrator",
        receiver="performance_agent",
        message_type=MessageType.TASK,
        payload={
            "telemetry": {
                "timestamp": "2026-10-31T10:00:00Z",
                "device_id": "SW_CAMPUS_1",
                "metrics": {
                    "latency_ms": 250,
                    "jitter_ms": 50,
                    "packet_loss_percent": 0.8,
                    "link_utilization_percent": 75,
                },
                "status": "Warning",
            }
        },
    )

    response = handle(message)

    assert response.message_type == MessageType.FINDING
    assert response.sender == "performance_agent"
    assert response.correlation_id == "CORR_001"
    assert len(response.payload["findings"]) == 4
    assert response.payload["root_cause_determined"] is False


def test_performance_agent_reports_missing_metrics():
    message = AgentMessage(
        message_id="MSG_002",
        correlation_id="CORR_002",
        incident_id="INC_002",
        sender="orchestrator",
        receiver="performance_agent",
        message_type=MessageType.TASK,
        payload={
            "telemetry": {
                "timestamp": "2026-10-31T10:00:00Z",
                "device_id": "SW_CAMPUS_2",
                "metrics": {"latency_ms": 200},
            }
        },
    )

    response = handle(message)

    assert response.status == MessageStatus.PARTIAL
    assert "jitter_ms" in response.payload["missing_metrics"]


def test_performance_agent_rejects_wrong_message_type():
    message = AgentMessage(
        message_id="MSG_003",
        correlation_id="CORR_003",
        incident_id="INC_003",
        sender="orchestrator",
        receiver="performance_agent",
        message_type=MessageType.RESPONSE,
        payload={},
    )

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
