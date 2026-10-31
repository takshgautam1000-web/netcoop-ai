
from datetime import datetime, timezone

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)
from agents.service_health_agent import handle


def make_message(payload):
    return AgentMessage(
        message_id="msg-001",
        correlation_id="corr-001",
        incident_id="incident-001",
        sender="orchestrator",
        receiver="service_health_agent",
        message_type=MessageType.TASK,
        payload=payload,
    )


def make_service_data():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_id": "DNS_DHCP_SERVER_01",
        "metrics": {
            "dns_resolution_success_percent": 99,
            "dns_response_time_ms": 50,
            "dns_timeout_count": 0,
            "dhcp_success_percent": 99,
            "dhcp_response_time_ms": 100,
            "dhcp_failure_count": 0,
        },
    }


def test_missing_service_data():
    message = make_message({"telemetry": {}})

    response = handle(message)

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.PARTIAL
    assert response.payload["findings"] == []
    assert len(response.payload["missing_data"]) == 2


def test_dns_degradation():
    service_data = make_service_data()

    service_data["metrics"]["dns_resolution_success_percent"] = 65
    service_data["metrics"]["dns_response_time_ms"] = 450
    service_data["metrics"]["dns_timeout_count"] = 35

    response = handle(
        make_message({"service_health": service_data})
    )

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.COMPLETED
    assert len(response.payload["findings"]) == 3


def test_healthy_services():
    response = handle(
        make_message({"service_health": make_service_data()})
    )

    assert response.message_type == MessageType.FINDING
    assert response.status == MessageStatus.COMPLETED
    assert response.payload["findings"] == []
    assert response.payload["missing_data"] == []


def test_invalid_service_data():
    invalid_data = make_service_data()
    invalid_data["metrics"]["dns_response_time_ms"] = -100

    response = handle(
        make_message({"service_health": invalid_data})
    )

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED


def test_wrong_message_type():
    message = make_message({"service_health": make_service_data()})
    message.message_type = MessageType.RESPONSE

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
