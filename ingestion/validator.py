
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from protocol.schemas import TelemetrySnapshot


class ValidationResult(BaseModel):
    is_valid: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def validate_telemetry(
    telemetry: TelemetrySnapshot,
    now: datetime | None = None,
    max_age_seconds: int = 300,
) -> ValidationResult:

    warnings = []
    errors = []

    if now is None:
        now = datetime.now(timezone.utc)

    timestamp = telemetry.timestamp

    # Check whether the timestamp has timezone information.
    if timestamp.tzinfo is None:
        errors.append("Timestamp must include timezone information.")
    else:
        age_seconds = (now - timestamp).total_seconds()

        if age_seconds > max_age_seconds:
            warnings.append("Telemetry is stale.")

        if age_seconds < 0:
            warnings.append("Telemetry timestamp is in the future.")

    # Check for missing measurements.
    metrics = telemetry.metrics

    expected_metrics = [
        "cpu_percent",
        "link_utilization_percent",
        "packet_loss_percent",
        "latency_ms",
        "jitter_ms",
        "queue_drops",
        "interface_errors",
    ]

    missing = [
        name
        for name in expected_metrics
        if getattr(metrics, name) is None
    ]

    if missing:
        warnings.append(
            f"Missing measurements: {', '.join(missing)}"
        )

    # Check whether reported status contradicts measurements.
    status = (telemetry.status or "").lower()

    critical_signals = (
        (metrics.cpu_percent is not None and metrics.cpu_percent >= 95)
        or (metrics.packet_loss_percent is not None and metrics.packet_loss_percent >= 10)
        or (metrics.latency_ms is not None and metrics.latency_ms >= 500)
        or (metrics.interface_errors is not None and metrics.interface_errors >= 100)
        or (metrics.queue_drops is not None and metrics.queue_drops >= 5000)
    )

    elevated_signals = (
        (metrics.cpu_percent is not None and metrics.cpu_percent >= 80)
        or (metrics.link_utilization_percent is not None and metrics.link_utilization_percent >= 85)
        or (metrics.packet_loss_percent is not None and metrics.packet_loss_percent >= 1)
        or (metrics.latency_ms is not None and metrics.latency_ms >= 100)
        or (metrics.jitter_ms is not None and metrics.jitter_ms >= 30)
        or (metrics.queue_drops is not None and metrics.queue_drops >= 50)
        or (metrics.interface_errors is not None and metrics.interface_errors >= 10)
    )

    if status == "healthy" and elevated_signals:
        warnings.append(
            "Reported status is Healthy, but metrics indicate possible degradation."
        )

    if status == "critical" and not critical_signals:
        warnings.append(
            "Reported status is Critical, but available metrics do not confirm critical conditions."
        )

    if status == "warning" and not elevated_signals:
        warnings.append(
            "Reported status is Warning, but available metrics show no elevated signals."
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        warnings=warnings,
        errors=errors,
    )
