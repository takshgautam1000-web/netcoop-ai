
from uuid import uuid4

from pydantic import ValidationError

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
    ServiceHealthSnapshot,
)


def handle(message: AgentMessage) -> AgentMessage:

    def make_response(message_type, payload, status):
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="service_health_agent",
            receiver="fault_correlation_agent",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Service Health Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    try:
        raw_service_data = message.payload.get("service_health")

        # No DNS/DHCP data was provided.
        if raw_service_data is None:
            return make_response(
                MessageType.FINDING,
                {
                    "agent": "service_health_agent",
                    "findings": [],
                    "missing_data": [
                        "DNS health measurements",
                        "DHCP health measurements",
                    ],
                    "observation": (
                        "Service health cannot be assessed because "
                        "DNS/DHCP measurements were not provided."
                    ),
                    "root_cause_determined": False,
                },
                MessageStatus.PARTIAL,
            )

        snapshot = ServiceHealthSnapshot.model_validate(raw_service_data)

        metrics = snapshot.metrics
        findings = []
        missing_data = []

        evidence = []

        service_metrics = [
            "dns_resolution_success_percent",
            "dns_response_time_ms",
            "dns_timeout_count",
            "dhcp_success_percent",
            "dhcp_response_time_ms",
            "dhcp_failure_count",
        ]

        for metric in service_metrics:
            value = getattr(metrics, metric)

            if value is not None:
                evidence.append({
                    "metric": metric,
                    "value": value,
                })

        # DNS checks
        if metrics.dns_resolution_success_percent is None:
            missing_data.append("dns_resolution_success_percent")
        elif metrics.dns_resolution_success_percent < 95:
            findings.append(
                "DNS resolution success rate is below 95%."
            )

        if metrics.dns_response_time_ms is None:
            missing_data.append("dns_response_time_ms")
        elif metrics.dns_response_time_ms > 200:
            findings.append("DNS response time is elevated.")

        if metrics.dns_timeout_count is None:
            missing_data.append("dns_timeout_count")
        elif metrics.dns_timeout_count > 5:
            findings.append("DNS timeouts are elevated.")

        # DHCP checks
        if metrics.dhcp_success_percent is None:
            missing_data.append("dhcp_success_percent")
        elif metrics.dhcp_success_percent < 95:
            findings.append(
                "DHCP success rate is below 95%."
            )

        if metrics.dhcp_response_time_ms is None:
            missing_data.append("dhcp_response_time_ms")
        elif metrics.dhcp_response_time_ms > 500:
            findings.append("DHCP response time is elevated.")

        if metrics.dhcp_failure_count is None:
            missing_data.append("dhcp_failure_count")
        elif metrics.dhcp_failure_count > 5:
            findings.append("DHCP failures are elevated.")

        status = (
            MessageStatus.PARTIAL
            if missing_data
            else MessageStatus.COMPLETED
        )

        return make_response(
            MessageType.FINDING,
            {
                "agent": "service_health_agent",
                "service_id": snapshot.service_id,
                "findings": findings,
                "evidence": evidence,
                "missing_data": missing_data,
                "root_cause_determined": False,
                "thresholds_are_heuristics": True,
            },
            status,
        )

    except (ValidationError, ValueError, TypeError) as error:
        return make_response(
            MessageType.ERROR,
            {"error": str(error)},
            MessageStatus.FAILED,
        )
