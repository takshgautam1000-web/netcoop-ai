from typing import Any

from pydantic import BaseModel, Field

from protocol.schemas import TelemetrySnapshot


# Organizer field name -> Our canonical field name
METRIC_MAPPING = {
    "cpu_utilization_pct": "cpu_percent",
    "link_utilization_pct": "link_utilization_percent",
    "packet_loss_pct": "packet_loss_percent",
}


class AdapterResult(BaseModel):
    """
    Contains normalized telemetry and information
    about missing measurements or adaptation warnings.
    """

    telemetry: TelemetrySnapshot

    missing_metrics: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def adapt_organizer_telemetry(raw: dict[str, Any]) -> AdapterResult:
    """
    Convert the organizer's telemetry format into
    our canonical TelemetrySnapshot format.
    """

    if not isinstance(raw, dict):
        raise ValueError("Telemetry input must be a dictionary.")

    if not isinstance(raw.get("metrics"), dict):
        raise ValueError("Telemetry must contain a metrics dictionary.")

    raw_metrics = raw["metrics"]

    # Preserve unknown metrics, but translate known organizer fields.
    normalized_metrics = {
        key: value
        for key, value in raw_metrics.items()
        if key not in METRIC_MAPPING
    }

    for organizer_name, canonical_name in METRIC_MAPPING.items():
        if organizer_name in raw_metrics:
            normalized_metrics[canonical_name] = raw_metrics[organizer_name]

    # Identify measurements that the organizer did not provide.
    expected_metrics = [
        "cpu_percent",
        "link_utilization_percent",
        "packet_loss_percent",
        "latency_ms",
        "jitter_ms",
        "queue_drops",
        "interface_errors",
    ]

    missing_metrics = [
        metric
        for metric in expected_metrics
        if metric not in normalized_metrics
        or normalized_metrics[metric] is None
    ]

    # Construct the canonical telemetry object.
    normalized_data = {
        "timestamp": raw.get("timestamp"),
        "device_id": raw.get("device_id"),
        "metrics": normalized_metrics,
        "status": raw.get("status"),
    }

    telemetry = TelemetrySnapshot.model_validate(normalized_data)

    warnings = []

    if missing_metrics:
        warnings.append(
            "Some telemetry measurements are unavailable."
        )

    return AdapterResult(
        telemetry=telemetry,
        missing_metrics=missing_metrics,
        warnings=warnings,
    )