# This is important because every agent will communicate using agreed data structures. 
# If agents interpret the same telemetry differently, interoperability fails.
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# 1. TELEMETRY METRICS
# --------------------------------------------------

class TelemetryMetrics(BaseModel):
    """
    Network measurements collected from a device.

    Optional fields are intentional:
    a missing measurement must remain None, not become zero.
    """

    model_config = ConfigDict(extra="allow")

    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    link_utilization_percent: float | None = Field(
        default=None, ge=0, le=100
    )
    packet_loss_percent: float | None = Field(
        default=None, ge=0, le=100
    )

    latency_ms: float | None = Field(default=None, ge=0)
    jitter_ms: float | None = Field(default=None, ge=0)

    queue_drops: int | None = Field(default=None, ge=0)
    interface_errors: int | None = Field(default=None, ge=0)


# --------------------------------------------------
# 2. TELEMETRY SNAPSHOT
# --------------------------------------------------

class TelemetrySnapshot(BaseModel):
    """
    Standard representation of one device's telemetry.
    """

    model_config = ConfigDict(extra="allow")

    timestamp: datetime
    device_id: str = Field(min_length=1)
    metrics: TelemetryMetrics
    # Preserve the device-reported status.
    # Agents will independently verify it using metrics.
    status: str | None = None


# --------------------------------------------------
# 3. AGENT COMMUNICATION PROTOCOL
# --------------------------------------------------

class MessageType(str, Enum):
    TASK = "TASK"
    FINDING = "FINDING"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"


class MessageStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class AgentMessage(BaseModel):
    """
    Standard versioned message exchanged between agents.
    """

    protocol_version: str = "1.0"

    message_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    incident_id: str = Field(min_length=1)

    sender: str = Field(min_length=1)
    receiver: str = Field(min_length=1)

    message_type: MessageType
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    payload: dict[str, Any]
    status: MessageStatus = MessageStatus.COMPLETED

    metadata: dict[str, Any] = Field(default_factory=dict)

# Define the service-health schema(for the agent whose job is to investigate whether network problems are actually caused by DNS or DHCP services.)

class ServiceHealthMetrics(BaseModel):
    dns_resolution_success_percent: float | None = Field(
        default=None, ge=0, le=100
    )
    dns_response_time_ms: float | None = Field(
        default=None, ge=0
    )
    dns_timeout_count: int | None = Field(
        default=None, ge=0
    )

    dhcp_success_percent: float | None = Field(
        default=None, ge=0, le=100
    )
    dhcp_response_time_ms: float | None = Field(
        default=None, ge=0
    )
    dhcp_failure_count: int | None = Field(
        default=None, ge=0
    )


class ServiceHealthSnapshot(BaseModel):
    timestamp: datetime
    service_id: str = Field(min_length=1)
    metrics: ServiceHealthMetrics