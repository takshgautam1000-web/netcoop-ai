from protocol.schemas import (
    TelemetryMetrics,
    TelemetrySnapshot,
    AgentMessage,
    MessageType,
)


def test_missing_metrics_remain_none():
    metrics = TelemetryMetrics(
        cpu_percent=50,
        latency_ms=120
    )

    assert metrics.jitter_ms is None
    assert metrics.interface_errors is None


def test_telemetry_snapshot():
    snapshot = TelemetrySnapshot(
        timestamp="2026-10-31T10:00:00Z",
        device_id="SW_CAMPUS_1",
        metrics={
            "cpu_percent": 45,
            "latency_ms": 120,
            "packet_loss_percent": 0.5
        },
        status="Warning"
    )

    assert snapshot.device_id == "SW_CAMPUS_1"
    assert snapshot.metrics.cpu_percent == 45


def test_agent_message():
    message = AgentMessage(
        message_id="MSG_001",
        correlation_id="CORR_001",
        incident_id="INC_001",
        sender="performance_agent",
        receiver="fault_correlation_agent",
        message_type=MessageType.FINDING,
        payload={
            "finding": "High latency detected",
            "latency_ms": 240
        }
    )

    assert message.sender == "performance_agent"
    assert message.payload["latency_ms"] == 240