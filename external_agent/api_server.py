
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from external_agent.legacy_adapter import adapt_legacy_telemetry
from orchestration.graph import build_graph


app = FastAPI(
    title="NETCOOP External Agent Gateway",
    version="1.0"
)

# Build the LangGraph workflow
graph = build_graph()


@app.get("/")
def home():
    return {
        "message": "NETCOOP External Agent Gateway is running"
    }


@app.post("/telemetry")
def receive_telemetry(raw_data: dict):

    # 1. Convert external v0.9 telemetry into canonical telemetry
    try:
        telemetry = adapt_legacy_telemetry(raw_data)

    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # 2. Bridge canonical telemetry into organizer input format
    metrics = telemetry.metrics

    organizer_data = {
        "timestamp": telemetry.timestamp.isoformat(),
        "device_id": telemetry.device_id,
        "status": telemetry.status,
        "metrics": {
            "cpu_utilization_pct": metrics.cpu_percent,
            "link_utilization_pct": metrics.link_utilization_percent,
            "packet_loss_pct": metrics.packet_loss_percent,
            "latency_ms": metrics.latency_ms,
            "jitter_ms": metrics.jitter_ms,
            "queue_drops": metrics.queue_drops,
            "interface_errors": metrics.interface_errors,
        }
    }

    # 3. Run the complete NETCOOP diagnosis workflow
    try:
        result = graph.invoke({
            "incident_id": f"INC-{uuid4().hex[:8].upper()}",
            "raw_telemetry": organizer_data,
            "topology": {},
            "affected_devices": [telemetry.device_id],
            "service_health": None,
        })

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis workflow failed: {str(error)}"
        )

    # 4. Return the unified diagnostic report
    return {
        "message": "Telemetry processed and diagnosis completed",
        "device_id": telemetry.device_id,
        "canonical_telemetry": telemetry.model_dump(mode="json"),
        "diagnostic_report": result["report"],
        "workflow_status": result.get("workflow_status")
    }
