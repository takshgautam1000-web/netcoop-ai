
from langgraph.graph import StateGraph, START, END

from orchestration.state import NetcoopState
from ingestion.pipeline import process_organizer_input

from orchestration.agent_nodes import (
    performance_node,
    infrastructure_node,
    connectivity_node,
    service_health_node,
    fault_correlation_node,
    recommendation_node,
    report_node,
)


def validate_telemetry_node(state: NetcoopState):
    raw_data = state["raw_telemetry"]

    result = process_organizer_input(raw_data)

    return {
        "normalized_telemetry": result.telemetry,
        "validation_result": {
            "is_valid": result.is_valid,
            "warnings": result.warnings,
            "errors": result.errors,
        },
        "evidence": result.evidence,
    }


def build_graph():

    builder = StateGraph(NetcoopState)

    # 1. Register all nodes
    builder.add_node("validate_telemetry", validate_telemetry_node)

    builder.add_node("performance", performance_node)
    builder.add_node("infrastructure", infrastructure_node)
    builder.add_node("connectivity", connectivity_node)
    builder.add_node("service_health", service_health_node)

    builder.add_node("fault_correlation", fault_correlation_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("report", report_node)

    # 2. Start with telemetry validation
    builder.add_edge(START, "validate_telemetry")

    # 3. Run four agents in parallel
    builder.add_edge("validate_telemetry", "performance")
    builder.add_edge("validate_telemetry", "infrastructure")
    builder.add_edge("validate_telemetry", "connectivity")
    builder.add_edge("validate_telemetry", "service_health")

    # 4. Wait for all four agents before correlation
    builder.add_edge(
        [
            "performance",
            "infrastructure",
            "connectivity",
            "service_health",
        ],
        "fault_correlation",
    )

    # 5. Correlation -> Recommendations -> Unified Report
    builder.add_edge("fault_correlation", "recommendation")
    builder.add_edge("recommendation", "report")

    # 6. Finish
    builder.add_edge("report", END)

    return builder.compile()

