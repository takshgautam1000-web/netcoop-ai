
import streamlit as st
import pandas as pd
import plotly.express as px
import json

from datetime import datetime, timezone
from uuid import uuid4

from orchestration.graph import build_graph


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NETCOOP AI | Network Operations Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #9CA3AF;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background-color: #171B26;
        border: 1px solid #303747;
        padding: 18px;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        color: #8B949E;
        padding: 25px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# GRAPH INITIALIZATION
# ============================================================

@st.cache_resource
def load_graph():
    return build_graph()


graph = load_graph()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌐 NETCOOP AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interoperable Multi-Agent Network Operations & Intelligence Platform'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# TELEMETRY SCENARIO GENERATOR
# ============================================================

def generate_telemetry(scenario):

    timestamp = (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    if scenario == "Latency Spike":

        metrics = {
            "cpu_utilization_pct": 55.0,
            "link_utilization_pct": 75.0,
            "packet_loss_pct": 1.0,
            "latency_ms": 250.0,
            "jitter_ms": 50.0,
            "queue_drops": 25
        }

        status = "Warning"

    elif scenario == "Hardware Failure":

        metrics = {
            "cpu_utilization_pct": 99.9,
            "link_utilization_pct": 100.0,
            "packet_loss_pct": 20.0,
            "latency_ms": 700.0,
            "queue_drops": 10000,
            "interface_errors": 250
        }

        status = "Critical"

    else:

        metrics = {
            "cpu_utilization_pct": 20.0,
            "link_utilization_pct": 35.0,
            "packet_loss_pct": 0.0,
            "latency_ms": 12.0,
            "jitter_ms": 3.0,
            "queue_drops": 0
        }

        status = "Healthy"

    return {
        "timestamp": timestamp,
        "device_id": "SW_CAMPUS_1",
        "status": status,
        "metrics": metrics
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Incident Configuration")

scenario = st.sidebar.selectbox(
    "Select Network Scenario",
    [
        "Normal",
        "Latency Spike",
        "Hardware Failure"
    ]
)

device_id = st.sidebar.text_input(
    "Device ID",
    value="SW_CAMPUS_1"
)

st.sidebar.divider()

st.sidebar.caption("NETCOOP AI Multi-Agent Diagnosis Engine")

run_button = st.sidebar.button(
    "🚀 Run Diagnosis",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN DIAGNOSIS
# ============================================================

if run_button:

    if not device_id.strip():

        st.sidebar.error("Device ID cannot be empty.")

    else:

        telemetry = generate_telemetry(scenario)
        telemetry["device_id"] = device_id.strip()

        initial_state = {
            "incident_id": f"INC-{uuid4().hex[:8].upper()}",
            "raw_telemetry": telemetry,
            "topology": {},
            "affected_devices": [telemetry["device_id"]],
            "service_health": None
        }

        with st.spinner(
            "NETCOOP agents are collaborating to investigate the incident..."
        ):

            try:

                result = graph.invoke(initial_state)

                st.session_state["report"] = result["report"]
                st.session_state["telemetry"] = telemetry

                st.session_state["workflow_status"] = (
                    result.get("workflow_status", "COMPLETED")
                )

                st.session_state["scenario"] = scenario

                st.success("Diagnostic workflow completed!")

            except Exception as error:

                st.error(f"Diagnosis failed: {error}")


# ============================================================
# DASHBOARD RESULTS
# ============================================================

if "report" not in st.session_state:

    st.info(
        "Select a network scenario from the sidebar "
        "and click Run Diagnosis to begin."
    )

    st.markdown("### How NETCOOP AI works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📥 Ingestion")
        st.write(
            "Collects, normalizes and validates network telemetry."
        )

    with col2:
        st.markdown("#### 🤖 Multi-Agent Analysis")
        st.write(
            "Specialized agents analyze performance, "
            "infrastructure, connectivity and service health."
        )

    with col3:
        st.markdown("#### 🔍 Diagnosis")
        st.write(
            "Correlates findings and generates evidence-based "
            "recommendations."
        )


else:

    report = st.session_state["report"]
    telemetry = st.session_state["telemetry"]

    metrics = telemetry.get("metrics", {})


    # ========================================================
    # INCIDENT OVERVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Incident Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Incident ID",
            report.get("incident_id", "N/A")
        )

    with col2:
        st.metric(
            "Diagnosis Status",
            report.get("status", "UNKNOWN").upper()
        )

    with col3:
        st.metric(
            "Workflow",
            st.session_state.get("workflow_status", "UNKNOWN")
        )

    st.divider()


    # ========================================================
    # ROOT CAUSE ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="section-title">🔍 Root Cause Analysis</div>',
        unsafe_allow_html=True
    )

    root_cause = report.get("suspected_root_cause")

    if root_cause:

        st.success(
            f"Leading hypothesis: "
            f"{root_cause.replace('_', ' ').title()}"
        )

    elif report.get("status") == "no_fault_detected":

        st.success("No fault detected in the available telemetry.")

    else:

        st.warning(
            "Insufficient evidence to establish a root cause."
        )

    confidence = report.get("confidence", {})

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Diagnostic Score",
            confidence.get("value", "N/A")
        )

    with col2:

        st.metric(
            "Score Type",
            confidence.get("type", "Unknown")
        )

    st.info(
        report.get(
            "diagnosis_explanation",
            "No diagnosis explanation available."
        )
    )

    st.divider()


    # ========================================================
    # NETWORK TELEMETRY
    # ========================================================

    st.markdown(
        '<div class="section-title">📡 Live Network Telemetry</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        value = metrics.get("cpu_utilization_pct")

        st.metric(
            "CPU Utilization",
            f"{value}%" if value is not None else "N/A"
        )

    with col2:

        value = metrics.get("link_utilization_pct")

        st.metric(
            "Link Utilization",
            f"{value}%" if value is not None else "N/A"
        )

    with col3:

        value = metrics.get("packet_loss_pct")

        st.metric(
            "Packet Loss",
            f"{value}%" if value is not None else "N/A"
        )

    with col4:

        value = metrics.get("latency_ms")

        st.metric(
            "Latency",
            f"{value} ms" if value is not None else "N/A"
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        value = metrics.get("jitter_ms")

        st.metric(
            "Jitter",
            f"{value} ms" if value is not None else "N/A"
        )

    with col2:

        value = metrics.get("queue_drops")

        st.metric(
            "Queue Drops",
            value if value is not None else "N/A"
        )

    with col3:

        value = metrics.get("interface_errors")

        st.metric(
            "Interface Errors",
            value if value is not None else "N/A"
        )

    st.caption(
        f"Device: {telemetry.get('device_id', 'Unknown')} "
        f"| Reported status: {telemetry.get('status', 'Unknown')}"
    )

    with st.expander("View Raw Telemetry JSON"):

        st.json(telemetry)

    st.divider()


    # ========================================================
    # TABBED INVESTIGATION VIEW
    # ========================================================

    overview_tab, evidence_tab, agents_tab, actions_tab, raw_tab = st.tabs(
        [
            "📋 Overview",
            "🔬 Evidence",
            "🤖 Agent Inspector",
            "🛠️ Recommendations",
            "📄 Raw Report"
        ]
    )


    # ========================================================
    # OVERVIEW TAB
    # ========================================================

    with overview_tab:

        st.subheader("Affected Devices")

        affected_devices = report.get("affected_devices", [])

        if affected_devices:

            st.write(", ".join(affected_devices))

        else:

            st.write("No affected devices identified.")

        st.subheader("Alternative Causes")

        alternatives = report.get("alternative_causes", [])

        if alternatives:

            st.dataframe(
                pd.DataFrame(alternatives),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.write("No alternative causes were ranked.")


    # ========================================================
    # EVIDENCE TAB
    # ========================================================

    with evidence_tab:

        st.subheader("Supporting Evidence")

        evidence = report.get("supporting_evidence", [])

        if evidence:

            evidence_df = pd.DataFrame(evidence)

            st.dataframe(
                evidence_df,
                use_container_width=True,
                hide_index=True
            )

            numeric_evidence = [
                item for item in evidence
                if isinstance(item.get("value"), (int, float))
            ]

            if numeric_evidence:

                chart_df = pd.DataFrame(numeric_evidence)

                chart_df["metric"] = chart_df["metric"].str.replace(
                    "_", " "
                ).str.title()

                fig = px.bar(
                    chart_df,
                    x="metric",
                    y="value",
                    title="Observed Evidence Values",
                    hover_data=["observation"]
                )

                fig.update_layout(
                    template="plotly_dark",
                    xaxis_title="Metric",
                    yaxis_title="Observed Value"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.caption(
                    "Values use different units. Compare individual "
                    "metrics using their units; bar heights are not "
                    "directly comparable across metrics."
                )

        else:

            st.warning("No supporting evidence available.")


    # ========================================================
    # AGENT INSPECTOR TAB
    # ========================================================

    with agents_tab:

        st.subheader("Multi-Agent Activity")

        evidence_sources = report.get("evidence_sources", {})

        if evidence_sources:

            agent_rows = []

            for agent, status in evidence_sources.items():

                agent_rows.append({
                    "Agent": agent.replace("_", " ").title(),
                    "Execution Status": status
                })

            agent_df = pd.DataFrame(agent_rows)

            st.dataframe(
                agent_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No agent execution information available.")

        st.subheader("Agent Collaboration Architecture")

        st.code(
            """
Performance Agent -----------+
Infrastructure Agent --------+
Connectivity Agent ----------+--> Fault Correlation
Service Health Agent --------+         |
                                      v
                              Recommendation Agent
                                      |
                                      v
                               Unified Report
            """,
            language="text"
        )

        st.caption(
            "Execution statuses are taken from the actual diagnostic report. "
            "The diagram represents the logical workflow."
        )


    # ========================================================
    # RECOMMENDATIONS TAB
    # ========================================================

    with actions_tab:

        st.subheader("Recommended Actions")

        recommendations = report.get("recommended_actions", [])

        if recommendations:

            for index, action in enumerate(recommendations, start=1):

                if isinstance(action, dict):

                    priority = action.get("priority", "NORMAL")
                    description = action.get("action", "")

                    st.markdown(
                        f"**{index}. {description}**"
                    )

                    st.caption(f"Priority: {priority}")

                else:

                    st.markdown(f"**{index}. {action}**")

        else:

            st.info("No recommended actions available.")

        st.divider()

        st.subheader("Limitations")

        for limitation in report.get("limitations", []):

            st.warning(limitation)

        st.subheader("Additional Data Needed")

        additional_data = report.get("additional_data_needed", [])

        if additional_data:

            for item in additional_data:

                st.write(f"- {item}")

        else:

            st.write("No additional data requested.")


    # ========================================================
    # RAW REPORT TAB
    # ========================================================

    with raw_tab:

        st.subheader("Complete Diagnostic Report")

        st.json(report)

        report_json = json.dumps(
            report,
            indent=4,
            default=str
        )

        st.download_button(
            label="⬇️ Download Diagnostic Report",
            data=report_json,
            file_name=f"{report.get('incident_id', 'incident')}.json",
            mime="application/json"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div class="footer">'
    'NETCOOP AI | Multi-Agent Network Operations Intelligence '
    '<br>Demonstration using simulated telemetry'
    '</div>',
    unsafe_allow_html=True
)

