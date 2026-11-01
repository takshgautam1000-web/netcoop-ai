# NETCOOP AI

**Interoperable Multi-Agent Network Operations & Intelligence Platform**

NETCOOP AI is a multi-agent network fault-diagnosis prototype. It accepts network telemetry, validates and normalizes the input, gathers findings from specialized agents, correlates evidence into ranked fault hypotheses, and produces a unified diagnostic report with recommended investigation or corrective actions.

## Live demo

**[Open the NETCOOP AI Streamlit demo](https://netcoop-ai-nfkb6flqvymdqv6txsxfax.streamlit.app/)**

The hosted Streamlit app is an interactive demonstration of the agent-collaboration flow and the hackathon evaluation criteria. The current hosted collaboration demo uses an in-app simulation of agent messages; it is not a live connection to the locally run LangGraph backend, MCP server, or campus network devices.

## What the system does

1. **Ingests telemetry** in the organizer's JSON format or through an external legacy-schema adapter.
2. **Validates and normalizes measurements**, preserving absent measurements as unknown rather than treating them as zero.
3. **Runs specialist investigations** for performance, infrastructure, connectivity, and service health.
4. **Correlates findings** to rank possible root causes, identify conflicts, and expose missing evidence.
5. **Generates recommendations** based on the leading diagnosis and available evidence.
6. **Builds a unified incident report** containing the diagnosis, supporting evidence, alternatives, recommended actions, and limitations.

## Agent architecture

| Agent / component | Responsibility |
|---|---|
| Performance Agent | Examines latency, jitter, packet loss, and link utilization. |
| Infrastructure Agent | Examines CPU utilization, queue drops, interface errors, and reported device status. |
| Connectivity Agent | Uses supplied network topology to inspect connected devices and shared neighbors. |
| Service Health Agent | Examines optional DNS and DHCP health measurements. |
| Fault Correlation Engine | Consumes specialist findings, ranks fault hypotheses, and checks for status/metric conflicts. |
| Recommendation Agent | Uses the correlated diagnosis to produce investigation and corrective-action recommendations. |
| LangGraph orchestrator | Coordinates the specialist nodes, correlation, recommendation, and report-building stages. |

The current backend runs the four specialist investigations, aggregates their findings, then performs fault correlation and recommendation generation. Iterative agent-to-agent negotiation and request-more-evidence rounds are future enhancements; they should not be confused with the current workflow.

## Organizer telemetry format

The original organizer generator provides three scenarios:

- `normal`
- `latency_spike`
- `hardware_failure`

A representative input has this shape:

```json
{
  "timestamp": "2026-10-31T12:00:00Z",
  "device_id": "SW_CAMPUS_1",
  "status": "Warning",
  "metrics": {
    "cpu_utilization_pct": 55.0,
    "link_utilization_pct": 75.0,
    "packet_loss_pct": 1.0,
    "latency_ms": 250.0,
    "jitter_ms": 50.0,
    "queue_drops": 25
  }
}
```

Not every scenario contains every metric. For example, the organizer's hardware-failure sample does not include `jitter_ms`, and the normal and latency-spike samples do not include `interface_errors`. Missing measurements are kept as unknown (`None` / absent); they are not silently replaced with zero or interpreted as healthy.

The backend also defines optional DNS/DHCP service-health inputs and topology context. These are separate from the organizer's original telemetry payload because the supplied generator does not provide them.

## Interoperability and MCP

NETCOOP uses Pydantic models for canonical telemetry and versioned agent-message envelopes. The message contract includes fields such as:

- `protocol_version`
- `message_id`
- `correlation_id`
- `incident_id`
- `sender` and `receiver`
- `message_type`
- `timestamp`
- `payload`
- `status` and `metadata`

Supported message types include `TASK`, `FINDING`, `REQUEST`, `RESPONSE`, `ERROR`, and `ACKNOWLEDGEMENT`.

### External telemetry adapter

The FastAPI gateway accepts a legacy telemetry schema (`0.9`) and converts its field names and units into the canonical telemetry representation. In particular, legacy latency and jitter values expressed in seconds are converted to milliseconds.

### Current MCP tools

The MCP server currently exposes **two implemented tools**:

| Tool | Purpose |
|---|---|
| `get_server_status` | Returns the MCP server's name, running status, and version. |
| `diagnose_incident` | Accepts organizer-format telemetry and invokes the LangGraph diagnosis workflow. |

The additional tools discussed for device telemetry, topology, health, interface statistics, and incident history are planned work, not currently implemented MCP tools.

## Technology stack

- Python
- Pydantic v2
- LangGraph
- NetworkX
- FastAPI and Uvicorn
- MCP Python SDK (Streamable HTTP)
- Streamlit (hosted demonstration)
- Pytest

## Running the backend locally

Run commands from the repository root, with the project's virtual environment activated.

### 1. Install dependencies

If the repository's `requirements.txt` is present:

```powershell
python -m pip install -r requirements.txt
```

Otherwise, install the core packages used by the current backend:

```powershell
python -m pip install "pydantic>=2,<3" networkx langgraph fastapi uvicorn "mcp[cli]==2.3.0" pytest
```

### 2. Run the diagnosis demo

```powershell
python run_demo.py
```

### 3. Run the scenario examples

```powershell
python run_scenarios.py
```

### 4. Start the external FastAPI gateway

```powershell
uvicorn external_agent.api_server:app --reload --port 8000
```

The gateway accepts external legacy telemetry at `POST /telemetry`.

### 5. Start the MCP server

In a separate terminal:

```powershell
python -m mcp_server.run_server
```

The current local Streamable HTTP endpoint is:

```text
http://127.0.0.1:8001/mcp
```

### 6. Run the independent MCP client

With the MCP server running, use another terminal:

```powershell
python -m mcp_server.test_client
```

### 7. Run tests

```powershell
python -m pytest -q
```

## Diagnostic output

The unified report includes:

- incident identifier and diagnostic status;
- suspected root-cause hypothesis;
- heuristic score and score type;
- affected devices and topology-derived connectivity findings where available;
- supporting evidence and alternative causes;
- recommended actions;
- evidence-source statuses;
- conflicts, limitations, and additional data needed.

**Scoring note:** hypothesis scores are heuristic points. They are not calibrated probabilities or statistically validated confidence estimates.

## Hackathon evaluation mapping

The project is organized around the supplied evaluation weights:

| Evaluation criterion | Weight | Evidence to demonstrate |
|---|---:|---|
| Agent interoperability and protocol | 30% | Canonical Pydantic schemas, versioned message envelopes, organizer/legacy adapters, FastAPI gateway, MCP tool discovery and calls. |
| Fault diagnosis and evidence | 25% | Validation, evidence extraction, ranked hypotheses, supporting evidence, alternatives, missing-data handling, and unified report. |
| Orchestration and conflict resolution | 15% | LangGraph specialist-agent execution, finding aggregation, correlation, status/metric conflict checks, and recommendation stage. |
| Robustness and validation | 15% | Malformed/out-of-range input handling, missing fields, stale timestamps, status conflicts, and unknown topology devices. |
| Code quality, documentation, and demo | 5% | Modular source code, tests, setup instructions, and reproducible example runs. |
| Innovation, usability, and extensibility | 10% | Multi-agent architecture, schema bridging, MCP exposure, topology context, and interactive demonstration. |
| **Total** | **100%** | |

The table maps project evidence to the rubric. It does not claim that these marks have been awarded.

## Current limitations and roadmap

The current implementation is a diagnostic prototype, not a production network-management system.

- The present hypothesis engine covers congestion, CPU overload, interface/hardware fault, DNS failure, and DHCP failure.
- Wi-Fi signal-quality diagnosis and upstream-route root-cause diagnosis are not yet implemented in the current hypothesis engine.
- The topology conclusions depend on the topology supplied to the Connectivity Agent.
- Iterative agent negotiation, bounded re-investigation, persistent incident history, and LangGraph interrupt/resume human approval remain future enhancements.
- MCP currently has two tools; additional device, topology, interface, health, and incident-history tools are planned.
- No real network equipment is modified. Recommendations are advisory.
- The hosted Streamlit demo is a collaboration-flow demonstrator and currently simulates its agent exchanges within the app; it is not evidence of live execution by the backend agents.

## Security note

Do not commit `.env` files, API keys, credentials, private network inventories, or sensitive telemetry. Keep virtual environments, caches, and generated files out of Git using `.gitignore`.

## Project status

NETCOOP AI is under active development. The core ingestion, specialist-agent, correlation, recommendation, report, LangGraph, FastAPI, and initial MCP components have been implemented. Integration, expanded MCP tools, deeper agent collaboration, evaluation, and documentation are ongoing.
