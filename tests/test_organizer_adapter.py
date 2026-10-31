import pytest

from ingestion.organizer_adapter import adapt_organizer_telemetry


TIMESTAMP = "2026-10-31T10:00:00Z"


def make_telemetry(fault_type):
    """Create deterministic examples using the organizer's exact format."""

    data = {
        "timestamp": TIMESTAMP,
        "device_id": "SW_CAMPUS_1",
        "metrics": {},
    }

    if fault_type == "normal":
        data["metrics"] = {
            "cpu_utilization_pct": 25,
            "link_utilization_pct": 35,
            "packet_loss_pct": 0.0,
            "latency_ms": 12,
            "jitter_ms": 3,
            "queue_drops": 0,
        }
        data["status"] = "Healthy"

    elif fault_type == "latency_spike":
        data["metrics"] = {
            "cpu_utilization_pct": 55,
            "link_utilization_pct": 75,
            "packet_loss_pct": 0.8,
            "latency_ms": 250,
            "jitter_ms": 50,
            "queue_drops": 25,
        }
        data["status"] = "Warning"

    elif fault_type == "hardware_failure":
        data["metrics"] = {
            "cpu_utilization_pct": 99.9,
            "link_utilization_pct": 100.0,
            "packet_loss_pct": 20,
            "latency_ms": 700,
            "queue_drops": 8000,
            "interface_errors": 250,
        }
        data["status"] = "Critical"

    return data


@pytest.mark.parametrize(
    "fault_type",
    ["normal", "latency_spike", "hardware_failure"],
)
def test_all_organizer_scenarios_are_adapted(fault_type):
    raw = make_telemetry(fault_type)

    result = adapt_organizer_telemetry(raw)

    assert result.telemetry.device_id == "SW_CAMPUS_1"
    assert result.telemetry.timestamp is not None


def test_organizer_field_names_are_normalized():
    raw = make_telemetry("hardware_failure")

    result = adapt_organizer_telemetry(raw)
    metrics = result.telemetry.metrics

    assert metrics.cpu_percent == 99.9
    assert metrics.link_utilization_percent == 100.0
    assert metrics.packet_loss_percent == 20


def test_missing_jitter_is_not_treated_as_zero():
    raw = make_telemetry("hardware_failure")

    result = adapt_organizer_telemetry(raw)

    assert result.telemetry.metrics.jitter_ms is None
    assert "jitter_ms" in result.missing_metrics


def test_missing_interface_errors_are_detected():
    raw = make_telemetry("normal")

    result = adapt_organizer_telemetry(raw)

    assert result.telemetry.metrics.interface_errors is None
    assert "interface_errors" in result.missing_metrics


def test_malformed_metrics_are_rejected():
    raw = make_telemetry("normal")
    raw["metrics"] = None

    with pytest.raises(ValueError):
        adapt_organizer_telemetry(raw)