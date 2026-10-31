
from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)

from agents.connectivity_agent import handle


def make_message():
    return AgentMessage(
        message_id="MSG_201",
        correlation_id="CORR_201",
        incident_id="INC_201",
        sender="orchestrator",
        receiver="connectivity_agent",
        message_type=MessageType.TASK,
        payload={
            "topology": {
                "nodes": [
                    {"device_id": "R1", "device_type": "router"},
                    {"device_id": "S1", "device_type": "switch"},
                    {"device_id": "S2", "device_type": "switch"},
                    {"device_id": "S3", "device_type": "switch"},
                ],
                "edges": [
                    {"source": "R1", "target": "S1"},
                    {"source": "R1", "target": "S2"},
                    {"source": "S2", "target": "S3"},
                ],
            },
            "affected_devices": ["S1", "S2"],
        },
    )


def test_connectivity_agent_finds_common_neighbor():
    response = handle(make_message())

    assert response.message_type == MessageType.FINDING
    assert response.sender == "connectivity_agent"
    assert response.correlation_id == "CORR_201"

    assert response.payload["common_neighbors"] == ["R1"]


def test_connectivity_agent_finds_connected_devices():
    response = handle(make_message())

    connected = response.payload["connected_devices"]

    assert "R1" in connected["S1"]
    assert "S3" in connected["S1"]


def test_connectivity_agent_handles_unknown_device():
    message = make_message()
    message.payload["affected_devices"] = ["S1", "UNKNOWN"]

    response = handle(message)

    assert response.status == MessageStatus.PARTIAL
    assert response.payload["unknown_devices"] == ["UNKNOWN"]


def test_connectivity_agent_rejects_wrong_message_type():
    message = make_message()
    message.message_type = MessageType.RESPONSE

    response = handle(message)

    assert response.message_type == MessageType.ERROR
    assert response.status == MessageStatus.FAILED
