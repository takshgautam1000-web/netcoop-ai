
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from protocol.schemas import TelemetrySnapshot


class EvidenceItem(BaseModel):
    evidence_id: str
    device_id: str
    metric: str
    value: float | int
    unit: str
    observation: str
    timestamp: datetime


class EvidenceReport(BaseModel):
    device_id: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    missing_metrics: list[str] = Field(default_factory=list)


# Metric name -> unit
METRIC_UNITS = {
    "cpu_percent": "%",
    "link_utilization_percent": "%",
    "packet_loss_percent": "%",
    "latency_ms": "ms",
    "jitter_ms": "ms",
    "queue_drops": "packets",
    "interface_errors": "errors",
}


def interpret_metric(metric: str, value: float | int) -> str:
    """Describe a measurement without deciding the root cause."""

    if metric == "cpu_percent":
        if value >= 95:
            return "Extremely high CPU utilization."
        if value >= 80:
            return "Elevated CPU utilization."

    elif metric == "link_utilization_percent":
        if value >= 95:
            return "Link is nearly saturated."
        if value >= 85:
            return "High link utilization."

    elif metric == "packet_loss_percent":
        if value >= 10:
            return "Severe packet loss."
        if value >= 1:
            return "Elevated packet loss."

    elif metric == "latency_ms":
        if value >= 500:
            return "Extremely high latency."
        if value >= 100:
            return "Elevated latency."

    elif metric == "jitter_ms":
        if value >= 30:
            return "Elevated network jitter."

    elif metric == "queue_drops":
        if value >= 5000:
            return "Very high number of queue drops."
        if value >= 50:
            return "Elevated queue drops."

    elif metric == "interface_errors":
        if value >= 100:
            return "High number of interface errors."
        if value >= 10:
            return "Elevated interface errors."

    return "No threshold breach detected by current heuristic."


def build_evidence(
    telemetry: TelemetrySnapshot,
) -> EvidenceReport:

    evidence_items = []
    missing_metrics = []

    for metric, unit in METRIC_UNITS.items():

        value = getattr(telemetry.metrics, metric)

        if value is None:
            missing_metrics.append(metric)
            continue

        observation = interpret_metric(metric, value)

        evidence_items.append(
            EvidenceItem(
                evidence_id=(
                    f"{telemetry.device_id}:"
                    f"{metric}:"
                    f"{telemetry.timestamp.isoformat()}"
                ),
                device_id=telemetry.device_id,
                metric=metric,
                value=value,
                unit=unit,
                observation=observation,
                timestamp=telemetry.timestamp,
            )
        )

    return EvidenceReport(
        device_id=telemetry.device_id,
        evidence=evidence_items,
        missing_metrics=missing_metrics,
    )
