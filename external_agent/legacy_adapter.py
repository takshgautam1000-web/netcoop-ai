
from protocol.schemas import TelemetrySnapshot


def adapt_legacy_telemetry(raw: dict) -> TelemetrySnapshot:
    """
    Converts external protocol v0.9 telemetry
    into NETCOOP's canonical v1.0 telemetry format.
    """

    if not isinstance(raw, dict):
        raise ValueError("External telemetry must be a dictionary.")

    if raw.get("schema_version") != "0.9":
        raise ValueError("Unsupported external schema version.")

    measurements = raw.get("measurements")

    if not isinstance(measurements, dict):
        raise ValueError("measurements must be a dictionary.")

    metrics = {
        "cpu_percent": measurements.get("cpu_pct"),
        "link_utilization_percent": measurements.get("link_pct"),
        "packet_loss_percent": measurements.get("packet_loss_pct"),
        "latency_ms": (
            measurements["latency_seconds"] * 1000
            if measurements.get("latency_seconds") is not None
            else None
        ),
        "jitter_ms": (
            measurements["jitter_seconds"] * 1000
            if measurements.get("jitter_seconds") is not None
            else None
        ),
        "queue_drops": measurements.get("queue_drop_count"),
        "interface_errors": measurements.get("interface_error_count"),
    }

    return TelemetrySnapshot(
        timestamp=raw["observed_at"],
        device_id=raw["device"],
        status=raw.get("device_status"),
        metrics=metrics,
    )
