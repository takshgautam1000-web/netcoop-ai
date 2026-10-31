
from uuid import uuid4

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)


RECOMMENDATIONS = {
    "congestion": [
        {
            "action": "Inspect network traffic and identify bandwidth-heavy devices.",
            "priority": "HIGH",
        },
        {
            "action": "Review link utilization, QoS policies and queue drops.",
            "priority": "HIGH",
        },
    ],

    "cpu_overload": [
        {
            "action": "Identify processes consuming excessive CPU.",
            "priority": "HIGH",
        },
        {
            "action": "Inspect device logs and review CPU utilization trends.",
            "priority": "MEDIUM",
        },
    ],

    "interface_or_hardware_fault": [
        {
            "action": "Inspect physical interfaces, cables and transceivers.",
            "priority": "HIGH",
        },
        {
            "action": "Review interface error counters and device logs.",
            "priority": "HIGH",
        },
    ],

    "dns_failure": [
        {
            "action": "Check DNS server availability and resolution failures.",
            "priority": "HIGH",
        },
        {
            "action": "Inspect DNS response times and timeout logs.",
            "priority": "MEDIUM",
        },
    ],

    "dhcp_failure": [
        {
            "action": "Check DHCP server availability and lease allocation failures.",
            "priority": "HIGH",
        },
        {
            "action": "Inspect DHCP pool capacity and server response times.",
            "priority": "MEDIUM",
        },
    ],
}


def handle(message: AgentMessage) -> AgentMessage:

    def make_response(message_type, payload, status):
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="recommendation_agent",
            receiver="netcoop_orchestrator",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Recommendation Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    diagnosis = message.payload.get("diagnosis")

    if not isinstance(diagnosis, dict):
        return make_response(
            MessageType.ERROR,
            {"error": "A valid diagnosis dictionary is required."},
            MessageStatus.FAILED,
        )

    primary_hypothesis = diagnosis.get("primary_hypothesis")

    primary_cause = (
        primary_hypothesis.get("hypothesis")
        if isinstance(primary_hypothesis, dict)
        else None
    )

    if primary_cause is None:
        actions = [
            {
                "action": "Collect additional telemetry before attempting remediation.",
                "priority": "HIGH",
            }
        ]
        status = MessageStatus.PARTIAL
    else:
        actions = RECOMMENDATIONS.get(primary_cause)

        if actions is None:
            actions = [
                {
                    "action": "Perform further investigation before remediation.",
                    "priority": "HIGH",
                }
            ]
            status = MessageStatus.PARTIAL
        else:
            status = MessageStatus.COMPLETED

    return make_response(
        MessageType.FINDING,
        {
            "agent": "recommendation_agent",
            "primary_cause": primary_cause,
            "recommended_actions": actions,
            "automated_remediation": False,
        },
        status,
    )
