
from datetime import datetime, timezone
import json

from orchestration.graph import build_graph

# Build the LangGraph workflow
graph = build_graph()

# Sample campus network telemetry
sample_telemetry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "device_id": "SW_CAMPUS_1",
    "metrics": {
        "cpu_utilization_pct": 55.0,
        "link_utilization_pct": 90.0,
        "packet_loss_pct": 2.0,
        "latency_ms": 250.0,
        "jitter_ms": 45.0,
        "queue_drops": 60,
    },
    "status": "Warning",
}

# Initial information passed into LangGraph
initial_state = {
    "incident_id": "INC-DEMO-001",
    "raw_telemetry": sample_telemetry,
    "topology": {},
    "affected_devices": ["SW_CAMPUS_1"],
    "service_health": None,
}

# Execute the complete workflow
result = graph.invoke(initial_state)

# Display the unified diagnostic report
print("\n========== NETCOOP DIAGNOSTIC REPORT ==========\n")

print(
    json.dumps(
        result["report"],
        indent=4,
        ensure_ascii=False,
    )
)

print("\n===============================================")
print("Workflow status:", result.get("workflow_status"))
