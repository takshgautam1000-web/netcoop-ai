
from datetime import datetime, timezone

from protocol.schemas import TelemetrySnapshot
from ingestion.validator import validate_telemetry


FIXED_NOW = datetime(2026, 10, 31, 10, 5, tzinfo=timezone.utc)


def make_snapshot():
    return TelemetrySnapshot(
        timestamp="2026-10-31T10:00:00Z",
        device_id="SW_CAMPUS_1",
        metrics={
            "cpu_percent": 25,
            "link_utilization_percent": 35,
            "packet_loss_percent": 0,
            "latency_ms": 12,
            "jitter_ms": 3,
            "queue_drops": 0,
            "interface_errors": 0,
        },
        status="Healthy",
    )


def test_healthy_telemetry():
    result = validate_telemetry(
        make_snapshot(), now=FIXED_NOW
    )

    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []


def test_stale_telemetry():
    snapshot = make_snapshot()

    result = validate_telemetry(
        snapshot,
        now=datetime(2026, 10, 31, 11, 0, tzinfo=timezone.utc),
    )

    assert any("stale" in warning for warning in result.warnings)


def test_status_mismatch():
    snapshot = make_snapshot()
    snapshot.metrics.cpu_percent = 99.9
    snapshot.status = "Healthy"

    result = validate_telemetry(
        snapshot, now=FIXED_NOW
    )

    assert any(
        "Reported status" in warning
        for warning in result.warnings
    )
