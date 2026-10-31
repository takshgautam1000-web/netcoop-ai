
from datetime import datetime, timezone
from orchestration.graph import build_graph

graph = build_graph()

def make_telemetry(fault_type):
    base = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": "SW_CAMPUS_1",
    }

    scenarios = {
        "normal": {
            "cpu_utilization_pct": 25.0,
            "link_utilization_pct": 35.0,
            "packet_loss_pct": 0.0,
            "latency_ms": 12.0,
            "jitter_ms": 3.0,
            "queue_drops": 0,
            "status": "Healthy",
        },
        "latency_spike": {
            "cpu_utilization_pct": 55.0,
            "link_utilization_pct": 75.0,
            "packet_loss_pct": 1.0,
            "latency_ms": 250.0,
            "jitter_ms": 50.0,
            "queue_drops": 25,
            "status": "Warning",
        },
        "hardware_failure": {
            "cpu_utilization_pct": 99.9,
            "link_utilization_pct": 100.0,
            "packet_loss_pct": 22.0,
            "latency_ms": 750.0,
            "queue_drops": 9000,
            "interface_errors": 250,
            "status": "Critical",
        },
    }

    data = scenarios[fault_type].copy()
    status = data.pop("status")

    base["metrics"] = data
    base["status"] = status

    return base


for scenario in ["normal", "latency_spike", "hardware_failure"]:
    print(f"\n{'=' * 20} {scenario.upper()} {'=' * 20}")

    result = graph.invoke({
        "incident_id": f"INC-{scenario.upper()}",
        "raw_telemetry": make_telemetry(scenario),
        "topology": {},
        "affected_devices": ["SW_CAMPUS_1"],
        "service_health": None,
    })

    report = result["report"]

    print("Diagnosis:", report["suspected_root_cause"])
    print("Status:", report["status"])
    print("Score:", report["confidence"])
    print("Alternatives:", report["alternative_causes"])
    print("Workflow:", result.get("workflow_status"))
