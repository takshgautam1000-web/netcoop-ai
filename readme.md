# NETCOOP AI

**Interoperable Multi-Agent Network Operations & Intelligence Platform**

NETCOOP AI is a multi-agent network fault diagnosis platform designed to analyze network telemetry, identify potential root causes, correlate evidence across specialized agents, and generate unified diagnostic reports.

## Key Features

- **Multi-Agent Architecture:** Specialized agents for performance, infrastructure, connectivity, service health, fault correlation and recommendations.
- **LangGraph Orchestration:** Coordinates agent execution and combines their findings.
- **Interoperability:** Uses structured, versioned message formats and telemetry adapters.
- **Evidence-Based Diagnosis:** Ranks potential faults using telemetry measurements and heuristic scoring.
- **External Agent Integration:** FastAPI gateway supporting an external telemetry schema.
- **MCP Integration:** Exposes diagnosis capabilities through an MCP server.
- **Interactive Dashboard:** Streamlit interface for running and inspecting diagnoses.

## Architecture

```text
Telemetry Input
      |
      v
Validation & Normalization
      |
      v
+-----------------------------+
|       Specialized Agents    |
| Performance | Infrastructure|
| Connectivity | Service Health|
+-----------------------------+
      |
      v
Fault Correlation Engine
      |
      v
Recommendation Agent
      |
      v
Unified Diagnostic Report
```

## Technology Stack

- Python
- Pydantic
- LangGraph
- FastAPI
- MCP
- NetworkX
- Streamlit
- Pytest

## Project Status

Currently under active development. Dashboard integration, evaluation, robustness improvements and documentation are ongoing.

## Running Locally

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd netcoop-ai
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run tests:

```bash
pytest -q
```

## Disclaimer

NETCOOP AI currently provides diagnostic hypotheses based on supplied telemetry and heuristic scoring. It does not directly modify production network infrastructure.
