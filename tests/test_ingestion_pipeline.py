
from datetime import datetime, timezone

from ingestion.pipeline import process_organizer_input


def make_organizer_data():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": "SW_CAMPUS_01",
        "metrics": {
            "cpu_utilization_pct": 99.9,
            "link_utilization_pct": 100.0,
            "packet_loss_pct": 20.0,
            "latency_ms": 700.0,
            "queue_drops": 8000,
            "interface_errors": 250,
        },
        "status": "Critical",
    }


def test_organizer_input_pipeline():
    result = process_organizer_input(make_organizer_data())

    assert result.is_valid is True
    assert result.telemetry["device_id"] == "SW_CAMPUS_01"

    # Organizer field names should be normalized.
    assert result.telemetry["metrics"]["cpu_percent"] == 99.9

    # Evidence should be generated.
    assert len(result.evidence["evidence"]) > 0


def test_missing_metrics_are_not_treated_as_zero():
    data = make_organizer_data()
    data["metrics"].pop("interface_errors")

    result = process_organizer_input(data)

    assert result.telemetry["metrics"]["interface_errors"] is None
    assert "interface_errors" in result.evidence["missing_metrics"]


def test_organizer_input_is_not_mutated():
    data = make_organizer_data()
    original = data.copy()

    process_organizer_input(data)

    assert data == original
