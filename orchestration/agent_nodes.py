
from uuid import uuid4

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)

from agents.performance_agent import handle as performance_handle
from agents.infrastructure_agent import handle as infrastructure_handle
from agents.connectivity_agent import handle as connectivity_handle
from agents.service_health_agent import handle as service_health_handle
from diagnosis.correlation_engine import correlate_findings
from diagnosis.report_builder import build_diagnostic_report
from agents.recommendation_agent import handle as recommendation_handle

def create_task_message(state, receiver, payload):
    return AgentMessage(
        message_id=str(uuid4()),
        correlation_id=state["incident_id"],
        incident_id=state["incident_id"],
        sender="netcoop_orchestrator",
        receiver=receiver,
        message_type=MessageType.TASK,
        payload=payload,
        status=MessageStatus.COMPLETED,
    )


def performance_node(state):
    message = create_task_message(
        state,
        "performance_agent",
        {"telemetry": state["normalized_telemetry"]},
    )

    response = performance_handle(message)
    return {"agent_findings": [response.model_dump(mode="json")]}


def infrastructure_node(state):
    message = create_task_message(
        state,
        "infrastructure_agent",
        {"telemetry": state["normalized_telemetry"]},
    )

    response = infrastructure_handle(message)
    return {"agent_findings": [response.model_dump(mode="json")]}


def connectivity_node(state):
    message = create_task_message(
        state,
        "connectivity_agent",
        {
            "topology": state.get("topology", {}),
            "affected_devices": state.get("affected_devices", []),
        },
    )

    response = connectivity_handle(message)
    return {"agent_findings": [response.model_dump(mode="json")]}


def service_health_node(state):
    message = create_task_message(
        state,
        "service_health_agent",
        {"service_health": state.get("service_health")},
    )

    response = service_health_handle(message)
    return {"agent_findings": [response.model_dump(mode="json")]}


def fault_correlation_node(state):
    # Convert the four agents' message dictionaries
    # back into validated AgentMessage objects.
    findings = [
        AgentMessage.model_validate(item)
        for item in state["agent_findings"]
    ]

    # Combine evidence and rank possible root causes.
    diagnosis = correlate_findings(findings)

    return {
        "diagnosis": diagnosis
    }

def report_node(state):
    connectivity_findings = {}

    for item in state.get("agent_findings", []):
        if item.get("sender") == "connectivity_agent":
            connectivity_findings = item.get("payload", {})
            break

    report = build_diagnostic_report(
        incident_id=state["incident_id"],
        diagnosis=state["diagnosis"],
        recommendations=state.get("recommendations", []),
        connectivity_findings=connectivity_findings,
    )

    return {
        "report": report,
        "workflow_status": "COMPLETED",
    }

def recommendation_node(state):
    message = create_task_message(
        state,
        "recommendation_agent",
        {
            "diagnosis": state["diagnosis"]
        }
    )

    response = recommendation_handle(message)

    if response.message_type == MessageType.ERROR:
        return {
            "agent_errors": [
                response.model_dump(mode="json")
            ]
        }

    return {
        "recommendations": response.payload.get(
            "recommended_actions", []
        )
    }