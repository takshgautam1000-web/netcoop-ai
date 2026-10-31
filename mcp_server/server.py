from mcp.server import MCPServer
from uuid import uuid4
from orchestration.graph import build_graph

graph = build_graph()

server = MCPServer(
    name="NETCOOP AI",
    version="1.0.0",
    description="Multi-agent network fault diagnosis platform",
    instructions=(
        "NETCOOP AI analyses network telemetry, "
        "identifies potential faults, and provides diagnostic reports."
    ),
)


@server.tool()
def get_server_status() -> dict:
    """Check whether the NETCOOP MCP server is running."""

    return {
        "server": "NETCOOP AI",
        "status": "running",
        "version": "1.0.0",
    }

@server.tool()
def diagnose_incident(telemetry: dict) -> dict:
    """
    Diagnose a network incident using the NETCOOP multi-agent workflow.
    Expects telemetry in the organizer's original JSON format.
    """

    try:
        device_id = telemetry.get("device_id")

        if not device_id:
            return {"error": "Missing device_id in telemetry."}

        incident_id = f"INC-{uuid4().hex[:8].upper()}"

        result = graph.invoke({
            "incident_id": incident_id,
            "raw_telemetry": telemetry,
            "topology": {},
            "affected_devices": [device_id],
            "service_health": None,
        })

        return {
            "incident_id": incident_id,
            "workflow_status": result.get("workflow_status"),
            "diagnostic_report": result.get("report"),
        }

    except Exception as error:
        return {
            "error": str(error),
            "message": "NETCOOP could not process this incident."
        }