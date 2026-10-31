
from protocol.schemas import TelemetrySnapshot
from ingestion.evidence_builder import build_evidence


def test_evidence_is_created():
    telemetry = TelemetrySnapshot(
        timestamp="2026-10-31T10:00:00Z",
        device_id="SW_CAMPUS_1",
        metrics={
            "cpu_percent": 99.9,
            "link_utilization_percent": 100,
            "packet_loss_percent": 20,
            "latency_ms": 700,
            "interface_errors": 250,
        },
        status="Critical",
    )

    report = build_evidence(telemetry)

    assert report.device_id == "SW_CAMPUS_1"
    assert len(report.evidence) == 5


def test_high_cpu_generates_observation():
    telemetry = TelemetrySnapshot(
        timestamp="2026-10-31T10:00:00Z",
        device_id="SW_CAMPUS_1",
        metrics={"cpu_percent": 99.9},
    )

    report = build_evidence(telemetry)

    cpu_evidence = next(
        item for item in report.evidence
        if item.metric == "cpu_percent"
    )

    assert "Extremely high" in cpu_evidence.observation


def test_missing_metrics_are_preserved():
    telemetry = TelemetrySnapshot(
        timestamp="2026-10-31T10:00:00Z",
        device_id="SW_CAMPUS_1",
        metrics={"cpu_percent": 50},
    )

    report = build_evidence(telemetry)

    assert "jitter_ms" in report.missing_metrics
    assert "interface_errors" in report.missing_metrics
    assert len(report.evidence) == 1
