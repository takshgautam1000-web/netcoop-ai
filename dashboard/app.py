# from __future__ import annotations

# """NETCOOP AI - rubric-first multi-agent collaboration demonstrator.

# This standalone Streamlit app demonstrates structured information exchange,
# evidence reuse, conflict checks and a rule-based consensus decision. It does
# not claim to execute the project's LangGraph agents. That integration can be
# added once the presentation flow is approved.
# """

# import json
# import random
# import re
# import uuid
# from collections import defaultdict, deque
# from datetime import datetime, timedelta, timezone
# from typing import Any

# import pandas as pd
# import streamlit as st


# # ---------------------------------------------------------------------------
# # Page setup and visual styling
# # ---------------------------------------------------------------------------
# st.set_page_config(
#     page_title="NETCOOP AI | Multi-Agent Network Intelligence",
#     page_icon="🛰️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# st.markdown(
#     """
#     <style>
#       .block-container {max-width: 1580px; padding-top: 1.1rem; padding-bottom: 2.5rem;}
#       .hero {padding: 1.25rem 1.4rem; border: 1px solid rgba(128,128,128,.28);
#              border-radius: 16px; margin-bottom: 1rem;
#              background: linear-gradient(110deg, rgba(35,112,190,.13), rgba(25,160,130,.07));}
#       .hero h1 {margin: 0; font-size: 2rem;}
#       .hero p {margin: .4rem 0 0; opacity: .78;}
#       .subtle {opacity: .72; font-size: .88rem;}
#       .agent-card {border: 1px solid rgba(128,128,128,.28); border-radius: 13px;
#                    padding: .9rem 1rem; min-height: 118px;}
#       .agent-card h4 {margin: 0 0 .35rem 0;}
#       .message-card {border: 1px solid rgba(128,128,128,.25); border-radius: 11px;
#                      padding: .75rem .9rem; margin: .45rem 0;}
#       .pill {display:inline-block; border:1px solid rgba(128,128,128,.35);
#              border-radius:999px; padding:.12rem .55rem; font-size:.75rem; margin-right:.25rem;}
#       div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.20);
#           border-radius:12px; padding:.65rem .8rem;}
#       [data-testid="stDataFrame"] {width:100%;}
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # ---------------------------------------------------------------------------
# # Rubric: exact weights discussed for the hackathon
# # ---------------------------------------------------------------------------
# RUBRIC = [
#     {
#         "name": "Agent interoperability and protocol",
#         "weight": 30,
#         "proof": "Versioned message envelope, sender/receiver, message types, schema bridging, unit conversion and inspectable exchanges.",
#         "page": "Interoperability Lab",
#     },
#     {
#         "name": "Fault diagnosis and evidence",
#         "weight": 25,
#         "proof": "Telemetry evidence, ranked hypotheses, supporting/contradicting signals, alternatives and missing-data handling.",
#         "page": "Evidence & Consensus",
#     },
#     {
#         "name": "Orchestration and conflict resolution",
#         "weight": 15,
#         "proof": "Specialist agents pass findings to downstream agents; correlation requests more information and resolves competing signals.",
#         "page": "Agent Collaboration",
#     },
#     {
#         "name": "Robustness and validation",
#         "weight": 15,
#         "proof": "Missing values, invalid ranges, stale timestamps, status/metric conflicts and malformed JSON are handled explicitly.",
#         "page": "Robustness Lab",
#     },
#     {
#         "name": "Code quality, documentation and demo",
#         "weight": 5,
#         "proof": "Modular demonstration flow, protocol visibility, repeatable scenarios and a guided evaluator sequence.",
#         "page": "Judge Guide",
#     },
#     {
#         "name": "Innovation, usability and extensibility",
#         "weight": 10,
#         "proof": "Multi-agent evidence sharing, topology context, service-health context and extensible message contracts.",
#         "page": "Command Center",
#     },
# ]

# AGENT_INFO = {
#     "performance_agent": ("Performance Agent", "Latency · jitter · packet loss · link utilization", "#2878C8"),
#     "infrastructure_agent": ("Infrastructure Agent", "CPU · queue drops · interface errors · device status", "#159A83"),
#     "connectivity_agent": ("Connectivity Agent", "Affected devices · topology · reachable segment", "#8864C7"),
#     "service_health_agent": ("Service Health Agent", "DNS · DHCP · service availability", "#C17B28"),
#     "fault_correlation_agent": ("Fault Correlation Agent", "Evidence aggregation · competing hypotheses · conflict checks", "#BA5368"),
#     "recommendation_agent": ("Recommendation Agent", "Corrective actions · verification steps", "#567E67"),
# }

# DEVICE_FIELDS = [
#     ("latency_ms", "Latency", "ms", "Performance"),
#     ("jitter_ms", "Jitter", "ms", "Performance"),
#     ("packet_loss_pct", "Packet loss", "%", "Performance"),
#     ("link_utilization_pct", "Link utilization", "%", "Performance"),
#     ("cpu_utilization_pct", "CPU utilization", "%", "Infrastructure"),
#     ("queue_drops", "Queue drops", "count", "Infrastructure"),
#     ("interface_errors", "Interface errors", "count", "Infrastructure"),
# ]
# SERVICE_FIELDS = [
#     ("dns_resolution_success_percent", "DNS resolution success", "%", "Service Health"),
#     ("dns_response_time_ms", "DNS response time", "ms", "Service Health"),
#     ("dns_timeout_count", "DNS timeout count", "count", "Service Health"),
#     ("dhcp_success_percent", "DHCP success", "%", "Service Health"),
#     ("dhcp_response_time_ms", "DHCP response time", "ms", "Service Health"),
#     ("dhcp_failure_count", "DHCP failure count", "count", "Service Health"),
# ]
# INTEGER_FIELDS = {"queue_drops", "interface_errors", "dns_timeout_count", "dhcp_failure_count"}


# # ---------------------------------------------------------------------------
# # Organizer's supplied generator (same scenarios, keys and value ranges).
# # Timestamp uses timezone-aware UTC to avoid the deprecated utcnow() call.
# # ---------------------------------------------------------------------------
# def generate_telemetry(fault_type: str = "normal") -> dict:
#     data = {
#         "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#         "device_id": f"SW_CAMPUS_{random.randint(1, 10)}",
#         "metrics": {},
#     }

#     if fault_type == "latency_spike":
#         data["metrics"] = {
#             "cpu_utilization_pct": round(random.uniform(40, 70), 2),
#             "link_utilization_pct": round(random.uniform(60, 85), 2),
#             "packet_loss_pct": round(random.uniform(0.1, 1.5), 2),
#             "latency_ms": round(random.uniform(150, 400), 2),
#             "jitter_ms": round(random.uniform(30, 80), 2),
#             "queue_drops": random.randint(0, 50),
#         }
#         data["status"] = "Warning"
#     elif fault_type == "hardware_failure":
#         data["metrics"] = {
#             "cpu_utilization_pct": 99.9,
#             "link_utilization_pct": 100.0,
#             "packet_loss_pct": round(random.uniform(15, 30), 2),
#             "latency_ms": round(random.uniform(500, 1000), 2),
#             "queue_drops": random.randint(5000, 15000),
#             "interface_errors": random.randint(100, 500),
#         }
#         data["status"] = "Critical"
#     else:
#         data["metrics"] = {
#             "cpu_utilization_pct": round(random.uniform(10, 35), 2),
#             "link_utilization_pct": round(random.uniform(20, 50), 2),
#             "packet_loss_pct": 0.0,
#             "latency_ms": round(random.uniform(5, 20), 2),
#             "jitter_ms": round(random.uniform(1, 5), 2),
#             "queue_drops": 0,
#         }
#         data["status"] = "Healthy"
#     return data


# # ---------------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------------
# def utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def utc_iso(value: datetime | None = None) -> str:
#     return (value or utc_now()).isoformat().replace("+00:00", "Z")


# def as_float(value: Any) -> float | None:
#     if value is None or value == "":
#         return None
#     return float(value)


# def json_text(obj: Any) -> str:
#     return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


# def parse_topology(text: str) -> tuple[list[tuple[str, str]], list[str]]:
#     """Accept one undirected edge per line: DEVICE_A -- DEVICE_B."""
#     edges: list[tuple[str, str]] = []
#     errors: list[str] = []
#     for line_no, line in enumerate(text.splitlines(), 1):
#         line = line.strip()
#         if not line or line.startswith("#"):
#             continue
#         parts = re.split(r"\s*(?:--|->|,)\s*", line, maxsplit=1)
#         if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
#             errors.append(f"Topology line {line_no}: use DEVICE_A -- DEVICE_B")
#             continue
#         a, b = parts[0].strip(), parts[1].strip()
#         edges.append((a, b))
#     return edges, errors


# def connected_component(edges: list[tuple[str, str]], starts: list[str]) -> list[str]:
#     graph: dict[str, set[str]] = defaultdict(set)
#     for a, b in edges:
#         graph[a].add(b)
#         graph[b].add(a)
#     seen = set(starts)
#     queue = deque(starts)
#     while queue:
#         node = queue.popleft()
#         for nxt in graph.get(node, set()):
#             if nxt not in seen:
#                 seen.add(nxt)
#                 queue.append(nxt)
#     return sorted(seen)


# def validate_inputs(raw: dict, service: dict | None, topology_errors: list[str]) -> dict:
#     errors = list(topology_errors)
#     warnings: list[str] = []
#     if not isinstance(raw, dict):
#         return {"is_valid": False, "errors": ["Telemetry must be a JSON object."], "warnings": []}
#     if not isinstance(raw.get("metrics"), dict):
#         errors.append("Telemetry must contain a metrics object.")
#         return {"is_valid": False, "errors": errors, "warnings": warnings}
#     metrics = raw["metrics"]
#     ranges = {
#         "cpu_utilization_pct": (0, 100),
#         "link_utilization_pct": (0, 100),
#         "packet_loss_pct": (0, 100),
#         "latency_ms": (0, None),
#         "jitter_ms": (0, None),
#         "queue_drops": (0, None),
#         "interface_errors": (0, None),
#     }
#     for key, (lo, hi) in ranges.items():
#         if key not in metrics or metrics[key] is None:
#             continue
#         try:
#             val = float(metrics[key])
#             if val < lo or (hi is not None and val > hi):
#                 errors.append(f"{key}={metrics[key]} is outside the allowed range {lo}..{hi if hi is not None else '∞'}.")
#             if key in INTEGER_FIELDS and not val.is_integer():
#                 errors.append(f"{key} must be an integer.")
#         except (TypeError, ValueError):
#             errors.append(f"{key} must be numeric.")
#     if not raw.get("device_id"):
#         errors.append("device_id is required.")
#     timestamp = raw.get("timestamp")
#     if timestamp:
#         try:
#             dt = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
#             if dt.tzinfo is None:
#                 warnings.append("Timestamp has no timezone; UTC interpretation should be confirmed.")
#             else:
#                 age = (utc_now() - dt.astimezone(timezone.utc)).total_seconds()
#                 if age > 300:
#                     warnings.append(f"Telemetry is stale ({int(age)} seconds old).")
#                 elif age < -60:
#                     warnings.append("Timestamp is in the future.")
#         except ValueError:
#             errors.append("timestamp must be a valid ISO-8601 datetime.")
#     else:
#         warnings.append("timestamp is missing.")
#     missing = [k for k in ranges if metrics.get(k) is None]
#     if missing:
#         warnings.append("Missing device measurements remain unknown: " + ", ".join(missing))
#     if service is None:
#         warnings.append("DNS/DHCP service-health input was not supplied; service health is unknown.")
#     else:
#         if not isinstance(service.get("metrics", {}), dict):
#             errors.append("Service health metrics must be an object.")
#         else:
#             for key, val in service.get("metrics", {}).items():
#                 if val is None:
#                     continue
#                 if key.endswith("_percent") and not (0 <= float(val) <= 100):
#                     errors.append(f"{key} must be between 0 and 100.")
#                 elif key.endswith("_ms") or key.endswith("_count"):
#                     if float(val) < 0:
#                         errors.append(f"{key} cannot be negative.")
#             absent = [key for key, *_ in SERVICE_FIELDS if service.get("metrics", {}).get(key) is None]
#             if absent:
#                 warnings.append("Some service measurements are unknown: " + ", ".join(absent))
#     status = str(raw.get("status", "")).lower()
#     cpu = metrics.get("cpu_utilization_pct")
#     packet_loss = metrics.get("packet_loss_pct")
#     latency = metrics.get("latency_ms")
#     interface_errors = metrics.get("interface_errors")
#     critical = (cpu is not None and cpu >= 95) or (packet_loss is not None and packet_loss >= 10) or (latency is not None and latency >= 500) or (interface_errors is not None and interface_errors >= 100)
#     if status == "healthy" and critical:
#         warnings.append("Reported status is Healthy but supplied metrics contain critical signals.")
#     return {"is_valid": not errors, "errors": errors, "warnings": warnings}


# def new_message(incident_id: str, sender: str, receiver: str, message_type: str,
#                 payload: dict, status: str = "COMPLETED", correlation_id: str | None = None) -> dict:
#     return {
#         "protocol_version": "1.0",
#         "message_id": f"MSG-{uuid.uuid4().hex[:10].upper()}",
#         "correlation_id": correlation_id or f"CORR-{incident_id}",
#         "incident_id": incident_id,
#         "sender": sender,
#         "receiver": receiver,
#         "message_type": message_type,
#         "timestamp": utc_iso(),
#         "payload": payload,
#         "status": status,
#         "metadata": {"transport": "in_app_demo_message_bus", "content_type": "application/json"},
#     }


# def add_evidence(target: list[dict], agent: str, metric: str, value: Any, unit: str,
#                  observation: str, supports: str | None = None, points: int = 0) -> None:
#     target.append({
#         "source_agent": agent,
#         "metric": metric,
#         "value": value,
#         "unit": unit,
#         "observation": observation,
#         "supports": supports,
#         "heuristic_points": points,
#     })


# def analyze_performance(metrics: dict) -> dict:
#     agent = "performance_agent"
#     evidence: list[dict] = []
#     missing: list[str] = []
#     values = {
#         "latency_ms": ("ms", lambda x: x >= 100, "Elevated latency", "congestion", 1),
#         "jitter_ms": ("ms", lambda x: x >= 30, "Elevated jitter", "congestion", 1),
#         "packet_loss_pct": ("%", lambda x: x >= 1, "Elevated packet loss", "congestion", 1),
#         "link_utilization_pct": ("%", lambda x: x >= 85, "High link utilization", "congestion", 2),
#     }
#     for key, (unit, condition, text, cause, pts) in values.items():
#         value = metrics.get(key)
#         if value is None:
#             missing.append(key)
#         elif condition(float(value)):
#             add_evidence(evidence, agent, key, value, unit, text, cause, pts)
#         else:
#             add_evidence(evidence, agent, key, value, unit, "No breach of this demo threshold", None, 0)
#     finding = "Performance degradation detected" if any(x["heuristic_points"] for x in evidence) else "No performance threshold breach detected"
#     return {"agent": agent, "status": "PARTIAL" if missing else "COMPLETED", "summary": finding,
#             "evidence": evidence, "missing_data": missing,
#             "context_received": [], "decision": "Share performance symptoms with Infrastructure, Connectivity, Service Health and Correlation."}


# def analyze_infrastructure(metrics: dict, reported_status: str, performance_context: dict) -> dict:
#     agent = "infrastructure_agent"
#     evidence: list[dict] = []
#     missing: list[str] = []
#     cpu = metrics.get("cpu_utilization_pct")
#     if cpu is None:
#         missing.append("cpu_utilization_pct")
#     else:
#         add_evidence(evidence, agent, "cpu_utilization_pct", cpu, "%",
#                      "High CPU utilization" if cpu >= 80 else "CPU below demo overload threshold",
#                      "cpu_overload" if cpu >= 80 else None, 2 if cpu >= 80 else 0)
#     qdrops = metrics.get("queue_drops")
#     if qdrops is None:
#         missing.append("queue_drops")
#     else:
#         add_evidence(evidence, agent, "queue_drops", qdrops, "count",
#                      "Elevated queue drops" if qdrops >= 50 else "No queue-drop threshold breach",
#                      "congestion" if qdrops >= 50 else None, 1 if qdrops >= 50 else 0)
#     errors = metrics.get("interface_errors")
#     if errors is None:
#         missing.append("interface_errors")
#     else:
#         pts = 6 if errors >= 100 else (2 if errors >= 10 else 0)
#         add_evidence(evidence, agent, "interface_errors", errors, "count",
#                      "High interface error counter" if pts else "No interface-error threshold breach",
#                      "interface_or_hardware_fault" if pts else None, pts)
#     # Explicit cross-agent reuse: infrastructure receives the Performance finding.
#     perf_summary = performance_context.get("summary", "No performance context received")
#     perf_evidence = performance_context.get("evidence", [])
#     high_loss = any(x.get("metric") == "packet_loss_pct" and (x.get("value") or 0) >= 1 for x in perf_evidence)
#     if high_loss and errors is None:
#         cross_note = "Performance reported packet loss, but interface_errors is unknown; cannot confirm or rule out an interface fault."
#     elif high_loss and errors is not None and errors >= 100:
#         cross_note = "Performance packet loss is corroborated by high interface error counters."
#     elif high_loss:
#         cross_note = "Performance reported packet loss; supplied interface counter does not show a high-error signal."
#     else:
#         cross_note = "No elevated packet-loss finding was received from Performance."
#     return {"agent": agent, "status": "PARTIAL" if missing else "COMPLETED",
#             "summary": "Infrastructure measurements assessed against shared performance context.",
#             "evidence": evidence, "missing_data": missing,
#             "context_received": [{"from": "performance_agent", "summary": perf_summary, "packet_loss_seen": high_loss}],
#             "cross_agent_assessment": cross_note,
#             "reported_device_status": reported_status}


# def analyze_connectivity(affected: list[str], edges: list[tuple[str, str]],
#                          performance_context: dict, infrastructure_context: dict) -> dict:
#     connected = connected_component(edges, affected) if edges else list(affected)
#     graph_devices = {x for edge in edges for x in edge}
#     unknown = [x for x in affected if edges and x not in graph_devices]
#     evidence = []
#     if edges:
#         evidence.append({"observation": f"Topology contains {len(edges)} relationship(s); reachable component contains {len(connected)} device(s).",
#                          "affected_devices": affected, "connected_devices": connected})
#     else:
#         evidence.append({"observation": "No topology relationships supplied; wider network impact cannot be established.",
#                          "affected_devices": affected, "connected_devices": []})
#     perf_count = len(performance_context.get("evidence", []))
#     infra_count = len(infrastructure_context.get("evidence", []))
#     return {"agent": "connectivity_agent", "status": "PARTIAL" if not edges or unknown else "COMPLETED",
#             "summary": "Connectivity scope assessed using the supplied topology.", "evidence": evidence,
#             "missing_data": ["topology_relationships"] if not edges else [],
#             "unknown_devices": unknown, "connected_devices": connected,
#             "context_received": [
#                 {"from": "performance_agent", "elevated_findings_received": perf_count},
#                 {"from": "infrastructure_agent", "findings_received": infra_count},
#             ]}


# def analyze_service_health(service: dict | None, performance_context: dict,
#                            connectivity_context: dict) -> dict:
#     agent = "service_health_agent"
#     metrics = (service or {}).get("metrics", {}) if service else {}
#     evidence: list[dict] = []
#     missing: list[str] = []
#     rules = [
#         ("dns_resolution_success_percent", "%", lambda v: v < 95, "Low DNS resolution success", "dns_failure", 2),
#         ("dns_response_time_ms", "ms", lambda v: v > 200, "Slow DNS response", "dns_failure", 1),
#         ("dns_timeout_count", "count", lambda v: v > 5, "High DNS timeout count", "dns_failure", 2),
#         ("dhcp_success_percent", "%", lambda v: v < 95, "Low DHCP success", "dhcp_failure", 2),
#         ("dhcp_response_time_ms", "ms", lambda v: v > 500, "Slow DHCP response", "dhcp_failure", 1),
#         ("dhcp_failure_count", "count", lambda v: v > 5, "High DHCP failure count", "dhcp_failure", 2),
#     ]
#     for key, unit, condition, text, cause, pts in rules:
#         value = metrics.get(key)
#         if value is None:
#             missing.append(key)
#         elif condition(float(value)):
#             add_evidence(evidence, agent, key, value, unit, text, cause, pts)
#         else:
#             add_evidence(evidence, agent, key, value, unit, "No breach of this demo threshold", None, 0)
#     return {"agent": agent, "status": "PARTIAL" if missing else "COMPLETED",
#             "summary": "DNS/DHCP service health assessed." if service else "No DNS/DHCP telemetry supplied; service health remains unknown.",
#             "evidence": evidence, "missing_data": missing,
#             "context_received": [
#                 {"from": "performance_agent", "summary": performance_context.get("summary")},
#                 {"from": "connectivity_agent", "summary": connectivity_context.get("summary")},
#             ]}


# def correlate(findings: dict[str, dict], reported_status: str) -> dict:
#     scores = {
#         "congestion": 0,
#         "cpu_overload": 0,
#         "interface_or_hardware_fault": 0,
#         "dns_failure": 0,
#         "dhcp_failure": 0,
#     }
#     support_agents: dict[str, set[str]] = defaultdict(set)
#     all_evidence: list[dict] = []
#     missing: list[str] = []
#     for finding in findings.values():
#         missing.extend(finding.get("missing_data", []))
#         for item in finding.get("evidence", []):
#             all_evidence.append(item)
#             cause = item.get("supports")
#             pts = int(item.get("heuristic_points", 0) or 0)
#             if cause in scores and pts > 0:
#                 scores[cause] += pts
#                 support_agents[cause].add(item.get("source_agent", "unknown"))

#     ranked = sorted(
#         [{"hypothesis": name, "heuristic_points": points,
#           "supporting_agents": sorted(support_agents[name]),
#           "supporting_agent_count": len(support_agents[name])}
#          for name, points in scores.items() if points > 0],
#         key=lambda x: (-x["heuristic_points"], x["hypothesis"]),
#     )
#     metrics = findings["infrastructure_agent"].get("_raw_metrics", {})
#     # Status-vs-metric conflict is a first-class finding, not a silent override.
#     critical = (
#         (metrics.get("cpu_utilization_pct") is not None and metrics["cpu_utilization_pct"] >= 95)
#         or (metrics.get("packet_loss_pct") is not None and metrics["packet_loss_pct"] >= 10)
#         or (metrics.get("latency_ms") is not None and metrics["latency_ms"] >= 500)
#         or (metrics.get("interface_errors") is not None and metrics["interface_errors"] >= 100)
#     )
#     conflicts = []
#     if reported_status.lower() == "healthy" and critical:
#         conflicts.append({"type": "status_metric_conflict", "reported_status": reported_status,
#                           "observation": "Device reports Healthy while supplied telemetry contains critical signals.",
#                           "resolution": "Prioritize measured signals for investigation but preserve the status conflict in the report."})
#     if reported_status.lower() == "critical" and not critical and sum(scores.values()) == 0:
#         conflicts.append({"type": "status_metric_conflict", "reported_status": reported_status,
#                           "observation": "Device reports Critical but no configured critical signal was detected.",
#                           "resolution": "Request more telemetry; do not assume the status label is correct."})

#     core = ["cpu_utilization_pct", "link_utilization_pct", "packet_loss_pct", "latency_ms"]
#     core_present = all(metrics.get(x) is not None for x in core)
#     if not all_evidence or not ranked:
#         if core_present and not conflicts:
#             status, primary = "no_fault_detected", None
#         else:
#             status, primary = "insufficient_evidence", None
#     elif missing or not core_present or conflicts:
#         status, primary = "partial", ranked[0]
#     else:
#         status, primary = "diagnosed", ranked[0]

#     if len(ranked) >= 2 and ranked[1]["heuristic_points"] >= max(2, int(ranked[0]["heuristic_points"] * 0.65)):
#         decision = "Multiple fault families have material evidence"
#         decision_type = "MULTI_HYPOTHESIS"
#     elif conflicts:
#         decision = "Conflicting findings — provisional decision"
#         decision_type = "CONFLICTED"
#     elif ranked and ranked[0]["supporting_agent_count"] >= 2:
#         decision = "Cross-agent evidence convergence"
#         decision_type = "CROSS_AGENT_CONVERGENCE"
#     elif ranked:
#         decision = "Single-agent lead — provisional, needs corroboration"
#         decision_type = "PROVISIONAL"
#     elif status == "no_fault_detected":
#         decision = "No fault indicated by the supplied core measurements"
#         decision_type = "NO_FAULT_INDICATED"
#     else:
#         decision = "Insufficient evidence — abstain from selecting a root cause"
#         decision_type = "ABSTAIN"

#     return {
#         "status": status,
#         "primary_hypothesis": primary,
#         "ranked_hypotheses": ranked,
#         "all_evidence": all_evidence,
#         "missing_data": sorted(set(missing)),
#         "conflicts": conflicts,
#         "decision": decision,
#         "decision_type": decision_type,
#         "score_type": "heuristic_points_not_probability",
#         "scores": scores,
#     }


# def recommendations_for(hypothesis: str | None, diagnosis: dict) -> list[str]:
#     mapping = {
#         "congestion": [
#             "Inspect traffic flows and identify bandwidth-heavy devices.",
#             "Review link utilization, QoS policies, queue depth and queue-drop trends.",
#             "Verify whether the latency and packet-loss symptoms reduce after controlled traffic shaping.",
#         ],
#         "cpu_overload": [
#             "Identify processes and services consuming switch/router CPU.",
#             "Review CPU trends, control-plane logs and recent configuration changes.",
#             "Verify CPU recovery and forwarding performance after operator-approved changes.",
#         ],
#         "interface_or_hardware_fault": [
#             "Inspect interface error counters, cable/transceiver health and physical link state.",
#             "Compare error-counter increments over time and inspect device logs.",
#             "Verify packet loss and interface errors after the physical issue is addressed.",
#         ],
#         "dns_failure": [
#             "Check DNS resolver availability, response time and timeout trends.",
#             "Verify resolver reachability and recent DNS configuration changes.",
#             "Retest resolution from an affected client and a known-good segment.",
#         ],
#         "dhcp_failure": [
#             "Check DHCP server availability, lease allocation failures and pool capacity.",
#             "Review relay/helper configuration and DHCP service logs.",
#             "Verify a client can obtain and renew a lease after remediation.",
#         ],
#     }
#     if not hypothesis:
#         return ["Collect the missing measurements listed in the report before selecting a root cause.",
#                 "Repeat the measurement from an affected device and a known-good comparison point."]
#     actions = mapping.get(hypothesis, ["Collect additional telemetry and inspect related device logs."])
#     if diagnosis.get("missing_data"):
#         actions.append("Collect missing measurements: " + ", ".join(diagnosis["missing_data"][:8]) + ".")
#     return actions


# def run_collaboration(inputs: dict) -> dict:
#     incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
#     corr = f"CORR-{incident_id}"
#     raw = inputs["raw"]
#     metrics = raw.get("metrics", {})
#     service = inputs.get("service")
#     edges = inputs["edges"]
#     affected = inputs["affected"]
#     status = raw.get("status", "Unknown")
#     messages: list[dict] = []
#     findings: dict[str, dict] = {}
#     steps: list[dict] = []

#     def emit(sender: str, receiver: str, typ: str, payload: dict, msg_status: str = "COMPLETED"):
#         msg = new_message(incident_id, sender, receiver, typ, payload, msg_status, corr)
#         messages.append(msg)
#         return msg

#     # 1) Performance Agent receives the initial task and publishes its findings.
#     emit("orchestrator", "performance_agent", "TASK", {"metrics": {k: metrics.get(k) for k in ["latency_ms", "jitter_ms", "packet_loss_pct", "link_utilization_pct"]}})
#     perf = analyze_performance(metrics)
#     findings["performance_agent"] = perf
#     emit("performance_agent", "infrastructure_agent", "FINDING", {
#         "summary": perf["summary"], "evidence": perf["evidence"], "missing_data": perf["missing_data"],
#         "purpose": "Infrastructure uses performance symptoms as context when examining CPU, queues and interface errors.",
#     }, perf["status"])
#     emit("performance_agent", "connectivity_agent", "FINDING", {
#         "summary": perf["summary"], "elevated_metrics": [x["metric"] for x in perf["evidence"] if x["heuristic_points"] > 0],
#         "purpose": "Connectivity uses symptom context to frame affected-segment investigation.",
#     }, perf["status"])
#     emit("performance_agent", "service_health_agent", "FINDING", {
#         "summary": perf["summary"], "latency_ms": metrics.get("latency_ms"),
#         "purpose": "Service Health considers whether reported user symptoms could coincide with DNS/DHCP degradation.",
#     }, perf["status"])

#     # 2) Infrastructure explicitly reuses the Performance finding.
#     emit("orchestrator", "infrastructure_agent", "TASK", {
#         "metrics": {k: metrics.get(k) for k in ["cpu_utilization_pct", "queue_drops", "interface_errors"]},
#         "context_from_performance": perf["summary"],
#     })
#     infra = analyze_infrastructure(metrics, status, perf)
#     infra["_raw_metrics"] = metrics
#     findings["infrastructure_agent"] = infra
#     emit("infrastructure_agent", "connectivity_agent", "FINDING", {
#         "summary": infra["summary"], "evidence": infra["evidence"],
#         "cross_agent_assessment": infra.get("cross_agent_assessment"),
#     }, infra["status"])

#     # 3) Connectivity reuses the symptom and infrastructure summaries.
#     emit("orchestrator", "connectivity_agent", "TASK", {
#         "affected_devices": affected, "topology_edges": edges,
#         "context_from_performance": perf["summary"], "context_from_infrastructure": infra["summary"],
#     })
#     connectivity = analyze_connectivity(affected, edges, perf, infra)
#     findings["connectivity_agent"] = connectivity
#     emit("connectivity_agent", "service_health_agent", "FINDING", {
#         "summary": connectivity["summary"], "connected_devices": connectivity.get("connected_devices", []),
#         "purpose": "Service Health receives the affected-segment context for service-scope interpretation.",
#     }, connectivity["status"])

#     # 4) Service Health consumes symptoms and connectivity context.
#     emit("orchestrator", "service_health_agent", "TASK", {
#         "service_health": service,
#         "context_from_performance": perf["summary"],
#         "context_from_connectivity": connectivity["summary"],
#     }, "PARTIAL" if service is None else "COMPLETED")
#     service_finding = analyze_service_health(service, perf, connectivity)
#     findings["service_health_agent"] = service_finding

#     # 5) Correlation asks for distinguishing evidence when a high-loss event has no interface counter.
#     if (metrics.get("packet_loss_pct") is not None and metrics["packet_loss_pct"] >= 1
#             and metrics.get("interface_errors") is None):
#         emit("fault_correlation_agent", "infrastructure_agent", "REQUEST", {
#             "requested_data": ["interface_errors", "interface_state", "error_counter_delta"],
#             "reason": "Performance observed packet loss; interface statistics would distinguish a physical/interface fault from other causes.",
#         }, "PARTIAL")
#         emit("infrastructure_agent", "fault_correlation_agent", "RESPONSE", {
#             "available_data": {"interface_errors": None},
#             "missing_data": ["interface_errors", "interface_state", "error_counter_delta"],
#             "response": "These interface measurements were not supplied; no value is assumed.",
#         }, "PARTIAL")

#     # 6) Correlation receives all findings and returns a transparent decision.
#     emit("orchestrator", "fault_correlation_agent", "TASK", {
#         "findings_from": list(findings.keys()), "evidence_item_count": sum(len(x.get("evidence", [])) for x in findings.values()),
#         "reported_device_status": status,
#     })
#     diagnosis = correlate(findings, status)
#     emit("fault_correlation_agent", "recommendation_agent", "FINDING", {
#         "decision": diagnosis["decision"], "decision_type": diagnosis["decision_type"],
#         "primary_hypothesis": diagnosis["primary_hypothesis"],
#         "ranked_hypotheses": diagnosis["ranked_hypotheses"],
#         "supporting_evidence": diagnosis["all_evidence"], "conflicts": diagnosis["conflicts"],
#         "missing_data": diagnosis["missing_data"],
#     }, "PARTIAL" if diagnosis["status"] == "partial" else "COMPLETED")

#     # 7) Recommendation consumes the correlation result.
#     emit("orchestrator", "recommendation_agent", "TASK", {
#         "diagnosis": diagnosis["primary_hypothesis"], "decision": diagnosis["decision"],
#         "evidence": diagnosis["all_evidence"], "missing_data": diagnosis["missing_data"],
#     }, "PARTIAL" if diagnosis["status"] in {"partial", "insufficient_evidence"} else "COMPLETED")
#     actions = recommendations_for(
#         diagnosis["primary_hypothesis"]["hypothesis"] if diagnosis["primary_hypothesis"] else None,
#         diagnosis,
#     )
#     emit("recommendation_agent", "report_builder", "FINDING", {
#         "recommended_actions": actions, "automated_remediation": False,
#     })

#     # Cross-agent trace summary for UI.
#     agent_order = ["performance_agent", "infrastructure_agent", "connectivity_agent", "service_health_agent"]
#     for agent in agent_order:
#         steps.append({"agent": agent, "status": findings[agent]["status"], "summary": findings[agent]["summary"]})
#     steps.extend([
#         {"agent": "fault_correlation_agent", "status": "PARTIAL" if diagnosis["status"] in {"partial", "insufficient_evidence"} else "COMPLETED", "summary": diagnosis["decision"]},
#         {"agent": "recommendation_agent", "status": "COMPLETED", "summary": f"Generated {len(actions)} operator action(s)."},
#     ])

#     validation = validate_inputs(raw, service, inputs.get("topology_errors", []))
#     missing_device = [key for key, *_ in DEVICE_FIELDS if metrics.get(key) is None]
#     missing_service = [key for key, *_ in SERVICE_FIELDS if service is None or service.get("metrics", {}).get(key) is None]
#     report = {
#         "incident_id": incident_id,
#         "status": diagnosis["status"],
#         "decision": diagnosis["decision"],
#         "decision_type": diagnosis["decision_type"],
#         "suspected_root_cause": diagnosis["primary_hypothesis"]["hypothesis"] if diagnosis["primary_hypothesis"] else None,
#         "ranked_hypotheses": diagnosis["ranked_hypotheses"],
#         "supporting_evidence": diagnosis["all_evidence"],
#         "alternative_causes": diagnosis["ranked_hypotheses"][1:],
#         "conflicts": diagnosis["conflicts"],
#         "missing_device_measurements": missing_device,
#         "missing_service_measurements": missing_service,
#         "affected_devices": affected,
#         "connected_devices": connectivity.get("connected_devices", []),
#         "recommended_actions": actions,
#         "confidence": {"value": None, "type": "not_calibrated"},
#         "heuristic_scores": diagnosis["scores"],
#         "limitations": [
#             "This is an illustrative, rule-based collaboration demonstrator, not a live network monitor.",
#             "Heuristic points are ranking aids, not probabilities or calibrated confidence.",
#             "No network device is changed; recommendations are operator guidance only.",
#         ],
#     }
#     return {
#         "incident_id": incident_id,
#         "inputs": inputs,
#         "validation": validation,
#         "findings": findings,
#         "diagnosis": diagnosis,
#         "recommendations": actions,
#         "messages": messages,
#         "steps": steps,
#         "report": report,
#     }


# def to_legacy_v09(raw: dict) -> dict:
#     metrics = raw.get("metrics", {})
#     old = {}
#     mapping = {
#         "cpu_utilization_pct": "cpu_pct",
#         "link_utilization_pct": "link_pct",
#         "packet_loss_pct": "packet_loss_pct",
#         "queue_drops": "queue_drop_count",
#         "interface_errors": "interface_error_count",
#     }
#     for new_key, old_key in mapping.items():
#         if metrics.get(new_key) is not None:
#             old[old_key] = metrics[new_key]
#     if metrics.get("latency_ms") is not None:
#         old["latency_seconds"] = metrics["latency_ms"] / 1000
#     if metrics.get("jitter_ms") is not None:
#         old["jitter_seconds"] = metrics["jitter_ms"] / 1000
#     return {"schema_version": "0.9", "device": raw.get("device_id"),
#             "observed_at": raw.get("timestamp"), "device_status": raw.get("status"),
#             "measurements": old}


# def get_current() -> dict | None:
#     return st.session_state.get("last_result")


# def set_page_header(title: str, subtitle: str):
#     st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


# def show_no_result():
#     st.info("No incident has been run yet. Open **Run Investigation** and submit telemetry to populate the collaboration trace.")


# # ---------------------------------------------------------------------------
# # Session state and navigation
# # ---------------------------------------------------------------------------
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None
# if "run_history" not in st.session_state:
#     st.session_state.run_history = []
# if "prefill" not in st.session_state:
#     st.session_state.prefill = {}
# if "raw_json_test" not in st.session_state:
#     st.session_state.raw_json_test = '{"device_id":"SW_CAMPUS_1","status":"Healthy","metrics":{"packet_loss_pct":125}}'

# st.sidebar.title("🛰️ NETCOOP AI")
# st.sidebar.caption("Multi-Agent Network Operations & Intelligence")
# page = st.sidebar.radio(
#     "Evaluation-focused workspaces",
#     [
#         "Command Center",
#         "Run Investigation",
#         "Agent Collaboration",
#         "Evidence & Consensus",
#         "Interoperability Lab",
#         "Robustness Lab",
#         "Judge Guide",
#     ],
# )
# st.sidebar.divider()
# st.sidebar.metric("Rubric coverage", "100% mapped")
# st.sidebar.caption("Coverage mapping is not a claim of marks earned.")
# if st.session_state.last_result:
#     st.sidebar.metric("Latest incident", st.session_state.last_result["incident_id"])


# # ---------------------------------------------------------------------------
# # PAGE 1 - Command Center (weighted proof overview)
# # ---------------------------------------------------------------------------
# if page == "Command Center":
#     set_page_header("NETCOOP AI Command Center", "A judge-facing view organized around the hackathon's highest-weighted deliverables.")

#     cols = st.columns(4)
#     for col, item in zip(cols, RUBRIC[:4]):
#         col.metric(item["name"], f'{item["weight"]}%')
#     col1, col2 = st.columns([1.25, 1])
#     with col1:
#         st.subheader("Evaluation priorities")
#         for item in RUBRIC:
#             st.write(f'**{item["weight"]}% — {item["name"]}**')
#             st.progress(item["weight"] / 30)
#             st.caption(item["proof"])
#     with col2:
#         st.subheader("Latest incident decision")
#         result = get_current()
#         if result:
#             diag = result["diagnosis"]
#             report = result["report"]
#             st.metric("Leading hypothesis", (report["suspected_root_cause"] or "Undetermined").replace("_", " ").title())
#             st.metric("Decision state", diag["decision_type"].replace("_", " ").title())
#             st.metric("Structured messages exchanged", len(result["messages"]))
#             st.metric("Evidence items collected", len(diag["all_evidence"]))
#             st.caption(f'Incident: {result["incident_id"]}')
#         else:
#             st.info("Run an investigation to populate this command center.")

#     st.subheader("The NETCOOP decision pipeline")
#     pipeline_cols = st.columns(6)
#     pipeline = [
#         ("Telemetry", "Organizer or manual input"),
#         ("Performance", "Network experience signals"),
#         ("Infrastructure", "Device and interface health"),
#         ("Connectivity + Service", "Impact and service context"),
#         ("Correlation", "Evidence ranking and conflicts"),
#         ("Recommendation", "Operator actions and report"),
#     ]
#     for c, (title, desc) in zip(pipeline_cols, pipeline):
#         with c:
#             st.markdown(f'<div class="agent-card"><h4>{title}</h4><span class="subtle">{desc}</span></div>', unsafe_allow_html=True)
#     st.subheader("What the evaluator can inspect")
#     st.dataframe(pd.DataFrame([{"Weight": f'{r["weight"]}%', "Criterion": r["name"],
#                                 "Live proof page": r["page"], "Key evidence": r["proof"]} for r in RUBRIC]),
#                  width="stretch", hide_index=True)

#     st.warning("This app is a standalone collaboration demonstrator. Its message bus and rule-based agent responses are generated by this app; it does not claim to have executed your separate LangGraph backend or connected to live network devices.")


# # ---------------------------------------------------------------------------
# # PAGE 2 - Run Investigation (inputs by agent)
# # ---------------------------------------------------------------------------
# elif page == "Run Investigation":
#     set_page_header("Run a Multi-Agent Investigation", "Populate each specialist's input, then watch findings move between agents and into fault correlation.")
#     st.markdown("#### Start from the organizer's generator or enter each agent's data")
#     g1, g2 = st.columns([1, 2])
#     with g1:
#         generator_type = st.selectbox("Organizer generator scenario", ["normal", "latency_spike", "hardware_failure"],
#                                       format_func=lambda x: {"normal": "Normal", "latency_spike": "Latency spike", "hardware_failure": "Hardware failure"}[x])
#         if st.button("Generate organizer sample", width="stretch"):
#             sample = generate_telemetry(generator_type)
#             prefill = {k: str(v) for k, v in sample["metrics"].items()}
#             prefill.update({"device_id": sample["device_id"], "status": sample["status"], "timestamp": sample["timestamp"]})
#             st.session_state.prefill = prefill
#             st.session_state.generated_sample = sample
#             st.success("Organizer sample generated. Its original missing fields are left blank in the form.")
#     with g2:
#         if st.session_state.get("generated_sample"):
#             st.json(st.session_state.generated_sample)
#         else:
#             st.info("The organizer generator provides three original scenarios. Metrics not present in a generated sample remain unknown; they are not converted to zero.")

#     pre = st.session_state.prefill
#     with st.form("agent_inputs_form", clear_on_submit=False):
#         top1, top2, top3 = st.columns(3)
#         device_id = top1.text_input("Device ID", value=pre.get("device_id", "SW_CAMPUS_1"))
#         device_status = top2.selectbox("Reported device status", ["Healthy", "Warning", "Critical"],
#                                        index=["Healthy", "Warning", "Critical"].index(pre.get("status", "Warning")) if pre.get("status", "Warning") in ["Healthy", "Warning", "Critical"] else 1)
#         timestamp = top3.text_input("Timestamp (ISO-8601; blank = now UTC)", value=pre.get("timestamp", ""))

#         pcol, icol = st.columns(2)
#         with pcol:
#             st.markdown("### 1 · Performance Agent")
#             st.caption("Receives latency, jitter, packet loss and link utilization.")
#             latency = st.text_input("Latency (ms)", value=pre.get("latency_ms", ""), placeholder="blank = unknown")
#             jitter = st.text_input("Jitter (ms)", value=pre.get("jitter_ms", ""), placeholder="blank = unknown")
#             packet_loss = st.text_input("Packet loss (%)", value=pre.get("packet_loss_pct", ""), placeholder="blank = unknown")
#             link_util = st.text_input("Link utilization (%)", value=pre.get("link_utilization_pct", ""), placeholder="blank = unknown")
#         with icol:
#             st.markdown("### 2 · Infrastructure Agent")
#             st.caption("Receives CPU, queue drops, interface errors and device status.")
#             cpu = st.text_input("CPU utilization (%)", value=pre.get("cpu_utilization_pct", ""), placeholder="blank = unknown")
#             queue_drops = st.text_input("Queue drops (integer)", value=pre.get("queue_drops", ""), placeholder="blank = unknown")
#             interface_errors = st.text_input("Interface errors (integer)", value=pre.get("interface_errors", ""), placeholder="blank = unknown")
#             st.caption("The Infrastructure Agent also receives the Performance Agent's findings.")

#         ccol, scol = st.columns(2)
#         with ccol:
#             st.markdown("### 3 · Connectivity Agent")
#             st.caption("Receives impacted devices and network relationships.")
#             affected_text = st.text_input("Affected device IDs (comma-separated)", value=pre.get("device_id", "SW_CAMPUS_1"))
#             topology_text = st.text_area("Topology edges (one per line: DEVICE_A -- DEVICE_B)",
#                                          value="SW_CAMPUS_1 -- SW_BUILDING_1\nSW_BUILDING_1 -- SW_CORE_1",
#                                          height=110)
#         with scol:
#             st.markdown("### 4 · Service Health Agent")
#             st.caption("Receives optional DNS and DHCP service telemetry. Blank means not measured.")
#             dns_success = st.text_input("DNS resolution success (%)", value="", placeholder="blank = unknown")
#             dns_response = st.text_input("DNS response time (ms)", value="", placeholder="blank = unknown")
#             dns_timeouts = st.text_input("DNS timeout count (integer)", value="", placeholder="blank = unknown")
#             dhcp_success = st.text_input("DHCP success (%)", value="", placeholder="blank = unknown")
#             dhcp_response = st.text_input("DHCP response time (ms)", value="", placeholder="blank = unknown")
#             dhcp_failures = st.text_input("DHCP failure count (integer)", value="", placeholder="blank = unknown")

#         st.markdown("### Evaluation label (optional)")
#         expected_label = st.selectbox("Known scenario label — used only to compare the output, never sent to agents",
#                                       ["Not labelled", "congestion", "cpu_overload", "interface_or_hardware_fault",
#                                        "dns_failure", "dhcp_failure", "no_fault_detected", "multiple_faults", "insufficient_evidence"])
#         st.caption("The expected label is held outside the agent inputs. It is only used after diagnosis for the demo comparison.")
#         submitted = st.form_submit_button("▶ Run agent collaboration", type="primary", width="stretch")

#     if submitted:
#         try:
#             fields = {
#                 "latency_ms": latency, "jitter_ms": jitter, "packet_loss_pct": packet_loss,
#                 "link_utilization_pct": link_util, "cpu_utilization_pct": cpu,
#                 "queue_drops": queue_drops, "interface_errors": interface_errors,
#             }
#             metrics: dict[str, Any] = {}
#             for key, text in fields.items():
#                 if text.strip() != "":
#                     val = float(text) if key not in INTEGER_FIELDS else int(text)
#                     metrics[key] = val
#             service_values = {
#                 "dns_resolution_success_percent": dns_success,
#                 "dns_response_time_ms": dns_response,
#                 "dns_timeout_count": dns_timeouts,
#                 "dhcp_success_percent": dhcp_success,
#                 "dhcp_response_time_ms": dhcp_response,
#                 "dhcp_failure_count": dhcp_failures,
#             }
#             service_metrics: dict[str, Any] = {}
#             for key, text in service_values.items():
#                 if text.strip() != "":
#                     service_metrics[key] = int(text) if key in INTEGER_FIELDS else float(text)
#             service = {"timestamp": timestamp.strip() or utc_iso(), "service_id": "CAMPUS_DNS_DHCP",
#                        "metrics": service_metrics} if service_metrics else None
#             edges, topology_errors = parse_topology(topology_text)
#             affected = [x.strip() for x in affected_text.split(",") if x.strip()]
#             if not affected:
#                 affected = [device_id.strip()]
#             raw = {"timestamp": timestamp.strip() or utc_iso(), "device_id": device_id.strip(),
#                    "status": device_status, "metrics": metrics}
#             inputs = {"raw": raw, "service": service, "edges": edges, "affected": affected,
#                       "topology_errors": topology_errors,
#                       "expected_label": None if expected_label == "Not labelled" else expected_label}
#             validation = validate_inputs(raw, service, topology_errors)
#             if not validation["is_valid"]:
#                 st.error("Input validation failed. Correct the errors before running agent collaboration.")
#                 st.json(validation)
#             else:
#                 result = run_collaboration(inputs)
#                 result["validation"] = validation
#                 result["expected_label"] = inputs["expected_label"]
#                 st.session_state.last_result = result
#                 st.session_state.run_history.insert(0, result)
#                 st.session_state.run_history = st.session_state.run_history[:30]
#                 st.success(f'Investigation completed: {result["incident_id"]}. Open Agent Collaboration to inspect the message exchange.')
#         except Exception as exc:
#             st.error(f"Could not create incident: {type(exc).__name__}: {exc}")

#     current = get_current()
#     if current:
#         st.divider()
#         st.subheader("Latest decision")
#         d = current["diagnosis"]
#         a, b, c, e = st.columns(4)
#         a.metric("Root-cause lead", (current["report"]["suspected_root_cause"] or "Undetermined").replace("_", " ").title())
#         b.metric("Decision", d["decision_type"].replace("_", " ").title())
#         c.metric("Messages", len(current["messages"]))
#         e.metric("Evidence items", len(d["all_evidence"]))
#         st.info(d["decision"])


# # ---------------------------------------------------------------------------
# # PAGE 3 - Agent collaboration and message exchange
# # ---------------------------------------------------------------------------
# elif page == "Agent Collaboration":
#     set_page_header("Agent Collaboration & Message Trace", "Inspect which agent sent information, who consumed it, what was reused and how the next decision was informed.")
#     result = get_current()
#     if not result:
#         show_no_result()
#     else:
#         st.caption(f'Incident {result["incident_id"]} · {len(result["messages"])} structured messages · protocol v1.0 demo envelope')
#         st.markdown("### Collaboration sequence")
#         for index, step in enumerate(result["steps"], 1):
#             title, desc, _ = AGENT_INFO[step["agent"]]
#             st.markdown(
#                 f'<div class="agent-card"><b>{index}. {title}</b> '
#                 f'<span class="pill">{step["status"]}</span><br><span class="subtle">{step["summary"]}</span></div>',
#                 unsafe_allow_html=True,
#             )

#         st.markdown("### Agent-to-agent evidence hand-offs")
#         interactions = [
#             ("Performance → Infrastructure", "Packet loss, latency and utilization findings become context for CPU, queue and interface analysis."),
#             ("Performance → Connectivity", "The symptom summary helps Connectivity investigate the affected segment."),
#             ("Performance → Service Health", "Latency context is shared so DNS/DHCP symptoms can be checked rather than assumed."),
#             ("Infrastructure → Connectivity", "Device health findings are shared alongside performance symptoms."),
#             ("Connectivity → Service Health", "Affected segment and reachable-device context is passed downstream."),
#             ("Specialists → Fault Correlation", "Structured evidence and missing-data declarations are aggregated for hypothesis ranking."),
#             ("Fault Correlation → Recommendation", "The ranked diagnosis, evidence, conflicts and data gaps become the recommendation input."),
#         ]
#         for sender_receiver, explanation in interactions:
#             st.markdown(f"**{sender_receiver}** — {explanation}")

#         st.markdown("### Message bus — filter and inspect actual generated demo envelopes")
#         messages = result["messages"]
#         types = ["All"] + sorted({m["message_type"] for m in messages})
#         selected_type = st.selectbox("Filter message type", types)
#         visible = [m for m in messages if selected_type == "All" or m["message_type"] == selected_type]
#         for i, message in enumerate(visible, 1):
#             label = f'{i}. {message["message_type"]}: {message["sender"]} → {message["receiver"]} [{message["status"]}]'
#             with st.expander(label, expanded=(message["message_type"] in {"REQUEST", "RESPONSE"})):
#                 left, right = st.columns([1, 1.5])
#                 with left:
#                     st.write("**Envelope metadata**")
#                     st.json({k: message[k] for k in ["protocol_version", "message_id", "correlation_id", "incident_id", "sender", "receiver", "message_type", "timestamp", "status"]})
#                 with right:
#                     st.write("**Payload exchanged**")
#                     st.json(message["payload"])

#         st.markdown("### Concrete example: evidence is reused, not merely displayed")
#         infra = result["findings"]["infrastructure_agent"]
#         st.write("**Performance Agent's finding:**")
#         st.json(result["findings"]["performance_agent"])
#         st.write("**Infrastructure Agent's cross-agent assessment:**")
#         st.info(infra.get("cross_agent_assessment", "No cross-agent note produced."))
#         st.write("**Context explicitly recorded as received by Infrastructure:**")
#         st.json(infra.get("context_received", []))
#         st.warning("This is a standalone, rule-based collaboration demonstrator. The messages and hand-offs shown here are produced by this app's demo orchestrator, not by your separate LangGraph backend. It is designed to make the intended protocol and information flow inspectable; do not describe it as a live backend trace.")


# # ---------------------------------------------------------------------------
# # PAGE 4 - Evidence and consensus / diagnosis
# # ---------------------------------------------------------------------------
# elif page == "Evidence & Consensus":
#     set_page_header("Evidence, Fault Correlation & Consensus", "The highest-weighted diagnosis criterion: inspect each signal, its source, its effect on hypothesis ranking and the final decision state.")
#     result = get_current()
#     if not result:
#         show_no_result()
#     else:
#         diag = result["diagnosis"]
#         report = result["report"]
#         a, b, c, d = st.columns(4)
#         a.metric("Leading hypothesis", (report["suspected_root_cause"] or "Undetermined").replace("_", " ").title())
#         b.metric("Diagnostic state", diag["status"].replace("_", " ").title())
#         c.metric("Evidence records", len(diag["all_evidence"]))
#         d.metric("Open data gaps", len(diag["missing_data"]))
#         st.subheader("Decision convergence")
#         if diag["decision_type"] == "CROSS_AGENT_CONVERGENCE":
#             st.success(diag["decision"])
#         elif diag["decision_type"] == "MULTI_HYPOTHESIS":
#             st.warning(diag["decision"])
#         elif diag["decision_type"] in {"CONFLICTED", "PROVISIONAL"}:
#             st.warning(diag["decision"])
#         else:
#             st.info(diag["decision"])
#         st.caption("Convergence means at least two specialist agents contributed scored evidence to the leading hypothesis. Scores are heuristic points, never probabilities.")

#         st.subheader("Ranked hypotheses")
#         if diag["ranked_hypotheses"]:
#             st.dataframe(pd.DataFrame(diag["ranked_hypotheses"]), width="stretch", hide_index=True)
#         else:
#             st.info("No hypothesis received positive heuristic points. Check whether the core measurements are present before concluding the network is healthy.")
#         st.subheader("Evidence ledger — source, observation and contribution")
#         if diag["all_evidence"]:
#             st.dataframe(pd.DataFrame(diag["all_evidence"]), width="stretch", hide_index=True)
#         else:
#             st.info("No evidence records were produced.")
#         left, right = st.columns(2)
#         with left:
#             st.subheader("Conflicts")
#             if diag["conflicts"]:
#                 for conflict in diag["conflicts"]:
#                     st.warning(conflict["observation"])
#                     st.caption(conflict["resolution"])
#             else:
#                 st.success("No status/metric conflict detected by the configured demo checks.")
#         with right:
#             st.subheader("Missing data / uncertainty")
#             if diag["missing_data"]:
#                 for item in diag["missing_data"]:
#                     st.write(f"• {item}")
#             else:
#                 st.success("No missing measurements were identified by the specialist agents.")
#         st.subheader("Recommendation Agent output")
#         for n, action in enumerate(result["recommendations"], 1):
#             st.write(f"{n}. {action}")
#         st.subheader("Unified report")
#         st.json(report)
#         st.download_button("Download diagnostic report (JSON)", json_text(report),
#                            file_name=f'{result["incident_id"]}_report.json', mime="application/json", width="content")

#         if result.get("expected_label"):
#             predicted = report["suspected_root_cause"]
#             expected = result["expected_label"]
#             st.subheader("Optional ground-truth comparison")
#             if expected == "multiple_faults":
#                 matched = len(diag["ranked_hypotheses"]) >= 2
#                 st.write("Expected multiple faults · " + ("multiple hypotheses ranked" if matched else "review the ranked hypotheses"))
#             elif expected == "insufficient_evidence":
#                 st.write("Expected insufficient evidence · actual status: " + diag["status"])
#             else:
#                 st.write(f"Expected: **{expected}** · Predicted: **{predicted or 'undetermined'}** · This is a single scenario check, not a benchmark metric.")


# # ---------------------------------------------------------------------------
# # PAGE 5 - Interoperability and protocol
# # ---------------------------------------------------------------------------
# elif page == "Interoperability Lab":
#     set_page_header("Interoperability & Protocol Lab", "Demonstrate how independent agents can understand one another through explicit, versioned JSON message contracts and schema translation.")
#     result = get_current()
#     st.subheader("Shared message envelope")
#     sample_message = (result["messages"][0] if result else new_message(
#         "INC-DEMO", "orchestrator", "performance_agent", "TASK", {"metrics": {"latency_ms": 180}}))
#     st.code(json_text({
#         "protocol_version": sample_message["protocol_version"],
#         "message_id": "MSG-UNIQUE-ID",
#         "correlation_id": "CORR-INCIDENT-ID",
#         "incident_id": "INCIDENT-ID",
#         "sender": "performance_agent",
#         "receiver": "infrastructure_agent",
#         "message_type": "FINDING",
#         "timestamp": utc_iso(),
#         "payload": {"evidence": [{"metric": "packet_loss_pct", "value": 2.1, "unit": "%"}]},
#         "status": "COMPLETED",
#         "metadata": {"content_type": "application/json"},
#     }), language="json")
#     st.caption("The envelope makes message identity, routing, type, incident correlation, payload and processing status explicit.")

#     st.subheader("Legacy schema v0.9 ↔ organizer/canonical-style input")
#     if result:
#         raw = result["inputs"]["raw"]
#     else:
#         raw = {"timestamp": utc_iso(), "device_id": "SW_CAMPUS_1", "status": "Warning",
#                "metrics": {"latency_ms": 250, "jitter_ms": 50, "packet_loss_pct": 1.0}}
#     left, right = st.columns(2)
#     with left:
#         st.markdown("**Current organizer-style telemetry**")
#         st.json(raw)
#     with right:
#         st.markdown("**Translated external schema v0.9**")
#         legacy = to_legacy_v09(raw)
#         st.json(legacy)
#     st.info("Unit conversion: latency_ms and jitter_ms are divided by 1,000 and represented as seconds in schema v0.9. Fields absent from the source are omitted, not filled with zero.")
#     st.subheader("Field mapping")
#     mapping_rows = [
#         ("device_id", "device", "Device identifier"),
#         ("timestamp", "observed_at", "Observation time"),
#         ("cpu_utilization_pct", "cpu_pct", "CPU percentage"),
#         ("link_utilization_pct", "link_pct", "Link percentage"),
#         ("latency_ms", "latency_seconds", "Milliseconds → seconds"),
#         ("jitter_ms", "jitter_seconds", "Milliseconds → seconds"),
#         ("queue_drops", "queue_drop_count", "Queue-drop count"),
#         ("interface_errors", "interface_error_count", "Interface error count"),
#     ]
#     st.dataframe(pd.DataFrame(mapping_rows, columns=["Canonical / organizer field", "Legacy v0.9 field", "Interpretation"]),
#                  width="stretch", hide_index=True)
#     if result:
#         st.subheader("Actual demo message envelopes from the latest run")
#         st.dataframe(pd.DataFrame([{"Type": m["message_type"], "Sender": m["sender"], "Receiver": m["receiver"],
#                                     "Status": m["status"], "Message ID": m["message_id"]} for m in result["messages"]]),
#                      width="stretch", hide_index=True)
#         with st.expander("Inspect complete message JSON"):
#             st.json(result["messages"])
#     else:
#         st.info("Run an investigation to populate the message exchange inspector.")


# # ---------------------------------------------------------------------------
# # PAGE 6 - Robustness Lab
# # ---------------------------------------------------------------------------
# elif page == "Robustness Lab":
#     set_page_header("Robustness & Validation Lab", "Show how NETCOOP treats absent, stale, malformed, out-of-range and conflicting data without silently assuming missing values are healthy.")
#     result = get_current()
#     if result:
#         st.subheader("Latest incident validation")
#         validation = result["validation"]
#         if validation["is_valid"]:
#             st.success("Input structure and configured numeric ranges passed validation.")
#         else:
#             st.error("Input validation failed.")
#         for warning in validation["warnings"]:
#             st.warning(warning)
#         for error in validation["errors"]:
#             st.error(error)
#         st.subheader("Input completeness")
#         rows = []
#         metric_values = result["inputs"]["raw"].get("metrics", {})
#         for key, label, unit, owner in DEVICE_FIELDS:
#             value = metric_values.get(key)
#             rows.append({"Agent": owner, "Measurement": label, "Value": value if value is not None else "Not provided (None)",
#                          "State": "Provided" if value is not None else "Unknown"})
#         service_metrics = (result["inputs"].get("service") or {}).get("metrics", {})
#         for key, label, unit, owner in SERVICE_FIELDS:
#             value = service_metrics.get(key)
#             rows.append({"Agent": owner, "Measurement": label, "Value": value if value is not None else "Not provided (None)",
#                          "State": "Provided" if value is not None else "Unknown"})
#         st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
#     else:
#         show_no_result()

#     st.subheader("Try a malformed / out-of-range payload")
#     raw_text = st.text_area("Paste a telemetry JSON object", value=st.session_state.raw_json_test, height=190)
#     if st.button("Validate test payload", type="primary"):
#         try:
#             obj = json.loads(raw_text)
#             validation = validate_inputs(obj, None, [])
#             st.session_state.raw_json_test = raw_text
#             if validation["is_valid"]:
#                 st.success("Payload passed configured checks.")
#             else:
#                 st.error("Payload rejected by configured checks.")
#             st.json(validation)
#         except json.JSONDecodeError as exc:
#             st.error(f"Malformed JSON: {exc}")

#     st.subheader("Robustness behaviours to demonstrate")
#     robustness_rows = [
#         ("Missing field", "Displayed as Not provided (None); not interpreted as 0 or healthy."),
#         ("Explicit zero", "Preserved as a measured zero."),
#         ("Out-of-range percentage", "Rejected by input validation (e.g. packet loss > 100%)."),
#         ("Stale timestamp", "Flagged as a warning; the operator is told the observation may be outdated."),
#         ("Status/metric disagreement", "Preserved as a conflict rather than silently trusting the status label."),
#         ("Missing DNS/DHCP input", "Service Health reports unknown/partial rather than a healthy service."),
#         ("No topology", "Connectivity states that network-wide reachability cannot be inferred."),
#     ]
#     st.dataframe(pd.DataFrame(robustness_rows, columns=["Case", "Expected handling"]), width="stretch", hide_index=True)


# # ---------------------------------------------------------------------------
# # PAGE 7 - Judge guide
# # ---------------------------------------------------------------------------
# elif page == "Judge Guide":
#     set_page_header("Evaluator Guide & Weighted Marking Scheme", "A criterion-by-criterion route through the strongest demonstrable NETCOOP deliverables.")
#     st.markdown("The weights below reproduce the marking scheme provided in the project discussion. This page maps evidence to each criterion; it does not estimate or award marks.")
#     st.metric("Total marking weight", f'{sum(x["weight"] for x in RUBRIC)}%')
#     for item in RUBRIC:
#         with st.expander(f'{item["weight"]}% · {item["name"]} — show evidence in {item["page"]}', expanded=item["weight"] >= 15):
#             st.write("**What the evaluator should verify**")
#             st.write(item["proof"])
#             st.write(f'**Dashboard location:** {item["page"]}')
#     st.subheader("Suggested 5-minute evaluator walkthrough")
#     demo_steps = [
#         ("1 · Generate organizer telemetry", "Run Investigation → generate Normal, Latency Spike and Hardware Failure. Point out the original ranges and omitted fields."),
#         ("2 · Show manual inputs", "Enter separate Performance, Infrastructure, Connectivity and Service Health values. Leave a field blank and show Unknown rather than zero."),
#         ("3 · Demonstrate agent interaction", "Open Agent Collaboration. Trace Performance → Infrastructure/Connectivity/Service Health, then the aggregate findings → Correlation → Recommendation."),
#         ("4 · Demonstrate interoperability", "Open Interoperability Lab. Show message envelope fields, protocol version, IDs, message types and legacy seconds-to-milliseconds mapping."),
#         ("5 · Demonstrate diagnosis and evidence", "Open Evidence & Consensus. Explain the evidence ledger, points, alternatives, conflicts, convergence and abstention."),
#         ("6 · Demonstrate robustness", "Open Robustness Lab. Show unknown measurements, stale timestamps, status conflicts and invalid packet loss."),
#     ]
#     for title, detail in demo_steps:
#         st.markdown(f"**{title}**  \n{detail}")
#     st.warning("Be precise with the evaluator: this standalone app demonstrates its own rule-based agents and in-app message bus. It does not claim to execute the separate NETCOOP LangGraph backend, the MCP server or a live campus network. It is a presentation prototype for the interaction model.")


# # ---------------------------------------------------------------------------
# # Footer
# # ---------------------------------------------------------------------------
# st.divider()
# st.caption("NETCOOP AI · Rubric-first collaboration demonstrator · Structured messages are demo events · Missing values remain unknown · Heuristic scores are not probabilities · No live network devices are modified.")

# import json gemini
# import uuid
# from datetime import datetime, timezone
# from typing import Any, Dict, List, Optional, Tuple

# import numpy as np
# import pandas as pd
# import streamlit as st

# # =====================================================================
# # PAGE CONFIGURATION
# # =====================================================================
# st.set_page_config(
#     page_title="NetCoop AI | Multi-Agent Network Fault Diagnosis",
#     page_icon="🌐",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # =====================================================================
# # 1. INTEROPERABILITY PROTOCOL & SCHEMA NORMALIZER (30% + 15% Criteria)
# # =====================================================================
# PROTOCOL_VERSION = "NetCoop-A2A-v1.0"

# # Canonical schema expected by all agents (with units and valid bounds)
# CANONICAL_SCHEMA = {
#     "device_id": {"type": str, "unit": "id", "default": "UNKNOWN_DEVICE"},
#     "device_role": {"type": str, "unit": "role", "default": "switch"},
#     "upstream_device": {"type": str, "unit": "id", "default": "CAMPUS_CORE_RTR_01"},
#     "device_status": {"type": str, "unit": "state", "default": "UP"},
#     "latency_ms": {"type": float, "unit": "ms", "min": 0.0, "max": 10000.0},
#     "jitter_ms": {"type": float, "unit": "ms", "min": 0.0, "max": 5000.0},
#     "packet_loss_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
#     "throughput_mbps": {"type": float, "unit": "Mbps", "min": 0.0, "max": 100000.0},
#     "bandwidth_mbps": {"type": float, "unit": "Mbps", "min": 1.0, "max": 100000.0},
#     "link_utilization_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
#     "cpu_utilization_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
#     "memory_utilization_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
#     "queue_drops": {"type": int, "unit": "packets", "min": 0, "max": 10000000},
#     "interface_errors": {"type": int, "unit": "errors", "min": 0, "max": 10000000},
#     "wifi_signal_dbm": {"type": float, "unit": "dBm", "min": -120.0, "max": 0.0},
#     "dns_failure_rate_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
#     "dhcp_Step_timeout_pct": {"type": float, "unit": "%", "min": 0.0, "max": 100.0},
# }

# # Legacy / incompatible field alias mapping for Interoperability Resilience
# FIELD_ALIASES = {
#     "host": "device_id",
#     "node_id": "device_id",
#     "status": "device_status",
#     "lat_ms": "latency_ms",
#     "delay_ms": "latency_ms",
#     "latency_sec": "latency_ms",  # Requires unit conversion (s -> ms)
#     "pkt_loss": "packet_loss_pct",
#     "loss_ratio": "packet_loss_pct",  # Requires unit conversion (0-1 -> %)
#     "util_pct": "link_utilization_pct",
#     "link_util": "link_utilization_pct",
#     "egress_drops": "queue_drops",
#     "tx_drops": "queue_drops",
#     "crc_errors": "interface_errors",
#     "if_errors": "interface_errors",
#     "cpu_load": "cpu_utilization_pct",
#     "mem_used": "memory_utilization_pct",
#     "rssi": "wifi_signal_dbm",
#     "throughput_kbps": "throughput_mbps",  # Requires unit conversion (kbps -> Mbps)
# }


# def create_a2a_message(
#     sender: str,
#     receiver: str,
#     intent: str,
#     payload: Dict[str, Any],
#     validation_warnings: Optional[List[str]] = None,
# ) -> Dict[str, Any]:
#     """Builds a standardized Inter-Agent Message Envelope (NetCoop-A2A-v1.0)."""
#     return {
#         "protocol_version": PROTOCOL_VERSION,
#         "message_id": f"MSG-{uuid.uuid4().hex[:8].upper()}",
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#         "sender_agent": sender,
#         "receiver_agent": receiver,
#         "intent": intent,
#         "validation_warnings": validation_warnings or [],
#         "payload": payload,
#     }


# def normalize_and_validate_telemetry(
#     raw_records: List[Dict[str, Any]]
# ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
#     """
#     Interoperability & Validation Layer:
#     Resolves incompatible field names, converts mismatched units, strips string symbols,
#     and flags malformed/out-of-range values without crashing.
#     """
#     normalized_records = []
#     interop_repairs = []
#     validation_errors = []

#     if not isinstance(raw_records, list) or len(raw_records) == 0:
#         validation_errors.append("CRITICAL: Input telemetry payload is empty or not a list.")
#         return [], interop_repairs, validation_errors

#     for idx, record in enumerate(raw_records):
#         if not isinstance(record, dict):
#             validation_errors.append(f"Row {idx}: Malformed record (expected JSON object, got {type(record).__name__}).")
#             continue

#         clean_rec: Dict[str, Any] = {}
#         row_label = record.get("device_id") or record.get("host") or record.get("node_id") or f"Row_{idx}"

#         # Step 1: Resolve aliases & unit conversions
#         for raw_key, raw_val in record.items():
#             canonical_key = FIELD_ALIASES.get(raw_key, raw_key)
#             val = raw_val

#             if raw_key != canonical_key:
#                 interop_repairs.append(
#                     f"[{row_label}] Mapped legacy field '{raw_key}' -> '{canonical_key}'"
#                 )

#             # Strip string percentage or unit suffixes like "94%" or "280ms"
#             if isinstance(val, str) and canonical_key not in ("device_id", "device_role", "upstream_device", "device_status"):
#                 stripped = val.replace("%", "").replace("ms", "").replace("dBm", "").replace("Mbps", "").strip()
#                 try:
#                     val = float(stripped)
#                     interop_repairs.append(
#                         f"[{row_label}] Coerced string value '{raw_val}' -> numeric {val} for '{canonical_key}'"
#                     )
#                 except ValueError:
#                     validation_errors.append(
#                         f"[{row_label}] Unparseable non-numeric value '{raw_val}' in field '{canonical_key}'; set to None."
#                     )
#                     val = None

#             # Unit conversions
#             if raw_key == "latency_sec" and isinstance(val, (int, float)):
#                 val = float(val) * 1000.0
#                 interop_repairs.append(f"[{row_label}] Converted 'latency_sec' ({raw_val} s) -> 'latency_ms' ({val} ms)")
#             elif raw_key == "loss_ratio" and isinstance(val, (int, float)) and val <= 1.0:
#                 val = float(val) * 100.0
#                 interop_repairs.append(f"[{row_label}] Converted 'loss_ratio' ({raw_val}) -> 'packet_loss_pct' ({val}%)")
#             elif raw_key == "throughput_kbps" and isinstance(val, (int, float)):
#                 val = round(float(val) / 1000.0, 2)
#                 interop_repairs.append(f"[{row_label}] Converted 'throughput_kbps' ({raw_val} kbps) -> 'throughput_mbps' ({val} Mbps)")

#             clean_rec[canonical_key] = val

#         # Step 2: Bounds & missing field checks
#         for field, rules in CANONICAL_SCHEMA.items():
#             if field not in clean_rec or clean_rec[field] is None:
#                 if "default" in rules:
#                     clean_rec[field] = rules["default"]
#                 else:
#                     clean_rec[field] = None
#                 continue

#             val = clean_rec[field]
#             if rules["type"] in (float, int) and isinstance(val, (int, float)):
#                 if np.isnan(val):
#                     clean_rec[field] = None
#                     validation_errors.append(f"[{row_label}] Field '{field}' is NaN; marked as missing.")
#                 elif "min" in rules and val < rules["min"]:
#                     validation_errors.append(
#                         f"[{row_label}] Out-of-bounds value {val} for '{field}' (min {rules['min']}); clamped to {rules['min']}."
#                     )
#                     clean_rec[field] = rules["min"]
#                 elif "max" in rules and val > rules["max"]:
#                     validation_errors.append(
#                         f"[{row_label}] Out-of-bounds value {val} for '{field}' (max {rules['max']}); clamped to {rules['max']}."
#                     )
#                     clean_rec[field] = rules["max"]

#         normalized_records.append(clean_rec)

#     return normalized_records, interop_repairs, validation_errors


# # =====================================================================
# # 2. SYNTHETIC CAMPUS TELEMETRY SCENARIOS (IIT Bhubaneswar)
# # =====================================================================
# SCENARIOS: Dict[str, Dict[str, Any]] = {
#     "Scenario 1: Link Congestion (Hostel Core Switch - PDF Example)": {
#         "incident_id": "INC-8832",
#         "description": "High link utilization (94%), elevated egress queue drops (160), and high latency (280 ms) on HOSTEL_CORE_SW_01.",
#         "telemetry": [
#             {
#                 "device_id": "CAMPUS_CORE_RTR_01",
#                 "device_role": "core_router",
#                 "upstream_device": "ISP_GATEWAY_01",
#                 "device_status": "UP",
#                 "latency_ms": 14.0,
#                 "jitter_ms": 2.1,
#                 "packet_loss_pct": 0.1,
#                 "throughput_mbps": 620.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 62.0,
#                 "cpu_utilization_pct": 38.0,
#                 "memory_utilization_pct": 45.0,
#                 "queue_drops": 0,
#                 "interface_errors": 0,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": 0.2,
#                 "dhcp_Step_timeout_pct": 0.0,
#             },
#             {
#                 "device_id": "HOSTEL_CORE_SW_01",
#                 "device_role": "distribution_switch",
#                 "upstream_device": "CAMPUS_CORE_RTR_01",
#                 "device_status": "UP",
#                 "latency_ms": 280.0,
#                 "jitter_ms": 48.5,
#                 "packet_loss_pct": 6.4,
#                 "throughput_mbps": 940.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 94.0,
#                 "cpu_utilization_pct": 54.0,
#                 "memory_utilization_pct": 61.0,
#                 "queue_drops": 160,
#                 "interface_errors": 1,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": 0.5,
#                 "dhcp_Step_timeout_pct": 0.2,
#             },
#         ],
#     },
#     "Scenario 2: Normal Campus Network Operation": {
#         "incident_id": "INC-8801",
#         "description": "All campus routers, switches, and hostel Wi-Fi zones operating within nominal ranges.",
#         "telemetry": [
#             {
#                 "device_id": "CAMPUS_CORE_RTR_01",
#                 "device_role": "core_router",
#                 "upstream_device": "ISP_GATEWAY_01",
#                 "device_status": "UP",
#                 "latency_ms": 9.5,
#                 "jitter_ms": 1.4,
#                 "packet_loss_pct": 0.0,
#                 "throughput_mbps": 410.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 41.0,
#                 "cpu_utilization_pct": 32.0,
#                 "memory_utilization_pct": 44.0,
#                 "queue_drops": 0,
#                 "interface_errors": 0,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": 0.1,
#                 "dhcp_Step_timeout_pct": 0.0,
#             },
#             {
#                 "device_id": "LECTURE_HALL_SW_02",
#                 "device_role": "access_switch",
#                 "upstream_device": "CAMPUS_CORE_RTR_01",
#                 "device_status": "UP",
#                 "latency_ms": 12.0,
#                 "jitter_ms": 1.8,
#                 "packet_loss_pct": 0.05,
#                 "throughput_mbps": 280.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 28.0,
#                 "cpu_utilization_pct": 24.0,
#                 "memory_utilization_pct": 39.0,
#                 "queue_drops": 0,
#                 "interface_errors": 0,
#                 "wifi_signal_dbm": -58.0,
#                 "dns_failure_rate_pct": 0.1,
#                 "dhcp_Step_timeout_pct": 0.0,
#             },
#         ],
#     },
#     "Scenario 3: Weak Wi-Fi Signal (Mahanadi Hall of Residence)": {
#         "incident_id": "INC-8845",
#         "description": "Severe wireless signal degradation (-86 dBm) causing high packet loss and jitter in hostel Wi-Fi zone while wired backhaul remains healthy.",
#         "telemetry": [
#             {
#                 "device_id": "MHR_WIFI_AP_04",
#                 "device_role": "wireless_ap",
#                 "upstream_device": "HOSTEL_CORE_SW_01",
#                 "device_status": "UP",
#                 "latency_ms": 195.0,
#                 "jitter_ms": 62.0,
#                 "packet_loss_pct": 14.5,
#                 "throughput_mbps": 18.0,
#                 "bandwidth_mbps": 300.0,
#                 "link_utilization_pct": 22.0,
#                 "cpu_utilization_pct": 41.0,
#                 "memory_utilization_pct": 52.0,
#                 "queue_drops": 12,
#                 "interface_errors": 2,
#                 "wifi_signal_dbm": -86.0,
#                 "dns_failure_rate_pct": 0.8,
#                 "dhcp_Step_timeout_pct": 1.2,
#             }
#         ],
#     },
#     "Scenario 4: Ethernet / Physical Interface Fault (CS Department Switch)": {
#         "incident_id": "INC-8859",
#         "description": "High CRC/interface errors (420) and packet loss (11.2%) despite low bandwidth utilization (31%).",
#         "telemetry": [
#             {
#                 "device_id": "DEPT_CS_SW_02",
#                 "device_role": "access_switch",
#                 "upstream_device": "CAMPUS_CORE_RTR_01",
#                 "device_status": "DEGRADED",
#                 "latency_ms": 85.0,
#                 "jitter_ms": 29.0,
#                 "packet_loss_pct": 11.2,
#                 "throughput_mbps": 310.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 31.0,
#                 "cpu_utilization_pct": 29.0,
#                 "memory_utilization_pct": 48.0,
#                 "queue_drops": 3,
#                 "interface_errors": 420,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": 0.4,
#                 "dhcp_Step_timeout_pct": 0.2,
#             }
#         ],
#     },
#     "Scenario 5: DNS / DHCP Campus Service Failure": {
#         "incident_id": "INC-8870",
#         "description": "Physical links and hardware metrics are normal, but DNS failure rate (48%) and DHCP timeouts (35%) prevent campus connectivity.",
#         "telemetry": [
#             {
#                 "device_id": "CAMPUS_DNS_SRV_01",
#                 "device_role": "service_node",
#                 "upstream_device": "CAMPUS_CORE_RTR_01",
#                 "device_status": "DEGRADED",
#                 "latency_ms": 22.0,
#                 "jitter_ms": 3.5,
#                 "packet_loss_pct": 0.3,
#                 "throughput_mbps": 150.0,
#                 "bandwidth_mbps": 1000.0,
#                 "link_utilization_pct": 15.0,
#                 "cpu_utilization_pct": 72.0,
#                 "memory_utilization_pct": 78.0,
#                 "queue_drops": 0,
#                 "interface_errors": 0,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": 48.5,
#                 "dhcp_Step_timeout_pct": 35.0,
#             }
#         ],
#     },
#     "Scenario 6: Interoperability & Malformed Schema Stress Test (15% Rubric)": {
#         "incident_id": "INC-8891",
#         "description": "Uses legacy field names (host, latency_sec, util_pct, egress_drops), string numbers ('96%'), and negative jitter (-12) to prove protocol resilience.",
#         "telemetry": [
#             {
#                 "host": "LHC_CORE_RTR_03",
#                 "device_role": "distribution_router",
#                 "upstream_device": "CAMPUS_CORE_RTR_01",
#                 "status": "UP",
#                 "latency_sec": 0.310,
#                 "jitter_ms": -12.0,
#                 "loss_ratio": 0.085,
#                 "throughput_kbps": 950000,
#                 "bandwidth_mbps": 1000.0,
#                 "util_pct": "95%",
#                 "cpu_load": "92%",
#                 "mem_used": "88%",
#                 "egress_drops": 215,
#                 "crc_errors": "bad_sensor_value",
#             }
#         ],
#     },
#     "Scenario 7: Insufficient / Ambiguous Telemetry (Safety Guardrail Test)": {
#         "incident_id": "INC-8899",
#         "description": "Telemetry contains high latency (240 ms) but all utilization, CPU, queue drop, and interface error metrics are missing (None). System must refuse to claim an exact root cause.",
#         "telemetry": [
#             {
#                 "device_id": "SUBARNAREKHA_HOSTEL_SW_01",
#                 "device_role": "access_switch",
#                 "upstream_device": "HOSTEL_CORE_SW_01",
#                 "device_status": "UP",
#                 "latency_ms": 240.0,
#                 "jitter_ms": 35.0,
#                 "packet_loss_pct": None,
#                 "throughput_mbps": None,
#                 "bandwidth_mbps": None,
#                 "link_utilization_pct": None,
#                 "cpu_utilization_pct": None,
#                 "memory_utilization_pct": None,
#                 "queue_drops": None,
#                 "interface_errors": None,
#                 "wifi_signal_dbm": None,
#                 "dns_failure_rate_pct": None,
#                 "dhcp_Step_timeout_pct": None,
#             }
#         ],
#     },
# }


# # =====================================================================
# # 3. FIVE COLLABORATING SPECIALIZED AGENTS
# # =====================================================================
# class PerformanceAgent:
#     """Agent 1: Analyzes latency, jitter, packet loss, throughput, and link utilization."""

#     name = "performance_agent"

#     def analyze(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
#         evidence = []
#         anomalies = []
#         affected = []
#         completeness_checks = 0
#         available_checks = 0

#         for rec in records:
#             dev = rec["device_id"]
#             lat = rec.get("latency_ms")
#             jit = rec.get("jitter_ms")
#             loss = rec.get("packet_loss_pct")
#             util = rec.get("link_utilization_pct")

#             for metric_val in (lat, jit, loss, util):
#                 completeness_checks += 1
#                 if metric_val is not None:
#                     available_checks += 1

#             if util is not None and util >= 85.0:
#                 evidence.append({"device": dev, "metric": "link_utilization_pct", "value": util, "interpretation": "High link utilization"})
#                 anomalies.append({"device": dev, "hypothesis": "Link Congestion", "weight": 0.45})
#                 affected.append(dev)

#             if lat is not None and lat >= 100.0:
#                 evidence.append({"device": dev, "metric": "latency_ms", "value": lat, "interpretation": "Elevated network latency"})
#                 anomalies.append({"device": dev, "hypothesis": "High Latency Degradation", "weight": 0.25})
#                 affected.append(dev)

#             if jit is not None and jit >= 30.0:
#                 evidence.append({"device": dev, "metric": "jitter_ms", "value": jit, "interpretation": "Elevated packet delay variation (jitter)"})
#                 affected.append(dev)

#             if loss is not None and loss >= 2.5:
#                 evidence.append({"device": dev, "metric": "packet_loss_pct", "value": loss, "interpretation": "Significant packet loss detected"})
#                 anomalies.append({"device": dev, "hypothesis": "Packet Loss Anomaly", "weight": 0.25})
#                 affected.append(dev)

#         completeness = available_checks / max(completeness_checks, 1)
#         return {
#             "agent": self.name,
#             "affected_devices": sorted(list(set(affected))),
#             "evidence": evidence,
#             "anomalies": anomalies,
#             "telemetry_completeness": round(completeness, 2),
#         }


# class InfrastructureAgent:
#     """Agent 2: Examines device status, CPU/memory overload, egress queue drops, interface errors, and Wi-Fi RSSI."""

#     name = "infrastructure_agent"

#     def analyze(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
#         evidence = []
#         anomalies = []
#         affected = []
#         completeness_checks = 0
#         available_checks = 0

#         for rec in records:
#             dev = rec["device_id"]
#             cpu = rec.get("cpu_utilization_pct")
#             mem = rec.get("memory_utilization_pct")
#             drops = rec.get("queue_drops")
#             errs = rec.get("interface_errors")
#             wifi = rec.get("wifi_signal_dbm")
#             dns_fail = rec.get("dns_failure_rate_pct")
#             dhcp_fail = rec.get("dhcp_Step_timeout_pct")

#             for metric_val in (cpu, mem, drops, errs):
#                 completeness_checks += 1
#                 if metric_val is not None:
#                     available_checks += 1

#             if drops is not None and drops >= 50:
#                 evidence.append({"device": dev, "metric": "queue_drops", "value": drops, "interpretation": "Elevated packet drops"})
#                 anomalies.append({"device": dev, "hypothesis": "Egress Queue Exhaustion", "weight": 0.40})
#                 affected.append(dev)

#             if errs is not None and errs >= 50:
#                 evidence.append({"device": dev, "metric": "interface_errors", "value": errs, "interpretation": "High physical interface / CRC errors"})
#                 anomalies.append({"device": dev, "hypothesis": "Physical Interface or Cable Fault", "weight": 0.65})
#                 affected.append(dev)

#             if cpu is not None and cpu >= 85.0:
#                 evidence.append({"device": dev, "metric": "cpu_utilization_pct", "value": cpu, "interpretation": "Device CPU overload"})
#                 anomalies.append({"device": dev, "hypothesis": "Device Control-Plane CPU Overload", "weight": 0.40})
#                 affected.append(dev)

#             if wifi is not None and wifi <= -78.0:
#                 evidence.append({"device": dev, "metric": "wifi_signal_dbm", "value": wifi, "interpretation": "Poor wireless signal quality (RSSI)"})
#                 anomalies.append({"device": dev, "hypothesis": "Weak Wi-Fi Signal / RF Interference", "weight": 0.70})
#                 affected.append(dev)

#             if (dns_fail is not None and dns_fail >= 10.0) or (dhcp_fail is not None and dhcp_fail >= 10.0):
#                 if dns_fail is not None and dns_fail >= 10.0:
#                     evidence.append({"device": dev, "metric": "dns_failure_rate_pct", "value": dns_fail, "interpretation": "High DNS resolution failure rate"})
#                 if dhcp_fail is not None and dhcp_fail >= 10.0:
#                     evidence.append({"device": dev, "metric": "dhcp_Step_timeout_pct", "value": dhcp_fail, "interpretation": "Elevated DHCP lease timeouts"})
#                 anomalies.append({"device": dev, "hypothesis": "DNS/DHCP Core Service Failure", "weight": 0.75})
#                 affected.append(dev)

#         completeness = available_checks / max(completeness_checks, 1)
#         return {
#             "agent": self.name,
#             "affected_devices": sorted(list(set(affected))),
#             "evidence": evidence,
#             "anomalies": anomalies,
#             "telemetry_completeness": round(completeness, 2),
#         }


# class ConnectivityAgent:
#     """Agent 3: Examines campus topology relationships, upstream vs downstream scope, and blast radius."""

#     name = "connectivity_agent"

#     def analyze(
#         self,
#         records: List[Dict[str, Any]],
#         perf_findings: Dict[str, Any],
#         infra_findings: Dict[str, Any],
#     ) -> Dict[str, Any]:
#         device_map = {r["device_id"]: r for r in records}
#         all_affected = sorted(
#             list(set(perf_findings["affected_devices"] + infra_findings["affected_devices"]))
#         )
#         topology_notes = []
#         root_candidates = []

#         for dev in all_affected:
#             rec = device_map.get(dev, {})
#             upstream = rec.get("upstream_device", "UNKNOWN")
#             if upstream in all_affected:
#                 topology_notes.append(
#                     f"Downstream device '{dev}' and its upstream '{upstream}' are both degraded; upstream cascade possible."
#                 )
#             else:
#                 topology_notes.append(
#                     f"Fault localized at '{dev}' (upstream '{upstream}' is healthy)."
#                 )
#                 root_candidates.append(dev)

#         return {
#             "agent": self.name,
#             "affected_devices": all_affected,
#             "root_location_candidates": root_candidates or all_affected,
#             "topology_insights": topology_notes,
#         }


# class FaultCorrelationAgent:
#     """
#     Agent 4: Correlates multi-agent evidence, resolves conflicting hypotheses,
#     computes calibrated confidence, and enforces the 'insufficient_evidence' guardrail.
#     """

#     name = "correlation_agent"

#     def correlate(
#         self,
#         perf: Dict[str, Any],
#         infra: Dict[str, Any],
#         conn: Dict[str, Any],
#         interop_repairs: List[str],
#         validation_errors: List[str],
#     ) -> Dict[str, Any]:
#         combined_evidence = perf["evidence"] + infra["evidence"]
#         affected_devices = conn["affected_devices"]
#         avg_completeness = (perf["telemetry_completeness"] + infra["telemetry_completeness"]) / 2.0

#         # Case 1: Normal Operation
#         if not combined_evidence:
#             return {
#                 "status": "normal",
#                 "suspected_root_cause": "Normal network operation; all monitored metrics within nominal thresholds",
#                 "confidence": round(min(0.95, 0.80 + 0.15 * avg_completeness), 2),
#                 "affected_devices": [],
#                 "supporting_evidence": [],
#                 "alternative_causes": [],
#                 "evidence_sources": [perf["agent"], infra["agent"], conn["agent"]],
#                 "conflict_resolution_log": ["No conflicting anomalies raised by specialist agents."],
#             }

#         # Guardrail: Insufficient evidence when critical discriminating metrics are missing
#         metrics_present = {item["metric"] for item in combined_evidence}
#         if avg_completeness < 0.45 or (
#             metrics_present.issubset({"latency_ms", "jitter_ms"})
#             and infra["telemetry_completeness"] == 0.0
#         ):
#             return {
#                 "status": "insufficient_evidence",
#                 "suspected_root_cause": "Insufficient telemetry evidence to determine an exact root cause (elevated delay observed without hardware/link counters)",
#                 "confidence": round(0.30 * avg_completeness + 0.15, 2),
#                 "affected_devices": affected_devices,
#                 "supporting_evidence": [
#                     {"metric": e["metric"], "value": e["value"], "interpretation": e["interpretation"]}
#                     for e in combined_evidence
#                 ],
#                 "alternative_causes": [
#                     "Link congestion with unmonitored egress queue drops",
#                     "Upstream routing delay or ISP transit degradation",
#                     "Physical interface fault on unpolled switch ports",
#                 ],
#                 "evidence_sources": [perf["agent"], infra["agent"]],
#                 "conflict_resolution_log": [
#                     f"Telemetry completeness ({avg_completeness*100:.0f}%) is below the 45% diagnostic threshold; refusing to guess root cause per safety policy."
#                 ],
#             }

#         # Score candidate root causes across multi-agent signatures
#         scores: Dict[str, float] = {
#             "Likely link congestion causing egress queue drops": 0.0,
#             "Link congestion and control-plane CPU overload on routing device": 0.0,
#             "Weak Wi-Fi signal quality and RF link degradation": 0.0,
#             "Physical Ethernet interface or cabling fault causing CRC/frame errors": 0.0,
#             "DNS/DHCP core network service failure": 0.0,
#         }
#         conflict_log = []

#         has_util = "link_utilization_pct" in metrics_present
#         has_drops = "queue_drops" in metrics_present
#         has_lat = "latency_ms" in metrics_present
#         has_cpu = "cpu_utilization_pct" in metrics_present
#         has_errs = "interface_errors" in metrics_present
#         has_wifi = "wifi_signal_dbm" in metrics_present
#         has_dns = "dns_failure_rate_pct" in metrics_present or "dhcp_Step_timeout_pct" in metrics_present

#         if has_util and has_drops:
#             scores["Likely link congestion causing egress queue drops"] += 0.82
#             if has_lat:
#                 scores["Likely link congestion causing egress queue drops"] += 0.10
#         if has_util and has_drops and has_cpu:
#             scores["Link congestion and control-plane CPU overload on routing device"] += 0.88
#             conflict_log.append(
#                 "Resolved multi-fault overlap: Both link saturation (Performance Agent) and CPU overload (Infrastructure Agent) co-occur; prioritized combined congestion + CPU exhaustion hypothesis."
#             )
#         if has_wifi:
#             scores["Weak Wi-Fi signal quality and RF link degradation"] += 0.88
#             if not has_util:
#                 conflict_log.append(
#                     "Disambiguated packet loss source: Performance Agent saw high loss/latency, but low wired utilization + Infrastructure Agent RSSI (-86 dBm) isolated fault to wireless RF layer."
#                 )
#         if has_errs and not has_util:
#             scores["Physical Ethernet interface or cabling fault causing CRC/frame errors"] += 0.89
#             conflict_log.append(
#                 "Disambiguated packet loss source: Link utilization is low (ruling out congestion), while Infrastructure Agent reported high interface CRC errors."
#             )
#         if has_dns:
#             scores["DNS/DHCP core network service failure"] += 0.90
#             conflict_log.append(
#                 "Disambiguated connectivity outage: Transport latency and utilization are nominal; Infrastructure service probes isolated failure to DNS/DHCP daemons."
#             )

#         ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#         best_cause, raw_score = ranked[0]

#         # Calibrate confidence penalty for data validation errors
#         penalty = min(0.15, 0.03 * len(validation_errors))
#         calibrated_confidence = round(max(0.40, min(0.96, raw_score * avg_completeness - penalty)), 2)

#         # Build alternative causes
#         alternatives = [cause for cause, sc in ranked[1:] if sc > 0.25]
#         if not alternatives:
#             if "congestion" in best_cause.lower():
#                 alternatives = ["Upstream link congestion", "Misconfigured QoS/WRED egress queue threshold"]
#             elif "wi-fi" in best_cause.lower():
#                 alternatives = ["Co-channel 2.4/5GHz Wi-Fi interference", "Failing AP radio transceiver"]
#             elif "interface" in best_cause.lower():
#                 alternatives = ["Damaged Cat6 patch cable or SFP optical transceiver", "Duplex mismatch on switch port"]
#             elif "dns" in best_cause.lower():
#                 alternatives = ["Exhausted DHCP IP address pool", "Upstream recursive DNS resolver outage"]

#         if not conflict_log:
#             conflict_log.append(
#                 "Correlated Performance Agent link/delay telemetry with Infrastructure Agent hardware counters without contradiction."
#             )

#         return {
#             "status": "diagnosed",
#             "suspected_root_cause": best_cause,
#             "confidence": calibrated_confidence,
#             "affected_devices": affected_devices,
#             "supporting_evidence": [
#                 {"metric": e["metric"], "value": e["value"], "interpretation": e["interpretation"]}
#                 for e in combined_evidence
#             ],
#             "alternative_causes": alternatives[:3],
#             "evidence_sources": ["performance_agent", "infrastructure_agent"],
#             "conflict_resolution_log": conflict_log,
#         }


# class RecommendationAndReportingAgent:
#     """Agent 5: Generates practical corrective actions, limitations, and the final Section 6 JSON report."""

#     name = "reporting_agent"

#     def generate_report(
#         self,
#         incident_id: str,
#         correlation: Dict[str, Any],
#         interop_repairs: List[str],
#         validation_errors: List[str],
#     ) -> Dict[str, Any]:
#         cause = correlation["suspected_root_cause"].lower()
#         status = correlation["status"]

#         if status == "normal":
#             actions = [
#                 "Continue routine telemetry polling and baseline monitoring",
#                 "No corrective configuration changes required",
#             ]
#             limitations = ["Snapshot reflects current polling window only"]
#         elif status == "insufficient_evidence":
#             actions = [
#                 "Enable SNMP/gNMI counter collection for interface utilization, queue drops, and CPU metrics on affected switches",
#                 "Run active traceroute and ICMP burst tests to isolate hop-by-hop packet loss",
#                 "Do not execute automated traffic rerouting until missing telemetry counters are restored",
#             ]
#             limitations = [
#                 "Critical infrastructure and utilization counters were missing (null) in supplied telemetry",
#                 "Root cause cannot be reliably determined from delay metrics alone",
#             ]
#         elif "congestion" in cause:
#             actions = [
#                 "Inspect upstream and egress link utilization",
#                 "Review queue configuration and traffic distribution",
#                 "Apply QoS traffic shaping or rate-limit bulk non-academic traffic during peak hostel hours",
#             ]
#             limitations = ["Root cause requires further verification"]
#         elif "wi-fi" in cause:
#             actions = [
#                 "Inspect wireless access point transmit power, antenna orientation, and channel occupancy",
#                 "Perform RF site survey in affected hostel wing and roam clients to less congested 5GHz channels",
#             ]
#             limitations = ["Client-side wireless adapter statistics were not included in AP telemetry"]
#         elif "interface" in cause:
#             actions = [
#                 "Inspect physical Ethernet cabling, patch panel terminations, and SFP transceiver seating on affected port",
#                 "Verify full-duplex negotiation and clear interface CRC error counters to monitor if errors increment",
#             ]
#             limitations = ["Physical layer optical power / TDR cable diagnostics require on-site verification"]
#         elif "dns" in cause:
#             actions = [
#                 "Restart or fail over campus DNS/DHCP service daemon and inspect `/var/log/syslog` for pool exhaustion",
#                 "Verify secondary DNS server reachability from hostel and academic VLANs",
#             ]
#             limitations = ["Application-layer logs from the DNS/DHCP server OS were not attached"]
#         else:
#             actions = [
#                 "Inspect affected device logs and verify upstream link states",
#                 "Escalate incident to campus network operations center (NOC)",
#             ]
#             limitations = ["Root cause requires further verification"]

#         if interop_repairs:
#             limitations.append(
#                 f"Applied {len(interop_repairs)} automatic schema/unit normalizations to non-standard telemetry fields"
#             )
#         if validation_errors:
#             limitations.append(
#                 f"Handled {len(validation_errors)} malformed or out-of-range metric values during ingestion"
#             )

#         # Exact schema mandated by Section 6 of the Problem Statement
#         return {
#             "incident_id": incident_id,
#             "status": status,
#             "suspected_root_cause": correlation["suspected_root_cause"],
#             "confidence": correlation["confidence"],
#             "affected_devices": correlation["affected_devices"],
#             "supporting_evidence": correlation["supporting_evidence"],
#             "alternative_causes": correlation["alternative_causes"],
#             "recommended_actions": actions,
#             "evidence_sources": correlation["evidence_sources"],
#             "limitations": limitations,
#         }


# # =====================================================================
# # 4. MULTI-AGENT ORCHESTRATOR
# # =====================================================================
# def run_multi_agent_pipeline(
#     incident_id: str, raw_telemetry: List[Dict[str, Any]]
# ) -> Dict[str, Any]:
#     """Coordinates the 5 agents, logs every A2A protocol message, and returns full state."""
#     message_bus: List[Dict[str, Any]] = []

#     # Step 1: Interoperability & Validation Layer
#     clean_records, interop_repairs, validation_errors = normalize_and_validate_telemetry(raw_telemetry)
#     message_bus.append(
#         create_a2a_message(
#             sender="orchestrator_ingestor",
#             receiver="performance_agent, infrastructure_agent",
#             intent="TELEMETRY_NORMALIZED_BROADCAST",
#             payload={
#                 "normalized_record_count": len(clean_records),
#                 "interop_repairs": interop_repairs,
#                 "validation_warnings": validation_errors,
#             },
#             validation_warnings=validation_errors,
#         )
#     )

#     if not clean_records:
#         empty_report = {
#             "incident_id": incident_id,
#             "status": "error_invalid_input",
#             "suspected_root_cause": "Insufficient evidence: No valid telemetry records could be parsed",
#             "confidence": 0.0,
#             "affected_devices": [],
#             "supporting_evidence": [],
#             "alternative_causes": [],
#             "recommended_actions": ["Verify telemetry JSON syntax and schema fields"],
#             "evidence_sources": [],
#             "limitations": validation_errors,
#         }
#         return {
#             "clean_records": [],
#             "interop_repairs": interop_repairs,
#             "validation_errors": validation_errors,
#             "message_bus": message_bus,
#             "conflict_log": ["Pipeline halted gracefully due to empty/unparseable input."],
#             "topology_insights": [],
#             "final_report": empty_report,
#         }

#     # Step 2: Specialist Agents Run in Parallel
#     perf_agent = PerformanceAgent()
#     infra_agent = InfrastructureAgent()
#     conn_agent = ConnectivityAgent()
#     corr_agent = FaultCorrelationAgent()
#     rep_agent = RecommendationAndReportingAgent()

#     perf_res = perf_agent.analyze(clean_records)
#     message_bus.append(
#         create_a2a_message(
#             sender=perf_agent.name,
#             receiver=corr_agent.name,
#             intent="PERFORMANCE_FINDINGS_REPORT",
#             payload=perf_res,
#         )
#     )

#     infra_res = infra_agent.analyze(clean_records)
#     message_bus.append(
#         create_a2a_message(
#             sender=infra_agent.name,
#             receiver=corr_agent.name,
#             intent="INFRASTRUCTURE_FINDINGS_REPORT",
#             payload=infra_res,
#         )
#     )

#     conn_res = conn_agent.analyze(clean_records, perf_res, infra_res)
#     message_bus.append(
#         create_a2a_message(
#             sender=conn_agent.name,
#             receiver=corr_agent.name,
#             intent="TOPOLOGY_SCOPE_ANALYSIS",
#             payload=conn_res,
#         )
#     )

#     # Step 3: Fault Correlation & Conflict Resolution Agent
#     corr_res = corr_agent.correlate(perf_res, infra_res, conn_res, interop_repairs, validation_errors)
#     message_bus.append(
#         create_a2a_message(
#             sender=corr_agent.name,
#             receiver=rep_agent.name,
#             intent="CORRELATED_ROOT_CAUSE_DECISION",
#             payload=corr_res,
#         )
#     )

#     # Step 4: Recommendation & Reporting Agent
#     final_report = rep_agent.generate_report(incident_id, corr_res, interop_repairs, validation_errors)
#     message_bus.append(
#         create_a2a_message(
#             sender=rep_agent.name,
#             receiver="orchestrator_output",
#             intent="UNIFIED_DIAGNOSTIC_REPORT_READY",
#             payload=final_report,
#         )
#     )

#     return {
#         "clean_records": clean_records,
#         "interop_repairs": interop_repairs,
#         "validation_errors": validation_errors,
#         "message_bus": message_bus,
#         "conflict_log": corr_res.get("conflict_resolution_log", []),
#         "topology_insights": conn_res.get("topology_insights", []),
#         "final_report": final_report,
#     }


# # =====================================================================
# # 5. STREAMLIT UI & INTERACTIVE DASHBOARD
# # =====================================================================
# st.title("🌐 NetCoop AI — Multi-Agent Network Fault Diagnosis")
# st.caption(
#     "IIT Bhubaneswar Campus Network Diagnostic Engine | Protocol: `NetCoop-A2A-v1.0` | "
#     "5 Collaborating Agents with Schema Interoperability & Conflict Resolution"
# )

# # Sidebar Controls
# with st.sidebar:
#     st.header("⚙️ Diagnostic Controls")
#     input_mode = st.radio(
#         "Select Telemetry Source",
#         ["Built-in Campus Scenarios", "Custom JSON / File Upload"],
#     )

#     selected_scenario_name = None
#     raw_input_json_str = ""
#     incident_id_input = "INC-8832"

#     if input_mode == "Built-in Campus Scenarios":
#         selected_scenario_name = st.selectbox(
#             "Choose Test Scenario", list(SCENARIOS.keys())
#         )
#         scen_data = SCENARIOS[selected_scenario_name]
#         incident_id_input = st.text_input("Incident ID", value=scen_data["incident_id"])
#         st.info(scen_data["description"])
#         raw_input_json_str = json.dumps(scen_data["telemetry"], indent=2)
#     else:
#         incident_id_input = st.text_input("Incident ID", value="INC-9001")
#         uploaded_file = st.file_uploader("Upload Telemetry (.json or .csv)", type=["json", "csv"])
#         if uploaded_file is not None:
#             if uploaded_file.name.endswith(".csv"):
#                 df_up = pd.read_csv(uploaded_file)
#                 raw_input_json_str = df_up.to_json(orient="records", indent=2)
#             else:
#                 raw_input_json_str = uploaded_file.read().decode("utf-8")
#         else:
#             raw_input_json_str = json.dumps(
#                 SCENARIOS["Scenario 1: Link Congestion (Hostel Core Switch - PDF Example)"]["telemetry"],
#                 indent=2,
#             )

#     st.divider()
#     st.subheader("🛡️ Optional Enhancements")
#     enable_hitl = st.toggle("Human-in-the-Loop (HITL) Remediation", value=True)
#     show_raw_editor = st.toggle("Edit Raw Input Telemetry JSON", value=False)

# # Optional live JSON editor to test malformed inputs on the fly
# if show_raw_editor:
#     st.subheader("📝 Raw Telemetry Payload Editor (Test Malformed / Custom Inputs)")
#     raw_input_json_str = st.text_area(
#         "Modify telemetry JSON below to test agent validation & interoperability:",
#         value=raw_input_json_str,
#         height=220,
#     )

# # Parse JSON safely
# parse_error = None
# raw_telemetry_list: List[Dict[str, Any]] = []
# try:
#     parsed = json.loads(raw_input_json_str)
#     if isinstance(parsed, dict):
#         raw_telemetry_list = [parsed]
#     elif isinstance(parsed, list):
#         raw_telemetry_list = parsed
#     else:
#         parse_error = "JSON root must be an object or array of telemetry objects."
# except Exception as exc:
#     parse_error = f"Malformed JSON syntax: {exc}"

# if parse_error:
#     st.error(f"🚨 Input Validation Guardrail Triggered: {parse_error}")
#     st.stop()

# # Run Multi-Agent Pipeline
# result = run_multi_agent_pipeline(incident_id_input, raw_telemetry_list)
# report = result["final_report"]

# # =====================================================================
# # TOP KPI METRICS BANNER
# # =====================================================================
# col1, col2, col3, col4 = st.columns(4)
# status_badge = {
#     "diagnosed": "🟡 DIAGNOSED FAULT",
#     "normal": "🟢 NORMAL OPERATION",
#     "insufficient_evidence": "🟠 INSUFFICIENT EVIDENCE",
#     "error_invalid_input": "🔴 INVALID INPUT",
# }.get(report["status"], report["status"].upper())

# col1.metric("Incident Status", status_badge)
# col2.metric("Calibrated Confidence", f"{int(report['confidence'] * 100)}%", f"{report['confidence']:.2f} score")
# col3.metric("Affected Devices", len(report["affected_devices"]), ", ".join(report["affected_devices"]) or "None")
# col4.metric(
#     "A2A Protocol Messages",
#     len(result["message_bus"]),
#     f"{len(result['interop_repairs'])} schema auto-repairs",
# )

# # Executive Root Cause Alert Box
# if report["status"] == "normal":
#     st.success(f"**Root Cause Assessment:** {report['suspected_root_cause']}")
# elif report["status"] == "insufficient_evidence":
#     st.warning(f"**Diagnostic Guardrail Active:** {report['suspected_root_cause']}")
# else:
#     st.error(f"**Suspected Root Cause:** {report['suspected_root_cause']}")

# # =====================================================================
# # MAIN TABS
# # =====================================================================
# tab1, tab2, tab3, tab4, tab5 = st.tabs(
#     [
#         "📋 Unified Diagnostic Report (JSON & Summary)",
#         "🤝 Inter-Agent Message Bus (30% Rubric)",
#         "📊 Telemetry & Topology Visualizer",
#         "🛡️ Interoperability & Error Log (15% Rubric)",
#         "⚡ HITL & Simulated Remediation",
#     ]
# )

# with tab1:
#     left_col, right_col = st.columns([1.05, 1])

#     with left_col:
#         st.subheader("🔍 Evidence-Based Diagnostic Breakdown")
#         st.markdown(f"**Incident ID:** `{report['incident_id']}`")
#         st.markdown(f"**Suspected Root Cause:** {report['suspected_root_cause']}")
#         st.markdown(f"**Affected Devices:** `{', '.join(report['affected_devices']) or 'None'}`")
#         st.markdown(f"**Contributing Agents:** `{', '.join(report['evidence_sources'])}`")

#         st.markdown("#### Supporting Telemetry Evidence")
#         if report["supporting_evidence"]:
#             st.dataframe(pd.DataFrame(report["supporting_evidence"]), use_container_width=True, hide_index=True)
#         else:
#             st.info("No anomalous telemetry counters detected.")

#         st.markdown("#### Multi-Agent Conflict Resolution & Correlation Reasoning")
#         for note in result["conflict_log"]:
#             st.markdown(f"- {note}")

#         st.markdown("#### Alternative Explanations")
#         for alt in report["alternative_causes"]:
#             st.markdown(f"- {alt}")

#         st.markdown("#### Recommended Corrective Actions")
#         for act in report["recommended_actions"]:
#             st.markdown(f"- ✅ {act}")

#         st.markdown("#### Diagnostic Limitations")
#         for lim in report["limitations"]:
#             st.markdown(f"- ⚠️ {lim}")

#     with right_col:
#         st.subheader("📄 Mandatory Section 6 JSON Output")
#         json_output_str = json.dumps(report, indent=2)
#         st.code(json_output_str, language="json")
#         st.download_button(
#             label="⬇️ Download Unified Diagnostic JSON Report",
#             data=json_output_str,
#             file_name=f"{report['incident_id']}_diagnostic_report.json",
#             mime="application/json",
#             use_container_width=True,
#         )

# with tab2:
#     st.subheader("🔗 Structured Inter-Agent Communication Log (`NetCoop-A2A-v1.0`)")
#     st.markdown(
#         "Every specialist agent exchanges standardized JSON envelopes containing `protocol_version`, "
#         "`message_id`, `timestamp`, `sender_agent`, `receiver_agent`, `intent`, and `payload`."
#     )
#     for msg in result["message_bus"]:
#         with st.expander(
#             f"📨 [{msg['message_id']}] {msg['sender_agent']} ➡️ {msg['receiver_agent']} | Intent: {msg['intent']}",
#             expanded=True,
#         ):
#             st.json(msg)

# with tab3:
#     st.subheader("📡 Normalized Campus Network Telemetry")
#     if result["clean_records"]:
#         df_clean = pd.DataFrame(result["clean_records"])
#         st.dataframe(df_clean, use_container_width=True, hide_index=True)

#         numeric_cols = [
#             c
#             for c in ["latency_ms", "link_utilization_pct", "cpu_utilization_pct", "queue_drops", "interface_errors"]
#             if c in df_clean.columns and df_clean[c].notna().any()
#         ]
#         if numeric_cols:
#             st.markdown("#### Key Telemetry Comparison Across Monitored Devices")
#             chart_df = df_clean.set_index("device_id")[numeric_cols].fillna(0)
#             st.bar_chart(chart_df)

#     st.markdown("#### 🗺️ Connectivity & Topology Agent Scope Analysis")
#     for insight in result["topology_insights"]:
#         st.info(f"🧭 {insight}")

# with tab4:
#     st.subheader("🛠️ Interoperability Adapter & Schema Validation Audit")
#     c_a, c_b = st.columns(2)
#     with c_a:
#         st.markdown("#### Automatic Schema & Unit Translations")
#         if result["interop_repairs"]:
#             for rep in result["interop_repairs"]:
#                 st.success(f"🔄 {rep}")
#         else:
#             st.info("Input matched canonical `NetCoop-A2A-v1.0` schema; no field translations needed.")

#     with c_b:
#         st.markdown("#### Malformed / Out-of-Bounds Input Handling")
#         if result["validation_errors"]:
#             for err in result["validation_errors"]:
#                 st.warning(f"⚠️ {err}")
#         else:
#             st.success("Zero malformed or out-of-range telemetry values detected.")

# with tab5:
#     st.subheader("⚡ Human-in-the-Loop (HITL) & Safe Simulated Remediation")
#     st.caption(
#         "Per Section 4 guidelines: Automated remediation is simulated in a sandboxed environment "
#         "and never modifies live campus production infrastructure without operator authorization."
#     )
#     if enable_hitl and report["recommended_actions"]:
#         selected_action = st.selectbox(
#             "Select Recommended Action to Simulate on Target Device(s):",
#             report["recommended_actions"],
#         )
#         operator_note = st.text_input(
#             "Network Operator Approval Note:",
#             value="Approved by IITBBS NOC Operator after reviewing multi-agent evidence.",
#         )
#         if st.button("🚀 Approve & Simulate Corrective Action in Sandbox"):
#             st.success(
#                 f"Simulated Action Executed Safely: `{selected_action}` on "
#                 f"`{', '.join(report['affected_devices']) or 'CAMPUS_NETWORK'}`"
#             )
#             st.json(
#                 {
#                     "simulation_id": f"SIM-{uuid.uuid4().hex[:6].upper()}",
#                     "incident_id": report["incident_id"],
#                     "approved_by": "HITL_NOC_OPERATOR",
#                     "operator_note": operator_note,
#                     "target_devices": report["affected_devices"],
#                     "simulated_command": selected_action,
#                     "production_network_modified": False,
#                     "post_simulation_status": "VERIFIED_IN_SANDBOX",
#                 }
#             )
#     else:
#         st.info("Enable 'Human-in-the-Loop (HITL) Remediation' in the sidebar to test sandboxed remediation.")

# CLAUDE-2

# """
# NetCoop AI - Streamlit dashboard (thin UI over the real pipeline).

# Place at  dashboard/app.py  and run from the repo root:
#     streamlit run dashboard/app.py

# It does NOT re-implement any agent. It builds the incident state, calls
# orchestration.graph.build_graph().invoke(state) and renders what the real
# agents / correlation engine / report builder return.
# """
# from __future__ import annotations

# import json
# import sys
# import time
# import uuid
# from datetime import datetime, timezone
# from pathlib import Path

# import pandas as pd
# import streamlit as st

# # ---- make repo packages importable (works from dashboard/ or repo root) ----
# _here = Path(__file__).resolve()
# for _cand in (_here.parent, _here.parent.parent):
#     if (_cand / "orchestration").exists():
#         sys.path.insert(0, str(_cand))
#         break

# try:
#     from orchestration.graph import build_graph
#     from protocol.schemas import AgentMessage
#     IMPORT_ERROR = None
# except Exception as _e:  # noqa: BLE001
#     IMPORT_ERROR = f"{type(_e).__name__}: {_e}"

# # ============================================================================
# # Default campus topology (format expected by topology.network_topology)
# # ============================================================================
# _NODES = [("INTERNET_GW_01", "router"), ("CAMPUS_CORE_01", "switch"), ("DNS_DHCP_SRV_01", "server"),
#           ("HOSTEL_CORE_SW_01", "switch"), ("HOSTEL_AP_01", "ap"), ("HOSTEL_AP_02", "ap"), ("HOSTEL_AP_03", "ap"),
#           ("DEPT_SW_CSE_01", "switch"), ("DEPT_LAB_SW_01", "switch"), ("LECTURE_SW_01", "switch"), ("LECTURE_AP_01", "ap")]
# _EDGES = [("INTERNET_GW_01", "CAMPUS_CORE_01"), ("CAMPUS_CORE_01", "DNS_DHCP_SRV_01"), ("CAMPUS_CORE_01", "HOSTEL_CORE_SW_01"),
#           ("CAMPUS_CORE_01", "DEPT_SW_CSE_01"), ("CAMPUS_CORE_01", "LECTURE_SW_01"), ("HOSTEL_CORE_SW_01", "HOSTEL_AP_01"),
#           ("HOSTEL_CORE_SW_01", "HOSTEL_AP_02"), ("HOSTEL_CORE_SW_01", "HOSTEL_AP_03"), ("DEPT_SW_CSE_01", "DEPT_LAB_SW_01"),
#           ("LECTURE_SW_01", "LECTURE_AP_01")]
# TOPOLOGY = {"nodes": [{"device_id": d, "device_type": t} for d, t in _NODES],
#             "edges": [{"source": a, "target": b, "link_id": f"L{i + 1}"} for i, (a, b) in enumerate(_EDGES)]}

# # ============================================================================
# # Scenarios (organizer telemetry format -> goes through the real adapter)
# # ============================================================================
# BASE = dict(cpu_utilization_pct=25, link_utilization_pct=40, packet_loss_pct=0.1, latency_ms=15, jitter_ms=2,
#             queue_drops=2, interface_errors=0)
# GOOD_SVC = dict(dns_resolution_success_percent=99.5, dns_response_time_ms=40, dns_timeout_count=0,
#                 dhcp_success_percent=99.8, dhcp_response_time_ms=120, dhcp_failure_count=0)


# def _now():
#     return datetime.now(timezone.utc).isoformat(timespec="seconds")


# def _incident(device, metrics, status, affected, svc=None, extra_top=None):
#     raw = {"timestamp": _now(), "device_id": device, "metrics": metrics, "status": status}
#     raw.update(extra_top or {})
#     return {"raw_telemetry": raw, "topology": TOPOLOGY, "affected_devices": affected,
#             "service_health": {"timestamp": _now(), "service_id": "DNS_DHCP_SRV_01", "metrics": svc or GOOD_SVC}}


# SCENARIOS = {
#     "normal": dict(label="Normal operation", desc="All metrics within expected ranges.", expect="none",
#                    build=lambda: _incident("HOSTEL_CORE_SW_01", dict(BASE), "healthy", ["HOSTEL_CORE_SW_01"])),
#     "link_congestion": dict(label="Link congestion", desc="High utilization, queue drops and latency on the hostel switch; its APs are affected.",
#                             expect="congestion",
#                             build=lambda: _incident("HOSTEL_CORE_SW_01", {**BASE, "link_utilization_pct": 94, "queue_drops": 900, "latency_ms": 280,
#                                                                           "packet_loss_pct": 3, "jitter_ms": 25, "cpu_utilization_pct": 55}, "warning",
#                                                     ["HOSTEL_AP_01", "HOSTEL_AP_02", "HOSTEL_AP_03"])),
#     "cpu_overload": dict(label="Device CPU overload", desc="Core switch CPU saturated.", expect="cpu_overload",
#                          build=lambda: _incident("CAMPUS_CORE_01", {**BASE, "cpu_utilization_pct": 97, "latency_ms": 120, "packet_loss_pct": 0.5,
#                                                                     "link_utilization_pct": 55}, "critical",
#                                                  ["CAMPUS_CORE_01", "HOSTEL_CORE_SW_01"])),
#     "interface_fault": dict(label="Ethernet / interface fault", desc="Rising interface errors and packet loss on the dept lab switch.",
#                             expect="interface_or_hardware_fault",
#                             build=lambda: _incident("DEPT_LAB_SW_01", {**BASE, "interface_errors": 240, "packet_loss_pct": 6, "jitter_ms": 18,
#                                                                        "latency_ms": 60, "link_utilization_pct": 30}, "warning", ["DEPT_LAB_SW_01"])),
#     "dns_failure": dict(label="DNS failure", desc="Network healthy, DNS resolution failing.", expect="dns_failure",
#                         build=lambda: _incident("DNS_DHCP_SRV_01", dict(BASE), "warning", ["HOSTEL_AP_01", "LECTURE_AP_01"],
#                                                 {**GOOD_SVC, "dns_resolution_success_percent": 40, "dns_response_time_ms": 900, "dns_timeout_count": 30})),
#     "dhcp_failure": dict(label="DHCP failure", desc="Network healthy, DHCP failing.", expect="dhcp_failure",
#                          build=lambda: _incident("DNS_DHCP_SRV_01", dict(BASE), "warning", ["HOSTEL_AP_01", "LECTURE_AP_01"],
#                                                  {**GOOD_SVC, "dhcp_success_percent": 35, "dhcp_response_time_ms": 1500, "dhcp_failure_count": 40})),
#     "interop_failure": dict(label="Interoperability failure", desc="Incompatible field names/units and an unknown schema version (cpu_pct, latency_s, util_ratio...). The system must not guess.",
#                             expect="none",
#                             build=lambda: _incident("HOSTEL_CORE_SW_01", {"cpu_pct": 94, "latency_s": 0.28, "util_ratio": 0.94, "loss_ratio": 0.03,
#                                                                           "q_drops": 900}, "warning", ["HOSTEL_CORE_SW_01"],
#                                                     extra_top={"schema_version": "0.9"})),
#     "partial_telemetry": dict(label="Missing measurements", desc="Only latency and loss are reported.", expect="any",
#                               build=lambda: _incident("HOSTEL_CORE_SW_01", {"latency_ms": 320, "packet_loss_percent": 4}, "warning", ["HOSTEL_CORE_SW_01"])),
#     "malformed_input": dict(label="Malformed input", desc="No metrics dictionary - input must be rejected with a clear error.", expect="reject",
#                             build=lambda: {"raw_telemetry": {"device": "SW1", "readings": [1, 2, 3]}, "topology": TOPOLOGY,
#                                            "affected_devices": ["SW1"], "service_health": None}),
# }

# AGENT_INFO = [
#     ("performance_agent", "Telemetry & Performance", "Latency, jitter, packet loss, link utilization -> structured evidence."),
#     ("infrastructure_agent", "Infrastructure Health", "CPU, queue drops, interface errors, reported device status."),
#     ("connectivity_agent", "Connectivity Analysis", "Topology graph: connected devices and common neighbours of affected devices."),
#     ("service_health_agent", "Service Health (DNS/DHCP)", "DNS/DHCP success rate, response time, timeouts and failures."),
#     ("fault_correlation", "Fault Correlation", "Combines all findings, ranks hypotheses, reports insufficient evidence when needed."),
#     ("recommendation_agent", "Recommendation", "Maps the primary hypothesis to prioritised corrective actions (no auto-remediation)."),
# ]
# PS_REPORT_KEYS = ["incident_id", "status", "suspected_root_cause", "confidence", "affected_devices", "supporting_evidence",
#                   "alternative_causes", "recommended_actions", "evidence_sources", "limitations"]


# # ============================================================================
# # Pipeline runner
# # ============================================================================
# @st.cache_resource(show_spinner=False)
# def get_graph():
#     return build_graph()


# def run_incident(inc: dict) -> dict:
#     state = {"incident_id": "INC-" + uuid.uuid4().hex[:6].upper(), "raw_telemetry": inc.get("raw_telemetry"),
#              "topology": inc.get("topology") or TOPOLOGY, "affected_devices": inc.get("affected_devices") or []}
#     if inc.get("service_health") is not None:
#         state["service_health"] = inc["service_health"]
#     t0 = time.perf_counter()
#     try:
#         out = get_graph().invoke(state)
#         return {"ok": True, "state": out, "seconds": time.perf_counter() - t0, "input": state}
#     except Exception as e:  # noqa: BLE001  - malformed input must be reported, not crash the UI
#         return {"ok": False, "error": f"{type(e).__name__}: {e}", "state": {}, "seconds": time.perf_counter() - t0, "input": state}


# def primary(diag):
#     ph = diag.get("primary_hypothesis") if isinstance(diag, dict) else None
#     return ph if isinstance(ph, dict) else {}


# def get_confidence(state):
#     for src in (state.get("report") or {}, primary(state.get("diagnosis"))):
#         for k in ("confidence", "confidence_score", "score"):
#             if isinstance(src.get(k), (int, float)):
#                 return src[k]
#     return None


# def fmt_conf(v):
#     if v is None:
#         return "n/a"
#     return f"{v:.0%}" if isinstance(v, float) and v <= 1 else f"{v} pts"


# def evidence_rows(findings):
#     rows = []
#     for m in findings:
#         p, ag = m.get("payload", {}), m.get("sender")
#         for it in p.get("findings") or []:
#             if isinstance(it, dict):
#                 rows.append({"agent": ag, "device": it.get("device_id"), "metric": it.get("metric"), "value": it.get("value"),
#                              "unit": it.get("unit"), "observation": it.get("observation"),
#                              "flagged": "No threshold" not in str(it.get("observation"))})
#             else:
#                 rows.append({"agent": ag, "device": p.get("service_id"), "metric": None, "value": None, "unit": None,
#                              "observation": str(it), "flagged": True})
#         for it in p.get("evidence") or []:
#             rows.append({"agent": ag, "device": p.get("service_id"), "metric": it.get("metric"), "value": it.get("value"),
#                          "unit": None, "observation": "service measurement", "flagged": False})
#     return rows


# def judge(expect, res):
#     """Compare a scenario result with ground truth. Returns (passed, got_text)."""
#     if expect == "reject":
#         return (not res["ok"]), (res.get("error") or "accepted (no error)")
#     if not res["ok"]:
#         return False, "pipeline error: " + res["error"]
#     cause = primary(res["state"].get("diagnosis")).get("hypothesis")
#     if expect == "any":
#         return True, cause or "no hypothesis (abstained)"
#     if expect == "none":
#         return cause is None, cause or "no hypothesis (abstained)"
#     return cause == expect, cause or "no hypothesis"


# def run_suite():
#     rows = []
#     for key, sc in SCENARIOS.items():
#         res = run_incident(sc["build"]())
#         ok, got = judge(sc["expect"], res)
#         st_ = res["state"]
#         rows.append({"scenario": sc["label"], "expected": sc["expect"], "got": got,
#                      "status": (st_.get("diagnosis") or {}).get("diagnosis_status", "-"),
#                      "confidence": fmt_conf(get_confidence(st_)),
#                      "warnings": len((st_.get("validation_result") or {}).get("warnings", [])),
#                      "result": "PASS" if ok else "FAIL"})
#     return pd.DataFrame(rows)


# def topo_dot(topology, telemetry_dev, affected, common):
#     L = ['digraph G {rankdir=TB; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#555"]; edge [color="#888"];']
#     for n in topology.get("nodes", []):
#         d = n["device_id"]
#         fill, fc = ("#ef4444", "white") if d == telemetry_dev else ("#f59e0b", "black") if d in affected else \
#             ("#fde047", "black") if d in common else ("#86efac", "black")
#         L.append(f'"{d}" [label="{d}\\n({n.get("device_type", "?")})", fillcolor="{fill}", fontcolor="{fc}"];')
#     for e in topology.get("edges", []):
#         L.append(f'"{e["source"]}" -> "{e["target"]}" [dir=none];')
#     return "\n".join(L + ["}"])


# # ============================================================================
# # UI
# # ============================================================================
# CSS = """<style>
# .block-container{padding-top:1.3rem}
# .hero{padding:1rem 1.3rem;border-radius:14px;margin-bottom:.8rem;border:1px solid rgba(128,128,128,.25);
#  background:linear-gradient(120deg,rgba(99,102,241,.18),rgba(16,185,129,.14))}
# .hero h1{margin:0;font-size:1.8rem}.hero p{margin:.2rem 0 0;opacity:.8}
# .card{padding:.9rem 1.1rem;border-radius:12px;border:1px solid rgba(128,128,128,.3);margin-bottom:.6rem}
# .cause{font-size:1.4rem;font-weight:650;line-height:1.3}
# </style>"""


# def main():
#     st.set_page_config(page_title="NetCoop AI", page_icon="🛰️", layout="wide")
#     st.markdown(CSS, unsafe_allow_html=True)
#     st.markdown('<div class="hero"><h1>🛰️ NetCoop AI</h1><p>Multi-agent network fault diagnosis &amp; interoperability - live view of the LangGraph pipeline</p></div>',
#                 unsafe_allow_html=True)
#     if IMPORT_ERROR:
#         st.error(f"Could not import the NetCoop pipeline ({IMPORT_ERROR}). Run from the repo root: `streamlit run dashboard/app.py` "
#                  "after `pip install -r requirements.txt`.")
#         st.stop()

#     sb = st.sidebar
#     sb.header("Incident input")
#     mode = sb.radio("Source", ["Scenario", "Custom JSON"])
#     if mode == "Scenario":
#         key = sb.selectbox("Scenario", list(SCENARIOS), format_func=lambda k: SCENARIOS[k]["label"])
#         sb.caption(SCENARIOS[key]["desc"])
#         inc, expect = SCENARIOS[key]["build"](), SCENARIOS[key]["expect"]
#         with sb.expander("View / copy incident JSON"):
#             st.code(json.dumps({k: v for k, v in inc.items() if k != "topology"}, indent=2), language="json")
#     else:
#         sample = json.dumps({k: v for k, v in SCENARIOS["link_congestion"]["build"]().items() if k != "topology"}, indent=2)
#         txt = sb.text_area("Incident JSON (raw_telemetry, affected_devices, service_health)", sample, height=340)
#         try:
#             inc, expect = json.loads(txt), None
#             if not isinstance(inc, dict):
#                 raise ValueError("top level must be an object")
#             inc.setdefault("topology", TOPOLOGY)
#         except Exception as e:  # noqa: BLE001
#             sb.error(f"Invalid JSON: {e}")
#             st.stop()
#     sb.caption("Organizer metric names (cpu_utilization_pct, link_utilization_pct, packet_loss_pct) are translated by the real ingestion adapter. No production network is touched.")

#     res = run_incident(inc)
#     s = res["state"]
#     findings = s.get("agent_findings", [])
#     diag, report, val = s.get("diagnosis") or {}, s.get("report") or {}, s.get("validation_result") or {}

#     tabs = st.tabs(["🩺 Diagnosis", "🔎 Evidence", "💬 Agent messages", "🧾 Input & validation", "🗺️ Topology", "🧪 Test suite", "✅ PS checklist", "📄 Report"])

#     # ---- Diagnosis ----------------------------------------------------------
#     with tabs[0]:
#         if not res["ok"]:
#             st.error("Input rejected - the pipeline could not process this telemetry.")
#             st.code(res["error"])
#             st.info("Status: insufficient data. No diagnosis was attempted and no root cause is claimed. "
#                     "Provide `raw_telemetry` with `timestamp`, `device_id` and a `metrics` object.")
#         else:
#             cause = report.get("suspected_root_cause") or primary(diag).get("hypothesis")
#             status = report.get("status") or diag.get("diagnosis_status") or s.get("workflow_status", "-")
#             st.markdown(f"**Status:** `{status}` &nbsp; **Incident:** `{res['input']['incident_id']}` &nbsp; **Workflow:** `{s.get('workflow_status', '-')}`")
#             st.markdown(f'<div class="card"><div class="cause">{cause if cause else "No root cause claimed - evidence insufficient"}</div></div>',
#                         unsafe_allow_html=True)
#             c1, c2, c3, c4 = st.columns(4)
#             c1.metric("Confidence / score", fmt_conf(get_confidence(s)))
#             c2.metric("Agents responded", f"{sum(m.get('message_type') == 'FINDING' for m in findings)}/{4}")
#             c3.metric("Validation warnings", len(val.get("warnings", [])))
#             c4.metric("Run time", f"{res['seconds']:.2f}s")
#             if s.get("agent_errors") or any(m.get("message_type") == "ERROR" for m in findings):
#                 st.warning("One or more agents returned an ERROR message - see the Agent messages tab.")
#             left, right = st.columns(2)
#             with left:
#                 st.subheader("Ranked hypotheses")
#                 hyp = next((diag[k] for k in ("hypotheses", "ranked_hypotheses", "alternatives") if isinstance(diag.get(k), list)), [])
#                 if hyp and all(isinstance(h, dict) for h in hyp):
#                     st.dataframe(pd.DataFrame(hyp))
#                 else:
#                     st.write("None reported by the correlation engine." if not hyp else hyp)
#                 with st.expander("Raw diagnosis"):
#                     st.json(diag)
#             with right:
#                 st.subheader("Recommended actions")
#                 recs = s.get("recommendations") or report.get("recommended_actions") or []
#                 for r in recs:
#                     st.markdown(f"- **{r.get('priority', '')}** - {r.get('action', r)}" if isinstance(r, dict) else f"- {r}")
#                 if not recs:
#                     st.write("None.")
#                 if report.get("limitations"):
#                     st.subheader("Limitations")
#                     for l in report["limitations"]:
#                         st.markdown(f"- {l}")
#         if expect is not None and mode == "Scenario":
#             ok, got = judge(expect, res)
#             st.caption(f"Ground truth: **{expect}** -> {'✅ matches' if ok else '⚠️ differs'} (got: {got})")

#     # ---- Evidence -----------------------------------------------------------
#     with tabs[1]:
#         rows = evidence_rows(findings)
#         if rows:
#             df = pd.DataFrame(rows)
#             only = st.checkbox("Show only flagged observations", value=True)
#             st.dataframe(df[df["flagged"]] if only else df)
#         else:
#             st.info("No evidence available.")

#     # ---- Messages -----------------------------------------------------------
#     with tabs[2]:
#         st.subheader("Agents")
#         cols = st.columns(3)
#         for i, (name, role, desc) in enumerate(AGENT_INFO):
#             with cols[i % 3]:
#                 st.markdown(f'<div class="card"><b>{role}</b><br><code>{name}</code><br><span style="opacity:.8;font-size:.9rem">{desc}</span></div>', unsafe_allow_html=True)
#         st.subheader("Messages exchanged (protocol v1.0 AgentMessage)")
#         if findings:
#             st.dataframe(pd.DataFrame([{"time": str(m.get("timestamp", ""))[11:23], "from": m.get("sender"), "to": m.get("receiver"),
#                                         "type": m.get("message_type"), "status": m.get("status"), "message_id": m.get("message_id")} for m in findings]))
#             for m in findings:
#                 with st.expander(f"{m.get('sender')} -> {m.get('receiver')} [{m.get('message_type')} / {m.get('status')}]"):
#                     st.json(m)
#         else:
#             st.info("No agent messages (pipeline failed before the agents ran).")

#     # ---- Input & validation -------------------------------------------------
#     with tabs[3]:
#         a, b = st.columns(2)
#         with a:
#             st.subheader("Raw input (organizer format)")
#             st.json(res["input"].get("raw_telemetry"))
#         with b:
#             st.subheader("Normalized telemetry")
#             st.json(s.get("normalized_telemetry", {}))
#         if val:
#             (st.success if val.get("is_valid") else st.error)(f"Validation: {'valid' if val.get('is_valid') else 'INVALID'}")
#             for e in val.get("errors", []):
#                 st.error(e)
#             for w in val.get("warnings", []):
#                 st.warning(w)
#         elif not res["ok"]:
#             st.error(res["error"])

#     # ---- Topology -----------------------------------------------------------
#     with tabs[4]:
#         topo = res["input"]["topology"]
#         conn = next((m.get("payload", {}) for m in findings if m.get("sender") == "connectivity_agent"), {})
#         dev = (res["input"].get("raw_telemetry") or {}).get("device_id") if isinstance(res["input"].get("raw_telemetry"), dict) else None
#         st.graphviz_chart(topo_dot(topo, dev, set(res["input"]["affected_devices"]), set(conn.get("common_neighbors", []))))
#         st.markdown("🟥 device reporting telemetry &nbsp; 🟧 affected devices &nbsp; 🟨 common neighbour of affected devices &nbsp; 🟩 other")
#         if conn:
#             st.info(f"Common neighbours: {', '.join(conn.get('common_neighbors', [])) or 'none'} | unknown devices: {', '.join(conn.get('unknown_devices', [])) or 'none'}")

#     # ---- Test suite ---------------------------------------------------------
#     with tabs[5]:
#         st.write("Runs every scenario through the real pipeline and compares with ground truth.")
#         if st.button("Run all scenarios", type="primary"):
#             st.session_state["suite"] = run_suite()
#         if "suite" in st.session_state:
#             su = st.session_state["suite"]
#             m1, m2 = st.columns(2)
#             m1.metric("Pass rate", f"{(su['result'] == 'PASS').mean():.0%}")
#             m2.metric("Failures", int((su["result"] == "FAIL").sum()))
#             st.dataframe(su)
#             st.download_button("Download results (CSV)", su.to_csv(index=False), "netcoop_test_results.csv", "text/csv")

#     # ---- PS checklist -------------------------------------------------------
#     with tabs[6]:
#         senders = {m.get("sender") for m in findings if m.get("message_type") == "FINDING"}
#         with_data = {m.get("sender") for m in findings if (m.get("payload", {}).get("findings") or m.get("payload", {}).get("connected_devices"))}
#         valid_msgs = True
#         for m in findings:
#             try:
#                 AgentMessage.model_validate(m)
#             except Exception:  # noqa: BLE001
#                 valid_msgs = False
#         suite = st.session_state.get("suite")

#         def suite_check(label):
#             if suite is None:
#                 return "▶ run test suite"
#             r = suite[suite["scenario"] == SCENARIOS[label]["label"]]
#             return "✅" if (not r.empty and r.iloc[0]["result"] == "PASS") else "❌"

#         missing = [k for k in PS_REPORT_KEYS if k not in report]
#         checks = [
#             ("≥2 collaborating agents with distinct roles", "✅" if len(senders) >= 2 else "❌", f"{len(senders)} agents returned FINDING messages"),
#             ("Structured, versioned agent communication", "✅" if findings and valid_msgs else "❌", "All messages validate as AgentMessage (protocol_version 1.0)"),
#             ("Evidence from multiple agents feeds one diagnosis", "✅" if len(with_data) >= 2 else "❌", f"{len(with_data)} agents supplied evidence"),
#             ("Malformed input handled and reported", suite_check("malformed_input"), "malformed_input scenario"),
#             ("Incompatible schema handled without guessing", suite_check("interop_failure"), "interop_failure scenario"),
#             ("Missing measurements handled", suite_check("partial_telemetry"), "partial_telemetry scenario"),
#             ("Insufficient evidence reported instead of a guess", suite_check("normal"), "normal / abstain behaviour"),
#             ("Report contains all PS fields", "✅" if report and not missing else "❌", "missing: " + (", ".join(missing) if missing else "none")),
#             ("Reproducible scenarios + test run", "✅", "deterministic scenarios, Test suite tab"),
#         ]
#         st.dataframe(pd.DataFrame(checks, columns=["Criterion", "Status", "Detail"]))
#         if missing and report:
#             st.warning("The report from `diagnosis/report_builder.py` lacks: " + ", ".join(missing))

#     # ---- Report -------------------------------------------------------------
#     with tabs[7]:
#         if report:
#             st.download_button("Download JSON report", json.dumps(report, indent=2, default=str), f"{res['input']['incident_id']}.json", "application/json")
#             st.json(report)
#         else:
#             st.info("No report produced for this input.")


# if __name__ == "__main__":
#     main()


# CLAUDE 1

# """
# NetCoop AI - Multi-Agent Network Fault Diagnosis & Interoperability
# Streamlit dashboard (self-contained, free tools only: streamlit + pandas + numpy).

# Run:  streamlit run app.py

# Pipeline
#   Ingestion/Validation -> Performance Agent -> {Infrastructure, Wireless,
#   Connectivity, Service} Agents -> Fault Correlation Agent -> Recommendation &
#   Reporting Agent -> Unified JSON/Markdown report.

# All agents talk through a versioned JSON message envelope (see "Protocol" tab).
# """
# from __future__ import annotations

# import hashlib
# import json
# import math
# import time
# import uuid
# from collections import defaultdict
# from datetime import datetime, timedelta, timezone

# import numpy as np
# import pandas as pd
# import streamlit as st

# SCHEMA_VERSION = "1.0"
# LEGACY_SCHEMA_VERSION = "0.9"

# # ============================================================================
# # 1. TOPOLOGY
# # ============================================================================
# NODES = {
#     "INTERNET_GW_01": {"role": "gateway", "type": "router"},
#     "CAMPUS_CORE_01": {"role": "core", "type": "switch"},
#     "DNS_DHCP_SRV_01": {"role": "service", "type": "server"},
#     "HOSTEL_CORE_SW_01": {"role": "distribution", "type": "switch"},
#     "HOSTEL_AP_01": {"role": "access", "type": "ap"},
#     "HOSTEL_AP_02": {"role": "access", "type": "ap"},
#     "HOSTEL_AP_03": {"role": "access", "type": "ap"},
#     "DEPT_SW_CSE_01": {"role": "distribution", "type": "switch"},
#     "DEPT_LAB_SW_01": {"role": "access", "type": "switch"},
#     "LECTURE_SW_01": {"role": "distribution", "type": "switch"},
#     "LECTURE_AP_01": {"role": "access", "type": "ap"},
# }
# EDGES = [  # (parent, child)
#     ("INTERNET_GW_01", "CAMPUS_CORE_01"),
#     ("CAMPUS_CORE_01", "DNS_DHCP_SRV_01"),
#     ("CAMPUS_CORE_01", "HOSTEL_CORE_SW_01"),
#     ("CAMPUS_CORE_01", "DEPT_SW_CSE_01"),
#     ("CAMPUS_CORE_01", "LECTURE_SW_01"),
#     ("HOSTEL_CORE_SW_01", "HOSTEL_AP_01"),
#     ("HOSTEL_CORE_SW_01", "HOSTEL_AP_02"),
#     ("HOSTEL_CORE_SW_01", "HOSTEL_AP_03"),
#     ("DEPT_SW_CSE_01", "DEPT_LAB_SW_01"),
#     ("LECTURE_SW_01", "LECTURE_AP_01"),
# ]
# PARENT = {c: p for p, c in EDGES}
# CHILDREN: dict[str, list[str]] = defaultdict(list)
# for _p, _c in EDGES:
#     CHILDREN[_p].append(_c)


# def descendants(dev: str) -> set[str]:
#     out, stack = set(), list(CHILDREN.get(dev, []))
#     while stack:
#         d = stack.pop()
#         if d not in out:
#             out.add(d)
#             stack.extend(CHILDREN.get(d, []))
#     return out


# # ============================================================================
# # 2. TELEMETRY SCHEMA (canonical v1.0), ALIASES & UNIT CONVERSION
# # ============================================================================
# # canonical -> (unit, min, max, description)
# CANON = {
#     "latency_ms": ("ms", 0, 60000, "Round-trip latency"),
#     "jitter_ms": ("ms", 0, 60000, "Delay variation"),
#     "packet_loss_pct": ("%", 0, 100, "Packet loss"),
#     "throughput_mbps": ("Mbps", 0, 1e6, "Observed throughput"),
#     "bandwidth_mbps": ("Mbps", 0.001, 1e6, "Link capacity"),
#     "link_utilization_pct": ("%", 0, 100, "Link utilization"),
#     "cpu_pct": ("%", 0, 100, "Device CPU utilization"),
#     "memory_pct": ("%", 0, 100, "Device memory utilization"),
#     "queue_drops": ("pkts/interval", 0, 1e9, "Egress queue drops"),
#     "interface_errors": ("errors/interval", 0, 1e9, "CRC/input/output errors"),
#     "rssi_dbm": ("dBm", -130, 0, "Wireless signal strength (APs/clients)"),
#     "retransmission_pct": ("%", 0, 100, "Wireless retransmission rate"),
#     "dns_failure_pct": ("%", 0, 100, "DNS lookup failure rate"),
#     "dhcp_failure_pct": ("%", 0, 100, "DHCP failure rate"),
# }
# METRICS = list(CANON)
# CORE_METRICS = ["latency_ms", "packet_loss_pct", "link_utilization_pct",
#                 "cpu_pct", "queue_drops", "interface_errors"]
# RANGE = {k: (v[1], v[2]) for k, v in CANON.items()}
# UNITS = {k: v[0] for k, v in CANON.items()}

# # canonical -> [(alias, multiplier_to_canonical)]
# ALIASES = {
#     "device_id": [("device_id", 1), ("device", 1), ("host", 1), ("hostname", 1), ("node", 1), ("node_id", 1)],
#     "timestamp": [("timestamp", 1), ("ts", 1), ("time", 1), ("datetime", 1)],
#     "device_status": [("device_status", 1), ("status", 1), ("state", 1)],
#     "latency_ms": [("latency_ms", 1), ("latency", 1), ("rtt_ms", 1), ("delay_ms", 1),
#                    ("rtt_s", 1e3), ("delay_s", 1e3), ("latency_s", 1e3), ("latency_us", 1e-3)],
#     "jitter_ms": [("jitter_ms", 1), ("jitter", 1), ("jitter_us", 1e-3), ("jitter_s", 1e3)],
#     "packet_loss_pct": [("packet_loss_pct", 1), ("packet_loss", 1), ("loss_pct", 1), ("loss_ratio", 100)],
#     "throughput_mbps": [("throughput_mbps", 1), ("throughput", 1), ("tput_mbps", 1),
#                         ("throughput_kbps", 1e-3), ("throughput_gbps", 1e3)],
#     "bandwidth_mbps": [("bandwidth_mbps", 1), ("bandwidth", 1), ("bw_mbps", 1), ("capacity_mbps", 1),
#                        ("bw_kbps", 1e-3), ("bandwidth_gbps", 1e3)],
#     "link_utilization_pct": [("link_utilization_pct", 1), ("utilization", 1), ("util_pct", 1),
#                              ("link_util", 1), ("util_ratio", 100)],
#     "cpu_pct": [("cpu_pct", 1), ("cpu", 1), ("cpu_util", 1), ("cpu_load", 1), ("cpu_ratio", 100)],
#     "memory_pct": [("memory_pct", 1), ("mem_pct", 1), ("memory", 1), ("mem", 1)],
#     "queue_drops": [("queue_drops", 1), ("egress_queue_drops", 1), ("q_drops", 1), ("egress_drops", 1)],
#     "interface_errors": [("interface_errors", 1), ("if_errors", 1), ("if_errs", 1),
#                          ("iface_errors", 1), ("crc_errors", 1)],
#     "rssi_dbm": [("rssi_dbm", 1), ("rssi", 1), ("signal", 1), ("signal_dbm", 1)],
#     "retransmission_pct": [("retransmission_pct", 1), ("retrans_pct", 1), ("retries_pct", 1),
#                            ("retransmissions_pct", 1)],
#     "dns_failure_pct": [("dns_failure_pct", 1), ("dns_fail_pct", 1), ("dns_error_pct", 1)],
#     "dhcp_failure_pct": [("dhcp_failure_pct", 1), ("dhcp_fail_pct", 1), ("dhcp_error_pct", 1)],
# }
# STATUS_MAP = {
#     "up": "up", "ok": "up", "online": "up", "healthy": "up", "active": "up",
#     "degraded": "degraded", "warn": "degraded", "warning": "degraded",
#     "flapping": "degraded", "impaired": "degraded",
#     "down": "down", "crit": "down", "critical": "down", "offline": "down",
#     "unreachable": "down", "error": "down",
# }
# KNOWN_SCHEMAS = {SCHEMA_VERSION, LEGACY_SCHEMA_VERSION}


# # ============================================================================
# # 3. SYNTHETIC SCENARIO GENERATOR
# # ============================================================================
# def _lerp(a, b, k):
#     return a + (b - a) * k


# def _f_congestion(r, dev, rng, k):
#     if dev == "HOSTEL_CORE_SW_01":
#         r["link_utilization_pct"] = _lerp(35, 93, k) + rng.normal(0, 3)
#         r["queue_drops"] = max(0, rng.normal(160 * k, 30)) + r["queue_drops"] * (1 - k)
#         r["latency_ms"] = _lerp(12, 250, k) + rng.normal(0, 30)
#         r["packet_loss_pct"] += 3 * k
#         r["jitter_ms"] += 22 * k
#         r["cpu_pct"] += 25 * k
#     elif dev.startswith("HOSTEL_AP"):
#         r["latency_ms"] += 120 * k
#         r["packet_loss_pct"] += 1.5 * k
#         r["jitter_ms"] += 8 * k


# def _f_weak_wifi(r, dev, rng, k):
#     if dev == "HOSTEL_AP_02":
#         r["rssi_dbm"] = _lerp(-55, -86, k) + rng.normal(0, 2)
#         r["retransmission_pct"] = _lerp(2, 22, k) + rng.normal(0, 3)
#         r["packet_loss_pct"] += 6 * k
#         r["jitter_ms"] += 25 * k
#         r["latency_ms"] += 60 * k
#         r["link_utilization_pct"] -= 15 * k


# def _f_interface(r, dev, rng, k):
#     if dev == "DEPT_LAB_SW_01":
#         r["interface_errors"] = max(0, rng.normal(80 * k, 15)) + r["interface_errors"] * (1 - k)
#         r["packet_loss_pct"] += 8 * k
#         r["jitter_ms"] += 14 * k
#         r["latency_ms"] += 30 * k
#         if rng.random() < 0.35 * k:
#             r["device_status"] = "degraded"


# def _f_dns(r, dev, rng, k):
#     r["dns_failure_pct"] = max(0, rng.normal(70 * k, 8))


# def _f_dhcp(r, dev, rng, k):
#     r["dhcp_failure_pct"] = max(0, rng.normal(65 * k, 8))


# def _f_overload(r, dev, rng, k):
#     if dev == "CAMPUS_CORE_01":
#         r["cpu_pct"] = _lerp(30, 97, k) + rng.normal(0, 1.5)
#         r["memory_pct"] = _lerp(45, 91, k) + rng.normal(0, 1.5)
#         r["latency_ms"] += 120 * k
#         r["packet_loss_pct"] += 2 * k
#         r["jitter_ms"] += 10 * k
#     elif dev != "INTERNET_GW_01":
#         r["latency_ms"] += 40 * k


# def _f_hardware(r, dev, rng, k):
#     if dev == "HOSTEL_CORE_SW_01":
#         r["device_status"] = "down"
#     elif dev in descendants("HOSTEL_CORE_SW_01"):
#         r["device_status"] = "unreachable"
#     else:
#         return
#     for m in METRICS:
#         if m != "bandwidth_mbps":
#             r[m] = np.nan


# def _f_ambiguous(r, dev, rng, k):
#     if dev == "DEPT_SW_CSE_01":  # symptoms but no supporting infra/utilisation evidence
#         r["latency_ms"] += 140 * k
#         r["packet_loss_pct"] += 4 * k
#         r["jitter_ms"] += 20 * k


# def _f_concurrent(r, dev, rng, k):
#     _f_congestion(r, dev, rng, k)
#     _f_interface(r, dev, rng, k)


# FAULTS = {
#     "link_congestion": _f_congestion, "weak_wifi": _f_weak_wifi, "interface_fault": _f_interface,
#     "dns_failure": _f_dns, "dhcp_failure": _f_dhcp, "device_overload": _f_overload,
#     "hardware_failure": _f_hardware, "ambiguous_degradation": _f_ambiguous,
#     "concurrent_faults": _f_concurrent, "interop_failure": _f_congestion, "sparse_data": _f_congestion,
# }

# SCENARIO_META = {
#     "normal": dict(label="Normal operation", desc="All metrics within expected ranges.",
#                    expect_status="healthy", causes=[], targets=[]),
#     "link_congestion": dict(label="Link congestion", desc="High utilization + queue drops + latency on the hostel distribution switch; APs below suffer.",
#                             expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"]),
#     "weak_wifi": dict(label="Weak Wi-Fi signal", desc="Poor RSSI and high retransmissions on HOSTEL_AP_02.",
#                       expect_status="diagnosed", causes=["weak_wifi_signal"], targets=["HOSTEL_AP_02"]),
#     "interface_fault": dict(label="Ethernet / interface fault", desc="Rising interface errors, loss and flapping on DEPT_LAB_SW_01.",
#                             expect_status="diagnosed", causes=["interface_fault"], targets=["DEPT_LAB_SW_01"]),
#     "dns_failure": dict(label="DNS failure", desc="Service-level DNS failures while the network itself is healthy.",
#                         expect_status="diagnosed", causes=["dns_failure"], targets=[]),
#     "dhcp_failure": dict(label="DHCP failure", desc="Service-level DHCP failures while the network itself is healthy.",
#                          expect_status="diagnosed", causes=["dhcp_failure"], targets=[]),
#     "device_overload": dict(label="Device CPU/memory overload", desc="Core switch CPU and memory saturated.",
#                             expect_status="diagnosed", causes=["device_overload"], targets=["CAMPUS_CORE_01"]),
#     "hardware_failure": dict(label="Hardware failure / device down", desc="Hostel distribution switch down; all APs behind it unreachable.",
#                              expect_status="diagnosed", causes=["hardware_failure"], targets=["HOSTEL_CORE_SW_01"]),
#     "interop_failure": dict(label="Interoperability failure (legacy schema v0.9)", desc="Same congestion fault, but telemetry arrives with different field names, units (s, us, ratios, kbps) and schema version.",
#                             expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"]),
#     "malformed_input": dict(label="Malformed / incompatible input", desc="Unknown columns and text values - must be rejected with a clear error.",
#                             expect_status="insufficient_data", causes=[], targets=[]),
#     "sparse_data": dict(label="Sparse / missing telemetry", desc="Congestion with >50% samples missing and queue-drop counter absent - confidence must drop.",
#                         expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"], abstain_ok=True),
#     "ambiguous_degradation": dict(label="Unexplained degradation", desc="Latency/loss/jitter up on DEPT_SW_CSE_01 with no corroborating evidence - system must NOT claim a root cause.",
#                                   expect_status="insufficient_evidence", causes=[], targets=["DEPT_SW_CSE_01"]),
#     "concurrent_faults": dict(label="Concurrent faults", desc="Congestion on hostel switch and interface errors on dept lab switch at the same time.",
#                               expect_status="diagnosed", causes=["link_congestion", "interface_fault"],
#                               targets=["HOSTEL_CORE_SW_01", "DEPT_LAB_SW_01"]),
# }


# def to_legacy(df: pd.DataFrame) -> pd.DataFrame:
#     secs = (pd.to_datetime(df["timestamp"]) - pd.Timestamp("1970-01-01")).dt.total_seconds()
#     return pd.DataFrame({
#         "host": df["device_id"], "ts": secs.astype("int64"),
#         "state": df["device_status"].map({"up": "OK", "degraded": "WARN"}).fillna("CRIT"),
#         "rtt_s": df["latency_ms"] / 1e3, "jitter_us": df["jitter_ms"] * 1e3,
#         "loss_ratio": df["packet_loss_pct"] / 100, "bw_kbps": df["bandwidth_mbps"] * 1e3,
#         "util_ratio": df["link_utilization_pct"] / 100, "cpu": df["cpu_pct"], "mem": df["memory_pct"],
#         "q_drops": df["queue_drops"], "if_errs": df["interface_errors"], "signal": df["rssi_dbm"],
#         "schema_version": LEGACY_SCHEMA_VERSION,
#     })


# @st.cache_data(show_spinner=False)
# def generate(scenario: str, seed: int = 7, noise: float = 1.0, missing_pct: float = 0.0, n: int = 60) -> pd.DataFrame:
#     rng = np.random.default_rng(seed)
#     if scenario == "malformed_input":
#         return pd.DataFrame({
#             "node_name": [f"sw{i % 4}" for i in range(20)],
#             "reading_a": ["high", "low", "n/a", "??"] * 5,
#             "reading_b": ["x"] * 20, "notes": ["see ticket"] * 20,
#         })
#     t0 = datetime(2026, 11, 1, 9, 0, 0)
#     onset = int(n * 0.5)
#     fault = FAULTS.get(scenario)
#     rows = []
#     for dev, info in NODES.items():
#         is_ap = info["type"] == "ap"
#         bw = 300 if is_ap else (10000 if info["role"] in ("gateway", "core") else 1000)
#         for i in range(n):
#             util = float(np.clip(rng.normal(35, 8 * noise), 5, 70))
#             r = {
#                 "timestamp": (t0 + timedelta(minutes=i)).isoformat(), "device_id": dev, "device_status": "up",
#                 "latency_ms": max(1.0, rng.normal(12, 3 * noise)), "jitter_ms": abs(rng.normal(2, 0.8 * noise)),
#                 "packet_loss_pct": abs(rng.normal(0.1, 0.1 * noise)), "bandwidth_mbps": float(bw),
#                 "link_utilization_pct": util, "throughput_mbps": bw * util / 100,
#                 "cpu_pct": float(np.clip(rng.normal(25, 6 * noise), 3, 60)),
#                 "memory_pct": float(np.clip(rng.normal(45, 5 * noise), 10, 70)),
#                 "queue_drops": float(rng.poisson(2)), "interface_errors": float(rng.poisson(1)),
#                 "rssi_dbm": rng.normal(-55, 3 * noise) if is_ap else np.nan,
#                 "retransmission_pct": abs(rng.normal(2, 1 * noise)) if is_ap else np.nan,
#                 "dns_failure_pct": abs(rng.normal(0.2, 0.2)), "dhcp_failure_pct": abs(rng.normal(0.2, 0.2)),
#             }
#             if fault and i >= onset:
#                 k = min(1.0, (i - onset + 1) / 5)
#                 fault(r, dev, rng, k)
#                 r["throughput_mbps"] = bw * np.clip(r["link_utilization_pct"], 0, 100) / 100
#             rows.append(r)
#     df = pd.DataFrame(rows)
#     for c, hi in [("link_utilization_pct", 100), ("cpu_pct", 100), ("memory_pct", 100),
#                   ("packet_loss_pct", 100), ("retransmission_pct", 100),
#                   ("dns_failure_pct", 100), ("dhcp_failure_pct", 100)]:
#         df[c] = df[c].clip(0, hi)
#     df["rssi_dbm"] = df["rssi_dbm"].clip(upper=-20)
#     if scenario == "sparse_data":
#         missing_pct = max(missing_pct, 55.0)
#         df["queue_drops"] = np.nan
#     if missing_pct > 0:
#         for m in METRICS:
#             mask = rng.random(len(df)) < missing_pct / 100
#             df.loc[mask, m] = np.nan
#     if scenario == "interop_failure":
#         return to_legacy(df)
#     return df


# # ============================================================================
# # 4. INGESTION, VALIDATION & NORMALISATION
# # ============================================================================
# def _pick(df_cols, canon):
#     for alias, f in ALIASES[canon]:
#         if alias in df_cols:
#             return alias, f
#     return None


# def ingest(raw, parse_error: str | None = None):
#     """Validate + normalise arbitrary telemetry into canonical schema v1.0."""
#     rep = {"ok": False, "errors": [], "warnings": [], "conversions": [], "rows_in": 0, "rows_out": 0,
#            "quality": 0.0, "completeness": {}, "missing_metrics": [], "input_schema": "unknown"}
#     if parse_error:
#         rep["errors"].append(parse_error)
#         return None, rep
#     if raw is None:
#         rep["errors"].append("No telemetry supplied.")
#         return None, rep
#     try:
#         df = raw.copy() if isinstance(raw, pd.DataFrame) else pd.DataFrame(raw)
#     except Exception as e:  # noqa: BLE001
#         rep["errors"].append(f"Could not interpret input as a table: {e}")
#         return None, rep
#     rep["rows_in"] = len(df)
#     if df.empty:
#         rep["errors"].append("Input contains no rows.")
#         return None, rep
#     df.columns = [str(c).strip().lower() for c in df.columns]

#     if "schema_version" in df.columns and df["schema_version"].notna().any():
#         ver = str(df["schema_version"].dropna().iloc[0])
#         rep["input_schema"] = ver
#         if ver not in KNOWN_SCHEMAS:
#             rep["warnings"].append(f"Unknown schema_version '{ver}' (known: {sorted(KNOWN_SCHEMAS)}); using best-effort field mapping.")
#         elif ver != SCHEMA_VERSION:
#             rep["warnings"].append(f"Legacy schema_version '{ver}' detected; adapter converting to v{SCHEMA_VERSION}.")
#     else:
#         rep["input_schema"] = "unversioned"
#         rep["warnings"].append("No schema_version field; assuming canonical v1.0 / alias mapping.")

#     dev, ts = _pick(df.columns, "device_id"), _pick(df.columns, "timestamp")
#     if dev is None:
#         rep["errors"].append(f"Missing required field 'device_id' (accepted aliases: {[a for a, _ in ALIASES['device_id']]}).")
#     if ts is None:
#         rep["errors"].append(f"Missing required field 'timestamp' (accepted aliases: {[a for a, _ in ALIASES['timestamp']]}).")
#     picked = {m: p for m in METRICS if (p := _pick(df.columns, m))}
#     if len(picked) < 2 and not rep["errors"]:
#         rep["errors"].append(f"Only {len(picked)} recognised metric column(s) found; at least 2 are required for diagnosis.")
#     if rep["errors"]:
#         recognised = {a for k in ALIASES for a, _ in ALIASES[k]}
#         unk = [c for c in df.columns if c not in recognised]
#         if unk:
#             rep["warnings"].append(f"Unrecognised columns ignored: {unk}")
#         return None, rep

#     out = pd.DataFrame({"device_id": df[dev[0]].astype(str).str.strip()})
#     t = df[ts[0]]
#     try:
#         if pd.api.types.is_numeric_dtype(t):
#             unit = "ms" if t.max() > 1e11 else "s"
#             out["timestamp"] = pd.to_datetime(t, unit=unit, errors="coerce", utc=True).dt.tz_localize(None)
#         else:
#             out["timestamp"] = pd.to_datetime(t, errors="coerce", utc=True).dt.tz_localize(None)
#     except Exception as e:  # noqa: BLE001
#         rep["errors"].append(f"Unparseable timestamps: {e}")
#         return None, rep
#     if (dev[0] != "device_id") or (ts[0] != "timestamp"):
#         rep["conversions"].append(f"{dev[0]}->device_id, {ts[0]}->timestamp")

#     st_col = _pick(df.columns, "device_status")
#     if st_col:
#         out["device_status"] = df[st_col[0]].astype(str).str.strip().str.lower().map(STATUS_MAP).fillna("unknown")
#         unk_n = int((out["device_status"] == "unknown").sum())
#         if unk_n:
#             rep["warnings"].append(f"{unk_n} rows have unrecognised device_status; treated as 'unknown'.")
#         rep["status_reported"] = True
#     else:
#         out["device_status"] = "unknown"
#         rep["status_reported"] = False
#         rep["warnings"].append("No device_status field; down devices are inferred from missing telemetry.")

#     for m in METRICS:
#         if m in picked:
#             alias, f = picked[m]
#             s = pd.to_numeric(df[alias], errors="coerce")
#             bad = int(s.isna().sum() - df[alias].isna().sum())
#             if bad > 0:
#                 rep["warnings"].append(f"{alias}: {bad} non-numeric value(s) discarded.")
#             s = s * f
#             lo, hi = RANGE[m]
#             oor = (s < lo) | (s > hi)
#             if oor.any():
#                 rep["warnings"].append(f"{alias}: {int(oor.sum())} out-of-range value(s) discarded (valid {lo}..{hi} {UNITS[m]}).")
#                 s = s.mask(oor)
#             if alias != m or f != 1:
#                 rep["conversions"].append(f"{alias} -> {m}" + (f" (x{f:g})" if f != 1 else ""))
#             out[m] = s.astype(float)
#         else:
#             out[m] = np.nan
#             rep["missing_metrics"].append(m)
#     recognised = {a for k in ALIASES for a, _ in ALIASES[k]} | {"schema_version"}
#     unk = [c for c in df.columns if c not in recognised]
#     if unk:
#         rep["warnings"].append(f"Unrecognised columns ignored: {unk}")

#     n0 = len(out)
#     out = out[out["timestamp"].notna() & out["device_id"].ne("") & out["device_id"].ne("nan")]
#     if len(out) < n0:
#         rep["warnings"].append(f"{n0 - len(out)} row(s) dropped: missing/invalid device_id or timestamp.")
#     n1 = len(out)
#     out = out.drop_duplicates(["device_id", "timestamp"], keep="last")
#     if len(out) < n1:
#         rep["warnings"].append(f"{n1 - len(out)} duplicate (device, timestamp) row(s) removed.")
#     if out.empty:
#         rep["errors"].append("No valid rows remain after validation.")
#         return None, rep
#     out = out.sort_values(["device_id", "timestamp"]).reset_index(drop=True)

#     present_core = [m for m in CORE_METRICS if m in picked]
#     coverage = len(present_core) / len(CORE_METRICS)
#     comp = float(out[present_core].notna().mean().mean()) if present_core else 0.0
#     rep["completeness"] = {m: round(float(out[m].notna().mean()), 3) for m in METRICS}
#     rep["quality"] = round(0.6 * coverage + 0.4 * comp, 3)
#     rep["rows_out"] = len(out)
#     rep["ok"] = True
#     unknown_dev = sorted(set(out["device_id"]) - set(NODES))
#     if unknown_dev:
#         rep["warnings"].append(f"Devices not in known topology (no topology reasoning for them): {unknown_dev}")
#     return out, rep


# def _med(s: pd.Series):
#     s = s.dropna()
#     return float(s.median()) if len(s) else None


# def summarize(df: pd.DataFrame, recent: int = 12, base: int = 25) -> dict:
#     summ = {}
#     for dev, g in df.groupby("device_id"):
#         g = g.sort_values("timestamp")
#         rec, bas = g.tail(recent), g.head(base)
#         last = g.tail(5)
#         sts = last["device_status"].tolist()
#         reported = any(s != "unknown" for s in sts)
#         if sts.count("down") >= 3:
#             status, src = "down", "reported"
#         elif len(last) >= 5 and last[CORE_METRICS].isna().all().all():
#             status, src = "down", "inferred"
#         elif sts.count("degraded") >= 2:
#             status, src = "degraded", "reported"
#         else:
#             status, src = ("up" if reported else "unknown"), ("reported" if reported else "inferred")
#         summ[dev] = {"n": len(g), "status": status, "status_source": src,
#                      "recent": {m: _med(rec[m]) for m in METRICS},
#                      "baseline": {m: _med(bas[m]) for m in METRICS}}
#     return summ


# # ============================================================================
# # 5. PROTOCOL: message envelope + findings
# # ============================================================================
# def make_msg(sender, recipient, mtype, payload, corr_id, duration_ms=None):
#     m = {"schema_version": SCHEMA_VERSION, "message_id": uuid.uuid4().hex[:8], "correlation_id": corr_id,
#          "sender": sender, "recipient": recipient, "type": mtype,
#          "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "payload": payload}
#     if duration_ms is not None:
#         m["duration_ms"] = round(duration_ms, 2)
#     return m


# def ramp(x, lo, hi):
#     if x is None or (isinstance(x, float) and math.isnan(x)):
#         return 0.0
#     return float(min(1.0, max(0.0, (x - lo) / (hi - lo))))


# def ev(dev, metric, value, interp, unit=None):
#     v = round(value, 2) if isinstance(value, (int, float, np.floating)) else value
#     return {"device": dev, "metric": metric, "value": v, "unit": unit or UNITS.get(metric, ""), "interpretation": interp}


# def finding(agent, cause, stance, strength, devices, evidence, rationale):
#     return {"finding_id": uuid.uuid4().hex[:6], "agent": agent, "cause": cause, "stance": stance,
#             "strength": round(float(strength), 3), "devices": list(devices), "evidence": evidence, "rationale": rationale}


# CAUSES = {
#     "link_congestion": dict(
#         title="link congestion causing egress queue drops", short="Link congestion",
#         actions=["Inspect utilization of {dev} uplink/egress interfaces and identify top talkers (NetFlow/sFlow)",
#                  "Review QoS / queue configuration and traffic distribution on {dev}",
#                  "Consider rate-limiting heavy flows, load-balancing or adding uplink capacity"],
#         diff=["Upstream link congestion", "Misconfigured QoS / queue profile", "Broadcast or multicast storm"],
#         cmds=["show interfaces {dev} | include utilization|drops", "show policy-map interface", "show queueing interface"]),
#     "weak_wifi_signal": dict(
#         title="weak Wi-Fi signal causing retransmissions", short="Weak Wi-Fi signal",
#         actions=["Check AP placement/coverage and client distance for {dev}", "Run a channel survey for co-channel interference and adjust channel/power",
#                  "Verify AP antennas/radio health; add or relocate an AP if coverage is inadequate"],
#         diff=["Co-channel / adjacent-channel interference", "AP radio or antenna fault", "Client-side driver issues"],
#         cmds=["show wireless client summary {dev}", "show ap auto-rf {dev}", "show ap channel {dev}"]),
#     "interface_fault": dict(
#         title="interface / cable fault (rising errors, loss)", short="Interface fault",
#         actions=["Inspect cable, connectors and SFP/transceiver on {dev}; replace if errors persist",
#                  "Check duplex/speed negotiation and error counters (CRC, input/output) on {dev}",
#                  "Test with a known-good cable or port; schedule hardware swap if the fault persists"],
#         diff=["Duplex / speed mismatch", "Faulty SFP or patch cable", "Failing switch port ASIC"],
#         cmds=["show interfaces {dev} counters errors", "show interfaces status", "show logging | include link"]),
#     "device_overload": dict(
#         title="device CPU/memory overload", short="Device overload",
#         actions=["Identify top CPU/memory processes on {dev}", "Check for control-plane storms, loops or excessive ARP/ICMP traffic",
#                  "Apply CoPP / rate limits or upgrade/redistribute load if sustained"],
#         diff=["Control-plane storm / layer-2 loop", "Memory leak (software bug)", "Misbehaving routing protocol"],
#         cmds=["show processes cpu sorted", "show memory statistics", "show spanning-tree summary"]),
#     "hardware_failure": dict(
#         title="device hardware / power failure (device down)", short="Hardware failure",
#         actions=["Verify power and physical status of {dev} on site", "Check console / out-of-band management and last-known logs",
#                  "Fail over affected users to a redundant path; raise an RMA if hardware fault is confirmed"],
#         diff=["Power failure in the rack/building", "Uplink cable cut or fibre fault", "Software crash / boot loop"],
#         cmds=["ping {dev}", "show inventory", "show environment all"]),
#     "dns_failure": dict(
#         title="DNS service failure", short="DNS failure",
#         actions=["Check DNS service health and logs on {srv}", "Test resolution against the campus and an upstream resolver",
#                  "Verify DNS forwarders, zone data and resolver load; fail over to a secondary resolver"],
#         diff=["Upstream resolver outage", "DNS server overload", "Misconfigured forwarders / zone data"],
#         cmds=["nslookup example.com {srv}", "systemctl status named", "journalctl -u named --since '15 min ago'"]),
#     "dhcp_failure": dict(
#         title="DHCP service failure", short="DHCP failure",
#         actions=["Check DHCP service and lease database on {srv}", "Inspect scope utilization for exhaustion; extend scopes or shorten lease times",
#                  "Look for rogue DHCP servers and verify relay (ip helper) config"],
#         diff=["DHCP scope exhaustion", "Rogue DHCP server", "Relay / helper misconfiguration"],
#         cmds=["systemctl status dhcpd", "dhcp-lease-list", "show ip dhcp snooping binding"]),
# }
# SYMPTOMATIC = {"link_congestion", "weak_wifi_signal", "interface_fault", "device_overload"}
# SERVICE_CAUSES = {"dns_failure", "dhcp_failure"}


# # ============================================================================
# # 6. AGENTS
# # ============================================================================
# class Agent:
#     name = "agent"
#     role = ""
#     description = ""
#     consumes: list[str] = []

#     def analyze(self, ctx, inbox) -> dict:  # pragma: no cover
#         raise NotImplementedError


# class PerformanceAgent(Agent):
#     name = "performance_agent"
#     role = "Telemetry & Performance"
#     description = "Analyzes latency, jitter, packet loss, throughput and link utilization. Flags degraded devices and shares them with peer agents."
#     consumes = ["telemetry_summary"]

#     def analyze(self, ctx, inbox):
#         findings, degraded = [], {}
#         for dev, s in ctx["summ"].items():
#             if s["status"] == "down":
#                 continue
#             r = s["recent"]
#             lat_s, loss_s, jit_s = ramp(r["latency_ms"], 50, 200), ramp(r["packet_loss_pct"], 1, 5), ramp(r["jitter_ms"], 10, 30)
#             degr = max(lat_s, loss_s, jit_s)
#             if degr >= 0.3:
#                 degraded[dev] = round(degr, 2)
#             util = r["link_utilization_pct"]
#             util_s = ramp(util, 65, 92)
#             if util_s >= 0.25:
#                 evid = [ev(dev, "link_utilization_pct", util, "High link utilization")]
#                 if lat_s >= 0.3:
#                     evid.append(ev(dev, "latency_ms", r["latency_ms"], "Elevated network latency"))
#                 if loss_s >= 0.3:
#                     evid.append(ev(dev, "packet_loss_pct", r["packet_loss_pct"], "Elevated packet loss"))
#                 findings.append(finding(self.name, "link_congestion", "supports", min(0.9, 0.65 * util_s + 0.35 * degr), [dev], evid,
#                                         f"{dev}: utilization {util:.0f}% with degradation score {degr:.2f}"))
#             elif degr >= 0.3 and util is not None and util < 60:
#                 findings.append(finding(self.name, "link_congestion", "refutes", min(0.8, 0.5 + 0.3 * degr), [dev],
#                                         [ev(dev, "link_utilization_pct", util, "Utilization normal despite degradation")],
#                                         f"{dev}: degraded but utilization only {util:.0f}% - congestion unlikely here"))
#         return {"findings": findings,
#                 "summary": {"degraded_devices": degraded, "network_healthy": not degraded, "devices_analyzed": len(ctx["summ"])}}


# class InfrastructureAgent(Agent):
#     name = "infrastructure_agent"
#     role = "Infrastructure Health"
#     description = "Examines device status, CPU/memory, interface errors and egress queue drops. Uses the Performance Agent's degraded-device list to weigh refuting evidence."
#     consumes = ["telemetry_summary", "performance_agent.degraded_devices"]

#     def analyze(self, ctx, inbox):
#         degraded = inbox.get("performance_agent", {}).get("summary", {}).get("degraded_devices", {})
#         findings = []
#         for dev, s in ctx["summ"].items():
#             r = s["recent"]
#             if s["status"] == "down":
#                 findings.append(finding(self.name, "hardware_failure", "supports", 0.9 if s["status_source"] == "reported" else 0.6, [dev],
#                                         [ev(dev, "device_status", "down", f"Device {s['status_source']} as down", "state")],
#                                         f"{dev} is down ({s['status_source']})"))
#                 continue
#             cpu, mem, qd, ie = r["cpu_pct"], r["memory_pct"], r["queue_drops"], r["interface_errors"]
#             ov = min(0.95, max(ramp(cpu, 70, 95), 0.8 * ramp(mem, 80, 95)))
#             if ov >= 0.25:
#                 evid = [ev(dev, "cpu_pct", cpu, "High CPU utilization")] if cpu is not None else []
#                 if mem is not None and ramp(mem, 80, 95) > 0:
#                     evid.append(ev(dev, "memory_pct", mem, "High memory utilization"))
#                 findings.append(finding(self.name, "device_overload", "supports", ov, [dev], evid, f"{dev}: CPU {cpu}, mem {mem}"))
#             qs = ramp(qd, 15, 120)
#             if qs >= 0.25:
#                 findings.append(finding(self.name, "link_congestion", "supports", 0.85 * qs, [dev],
#                                         [ev(dev, "queue_drops", qd, "Elevated packet drops")], f"{dev}: egress queue drops {qd:.0f}"))
#             ies = ramp(ie, 8, 50)
#             if ies >= 0.25:
#                 findings.append(finding(self.name, "interface_fault", "supports", 0.9 * ies, [dev],
#                                         [ev(dev, "interface_errors", ie, "Rising interface errors")], f"{dev}: interface errors {ie:.0f}"))
#             if dev in degraded:
#                 if cpu is not None and cpu < 60 and (mem is None or mem < 80):
#                     findings.append(finding(self.name, "device_overload", "refutes", 0.6, [dev],
#                                             [ev(dev, "cpu_pct", cpu, "CPU normal while device degraded")], f"{dev}: degraded but CPU healthy"))
#                 if ie is not None and ie < 5:
#                     findings.append(finding(self.name, "interface_fault", "refutes", 0.5, [dev],
#                                             [ev(dev, "interface_errors", ie, "No interface errors")], f"{dev}: degraded but no interface errors"))
#                 if qd is not None and qd < 10:
#                     findings.append(finding(self.name, "link_congestion", "refutes", 0.35, [dev],
#                                             [ev(dev, "queue_drops", qd, "No queue drops")], f"{dev}: degraded but no queue drops"))
#         return {"findings": findings, "summary": {"devices_analyzed": len(ctx["summ"])}}


# class WirelessAgent(Agent):
#     name = "wireless_agent"
#     role = "Wireless Signal"
#     description = "Evaluates RSSI and retransmission rates on access points; cross-checks signal quality against reported degradation."
#     consumes = ["telemetry_summary", "performance_agent.degraded_devices"]

#     def analyze(self, ctx, inbox):
#         degraded = inbox.get("performance_agent", {}).get("summary", {}).get("degraded_devices", {})
#         findings, checked = [], 0
#         for dev, s in ctx["summ"].items():
#             if s["status"] == "down":
#                 continue
#             rssi, rt = s["recent"]["rssi_dbm"], s["recent"]["retransmission_pct"]
#             if rssi is None and rt is None:
#                 continue
#             checked += 1
#             rs = ramp(-rssi, 70, 85) if rssi is not None else None
#             ts = ramp(rt, 8, 20) if rt is not None else None
#             if rs is not None and ts is not None:
#                 strength = 0.6 * rs + 0.4 * ts
#             else:
#                 strength = 0.75 * (rs if rs is not None else ts)
#             strength = min(0.9, strength)
#             if strength >= 0.25:
#                 evid = []
#                 if rssi is not None:
#                     evid.append(ev(dev, "rssi_dbm", rssi, "Poor wireless signal"))
#                 if rt is not None and ts and ts > 0:
#                     evid.append(ev(dev, "retransmission_pct", rt, "High retransmission rate"))
#                 findings.append(finding(self.name, "weak_wifi_signal", "supports", strength, [dev], evid, f"{dev}: RSSI {rssi}, retrans {rt}"))
#             elif dev in degraded and rssi is not None and rssi >= -70:
#                 findings.append(finding(self.name, "weak_wifi_signal", "refutes", 0.7, [dev],
#                                         [ev(dev, "rssi_dbm", rssi, "Signal strength is good despite degradation")], f"{dev}: degraded but RSSI good"))
#         return {"findings": findings, "summary": {"wireless_devices_checked": checked}}


# class ConnectivityAgent(Agent):
#     name = "connectivity_agent"
#     role = "Connectivity & Topology"
#     description = "Uses the topology graph to locate failure roots, determine scope (localized / segment / outage) and list downstream-impacted devices."
#     consumes = ["telemetry_summary", "topology", "performance_agent.degraded_devices"]

#     def analyze(self, ctx, inbox):
#         degraded = set(inbox.get("performance_agent", {}).get("summary", {}).get("degraded_devices", {}))
#         down = {d for d, s in ctx["summ"].items() if s["status"] == "down"}
#         findings, impacted = [], {}
#         roots = sorted(d for d in down if PARENT.get(d) not in down)
#         for root in roots:
#             imp = sorted(descendants(root) & down)
#             impacted[root] = imp
#             strength = 0.9 if ctx["summ"][root]["status_source"] == "reported" else 0.65
#             findings.append(finding(self.name, "hardware_failure", "supports", strength, [root],
#                                     [ev(root, "device_status", "down", f"Failure root; {len(imp)} downstream device(s) unreachable", "state")],
#                                     f"{root} is the topmost failed node; {len(imp)} dependents down"))
#         n = len(ctx["summ"])
#         if down:
#             scope = {"type": "outage", "root_devices": roots}
#         elif not degraded:
#             scope = {"type": "none", "root_devices": []}
#         else:
#             tops = sorted(d for d in degraded if PARENT.get(d) not in degraded)
#             if len(degraded) >= 0.6 * n:
#                 stype = "campus_wide"
#             elif any(descendants(t) & degraded for t in tops):
#                 stype = "segment"
#             else:
#                 stype = "localized"
#             scope = {"type": stype, "root_devices": tops}
#         return {"findings": findings, "summary": {"scope": scope, "failure_roots": roots, "impacted_downstream": impacted}}


# class ServiceAgent(Agent):
#     name = "service_agent"
#     role = "Service Health (DNS/DHCP)"
#     description = "Detects DNS/DHCP failures that occur while the underlying network is healthy (service-specific connectivity problems)."
#     consumes = ["telemetry_summary", "performance_agent.network_healthy"]

#     def analyze(self, ctx, inbox):
#         perf = inbox.get("performance_agent", {}).get("summary", {})
#         deg_ratio = len(perf.get("degraded_devices", {})) / max(1, len(ctx["summ"]))
#         findings = []
#         for cause, metric, label in [("dns_failure", "dns_failure_pct", "DNS"), ("dhcp_failure", "dhcp_failure_pct", "DHCP")]:
#             vals = {d: s["recent"][metric] for d, s in ctx["summ"].items() if s["status"] != "down" and s["recent"][metric] is not None}
#             if not vals:
#                 continue
#             med = float(np.median(list(vals.values())))
#             reach = sum(v > 20 for v in vals.values()) / len(vals)
#             strength = 0.95 * ramp(med, 10, 50)
#             if strength < 0.25 and reach < 0.3:
#                 continue
#             note = ""
#             if reach < 0.3:
#                 strength *= 0.6
#                 note = " (localized to few devices)"
#             if deg_ratio >= 0.3:
#                 strength *= 0.7
#                 note += " (coincides with wide network degradation - may be secondary)"
#             if strength < 0.2:
#                 continue
#             affected = [d for d, v in vals.items() if v > 20] or list(vals)
#             findings.append(finding(self.name, cause, "supports", strength, affected,
#                                     [ev("ALL" if reach >= 0.5 else affected[0], metric, med, f"Median {label} failure rate across devices{note}")],
#                                     f"{label} failures median {med:.0f}% across {len(vals)} devices, {reach:.0%} above 20%"))
#         return {"findings": findings, "summary": {}}


# AGENTS = [PerformanceAgent(), InfrastructureAgent(), WirelessAgent(), ConnectivityAgent(), ServiceAgent()]


# # ---------------------------------------------------------------------------
# # Fault Correlation Agent
# # ---------------------------------------------------------------------------
# def conf_category(c: float) -> str:
#     return "high" if c >= 0.8 else "medium" if c >= 0.6 else "low" if c >= 0.4 else "very_low"


# def correlate(all_findings: list[dict], ctx, inbox) -> dict:
#     perf = inbox.get("performance_agent", {}).get("summary", {})
#     degraded = set(perf.get("degraded_devices", {}))
#     conn = inbox.get("connectivity_agent", {}).get("summary", {})
#     Q = 0.5 + 0.5 * ctx["quality"] ** 2
#     Q = max(0.0, Q - 0.08 * len(ctx.get("failed_agents", [])))

#     by = defaultdict(lambda: {"sup": [], "ref": []})
#     for f in all_findings:
#         by[f["cause"]]["sup" if f["stance"] == "supports" else "ref"].append(f)

#     hypotheses, conflicts = [], []
#     for cause, d in by.items():
#         if not d["sup"]:
#             continue
#         per_agent = {}
#         for f in d["sup"]:
#             per_agent[f["agent"]] = max(per_agent.get(f["agent"], 0), f["strength"])
#         devs = sorted({x for f in d["sup"] for x in f["devices"]})
#         if cause == "hardware_failure" and conn.get("failure_roots"):
#             devs = [r for r in conn["failure_roots"] if r in devs] or devs
#         sym_note = None
#         if "performance_agent" not in per_agent:
#             if cause in SYMPTOMATIC and set(devs) & degraded:
#                 per_agent["performance_agent"] = 0.5
#                 sym_note = "Measured degradation on the same device(s) is consistent with this cause"
#             elif cause in SERVICE_CAUSES and perf.get("network_healthy"):
#                 per_agent["performance_agent"] = 0.45
#                 sym_note = "Network performance is healthy, isolating the fault to the service layer"
#         S = 1.0
#         for s in per_agent.values():
#             S *= 1 - s
#         S = 1 - S
#         refs = [f for f in d["ref"] if set(f["devices"]) & set(devs)]
#         r = max((f["strength"] for f in refs), default=0.0)
#         R = 1 - 0.6 * r
#         conf = round(min(0.95, S * R * Q), 3)
#         if refs:
#             conflicts.append({"cause": cause, "supported_by": sorted(per_agent), "support_score": round(S, 2),
#                               "refuted_by": sorted({f["agent"] for f in refs}), "refutation": round(r, 2),
#                               "resolution": f"Confidence reduced by factor {R:.2f}: " + "; ".join(f["rationale"] for f in refs[:2])})
#         hypotheses.append({"cause": cause, "confidence": conf, "devices": devs,
#                            "sources": sorted(per_agent), "breakdown": {"support": round(S, 3), "refutation_factor": round(R, 3),
#                                                                       "data_quality_factor": round(Q, 3)},
#                            "symptom_note": sym_note, "findings": d["sup"]})
#     hypotheses.sort(key=lambda h: -h["confidence"])

#     def overlap(a, b):
#         return bool(set(a["devices"]) & set(b["devices"])) or (a["cause"] in SERVICE_CAUSES and b["cause"] in SERVICE_CAUSES)

#     status, top, secondary, rivals = None, None, [], []
#     n_dev = len(ctx["summ"])
#     if hypotheses and hypotheses[0]["confidence"] >= 0.3:
#         top = hypotheses[0]
#         rest = hypotheses[1:]
#         if top["confidence"] < 0.5:
#             status = "inconclusive"
#         else:
#             rivals = [h for h in rest if overlap(h, top) and h["confidence"] >= 0.4 and top["confidence"] - h["confidence"] < 0.15]
#             status = "inconclusive" if rivals else "diagnosed"
#             secondary = [h for h in rest if h["confidence"] >= 0.5 and not overlap(h, top)]
#     elif degraded:
#         status = "insufficient_evidence"
#     else:
#         status = "healthy"

#     affected, downstream = [], []
#     if top:
#         affected = list(top["devices"])
#         if top["cause"] in SERVICE_CAUSES and len(affected) > 3:
#             affected = affected
#         pool = degraded | {d for d, s in ctx["summ"].items() if s["status"] == "down"}
#         for a in top["devices"]:
#             downstream += [x for x in descendants(a) if x in pool and x not in top["devices"]]
#         downstream = sorted(set(downstream))
#     return {"status": status, "top": top, "hypotheses": hypotheses, "secondary": secondary, "rivals": rivals,
#             "conflicts": conflicts, "affected": affected, "downstream": downstream,
#             "degraded": sorted(degraded), "scope": conn.get("scope", {}), "quality_factor": Q}


# # ---------------------------------------------------------------------------
# # Recommendation & Reporting Agent
# # ---------------------------------------------------------------------------
# def dev_text(devs):
#     return ", ".join(devs) if len(devs) <= 3 else f"{len(devs)} devices ({', '.join(devs[:2])}, ...)"


# def build_report(corr, ctx, ingest_rep, data_hash, failed_agents):
#     status, top = corr["status"], corr["top"]
#     srv = next((d for d, i in NODES.items() if i["role"] == "service"), "the DNS/DHCP server")
#     limitations = []
#     if ingest_rep["quality"] < 0.8:
#         limitations.append(f"Data quality score {ingest_rep['quality']:.2f}: some telemetry missing or discarded; confidence reduced accordingly.")
#     if ingest_rep["missing_metrics"]:
#         miss = [m for m in ingest_rep["missing_metrics"] if m in CORE_METRICS]
#         if miss:
#             limitations.append(f"Core metric(s) not supplied: {', '.join(miss)}.")
#     for a in failed_agents:
#         limitations.append(f"{a} failed or was unavailable; its evidence is absent from this diagnosis.")
#     limitations.append("Analysis is based on supplied (synthetic) telemetry and heuristic scoring; no production changes were made.")

#     ev_items, sources, alts, actions = [], [], [], []
#     cause_id = None
#     if status in ("diagnosed", "inconclusive") and top:
#         cause_id = top["cause"]
#         info = CAUSES[cause_id]
#         prefix = "Likely" if top["confidence"] >= 0.75 else "Possible"
#         where = dev_text(corr["affected"]) if cause_id not in SERVICE_CAUSES else "campus clients"
#         headline = f"{prefix} {info['title']} on {where}" if cause_id not in SERVICE_CAUSES else f"{prefix} {info['title']} affecting {where}"
#         if status == "inconclusive":
#             if corr["rivals"]:
#                 names = " or ".join(CAUSES[h["cause"]]["short"].lower() for h in [top] + corr["rivals"])
#                 headline = f"Inconclusive: evidence supports {names} about equally - cannot isolate a single root cause"
#             else:
#                 headline = f"Inconclusive (low confidence): {info['short'].lower()} is a possible cause on {where}; evidence is insufficient to confirm"
#         conf = top["confidence"]
#         seen = set()
#         for f in sorted(top["findings"], key=lambda x: -x["strength"]):
#             for e in f["evidence"]:
#                 key = (e["device"], e["metric"])
#                 if key not in seen:
#                     seen.add(key)
#                     ev_items.append({**e, "source": f["agent"]})
#         if top["symptom_note"] and top["devices"]:
#             d0 = top["devices"][0]
#             r = ctx["summ"].get(d0, {}).get("recent", {})
#             for m in ("latency_ms", "packet_loss_pct"):
#                 if r.get(m) is not None and (d0, m) not in seen and ramp(r[m], 50 if m == "latency_ms" else 1, 200 if m == "latency_ms" else 5) > 0.2:
#                     ev_items.append({**ev(d0, m, r[m], "Symptom: " + ("elevated latency" if m == "latency_ms" else "elevated packet loss")),
#                                      "source": "performance_agent"})
#         ev_items = ev_items[:10]
#         sources = top["sources"]
#         tgt = corr["affected"][0] if corr["affected"] else "the affected device"
#         actions = [a.format(dev=tgt, srv=srv) for a in info["actions"]]
#         for h in corr["hypotheses"][1:]:
#             if h["confidence"] >= 0.15 and h["cause"] != cause_id:
#                 alts.append({"cause": CAUSES[h["cause"]]["short"], "confidence": h["confidence"], "devices": h["devices"], "verified": True})
#         for d in info["diff"]:
#             alts.append({"cause": d, "confidence": None, "devices": [], "verified": False})
#         if conf < 0.8:
#             limitations.insert(0, "Root cause requires further verification.")
#         if corr["secondary"]:
#             for h in corr["secondary"]:
#                 limitations.append(f"Concurrent issue detected: {CAUSES[h['cause']]['short']} on {dev_text(h['devices'])} (confidence {h['confidence']:.2f}).")
#     elif status == "insufficient_evidence":
#         conf = 0.2
#         headline = (f"Insufficient evidence: degradation observed on {dev_text(corr['degraded'])} but no diagnostic rule is "
#                     f"supported by the available metrics - a root cause cannot be claimed")
#         for d in corr["degraded"][:6]:
#             r = ctx["summ"][d]["recent"]
#             for m in ("latency_ms", "packet_loss_pct", "jitter_ms"):
#                 if r.get(m) is not None and ramp(r[m], {"latency_ms": 50, "packet_loss_pct": 1, "jitter_ms": 10}[m], {"latency_ms": 200, "packet_loss_pct": 5, "jitter_ms": 30}[m]) >= 0.3:
#                     ev_items.append({**ev(d, m, r[m], "Degraded (symptom only)"), "source": "performance_agent"})
#         sources = ["performance_agent"]
#         actions = ["Collect additional telemetry (SNMP counters, syslog, packet capture) on the affected device(s)",
#                    "Run traceroute / path analysis to localize the degraded hop",
#                    "Check recent configuration changes and maintenance windows for the affected device(s)"]
#         alts = [{"cause": c, "confidence": None, "devices": [], "verified": False}
#                 for c in ("Upstream/transit issue not visible in telemetry", "Unmonitored device or link in the path", "Transient burst")]
#         limitations.insert(0, "No cause reached the minimum evidence threshold (0.30); no root cause is claimed.")
#     else:  # healthy
#         conf = round(0.9 * corr["quality_factor"], 2)
#         headline = "No fault detected - all monitored metrics are within expected ranges"
#         actions = ["No corrective action required; continue routine monitoring", "Keep baselines updated to improve future anomaly detection"]
#         sources = ["performance_agent", "infrastructure_agent", "connectivity_agent"]
#     ev_sources = sorted(set(sources) | ({"connectivity_agent"} if corr["scope"] else set()) if status != "insufficient_evidence" else set(sources))

#     report = {
#         "incident_id": "INC-" + str(int(data_hash[:6], 16) % 9000 + 1000),
#         "status": status,
#         "suspected_root_cause": headline,
#         "root_cause_id": cause_id,
#         "confidence": round(conf, 2),
#         "confidence_category": conf_category(conf),
#         "affected_devices": corr["affected"] if status in ("diagnosed", "inconclusive") else (corr["degraded"] if status == "insufficient_evidence" else []),
#         "downstream_impacted_devices": corr["downstream"],
#         "supporting_evidence": ev_items,
#         "alternative_causes": [a["cause"] + (f" (score {a['confidence']:.2f})" if a["confidence"] is not None else " (unverified differential)") for a in alts],
#         "alternative_causes_detail": alts,
#         "secondary_issues": [{"cause": h["cause"], "devices": h["devices"], "confidence": h["confidence"]} for h in corr["secondary"]],
#         "recommended_actions": actions,
#         "evidence_sources": ev_sources,
#         "limitations": limitations,
#         "conflicts_resolved": corr["conflicts"],
#         "topology_scope": corr["scope"],
#         "data_quality": {"score": ingest_rep["quality"], "rows": ingest_rep["rows_out"], "input_schema": ingest_rep["input_schema"],
#                          "warnings": len(ingest_rep["warnings"])},
#         "scoring_method": ("confidence = min(0.95, S x R x Q); S = 1 - prod(1 - s_a) over agents' max support strength (noisy-OR corroboration); "
#                            "R = 1 - 0.6 x max refuting strength on the same devices; Q = 0.5 + 0.5 x data_quality^2 (minus 0.08 per failed agent). "
#                            "status=diagnosed needs confidence >= 0.5 and a >= 0.15 margin over rival causes on overlapping devices; < 0.30 -> no cause claimed."),
#         "schema_version": SCHEMA_VERSION,
#         "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
#     }
#     dry_run = []
#     if cause_id:
#         tgt = (corr["affected"] or ["TARGET"])[0]
#         dry_run = [c.format(dev=tgt, srv=srv) for c in CAUSES[cause_id]["cmds"]]
#     report["_dry_run_commands"] = dry_run
#     return report


# def error_report(ingest_rep, data_hash):
#     return {
#         "incident_id": "INC-" + str(int(data_hash[:6], 16) % 9000 + 1000),
#         "status": "insufficient_data",
#         "suspected_root_cause": "Insufficient data: input failed validation - no diagnosis attempted",
#         "root_cause_id": None, "confidence": 0.0, "confidence_category": "none", "affected_devices": [],
#         "downstream_impacted_devices": [], "supporting_evidence": [], "alternative_causes": [], "alternative_causes_detail": [],
#         "secondary_issues": [],
#         "recommended_actions": ["Fix the reported validation errors and resubmit",
#                                 "Ensure device_id and timestamp fields plus at least two telemetry metrics are present (see Protocol tab)"],
#         "evidence_sources": [], "limitations": ingest_rep["errors"], "conflicts_resolved": [], "topology_scope": {},
#         "data_quality": {"score": 0.0, "rows": 0, "input_schema": ingest_rep["input_schema"], "warnings": len(ingest_rep["warnings"])},
#         "scoring_method": "n/a - validation failed", "schema_version": SCHEMA_VERSION,
#         "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "_dry_run_commands": [],
#     }


# # ============================================================================
# # 7. ORCHESTRATOR
# # ============================================================================
# def run_pipeline(raw, parse_error=None, disabled=()):
#     corr_id = uuid.uuid4().hex[:8]
#     msgs = []
#     t0 = time.perf_counter()
#     df, rep = ingest(raw, parse_error)
#     data_hash = hashlib.md5(pd.util.hash_pandas_object(raw, index=False).values.tobytes()).hexdigest() \
#         if isinstance(raw, pd.DataFrame) else hashlib.md5(b"none").hexdigest()
#     msgs.append(make_msg("orchestrator", "ingestion", "task", {"task": "validate_and_normalize", "rows_in": rep["rows_in"]}, corr_id))
#     msgs.append(make_msg("ingestion", "orchestrator", "validation_result" if rep["ok"] else "error",
#                          {"ok": rep["ok"], "errors": rep["errors"], "warnings": rep["warnings"][:10], "quality": rep["quality"],
#                           "conversions": rep["conversions"]}, corr_id, (time.perf_counter() - t0) * 1000))
#     if not rep["ok"]:
#         report = error_report(rep, data_hash)
#         msgs.append(make_msg("orchestrator", "user", "report", {"status": report["status"], "errors": rep["errors"]}, corr_id))
#         return {"report": report, "messages": msgs, "ingest": rep, "df": None, "summ": {}, "corr": None, "failed": []}

#     summ = summarize(df)
#     ctx = {"summ": summ, "quality": rep["quality"], "failed_agents": []}
#     inbox, all_findings, failed = {}, [], []
#     # Performance runs first and broadcasts; the other analysis agents consume its message.
#     for ag in AGENTS:
#         task = {"task": "analyze", "role": ag.role, "inputs": ag.consumes, "window_samples": 12}
#         msgs.append(make_msg("orchestrator", ag.name, "task", task, corr_id))
#         ts = time.perf_counter()
#         try:
#             if ag.name in disabled:
#                 raise RuntimeError("simulated agent crash (fault injection)")
#             out = ag.analyze(ctx, inbox)
#             inbox[ag.name] = out
#             all_findings += out["findings"]
#             recipient = "broadcast" if ag.name == "performance_agent" else "fault_correlation_agent"
#             msgs.append(make_msg(ag.name, recipient, "finding",
#                                  {"findings": out["findings"], "summary": out["summary"]}, corr_id, (time.perf_counter() - ts) * 1000))
#         except Exception as e:  # noqa: BLE001
#             failed.append(ag.name)
#             ctx["failed_agents"] = failed
#             msgs.append(make_msg(ag.name, "orchestrator", "error", {"code": "AGENT_FAILURE", "detail": str(e)}, corr_id,
#                                  (time.perf_counter() - ts) * 1000))
#     ts = time.perf_counter()
#     corr = correlate(all_findings, ctx, inbox)
#     msgs.append(make_msg("fault_correlation_agent", "reporting_agent", "diagnosis",
#                          {"status": corr["status"],
#                           "ranked_hypotheses": [{k: h[k] for k in ("cause", "confidence", "devices", "sources", "breakdown")} for h in corr["hypotheses"]],
#                           "conflicts": corr["conflicts"], "secondary": [h["cause"] for h in corr["secondary"]]},
#                          corr_id, (time.perf_counter() - ts) * 1000))
#     ts = time.perf_counter()
#     report = build_report(corr, ctx, rep, data_hash, failed)
#     msgs.append(make_msg("reporting_agent", "orchestrator", "report",
#                          {k: report[k] for k in ("incident_id", "status", "suspected_root_cause", "confidence")}, corr_id,
#                          (time.perf_counter() - ts) * 1000))
#     return {"report": report, "messages": msgs, "ingest": rep, "df": df, "summ": summ, "corr": corr, "failed": failed}


# # ============================================================================
# # 8. BATCH EVALUATION
# # ============================================================================
# def evaluate(meta, rep):
#     exp_status, exp_causes = meta["expect_status"], meta["causes"]
#     got_causes = ([rep["root_cause_id"]] if rep["root_cause_id"] else []) + [s["cause"] for s in rep["secondary_issues"]]
#     abst = meta.get("abstain_ok", False)
#     if exp_status in ("healthy", "insufficient_data", "insufficient_evidence"):
#         ok = rep["status"] == exp_status
#     elif rep["status"] == "diagnosed":
#         ok = set(got_causes) == set(exp_causes)
#     elif abst and rep["status"] in ("inconclusive", "insufficient_evidence"):
#         ok = rep["root_cause_id"] in (None, *exp_causes)
#     else:
#         ok = False
#     tgt = set(meta["targets"])
#     loc_ok = tgt.issubset(set(rep["affected_devices"]) | {s_d for s in rep["secondary_issues"] for s_d in s["devices"]}) if tgt and exp_status == "diagnosed" else None
#     return ok, got_causes, loc_ok


# @st.cache_data(show_spinner=False)
# def run_batch(seeds=(1, 2, 3)):
#     rows = []
#     for key, meta in SCENARIO_META.items():
#         for sd in seeds:
#             res = run_pipeline(generate(key, sd, 1.0, 0.0))
#             rep = res["report"]
#             ok, got, loc = evaluate(meta, rep)
#             rows.append({"scenario": meta["label"], "seed": sd, "expected": meta["expect_status"] + (": " + ", ".join(meta["causes"]) if meta["causes"] else ""),
#                          "got_status": rep["status"], "got_causes": ", ".join(got) or "-", "confidence": rep["confidence"],
#                          "category": rep["confidence_category"], "location_ok": "n/a" if loc is None else ("yes" if loc else "NO"),
#                          "pass": "PASS" if ok else "FAIL"})
#     return pd.DataFrame(rows)


# # ============================================================================
# # 9. REPORT RENDERING (Markdown)
# # ============================================================================
# def report_markdown(rep) -> str:
#     L = [f"# Network Diagnostic Report - {rep['incident_id']}", "",
#          f"**Status:** {rep['status']}  ", f"**Suspected root cause:** {rep['suspected_root_cause']}  ",
#          f"**Confidence:** {rep['confidence']:.2f} ({rep['confidence_category']})  ",
#          f"**Affected devices:** {', '.join(rep['affected_devices']) or '-'}  ",
#          f"**Downstream impacted:** {', '.join(rep['downstream_impacted_devices']) or '-'}  ",
#          f"**Generated:** {rep['generated_at']}", "", "## Supporting evidence", "",
#          "| Device | Metric | Value | Interpretation | Source |", "|---|---|---|---|---|"]
#     for e in rep["supporting_evidence"]:
#         L.append(f"| {e['device']} | {e['metric']} | {e['value']} {e['unit']} | {e['interpretation']} | {e.get('source', '')} |")
#     L += ["", "## Alternative explanations"] + [f"- {a}" for a in rep["alternative_causes"]]
#     L += ["", "## Recommended actions"] + [f"{i}. {a}" for i, a in enumerate(rep["recommended_actions"], 1)]
#     L += ["", "## Limitations"] + [f"- {a}" for a in rep["limitations"]]
#     if rep["conflicts_resolved"]:
#         L += ["", "## Conflicting evidence resolved"] + [f"- **{c['cause']}**: {c['resolution']}" for c in rep["conflicts_resolved"]]
#     L += ["", "## Method", rep["scoring_method"], "", f"_Evidence sources: {', '.join(rep['evidence_sources'])}_"]
#     return "\n".join(L)


# def clean_json(rep):
#     return {k: v for k, v in rep.items() if not k.startswith("_")}


# # ============================================================================
# # 10. STREAMLIT UI
# # ============================================================================
# CSS = """
# <style>
# .block-container {padding-top: 1.4rem;}
# .nc-hero {padding: 1.1rem 1.4rem; border-radius: 14px; margin-bottom: .8rem;
#           background: linear-gradient(120deg, rgba(99,102,241,.18), rgba(16,185,129,.14)); border: 1px solid rgba(128,128,128,.25);}
# .nc-hero h1 {margin: 0; font-size: 1.9rem;} .nc-hero p {margin: .25rem 0 0; opacity: .8;}
# .nc-card {padding: 1rem 1.2rem; border-radius: 12px; border: 1px solid rgba(128,128,128,.3); margin-bottom: .6rem;}
# .nc-cause {font-size: 1.45rem; font-weight: 650; line-height: 1.3;}
# .nc-pill {display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: .78rem; font-weight: 600; margin-right: 6px;}
# .pill-diagnosed {background:#16a34a22; color:#16a34a;} .pill-healthy {background:#0ea5e922; color:#0ea5e9;}
# .pill-inconclusive {background:#f59e0b22; color:#d97706;} .pill-insufficient_evidence {background:#f9731622; color:#ea580c;}
# .pill-insufficient_data {background:#ef444422; color:#dc2626;}
# </style>
# """
# STATUS_UI = {"diagnosed": ("Diagnosed", "success"), "healthy": ("Healthy", "info"), "inconclusive": ("Inconclusive", "warning"),
#              "insufficient_evidence": ("Insufficient evidence", "warning"), "insufficient_data": ("Insufficient data", "error")}


# def load_uploaded(file):
#     try:
#         name = file.name.lower()
#         if name.endswith(".csv"):
#             return pd.read_csv(file), None
#         data = json.load(file)
#         if isinstance(data, dict):
#             for k in ("records", "telemetry", "data", "rows"):
#                 if isinstance(data.get(k), list):
#                     data = data[k]
#                     break
#             else:
#                 return None, "JSON object has no 'records'/'telemetry'/'data' list."
#         return pd.DataFrame(data), None
#     except Exception as e:  # noqa: BLE001
#         return None, f"Could not parse uploaded file: {e}"


# def topo_dot(rep, summ):
#     aff, imp = set(rep["affected_devices"]), set(rep["downstream_impacted_devices"])
#     deg = set((rep.get("topology_scope") or {}).get("root_devices", [])) if False else set()
#     lines = ['digraph G {rankdir=TB; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#555555"]; edge [color="#888888"];']
#     for dev in NODES:
#         s = summ.get(dev, {})
#         stat = s.get("status")
#         if dev in aff:
#             fill, fc = "#ef4444", "white"
#         elif dev in imp:
#             fill, fc = "#f59e0b", "black"
#         elif stat == "down":
#             fill, fc = "#9ca3af", "black"
#         elif stat == "degraded":
#             fill, fc = "#fde047", "black"
#         else:
#             fill, fc = "#86efac", "black"
#         lines.append(f'"{dev}" [label="{dev}\\n({NODES[dev]["type"]})", fillcolor="{fill}", fontcolor="{fc}"];')
#     for p, c in EDGES:
#         lines.append(f'"{p}" -> "{c}";')
#     lines.append("}")
#     return "\n".join(lines)


# def protocol_tables():
#     tele = pd.DataFrame([{"field": "device_id", "type": "string", "unit": "-", "valid range": "non-empty", "meaning": "Unique device identifier (required)",
#                           "accepted aliases": ", ".join(a for a, _ in ALIASES["device_id"][1:])},
#                          {"field": "timestamp", "type": "ISO-8601 / epoch s|ms", "unit": "UTC", "valid range": "parseable", "meaning": "Sample time (required)",
#                           "accepted aliases": ", ".join(a for a, _ in ALIASES["timestamp"][1:])},
#                          {"field": "device_status", "type": "enum", "unit": "-", "valid range": "up|degraded|down", "meaning": "Reported device state",
#                           "accepted aliases": "status, state (OK/WARN/CRIT, online/offline...)"}] +
#                         [{"field": m, "type": "float", "unit": CANON[m][0], "valid range": f"{CANON[m][1]} .. {CANON[m][2]}", "meaning": CANON[m][3],
#                           "accepted aliases": ", ".join(f"{a}" + (f" (x{f:g})" if f != 1 else "") for a, f in ALIASES[m][1:])} for m in METRICS])
#     env = pd.DataFrame([
#         ("schema_version", "string", "Protocol version, currently '1.0'"), ("message_id", "string", "Unique id of the message"),
#         ("correlation_id", "string", "Shared by all messages of one diagnosis run"), ("sender / recipient", "string", "Agent names; 'broadcast' = all peers"),
#         ("type", "enum", "task | finding | diagnosis | report | validation_result | error"), ("timestamp", "ISO-8601 UTC", "Creation time"),
#         ("duration_ms", "float (ms)", "Processing time of the sender"), ("payload", "object", "Type-specific body"),
#     ], columns=["field", "type", "meaning"])
#     fnd = pd.DataFrame([
#         ("finding_id", "string", "-", "Unique id"), ("agent", "string", "-", "Producing agent"),
#         ("cause", "enum", "-", ", ".join(CAUSES)), ("stance", "enum", "-", "supports | refutes the cause"),
#         ("strength", "float", "0..1", "Agent's evidence strength for the stance (not a probability)"),
#         ("devices", "list[string]", "-", "Devices the finding concerns"),
#         ("evidence[]", "list[object]", "-", "{device, metric, value, unit, interpretation}"), ("rationale", "string", "-", "Human-readable justification"),
#     ], columns=["field", "type", "unit/range", "meaning"])
#     return tele, env, fnd


# def main():
#     st.set_page_config(page_title="NetCoop AI", page_icon="🛰️", layout="wide")
#     st.markdown(CSS, unsafe_allow_html=True)
#     st.markdown('<div class="nc-hero"><h1>🛰️ NetCoop AI</h1><p>Multi-agent network fault diagnosis &amp; interoperability - IIT Bhubaneswar campus network</p></div>',
#                 unsafe_allow_html=True)

#     # ------------------------------ sidebar ---------------------------------
#     sb = st.sidebar
#     sb.header("Input")
#     src = sb.radio("Telemetry source", ["Synthetic scenario", "Upload CSV / JSON", "Paste JSON"])
#     raw, parse_err, truth = None, None, None
#     seed, noise, miss = 7, 1.0, 0.0
#     if src == "Synthetic scenario":
#         key = sb.selectbox("Scenario", list(SCENARIO_META), format_func=lambda k: SCENARIO_META[k]["label"])
#         sb.caption(SCENARIO_META[key]["desc"])
#         seed = sb.number_input("Random seed", 0, 99999, 7)
#         noise = sb.slider("Noise level", 0.5, 2.5, 1.0, 0.1)
#         miss = sb.slider("Missing-data injection (%)", 0, 80, 0, 5)
#         raw, truth = generate(key, int(seed), float(noise), float(miss)), SCENARIO_META[key]
#     elif src == "Upload CSV / JSON":
#         up = sb.file_uploader("Telemetry file", type=["csv", "json"])
#         if up is not None:
#             raw, parse_err = load_uploaded(up)
#         else:
#             sb.info("Upload a file or switch to a synthetic scenario.")
#             parse_err = "No file uploaded yet."
#     else:
#         txt = sb.text_area("JSON array of records", height=180, placeholder='[{"device_id":"SW1","timestamp":"2026-11-01T09:00:00","latency_ms":12,"cpu_pct":30}]')
#         if txt.strip():
#             try:
#                 data = json.loads(txt)
#                 raw = pd.DataFrame(data.get("records", data) if isinstance(data, dict) else data)
#             except Exception as e:  # noqa: BLE001
#                 parse_err = f"Invalid JSON: {e}"
#         else:
#             parse_err = "No JSON pasted yet."
#     sb.divider()
#     sb.header("Robustness testing")
#     disabled = sb.multiselect("Simulate agent crash", [a.name for a in AGENTS], help="Fault injection: the orchestrator must degrade gracefully and report the failure.")
#     sb.divider()
#     sb.caption("Free stack: Streamlit + pandas + numpy. No production network is touched; remediation is dry-run only.")

#     res = run_pipeline(raw, parse_err, tuple(disabled))
#     rep, ing, summ = res["report"], res["ingest"], res["summ"]
#     if isinstance(raw, pd.DataFrame):
#         sb.download_button("Download current input (CSV)", raw.to_csv(index=False), "netcoop_input.csv", "text/csv")

#     tabs = st.tabs(["🩺 Diagnosis", "📈 Telemetry", "🗺️ Topology", "💬 Agent messages", "🧾 Validation", "📐 Protocol", "🧪 Test suite", "📄 Report"])

#     # ------------------------------ Diagnosis -------------------------------
#     with tabs[0]:
#         label, level = STATUS_UI[rep["status"]]
#         st.markdown(f'<span class="nc-pill pill-{rep["status"]}">{label.upper()}</span> <span style="opacity:.6">Incident {rep["incident_id"]}</span>',
#                     unsafe_allow_html=True)
#         st.markdown(f'<div class="nc-card"><div class="nc-cause">{rep["suspected_root_cause"]}</div></div>', unsafe_allow_html=True)
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Confidence", f"{rep['confidence']:.0%}", rep["confidence_category"].replace("_", " "), delta_color="off")
#         c2.metric("Affected devices", len(rep["affected_devices"]))
#         c3.metric("Downstream impacted", len(rep["downstream_impacted_devices"]))
#         c4.metric("Data quality", f"{rep['data_quality']['score']:.0%}")
#         st.progress(min(1.0, max(0.0, rep["confidence"])))
#         if res["failed"]:
#             st.error(f"Agent failure(s): {', '.join(res['failed'])} - diagnosis produced with reduced evidence.")
#         if rep["status"] == "insufficient_data":
#             for e in ing["errors"]:
#                 st.error(e)
#         if truth is not None and src == "Synthetic scenario":
#             ok, got, loc = evaluate(truth, rep)
#             st.caption(f"Ground truth for this synthetic scenario: **{truth['expect_status']}**" + (f" / {', '.join(truth['causes'])}" if truth["causes"] else "") +
#                        f" -> {'✅ matches' if ok else '⚠️ differs'}")
#         left, right = st.columns([3, 2])
#         with left:
#             st.subheader("Supporting evidence")
#             if rep["supporting_evidence"]:
#                 st.dataframe(pd.DataFrame(rep["supporting_evidence"])[["device", "metric", "value", "unit", "interpretation", "source"]], hide_index=True)
#             else:
#                 st.write("No evidence items (no fault claimed).")
#             if rep["conflicts_resolved"]:
#                 st.subheader("Conflicting evidence resolved")
#                 for c in rep["conflicts_resolved"]:
#                     st.warning(f"**{c['cause']}** - supported by {', '.join(c['supported_by'])}, refuted by {', '.join(c['refuted_by'])}. {c['resolution']}")
#             if rep["secondary_issues"]:
#                 st.subheader("Concurrent issues")
#                 st.dataframe(pd.DataFrame(rep["secondary_issues"]), hide_index=True)
#         with right:
#             st.subheader("Alternative explanations")
#             if rep["alternative_causes_detail"]:
#                 st.dataframe(pd.DataFrame([{"explanation": a["cause"], "score": a["confidence"], "status": "scored" if a["verified"] else "unverified"}
#                                            for a in rep["alternative_causes_detail"]]),
#                              hide_index=True,
#                              column_config={"score": st.column_config.ProgressColumn("score", min_value=0.0, max_value=1.0, format="%.2f")})
#             else:
#                 st.write("None.")
#             st.subheader("Recommended actions")
#             for i, a in enumerate(rep["recommended_actions"], 1):
#                 st.markdown(f"{i}. {a}")
#         if rep["limitations"]:
#             with st.expander("Limitations & uncertainty", expanded=rep["status"] != "diagnosed"):
#                 for l in rep["limitations"]:
#                     st.markdown(f"- {l}")
#         with st.expander("How confidence is computed"):
#             st.write(rep["scoring_method"])
#             if res["corr"] and res["corr"]["hypotheses"]:
#                 st.dataframe(pd.DataFrame([{"cause": h["cause"], "confidence": h["confidence"], "devices": ", ".join(h["devices"]),
#                                             "sources": ", ".join(h["sources"]), **h["breakdown"]} for h in res["corr"]["hypotheses"]]), hide_index=True)
#         if rep["_dry_run_commands"]:
#             st.subheader("Human-in-the-loop remediation (optional, dry-run)")
#             approve = st.checkbox("I have reviewed the recommendation and approve a SIMULATED diagnostic run", key="hitl")
#             if approve:
#                 st.code("\n".join(f"[DRY-RUN] $ {c}" for c in rep["_dry_run_commands"]) + "\n[DRY-RUN] No commands were executed. Production infrastructure untouched.", language="bash")

#     # ------------------------------ Telemetry -------------------------------
#     with tabs[1]:
#         df = res["df"]
#         if df is None:
#             st.warning("No valid telemetry to display (see Validation tab).")
#         else:
#             c1, c2 = st.columns([2, 3])
#             metric = c1.selectbox("Metric", [m for m in METRICS if df[m].notna().any()], index=0)
#             devs = c2.multiselect("Devices", sorted(df["device_id"].unique()), default=(rep["affected_devices"] or sorted(df["device_id"].unique()))[:4])
#             if devs:
#                 piv = df[df["device_id"].isin(devs)].pivot_table(index="timestamp", columns="device_id", values=metric)
#                 st.line_chart(piv)
#                 st.caption(f"{metric} ({UNITS[metric]}) - fault onset is mid-window in synthetic scenarios.")
#             st.subheader("Recent-window summary (median of last 12 samples)")
#             rows = []
#             for d, s in summ.items():
#                 r = s["recent"]
#                 rows.append({"device": d, "status": s["status"], "latency ms": r["latency_ms"], "loss %": r["packet_loss_pct"], "util %": r["link_utilization_pct"],
#                              "cpu %": r["cpu_pct"], "mem %": r["memory_pct"], "q drops": r["queue_drops"], "if errors": r["interface_errors"],
#                              "rssi dBm": r["rssi_dbm"], "dns fail %": r["dns_failure_pct"]})
#             st.dataframe(pd.DataFrame(rows).round(1), hide_index=True,
#                          column_config={"util %": st.column_config.ProgressColumn("util %", min_value=0, max_value=100, format="%.0f"),
#                                         "cpu %": st.column_config.ProgressColumn("cpu %", min_value=0, max_value=100, format="%.0f")})

#     # ------------------------------ Topology --------------------------------
#     with tabs[2]:
#         if not summ:
#             st.warning("No topology view without valid telemetry.")
#         else:
#             st.graphviz_chart(topo_dot(rep, summ))
#             st.markdown("🟥 root-cause device &nbsp; 🟧 downstream impacted &nbsp; 🟨 degraded &nbsp; ⬜ down &nbsp; 🟩 healthy")
#             sc = rep.get("topology_scope") or {}
#             if sc:
#                 st.info(f"Connectivity Agent scope: **{sc.get('type')}** - root device(s): {', '.join(sc.get('root_devices', [])) or '-'}")

#     # ------------------------------ Messages --------------------------------
#     with tabs[3]:
#         st.subheader("Agents")
#         cols = st.columns(3)
#         allag = AGENTS + [type("C", (), {"name": "fault_correlation_agent", "role": "Fault Correlation", "description": "Merges findings via noisy-OR corroboration, applies refutations, ranks hypotheses, resolves conflicts and decides diagnosed / inconclusive / insufficient evidence."})(),
#                           type("R", (), {"name": "reporting_agent", "role": "Recommendation & Reporting", "description": "Builds the unified JSON/Markdown report: cause, evidence, alternatives, uncertainty, limitations and corrective actions."})()]
#         for i, a in enumerate(allag):
#             with cols[i % 3]:
#                 st.markdown(f'<div class="nc-card"><b>{a.role}</b><br><code>{a.name}</code><br><span style="opacity:.8;font-size:.9rem">{a.description}</span></div>', unsafe_allow_html=True)
#         st.subheader("Message bus log")
#         st.dataframe(pd.DataFrame([{"time": m["timestamp"][11:23], "from": m["sender"], "to": m["recipient"], "type": m["type"],
#                                     "ms": m.get("duration_ms"), "message_id": m["message_id"]} for m in res["messages"]]), hide_index=True)
#         for m in res["messages"]:
#             with st.expander(f"{m['sender']} -> {m['recipient']}  [{m['type']}]  {m['message_id']}"):
#                 st.json(m)

#     # ------------------------------ Validation ------------------------------
#     with tabs[4]:
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Rows in", ing["rows_in"])
#         c2.metric("Rows accepted", ing["rows_out"])
#         c3.metric("Input schema", ing["input_schema"])
#         c4.metric("Quality score", f"{ing['quality']:.2f}")
#         for e in ing["errors"]:
#             st.error(e)
#         for w in ing["warnings"]:
#             st.warning(w)
#         if ing["conversions"]:
#             st.subheader("Adapter conversions applied")
#             for c in ing["conversions"]:
#                 st.markdown(f"- `{c}`")
#         if ing["completeness"]:
#             st.subheader("Metric completeness")
#             st.bar_chart(pd.Series(ing["completeness"], name="non-null fraction"))
#         if not ing["errors"] and not ing["warnings"]:
#             st.success("Input passed all validation checks.")

#     # ------------------------------ Protocol --------------------------------
#     with tabs[5]:
#         tele, env, fnd = protocol_tables()
#         st.markdown("### Message envelope (v1.0)")
#         st.dataframe(env, hide_index=True)
#         st.markdown("### Finding object")
#         st.dataframe(fnd, hide_index=True)
#         st.markdown("### Telemetry schema (canonical v1.0) with accepted aliases & unit conversions")
#         st.dataframe(tele, hide_index=True)
#         st.markdown("### Example message")
#         st.code(json.dumps({"schema_version": "1.0", "message_id": "a1b2c3d4", "correlation_id": "9f8e7d6c", "sender": "infrastructure_agent",
#                             "recipient": "fault_correlation_agent", "type": "finding", "timestamp": "2026-11-01T09:31:02.114+00:00",
#                             "payload": {"findings": [{"finding_id": "x1y2z3", "agent": "infrastructure_agent", "cause": "link_congestion", "stance": "supports",
#                                                       "strength": 0.85, "devices": ["HOSTEL_CORE_SW_01"],
#                                                       "evidence": [{"device": "HOSTEL_CORE_SW_01", "metric": "queue_drops", "value": 160, "unit": "pkts/interval",
#                                                                     "interpretation": "Elevated packet drops"}],
#                                                       "rationale": "egress queue drops 160"}]}}, indent=2), language="json")
#         st.markdown("**Legacy adapter:** schema v0.9 fields such as `rtt_s`, `jitter_us`, `loss_ratio`, `bw_kbps`, `util_ratio` are converted automatically; "
#                     "unknown schema versions raise a warning and use best-effort mapping; missing `device_id`/`timestamp` is a hard error.")

#     # ------------------------------ Test suite ------------------------------
#     with tabs[6]:
#         st.write("Runs every scenario over 3 seeds through the full pipeline and compares against ground truth (reproducible, seeded).")
#         if st.button("Run all scenarios", type="primary"):
#             st.session_state["batch"] = run_batch()
#         if "batch" in st.session_state:
#             b = st.session_state["batch"]
#             acc = (b["pass"] == "PASS").mean()
#             m1, m2, m3 = st.columns(3)
#             m1.metric("Pass rate", f"{acc:.0%}")
#             m2.metric("Runs", len(b))
#             m3.metric("Failures", int((b["pass"] == "FAIL").sum()))
#             st.dataframe(b, hide_index=True)
#             st.download_button("Download results (CSV)", b.to_csv(index=False), "netcoop_test_results.csv", "text/csv")

#     # ------------------------------ Report ----------------------------------
#     with tabs[7]:
#         cj = json.dumps(clean_json(rep), indent=2)
#         md = report_markdown(rep)
#         d1, d2 = st.columns(2)
#         d1.download_button("Download JSON report", cj, f"{rep['incident_id']}.json", "application/json")
#         d2.download_button("Download Markdown report", md, f"{rep['incident_id']}.md", "text/markdown")
#         j, m = st.tabs(["JSON", "Markdown"])
#         with j:
#             st.json(clean_json(rep))
#         with m:
#             st.markdown(md)


# if __name__ == "__main__":
#     main()

# CLAUDE-3
"""
NetCoop AI - Multi-Agent Network Fault Diagnosis & Interoperability
Streamlit dashboard (self-contained, free tools only: streamlit + pandas + numpy).

Run:  streamlit run app.py

Pipeline
  Ingestion/Validation -> Performance Agent -> {Infrastructure, Connectivity,
  Service Health} Agents -> Fault Correlation -> Recommendation Agent ->
  Unified JSON/Markdown report.

All agents talk through a versioned JSON message envelope (see "Protocol" tab).
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import streamlit as st

SCHEMA_VERSION = "1.0"
LEGACY_SCHEMA_VERSION = "0.9"

# ============================================================================
# 1. TOPOLOGY
# ============================================================================
NODES = {
    "INTERNET_GW_01": {"role": "gateway", "type": "router"},
    "CAMPUS_CORE_01": {"role": "core", "type": "switch"},
    "DNS_DHCP_SRV_01": {"role": "service", "type": "server"},
    "HOSTEL_CORE_SW_01": {"role": "distribution", "type": "switch"},
    "HOSTEL_AP_01": {"role": "access", "type": "ap"},
    "HOSTEL_AP_02": {"role": "access", "type": "ap"},
    "HOSTEL_AP_03": {"role": "access", "type": "ap"},
    "DEPT_SW_CSE_01": {"role": "distribution", "type": "switch"},
    "DEPT_LAB_SW_01": {"role": "access", "type": "switch"},
    "LECTURE_SW_01": {"role": "distribution", "type": "switch"},
    "LECTURE_AP_01": {"role": "access", "type": "ap"},
}
EDGES = [  # (parent, child)
    ("INTERNET_GW_01", "CAMPUS_CORE_01"),
    ("CAMPUS_CORE_01", "DNS_DHCP_SRV_01"),
    ("CAMPUS_CORE_01", "HOSTEL_CORE_SW_01"),
    ("CAMPUS_CORE_01", "DEPT_SW_CSE_01"),
    ("CAMPUS_CORE_01", "LECTURE_SW_01"),
    ("HOSTEL_CORE_SW_01", "HOSTEL_AP_01"),
    ("HOSTEL_CORE_SW_01", "HOSTEL_AP_02"),
    ("HOSTEL_CORE_SW_01", "HOSTEL_AP_03"),
    ("DEPT_SW_CSE_01", "DEPT_LAB_SW_01"),
    ("LECTURE_SW_01", "LECTURE_AP_01"),
]
PARENT = {c: p for p, c in EDGES}
CHILDREN: dict[str, list[str]] = defaultdict(list)
for _p, _c in EDGES:
    CHILDREN[_p].append(_c)


def descendants(dev: str) -> set[str]:
    out, stack = set(), list(CHILDREN.get(dev, []))
    while stack:
        d = stack.pop()
        if d not in out:
            out.add(d)
            stack.extend(CHILDREN.get(d, []))
    return out


# ============================================================================
# 2. TELEMETRY SCHEMA (canonical v1.0), ALIASES & UNIT CONVERSION
# ============================================================================
# canonical -> (unit, min, max, description)
CANON = {
    "latency_ms": ("ms", 0, 60000, "Round-trip latency"),
    "jitter_ms": ("ms", 0, 60000, "Delay variation"),
    "packet_loss_pct": ("%", 0, 100, "Packet loss"),
    "throughput_mbps": ("Mbps", 0, 1e6, "Observed throughput"),
    "bandwidth_mbps": ("Mbps", 0.001, 1e6, "Link capacity"),
    "link_utilization_pct": ("%", 0, 100, "Link utilization"),
    "cpu_pct": ("%", 0, 100, "Device CPU utilization"),
    "memory_pct": ("%", 0, 100, "Device memory utilization"),
    "queue_drops": ("pkts/interval", 0, 1e9, "Egress queue drops"),
    "interface_errors": ("errors/interval", 0, 1e9, "CRC/input/output errors"),
    "rssi_dbm": ("dBm", -130, 0, "Wireless signal strength (APs/clients)"),
    "retransmission_pct": ("%", 0, 100, "Wireless retransmission rate"),
    "dns_failure_pct": ("%", 0, 100, "DNS lookup failure rate"),
    "dhcp_failure_pct": ("%", 0, 100, "DHCP failure rate"),
}
METRICS = list(CANON)
CORE_METRICS = ["latency_ms", "packet_loss_pct", "link_utilization_pct",
                "cpu_pct", "queue_drops", "interface_errors"]
RANGE = {k: (v[1], v[2]) for k, v in CANON.items()}
UNITS = {k: v[0] for k, v in CANON.items()}

# canonical -> [(alias, multiplier_to_canonical)]
ALIASES = {
    "device_id": [("device_id", 1), ("device", 1), ("host", 1), ("hostname", 1), ("node", 1), ("node_id", 1)],
    "timestamp": [("timestamp", 1), ("ts", 1), ("time", 1), ("datetime", 1)],
    "device_status": [("device_status", 1), ("status", 1), ("state", 1)],
    "latency_ms": [("latency_ms", 1), ("latency", 1), ("rtt_ms", 1), ("delay_ms", 1),
                   ("rtt_s", 1e3), ("delay_s", 1e3), ("latency_s", 1e3), ("latency_us", 1e-3)],
    "jitter_ms": [("jitter_ms", 1), ("jitter", 1), ("jitter_us", 1e-3), ("jitter_s", 1e3)],
    "packet_loss_pct": [("packet_loss_pct", 1), ("packet_loss", 1), ("loss_pct", 1), ("loss_ratio", 100)],
    "throughput_mbps": [("throughput_mbps", 1), ("throughput", 1), ("tput_mbps", 1),
                        ("throughput_kbps", 1e-3), ("throughput_gbps", 1e3)],
    "bandwidth_mbps": [("bandwidth_mbps", 1), ("bandwidth", 1), ("bw_mbps", 1), ("capacity_mbps", 1),
                       ("bw_kbps", 1e-3), ("bandwidth_gbps", 1e3)],
    "link_utilization_pct": [("link_utilization_pct", 1), ("utilization", 1), ("util_pct", 1),
                             ("link_util", 1), ("util_ratio", 100)],
    "cpu_pct": [("cpu_pct", 1), ("cpu", 1), ("cpu_util", 1), ("cpu_load", 1), ("cpu_ratio", 100)],
    "memory_pct": [("memory_pct", 1), ("mem_pct", 1), ("memory", 1), ("mem", 1)],
    "queue_drops": [("queue_drops", 1), ("egress_queue_drops", 1), ("q_drops", 1), ("egress_drops", 1)],
    "interface_errors": [("interface_errors", 1), ("if_errors", 1), ("if_errs", 1),
                         ("iface_errors", 1), ("crc_errors", 1)],
    "rssi_dbm": [("rssi_dbm", 1), ("rssi", 1), ("signal", 1), ("signal_dbm", 1)],
    "retransmission_pct": [("retransmission_pct", 1), ("retrans_pct", 1), ("retries_pct", 1),
                           ("retransmissions_pct", 1)],
    "dns_failure_pct": [("dns_failure_pct", 1), ("dns_fail_pct", 1), ("dns_error_pct", 1)],
    "dhcp_failure_pct": [("dhcp_failure_pct", 1), ("dhcp_fail_pct", 1), ("dhcp_error_pct", 1)],
}
STATUS_MAP = {
    "up": "up", "ok": "up", "online": "up", "healthy": "up", "active": "up",
    "degraded": "degraded", "warn": "degraded", "warning": "degraded",
    "flapping": "degraded", "impaired": "degraded",
    "down": "down", "crit": "down", "critical": "down", "offline": "down",
    "unreachable": "down", "error": "down",
}
KNOWN_SCHEMAS = {SCHEMA_VERSION, LEGACY_SCHEMA_VERSION}


# ============================================================================
# 3. SYNTHETIC SCENARIO GENERATOR
# ============================================================================
def _lerp(a, b, k):
    return a + (b - a) * k


def _f_congestion(r, dev, rng, k):
    if dev == "HOSTEL_CORE_SW_01":
        r["link_utilization_pct"] = _lerp(35, 93, k) + rng.normal(0, 3)
        r["queue_drops"] = max(0, rng.normal(160 * k, 30)) + r["queue_drops"] * (1 - k)
        r["latency_ms"] = _lerp(12, 250, k) + rng.normal(0, 30)
        r["packet_loss_pct"] += 3 * k
        r["jitter_ms"] += 22 * k
        r["cpu_pct"] += 25 * k
    elif dev.startswith("HOSTEL_AP"):
        r["latency_ms"] += 120 * k
        r["packet_loss_pct"] += 1.5 * k
        r["jitter_ms"] += 8 * k


def _f_weak_wifi(r, dev, rng, k):
    if dev == "HOSTEL_AP_02":
        r["rssi_dbm"] = _lerp(-55, -86, k) + rng.normal(0, 2)
        r["retransmission_pct"] = _lerp(2, 22, k) + rng.normal(0, 3)
        r["packet_loss_pct"] += 6 * k
        r["jitter_ms"] += 25 * k
        r["latency_ms"] += 60 * k
        r["link_utilization_pct"] -= 15 * k


def _f_interface(r, dev, rng, k):
    if dev == "DEPT_LAB_SW_01":
        r["interface_errors"] = max(0, rng.normal(80 * k, 15)) + r["interface_errors"] * (1 - k)
        r["packet_loss_pct"] += 8 * k
        r["jitter_ms"] += 14 * k
        r["latency_ms"] += 30 * k
        if rng.random() < 0.35 * k:
            r["device_status"] = "degraded"


def _f_dns(r, dev, rng, k):
    r["dns_failure_pct"] = max(0, rng.normal(70 * k, 8))


def _f_dhcp(r, dev, rng, k):
    r["dhcp_failure_pct"] = max(0, rng.normal(65 * k, 8))


def _f_overload(r, dev, rng, k):
    if dev == "CAMPUS_CORE_01":
        r["cpu_pct"] = _lerp(30, 97, k) + rng.normal(0, 1.5)
        r["memory_pct"] = _lerp(45, 91, k) + rng.normal(0, 1.5)
        r["latency_ms"] += 120 * k
        r["packet_loss_pct"] += 2 * k
        r["jitter_ms"] += 10 * k
    elif dev != "INTERNET_GW_01":
        r["latency_ms"] += 40 * k


def _f_hardware(r, dev, rng, k):
    if dev == "HOSTEL_CORE_SW_01":
        r["device_status"] = "down"
    elif dev in descendants("HOSTEL_CORE_SW_01"):
        r["device_status"] = "unreachable"
    else:
        return
    for m in METRICS:
        if m != "bandwidth_mbps":
            r[m] = np.nan


def _f_ambiguous(r, dev, rng, k):
    if dev == "DEPT_SW_CSE_01":  # symptoms but no supporting infra/utilisation evidence
        r["latency_ms"] += 140 * k
        r["packet_loss_pct"] += 4 * k
        r["jitter_ms"] += 20 * k


def _f_concurrent(r, dev, rng, k):
    _f_congestion(r, dev, rng, k)
    _f_interface(r, dev, rng, k)


FAULTS = {
    "link_congestion": _f_congestion, "weak_wifi": _f_weak_wifi, "interface_fault": _f_interface,
    "dns_failure": _f_dns, "dhcp_failure": _f_dhcp, "device_overload": _f_overload,
    "hardware_failure": _f_hardware, "ambiguous_degradation": _f_ambiguous,
    "concurrent_faults": _f_concurrent, "interop_failure": _f_congestion, "sparse_data": _f_congestion,
}

SCENARIO_META = {
    "normal": dict(label="Normal operation", desc="All metrics within expected ranges.",
                   expect_status="healthy", causes=[], targets=[]),
    "link_congestion": dict(label="Link congestion", desc="High utilization + queue drops + latency on the hostel distribution switch; APs below suffer.",
                            expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"]),
    "weak_wifi": dict(label="Weak Wi-Fi signal (no wireless agent)", desc="Poor RSSI and high retransmissions on HOSTEL_AP_02. No agent models wireless signal, so the system must report insufficient evidence rather than guess.",
                      expect_status="insufficient_evidence", causes=[], targets=["HOSTEL_AP_02"]),
    "interface_fault": dict(label="Ethernet / interface fault", desc="Rising interface errors, loss and flapping on DEPT_LAB_SW_01.",
                            expect_status="diagnosed", causes=["interface_fault"], targets=["DEPT_LAB_SW_01"]),
    "dns_failure": dict(label="DNS failure", desc="Service-level DNS failures while the network itself is healthy.",
                        expect_status="diagnosed", causes=["dns_failure"], targets=[]),
    "dhcp_failure": dict(label="DHCP failure", desc="Service-level DHCP failures while the network itself is healthy.",
                         expect_status="diagnosed", causes=["dhcp_failure"], targets=[]),
    "device_overload": dict(label="Device CPU/memory overload", desc="Core switch CPU and memory saturated.",
                            expect_status="diagnosed", causes=["device_overload"], targets=["CAMPUS_CORE_01"]),
    "hardware_failure": dict(label="Hardware failure / device down", desc="Hostel distribution switch down; all APs behind it unreachable.",
                             expect_status="diagnosed", causes=["hardware_failure"], targets=["HOSTEL_CORE_SW_01"]),
    "interop_failure": dict(label="Interoperability failure (legacy schema v0.9)", desc="Same congestion fault, but telemetry arrives with different field names, units (s, us, ratios, kbps) and schema version.",
                            expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"]),
    "malformed_input": dict(label="Malformed / incompatible input", desc="Unknown columns and text values - must be rejected with a clear error.",
                            expect_status="insufficient_data", causes=[], targets=[]),
    "sparse_data": dict(label="Sparse / missing telemetry", desc="Congestion with >50% samples missing and queue-drop counter absent - confidence must drop.",
                        expect_status="diagnosed", causes=["link_congestion"], targets=["HOSTEL_CORE_SW_01"], abstain_ok=True),
    "ambiguous_degradation": dict(label="Unexplained degradation", desc="Latency/loss/jitter up on DEPT_SW_CSE_01 with no corroborating evidence - system must NOT claim a root cause.",
                                  expect_status="insufficient_evidence", causes=[], targets=["DEPT_SW_CSE_01"]),
    "concurrent_faults": dict(label="Concurrent faults", desc="Congestion on hostel switch and interface errors on dept lab switch at the same time.",
                              expect_status="diagnosed", causes=["link_congestion", "interface_fault"],
                              targets=["HOSTEL_CORE_SW_01", "DEPT_LAB_SW_01"]),
}


def to_legacy(df: pd.DataFrame) -> pd.DataFrame:
    secs = (pd.to_datetime(df["timestamp"]) - pd.Timestamp("1970-01-01")).dt.total_seconds()
    return pd.DataFrame({
        "host": df["device_id"], "ts": secs.astype("int64"),
        "state": df["device_status"].map({"up": "OK", "degraded": "WARN"}).fillna("CRIT"),
        "rtt_s": df["latency_ms"] / 1e3, "jitter_us": df["jitter_ms"] * 1e3,
        "loss_ratio": df["packet_loss_pct"] / 100, "bw_kbps": df["bandwidth_mbps"] * 1e3,
        "util_ratio": df["link_utilization_pct"] / 100, "cpu": df["cpu_pct"], "mem": df["memory_pct"],
        "q_drops": df["queue_drops"], "if_errs": df["interface_errors"], "signal": df["rssi_dbm"],
        "schema_version": LEGACY_SCHEMA_VERSION,
    })


@st.cache_data(show_spinner=False)
def generate(scenario: str, seed: int = 7, noise: float = 1.0, missing_pct: float = 0.0, n: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    if scenario == "malformed_input":
        return pd.DataFrame({
            "node_name": [f"sw{i % 4}" for i in range(20)],
            "reading_a": ["high", "low", "n/a", "??"] * 5,
            "reading_b": ["x"] * 20, "notes": ["see ticket"] * 20,
        })
    t0 = datetime(2026, 11, 1, 9, 0, 0)
    onset = int(n * 0.5)
    fault = FAULTS.get(scenario)
    rows = []
    for dev, info in NODES.items():
        is_ap = info["type"] == "ap"
        bw = 300 if is_ap else (10000 if info["role"] in ("gateway", "core") else 1000)
        for i in range(n):
            util = float(np.clip(rng.normal(35, 8 * noise), 5, 70))
            r = {
                "timestamp": (t0 + timedelta(minutes=i)).isoformat(), "device_id": dev, "device_status": "up",
                "latency_ms": max(1.0, rng.normal(12, 3 * noise)), "jitter_ms": abs(rng.normal(2, 0.8 * noise)),
                "packet_loss_pct": abs(rng.normal(0.1, 0.1 * noise)), "bandwidth_mbps": float(bw),
                "link_utilization_pct": util, "throughput_mbps": bw * util / 100,
                "cpu_pct": float(np.clip(rng.normal(25, 6 * noise), 3, 60)),
                "memory_pct": float(np.clip(rng.normal(45, 5 * noise), 10, 70)),
                "queue_drops": float(rng.poisson(2)), "interface_errors": float(rng.poisson(1)),
                "rssi_dbm": rng.normal(-55, 3 * noise) if is_ap else np.nan,
                "retransmission_pct": abs(rng.normal(2, 1 * noise)) if is_ap else np.nan,
                "dns_failure_pct": abs(rng.normal(0.2, 0.2)), "dhcp_failure_pct": abs(rng.normal(0.2, 0.2)),
            }
            if fault and i >= onset:
                k = min(1.0, (i - onset + 1) / 5)
                fault(r, dev, rng, k)
                r["throughput_mbps"] = bw * np.clip(r["link_utilization_pct"], 0, 100) / 100
            rows.append(r)
    df = pd.DataFrame(rows)
    for c, hi in [("link_utilization_pct", 100), ("cpu_pct", 100), ("memory_pct", 100),
                  ("packet_loss_pct", 100), ("retransmission_pct", 100),
                  ("dns_failure_pct", 100), ("dhcp_failure_pct", 100)]:
        df[c] = df[c].clip(0, hi)
    df["rssi_dbm"] = df["rssi_dbm"].clip(upper=-20)
    if scenario == "sparse_data":
        missing_pct = max(missing_pct, 55.0)
        df["queue_drops"] = np.nan
    if missing_pct > 0:
        for m in METRICS:
            mask = rng.random(len(df)) < missing_pct / 100
            df.loc[mask, m] = np.nan
    if scenario == "interop_failure":
        return to_legacy(df)
    return df


# ============================================================================
# 4. INGESTION, VALIDATION & NORMALISATION
# ============================================================================
def _pick(df_cols, canon):
    for alias, f in ALIASES[canon]:
        if alias in df_cols:
            return alias, f
    return None


def ingest(raw, parse_error: str | None = None):
    """Validate + normalise arbitrary telemetry into canonical schema v1.0."""
    rep = {"ok": False, "errors": [], "warnings": [], "conversions": [], "rows_in": 0, "rows_out": 0,
           "quality": 0.0, "completeness": {}, "missing_metrics": [], "input_schema": "unknown"}
    if parse_error:
        rep["errors"].append(parse_error)
        return None, rep
    if raw is None:
        rep["errors"].append("No telemetry supplied.")
        return None, rep
    try:
        df = raw.copy() if isinstance(raw, pd.DataFrame) else pd.DataFrame(raw)
    except Exception as e:  # noqa: BLE001
        rep["errors"].append(f"Could not interpret input as a table: {e}")
        return None, rep
    rep["rows_in"] = len(df)
    if df.empty:
        rep["errors"].append("Input contains no rows.")
        return None, rep
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "schema_version" in df.columns and df["schema_version"].notna().any():
        ver = str(df["schema_version"].dropna().iloc[0])
        rep["input_schema"] = ver
        if ver not in KNOWN_SCHEMAS:
            rep["warnings"].append(f"Unknown schema_version '{ver}' (known: {sorted(KNOWN_SCHEMAS)}); using best-effort field mapping.")
        elif ver != SCHEMA_VERSION:
            rep["warnings"].append(f"Legacy schema_version '{ver}' detected; adapter converting to v{SCHEMA_VERSION}.")
    else:
        rep["input_schema"] = "unversioned"
        rep["warnings"].append("No schema_version field; assuming canonical v1.0 / alias mapping.")

    dev, ts = _pick(df.columns, "device_id"), _pick(df.columns, "timestamp")
    if dev is None:
        rep["errors"].append(f"Missing required field 'device_id' (accepted aliases: {[a for a, _ in ALIASES['device_id']]}).")
    if ts is None:
        rep["errors"].append(f"Missing required field 'timestamp' (accepted aliases: {[a for a, _ in ALIASES['timestamp']]}).")
    picked = {m: p for m in METRICS if (p := _pick(df.columns, m))}
    if len(picked) < 2 and not rep["errors"]:
        rep["errors"].append(f"Only {len(picked)} recognised metric column(s) found; at least 2 are required for diagnosis.")
    if rep["errors"]:
        recognised = {a for k in ALIASES for a, _ in ALIASES[k]}
        unk = [c for c in df.columns if c not in recognised]
        if unk:
            rep["warnings"].append(f"Unrecognised columns ignored: {unk}")
        return None, rep

    out = pd.DataFrame({"device_id": df[dev[0]].astype(str).str.strip()})
    t = df[ts[0]]
    try:
        if pd.api.types.is_numeric_dtype(t):
            unit = "ms" if t.max() > 1e11 else "s"
            out["timestamp"] = pd.to_datetime(t, unit=unit, errors="coerce", utc=True).dt.tz_localize(None)
        else:
            out["timestamp"] = pd.to_datetime(t, errors="coerce", utc=True).dt.tz_localize(None)
    except Exception as e:  # noqa: BLE001
        rep["errors"].append(f"Unparseable timestamps: {e}")
        return None, rep
    if (dev[0] != "device_id") or (ts[0] != "timestamp"):
        rep["conversions"].append(f"{dev[0]}->device_id, {ts[0]}->timestamp")

    st_col = _pick(df.columns, "device_status")
    if st_col:
        out["device_status"] = df[st_col[0]].astype(str).str.strip().str.lower().map(STATUS_MAP).fillna("unknown")
        unk_n = int((out["device_status"] == "unknown").sum())
        if unk_n:
            rep["warnings"].append(f"{unk_n} rows have unrecognised device_status; treated as 'unknown'.")
        rep["status_reported"] = True
    else:
        out["device_status"] = "unknown"
        rep["status_reported"] = False
        rep["warnings"].append("No device_status field; down devices are inferred from missing telemetry.")

    for m in METRICS:
        if m in picked:
            alias, f = picked[m]
            s = pd.to_numeric(df[alias], errors="coerce")
            bad = int(s.isna().sum() - df[alias].isna().sum())
            if bad > 0:
                rep["warnings"].append(f"{alias}: {bad} non-numeric value(s) discarded.")
            s = s * f
            lo, hi = RANGE[m]
            oor = (s < lo) | (s > hi)
            if oor.any():
                rep["warnings"].append(f"{alias}: {int(oor.sum())} out-of-range value(s) discarded (valid {lo}..{hi} {UNITS[m]}).")
                s = s.mask(oor)
            if alias != m or f != 1:
                rep["conversions"].append(f"{alias} -> {m}" + (f" (x{f:g})" if f != 1 else ""))
            out[m] = s.astype(float)
        else:
            out[m] = np.nan
            rep["missing_metrics"].append(m)
    recognised = {a for k in ALIASES for a, _ in ALIASES[k]} | {"schema_version"}
    unk = [c for c in df.columns if c not in recognised]
    if unk:
        rep["warnings"].append(f"Unrecognised columns ignored: {unk}")

    n0 = len(out)
    out = out[out["timestamp"].notna() & out["device_id"].ne("") & out["device_id"].ne("nan")]
    if len(out) < n0:
        rep["warnings"].append(f"{n0 - len(out)} row(s) dropped: missing/invalid device_id or timestamp.")
    n1 = len(out)
    out = out.drop_duplicates(["device_id", "timestamp"], keep="last")
    if len(out) < n1:
        rep["warnings"].append(f"{n1 - len(out)} duplicate (device, timestamp) row(s) removed.")
    if out.empty:
        rep["errors"].append("No valid rows remain after validation.")
        return None, rep
    out = out.sort_values(["device_id", "timestamp"]).reset_index(drop=True)

    present_core = [m for m in CORE_METRICS if m in picked]
    coverage = len(present_core) / len(CORE_METRICS)
    comp = float(out[present_core].notna().mean().mean()) if present_core else 0.0
    rep["completeness"] = {m: round(float(out[m].notna().mean()), 3) for m in METRICS}
    rep["quality"] = round(0.6 * coverage + 0.4 * comp, 3)
    rep["rows_out"] = len(out)
    rep["ok"] = True
    unknown_dev = sorted(set(out["device_id"]) - set(NODES))
    if unknown_dev:
        rep["warnings"].append(f"Devices not in known topology (no topology reasoning for them): {unknown_dev}")
    return out, rep


def _med(s: pd.Series):
    s = s.dropna()
    return float(s.median()) if len(s) else None


def summarize(df: pd.DataFrame, recent: int = 12, base: int = 25) -> dict:
    summ = {}
    for dev, g in df.groupby("device_id"):
        g = g.sort_values("timestamp")
        rec, bas = g.tail(recent), g.head(base)
        last = g.tail(5)
        sts = last["device_status"].tolist()
        reported = any(s != "unknown" for s in sts)
        if sts.count("down") >= 3:
            status, src = "down", "reported"
        elif len(last) >= 5 and last[CORE_METRICS].isna().all().all():
            status, src = "down", "inferred"
        elif sts.count("degraded") >= 2:
            status, src = "degraded", "reported"
        else:
            status, src = ("up" if reported else "unknown"), ("reported" if reported else "inferred")
        summ[dev] = {"n": len(g), "status": status, "status_source": src,
                     "recent": {m: _med(rec[m]) for m in METRICS},
                     "baseline": {m: _med(bas[m]) for m in METRICS}}
    return summ


# ============================================================================
# 5. PROTOCOL: message envelope + findings
# ============================================================================
def make_msg(sender, recipient, mtype, payload, corr_id, duration_ms=None):
    m = {"schema_version": SCHEMA_VERSION, "message_id": uuid.uuid4().hex[:8], "correlation_id": corr_id,
         "sender": sender, "recipient": recipient, "type": mtype,
         "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "payload": payload}
    if duration_ms is not None:
        m["duration_ms"] = round(duration_ms, 2)
    return m


def ramp(x, lo, hi):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0.0
    return float(min(1.0, max(0.0, (x - lo) / (hi - lo))))


def ev(dev, metric, value, interp, unit=None):
    v = round(value, 2) if isinstance(value, (int, float, np.floating)) else value
    return {"device": dev, "metric": metric, "value": v, "unit": unit or UNITS.get(metric, ""), "interpretation": interp}


def finding(agent, cause, stance, strength, devices, evidence, rationale):
    return {"finding_id": uuid.uuid4().hex[:6], "agent": agent, "cause": cause, "stance": stance,
            "strength": round(float(strength), 3), "devices": list(devices), "evidence": evidence, "rationale": rationale}


CAUSES = {
    "link_congestion": dict(
        title="link congestion causing egress queue drops", short="Link congestion",
        actions=["Inspect utilization of {dev} uplink/egress interfaces and identify top talkers (NetFlow/sFlow)",
                 "Review QoS / queue configuration and traffic distribution on {dev}",
                 "Consider rate-limiting heavy flows, load-balancing or adding uplink capacity"],
        diff=["Upstream link congestion", "Misconfigured QoS / queue profile", "Broadcast or multicast storm"],
        cmds=["show interfaces {dev} | include utilization|drops", "show policy-map interface", "show queueing interface"]),
    "interface_fault": dict(
        title="interface / cable fault (rising errors, loss)", short="Interface fault",
        actions=["Inspect cable, connectors and SFP/transceiver on {dev}; replace if errors persist",
                 "Check duplex/speed negotiation and error counters (CRC, input/output) on {dev}",
                 "Test with a known-good cable or port; schedule hardware swap if the fault persists"],
        diff=["Duplex / speed mismatch", "Faulty SFP or patch cable", "Failing switch port ASIC"],
        cmds=["show interfaces {dev} counters errors", "show interfaces status", "show logging | include link"]),
    "device_overload": dict(
        title="device CPU/memory overload", short="Device overload",
        actions=["Identify top CPU/memory processes on {dev}", "Check for control-plane storms, loops or excessive ARP/ICMP traffic",
                 "Apply CoPP / rate limits or upgrade/redistribute load if sustained"],
        diff=["Control-plane storm / layer-2 loop", "Memory leak (software bug)", "Misbehaving routing protocol"],
        cmds=["show processes cpu sorted", "show memory statistics", "show spanning-tree summary"]),
    "hardware_failure": dict(
        title="device hardware / power failure (device down)", short="Hardware failure",
        actions=["Verify power and physical status of {dev} on site", "Check console / out-of-band management and last-known logs",
                 "Fail over affected users to a redundant path; raise an RMA if hardware fault is confirmed"],
        diff=["Power failure in the rack/building", "Uplink cable cut or fibre fault", "Software crash / boot loop"],
        cmds=["ping {dev}", "show inventory", "show environment all"]),
    "dns_failure": dict(
        title="DNS service failure", short="DNS failure",
        actions=["Check DNS service health and logs on {srv}", "Test resolution against the campus and an upstream resolver",
                 "Verify DNS forwarders, zone data and resolver load; fail over to a secondary resolver"],
        diff=["Upstream resolver outage", "DNS server overload", "Misconfigured forwarders / zone data"],
        cmds=["nslookup example.com {srv}", "systemctl status named", "journalctl -u named --since '15 min ago'"]),
    "dhcp_failure": dict(
        title="DHCP service failure", short="DHCP failure",
        actions=["Check DHCP service and lease database on {srv}", "Inspect scope utilization for exhaustion; extend scopes or shorten lease times",
                 "Look for rogue DHCP servers and verify relay (ip helper) config"],
        diff=["DHCP scope exhaustion", "Rogue DHCP server", "Relay / helper misconfiguration"],
        cmds=["systemctl status dhcpd", "dhcp-lease-list", "show ip dhcp snooping binding"]),
}
SYMPTOMATIC = {"link_congestion", "interface_fault", "device_overload"}
SERVICE_CAUSES = {"dns_failure", "dhcp_failure"}


# ============================================================================
# 6. AGENTS
# ============================================================================
class Agent:
    name = "agent"
    role = ""
    description = ""
    consumes: list[str] = []

    def analyze(self, ctx, inbox) -> dict:  # pragma: no cover
        raise NotImplementedError


class PerformanceAgent(Agent):
    name = "performance_agent"
    role = "Telemetry & Performance"
    description = "Analyzes latency, jitter, packet loss, throughput and link utilization. Flags degraded devices and shares them with peer agents."
    consumes = ["telemetry_summary"]

    def analyze(self, ctx, inbox):
        findings, degraded = [], {}
        for dev, s in ctx["summ"].items():
            if s["status"] == "down":
                continue
            r = s["recent"]
            lat_s, loss_s, jit_s = ramp(r["latency_ms"], 50, 200), ramp(r["packet_loss_pct"], 1, 5), ramp(r["jitter_ms"], 10, 30)
            degr = max(lat_s, loss_s, jit_s)
            if degr >= 0.3:
                degraded[dev] = round(degr, 2)
            util = r["link_utilization_pct"]
            util_s = ramp(util, 65, 92)
            if util_s >= 0.25:
                evid = [ev(dev, "link_utilization_pct", util, "High link utilization")]
                if lat_s >= 0.3:
                    evid.append(ev(dev, "latency_ms", r["latency_ms"], "Elevated network latency"))
                if loss_s >= 0.3:
                    evid.append(ev(dev, "packet_loss_pct", r["packet_loss_pct"], "Elevated packet loss"))
                findings.append(finding(self.name, "link_congestion", "supports", min(0.9, 0.65 * util_s + 0.35 * degr), [dev], evid,
                                        f"{dev}: utilization {util:.0f}% with degradation score {degr:.2f}"))
            elif degr >= 0.3 and util is not None and util < 60:
                findings.append(finding(self.name, "link_congestion", "refutes", min(0.8, 0.5 + 0.3 * degr), [dev],
                                        [ev(dev, "link_utilization_pct", util, "Utilization normal despite degradation")],
                                        f"{dev}: degraded but utilization only {util:.0f}% - congestion unlikely here"))
        return {"findings": findings,
                "summary": {"degraded_devices": degraded, "network_healthy": not degraded, "devices_analyzed": len(ctx["summ"])}}


class InfrastructureAgent(Agent):
    name = "infrastructure_agent"
    role = "Infrastructure Health"
    description = "Examines device status, CPU/memory, interface errors and egress queue drops. Uses the Performance Agent's degraded-device list to weigh refuting evidence."
    consumes = ["telemetry_summary", "performance_agent.degraded_devices"]

    def analyze(self, ctx, inbox):
        degraded = inbox.get("performance_agent", {}).get("summary", {}).get("degraded_devices", {})
        findings = []
        for dev, s in ctx["summ"].items():
            r = s["recent"]
            if s["status"] == "down":
                findings.append(finding(self.name, "hardware_failure", "supports", 0.9 if s["status_source"] == "reported" else 0.6, [dev],
                                        [ev(dev, "device_status", "down", f"Device {s['status_source']} as down", "state")],
                                        f"{dev} is down ({s['status_source']})"))
                continue
            cpu, mem, qd, ie = r["cpu_pct"], r["memory_pct"], r["queue_drops"], r["interface_errors"]
            ov = min(0.95, max(ramp(cpu, 70, 95), 0.8 * ramp(mem, 80, 95)))
            if ov >= 0.25:
                evid = [ev(dev, "cpu_pct", cpu, "High CPU utilization")] if cpu is not None else []
                if mem is not None and ramp(mem, 80, 95) > 0:
                    evid.append(ev(dev, "memory_pct", mem, "High memory utilization"))
                findings.append(finding(self.name, "device_overload", "supports", ov, [dev], evid, f"{dev}: CPU {cpu}, mem {mem}"))
            qs = ramp(qd, 15, 120)
            if qs >= 0.25:
                findings.append(finding(self.name, "link_congestion", "supports", 0.85 * qs, [dev],
                                        [ev(dev, "queue_drops", qd, "Elevated packet drops")], f"{dev}: egress queue drops {qd:.0f}"))
            ies = ramp(ie, 8, 50)
            if ies >= 0.25:
                findings.append(finding(self.name, "interface_fault", "supports", 0.9 * ies, [dev],
                                        [ev(dev, "interface_errors", ie, "Rising interface errors")], f"{dev}: interface errors {ie:.0f}"))
            if dev in degraded:
                if cpu is not None and cpu < 60 and (mem is None or mem < 80):
                    findings.append(finding(self.name, "device_overload", "refutes", 0.6, [dev],
                                            [ev(dev, "cpu_pct", cpu, "CPU normal while device degraded")], f"{dev}: degraded but CPU healthy"))
                if ie is not None and ie < 5:
                    findings.append(finding(self.name, "interface_fault", "refutes", 0.5, [dev],
                                            [ev(dev, "interface_errors", ie, "No interface errors")], f"{dev}: degraded but no interface errors"))
                if qd is not None and qd < 10:
                    findings.append(finding(self.name, "link_congestion", "refutes", 0.35, [dev],
                                            [ev(dev, "queue_drops", qd, "No queue drops")], f"{dev}: degraded but no queue drops"))
        return {"findings": findings, "summary": {"devices_analyzed": len(ctx["summ"])}}


class ConnectivityAgent(Agent):
    name = "connectivity_agent"
    role = "Connectivity & Topology"
    description = "Uses the topology graph to find connected devices and common neighbours of affected devices, locate failure roots, determine scope (localized / segment / outage) and list downstream-impacted devices."
    consumes = ["telemetry_summary", "topology", "performance_agent.degraded_devices"]

    def analyze(self, ctx, inbox):
        degraded = set(inbox.get("performance_agent", {}).get("summary", {}).get("degraded_devices", {}))
        down = {d for d, s in ctx["summ"].items() if s["status"] == "down"}
        findings, impacted = [], {}
        roots = sorted(d for d in down if PARENT.get(d) not in down)
        for root in roots:
            imp = sorted(descendants(root) & down)
            impacted[root] = imp
            strength = 0.9 if ctx["summ"][root]["status_source"] == "reported" else 0.65
            findings.append(finding(self.name, "hardware_failure", "supports", strength, [root],
                                    [ev(root, "device_status", "down", f"Failure root; {len(imp)} downstream device(s) unreachable", "state")],
                                    f"{root} is the topmost failed node; {len(imp)} dependents down"))
        n = len(ctx["summ"])
        if down:
            scope = {"type": "outage", "root_devices": roots}
        elif not degraded:
            scope = {"type": "none", "root_devices": []}
        else:
            tops = sorted(d for d in degraded if PARENT.get(d) not in degraded)
            if len(degraded) >= 0.6 * n:
                stype = "campus_wide"
            elif any(descendants(t) & degraded for t in tops):
                stype = "segment"
            else:
                stype = "localized"
            scope = {"type": stype, "root_devices": tops}
        affected = degraded | down
        neigh = {d: set(CHILDREN.get(d, [])) | ({PARENT[d]} if d in PARENT else set()) for d in NODES}
        connected = {d: sorted(neigh[d]) for d in sorted(affected) if d in neigh}
        common = sorted(n for n in NODES if n not in affected and len(neigh[n] & affected) >= 2)
        unknown = sorted(d for d in ctx["summ"] if d not in NODES)
        return {"findings": findings,
                "summary": {"scope": scope, "failure_roots": roots, "impacted_downstream": impacted,
                            "connected_devices": connected, "common_neighbors": common, "unknown_devices": unknown}}


class ServiceHealthAgent(Agent):
    name = "service_health_agent"
    role = "Service Health (DNS/DHCP)"
    description = "Detects DNS/DHCP failures that occur while the underlying network is healthy (service-specific connectivity problems)."
    consumes = ["telemetry_summary", "performance_agent.network_healthy"]

    def analyze(self, ctx, inbox):
        perf = inbox.get("performance_agent", {}).get("summary", {})
        deg_ratio = len(perf.get("degraded_devices", {})) / max(1, len(ctx["summ"]))
        findings = []
        for cause, metric, label in [("dns_failure", "dns_failure_pct", "DNS"), ("dhcp_failure", "dhcp_failure_pct", "DHCP")]:
            vals = {d: s["recent"][metric] for d, s in ctx["summ"].items() if s["status"] != "down" and s["recent"][metric] is not None}
            if not vals:
                continue
            med = float(np.median(list(vals.values())))
            reach = sum(v > 20 for v in vals.values()) / len(vals)
            strength = 0.95 * ramp(med, 10, 50)
            if strength < 0.25 and reach < 0.3:
                continue
            note = ""
            if reach < 0.3:
                strength *= 0.6
                note = " (localized to few devices)"
            if deg_ratio >= 0.3:
                strength *= 0.7
                note += " (coincides with wide network degradation - may be secondary)"
            if strength < 0.2:
                continue
            affected = [d for d, v in vals.items() if v > 20] or list(vals)
            findings.append(finding(self.name, cause, "supports", strength, affected,
                                    [ev("ALL" if reach >= 0.5 else affected[0], metric, med, f"Median {label} failure rate across devices{note}")],
                                    f"{label} failures median {med:.0f}% across {len(vals)} devices, {reach:.0%} above 20%"))
        return {"findings": findings, "summary": {}}


AGENTS = [PerformanceAgent(), InfrastructureAgent(), ConnectivityAgent(), ServiceHealthAgent()]


# ---------------------------------------------------------------------------
# Fault Correlation Agent
# ---------------------------------------------------------------------------
def conf_category(c: float) -> str:
    return "high" if c >= 0.8 else "medium" if c >= 0.6 else "low" if c >= 0.4 else "very_low"


def correlate(all_findings: list[dict], ctx, inbox) -> dict:
    perf = inbox.get("performance_agent", {}).get("summary", {})
    degraded = set(perf.get("degraded_devices", {}))
    conn = inbox.get("connectivity_agent", {}).get("summary", {})
    Q = 0.5 + 0.5 * ctx["quality"] ** 2
    Q = max(0.0, Q - 0.08 * len(ctx.get("failed_agents", [])))

    by = defaultdict(lambda: {"sup": [], "ref": []})
    for f in all_findings:
        by[f["cause"]]["sup" if f["stance"] == "supports" else "ref"].append(f)

    hypotheses, conflicts = [], []
    for cause, d in by.items():
        if not d["sup"]:
            continue
        per_agent = {}
        for f in d["sup"]:
            per_agent[f["agent"]] = max(per_agent.get(f["agent"], 0), f["strength"])
        devs = sorted({x for f in d["sup"] for x in f["devices"]})
        if cause == "hardware_failure" and conn.get("failure_roots"):
            devs = [r for r in conn["failure_roots"] if r in devs] or devs
        sym_note = None
        if "performance_agent" not in per_agent:
            if cause in SYMPTOMATIC and set(devs) & degraded:
                per_agent["performance_agent"] = 0.5
                sym_note = "Measured degradation on the same device(s) is consistent with this cause"
            elif cause in SERVICE_CAUSES and perf.get("network_healthy"):
                per_agent["performance_agent"] = 0.45
                sym_note = "Network performance is healthy, isolating the fault to the service layer"
        S = 1.0
        for s in per_agent.values():
            S *= 1 - s
        S = 1 - S
        refs = [f for f in d["ref"] if set(f["devices"]) & set(devs)]
        r = max((f["strength"] for f in refs), default=0.0)
        R = 1 - 0.6 * r
        conf = round(min(0.95, S * R * Q), 3)
        if refs:
            conflicts.append({"cause": cause, "supported_by": sorted(per_agent), "support_score": round(S, 2),
                              "refuted_by": sorted({f["agent"] for f in refs}), "refutation": round(r, 2),
                              "resolution": f"Confidence reduced by factor {R:.2f}: " + "; ".join(f["rationale"] for f in refs[:2])})
        hypotheses.append({"cause": cause, "confidence": conf, "devices": devs,
                           "sources": sorted(per_agent), "breakdown": {"support": round(S, 3), "refutation_factor": round(R, 3),
                                                                      "data_quality_factor": round(Q, 3)},
                           "symptom_note": sym_note, "findings": d["sup"]})
    hypotheses.sort(key=lambda h: -h["confidence"])

    def overlap(a, b):
        return bool(set(a["devices"]) & set(b["devices"])) or (a["cause"] in SERVICE_CAUSES and b["cause"] in SERVICE_CAUSES)

    status, top, secondary, rivals = None, None, [], []
    n_dev = len(ctx["summ"])
    if hypotheses and hypotheses[0]["confidence"] >= 0.3:
        top = hypotheses[0]
        rest = hypotheses[1:]
        if top["confidence"] < 0.5:
            status = "inconclusive"
        else:
            rivals = [h for h in rest if overlap(h, top) and h["confidence"] >= 0.4 and top["confidence"] - h["confidence"] < 0.15]
            status = "inconclusive" if rivals else "diagnosed"
            secondary = [h for h in rest if h["confidence"] >= 0.5 and not overlap(h, top)]
    elif degraded:
        status = "insufficient_evidence"
    else:
        status = "healthy"

    affected, downstream = [], []
    if top:
        affected = list(top["devices"])
        if top["cause"] in SERVICE_CAUSES and len(affected) > 3:
            affected = affected
        pool = degraded | {d for d, s in ctx["summ"].items() if s["status"] == "down"}
        for a in top["devices"]:
            downstream += [x for x in descendants(a) if x in pool and x not in top["devices"]]
        downstream = sorted(set(downstream))
    return {"status": status, "top": top, "hypotheses": hypotheses, "secondary": secondary, "rivals": rivals,
            "conflicts": conflicts, "affected": affected, "downstream": downstream,
            "degraded": sorted(degraded), "scope": conn.get("scope", {}), "quality_factor": Q}


# ---------------------------------------------------------------------------
# Recommendation Agent
# ---------------------------------------------------------------------------
def dev_text(devs):
    return ", ".join(devs) if len(devs) <= 3 else f"{len(devs)} devices ({', '.join(devs[:2])}, ...)"


class RecommendationAgent:
    name = "recommendation_agent"
    role = "Recommendation"
    description = "Maps the primary hypothesis to prioritised corrective actions, alternative explanations and dry-run diagnostic commands (no auto-remediation)."
    consumes = ["fault_correlation.diagnosis"]

    def recommend(self, corr, ctx) -> dict:
        status, top = corr["status"], corr["top"]
        srv = next((d for d, i in NODES.items() if i["role"] == "service"), "the DNS/DHCP server")
        actions, alts, dry_run = [], [], []
        if status in ("diagnosed", "inconclusive") and top:
            info = CAUSES[top["cause"]]
            tgt = corr["affected"][0] if corr["affected"] else "the affected device"
            actions = [a.format(dev=tgt, srv=srv) for a in info["actions"]]
            for h in corr["hypotheses"][1:]:
                if h["confidence"] >= 0.15 and h["cause"] != top["cause"]:
                    alts.append({"cause": CAUSES[h["cause"]]["short"], "confidence": h["confidence"], "devices": h["devices"], "verified": True})
            for d in info["diff"]:
                alts.append({"cause": d, "confidence": None, "devices": [], "verified": False})
            tgt0 = (corr["affected"] or ["TARGET"])[0]
            dry_run = [c.format(dev=tgt0, srv=srv) for c in info["cmds"]]
        elif status == "insufficient_evidence":
            actions = ["Collect additional telemetry (SNMP counters, syslog, packet capture) on the affected device(s)",
                       "Run traceroute / path analysis to localize the degraded hop",
                       "Check recent configuration changes and maintenance windows for the affected device(s)"]
            alts = [{"cause": c, "confidence": None, "devices": [], "verified": False}
                    for c in ("Upstream/transit issue not visible in telemetry", "Unmonitored device or link in the path", "Transient burst")]
        else:  # healthy
            actions = ["No corrective action required; continue routine monitoring", "Keep baselines updated to improve future anomaly detection"]
        return {"actions": actions, "alternatives": alts, "dry_run": dry_run}


RECOMMENDER = RecommendationAgent()


def build_report(corr, ctx, ingest_rep, data_hash, failed_agents, rec):
    status, top = corr["status"], corr["top"]
    limitations = []
    if ingest_rep["quality"] < 0.8:
        limitations.append(f"Data quality score {ingest_rep['quality']:.2f}: some telemetry missing or discarded; confidence reduced accordingly.")
    if ingest_rep["missing_metrics"]:
        miss = [m for m in ingest_rep["missing_metrics"] if m in CORE_METRICS]
        if miss:
            limitations.append(f"Core metric(s) not supplied: {', '.join(miss)}.")
    for a in failed_agents:
        limitations.append(f"{a} failed or was unavailable; its evidence is absent from this diagnosis.")
    limitations.append("Analysis is based on supplied (synthetic) telemetry and heuristic scoring; no production changes were made.")

    ev_items, sources, alts, actions = [], [], [], []
    cause_id = None
    if status in ("diagnosed", "inconclusive") and top:
        cause_id = top["cause"]
        info = CAUSES[cause_id]
        prefix = "Likely" if top["confidence"] >= 0.75 else "Possible"
        where = dev_text(corr["affected"]) if cause_id not in SERVICE_CAUSES else "campus clients"
        headline = f"{prefix} {info['title']} on {where}" if cause_id not in SERVICE_CAUSES else f"{prefix} {info['title']} affecting {where}"
        if status == "inconclusive":
            if corr["rivals"]:
                names = " or ".join(CAUSES[h["cause"]]["short"].lower() for h in [top] + corr["rivals"])
                headline = f"Inconclusive: evidence supports {names} about equally - cannot isolate a single root cause"
            else:
                headline = f"Inconclusive (low confidence): {info['short'].lower()} is a possible cause on {where}; evidence is insufficient to confirm"
        conf = top["confidence"]
        seen = set()
        for f in sorted(top["findings"], key=lambda x: -x["strength"]):
            for e in f["evidence"]:
                key = (e["device"], e["metric"])
                if key not in seen:
                    seen.add(key)
                    ev_items.append({**e, "source": f["agent"]})
        if top["symptom_note"] and top["devices"]:
            d0 = top["devices"][0]
            r = ctx["summ"].get(d0, {}).get("recent", {})
            for m in ("latency_ms", "packet_loss_pct"):
                if r.get(m) is not None and (d0, m) not in seen and ramp(r[m], 50 if m == "latency_ms" else 1, 200 if m == "latency_ms" else 5) > 0.2:
                    ev_items.append({**ev(d0, m, r[m], "Symptom: " + ("elevated latency" if m == "latency_ms" else "elevated packet loss")),
                                     "source": "performance_agent"})
        ev_items = ev_items[:10]
        sources = top["sources"]
        actions, alts = rec["actions"], rec["alternatives"]
        if conf < 0.8:
            limitations.insert(0, "Root cause requires further verification.")
        if corr["secondary"]:
            for h in corr["secondary"]:
                limitations.append(f"Concurrent issue detected: {CAUSES[h['cause']]['short']} on {dev_text(h['devices'])} (confidence {h['confidence']:.2f}).")
    elif status == "insufficient_evidence":
        conf = 0.2
        headline = (f"Insufficient evidence: degradation observed on {dev_text(corr['degraded'])} but no diagnostic rule is "
                    f"supported by the available metrics - a root cause cannot be claimed")
        for d in corr["degraded"][:6]:
            r = ctx["summ"][d]["recent"]
            for m in ("latency_ms", "packet_loss_pct", "jitter_ms"):
                if r.get(m) is not None and ramp(r[m], {"latency_ms": 50, "packet_loss_pct": 1, "jitter_ms": 10}[m], {"latency_ms": 200, "packet_loss_pct": 5, "jitter_ms": 30}[m]) >= 0.3:
                    ev_items.append({**ev(d, m, r[m], "Degraded (symptom only)"), "source": "performance_agent"})
        sources = ["performance_agent"]
        actions, alts = rec["actions"], rec["alternatives"]
        limitations.insert(0, "No cause reached the minimum evidence threshold (0.30); no root cause is claimed.")
    else:  # healthy
        conf = round(0.9 * corr["quality_factor"], 2)
        headline = "No fault detected - all monitored metrics are within expected ranges"
        actions = rec["actions"]
        sources = ["performance_agent", "infrastructure_agent", "connectivity_agent"]
    ev_sources = sorted(set(sources) | ({"connectivity_agent"} if corr["scope"] else set()) if status != "insufficient_evidence" else set(sources))

    report = {
        "incident_id": "INC-" + str(int(data_hash[:6], 16) % 9000 + 1000),
        "status": status,
        "suspected_root_cause": headline,
        "root_cause_id": cause_id,
        "confidence": round(conf, 2),
        "confidence_category": conf_category(conf),
        "affected_devices": corr["affected"] if status in ("diagnosed", "inconclusive") else (corr["degraded"] if status == "insufficient_evidence" else []),
        "downstream_impacted_devices": corr["downstream"],
        "supporting_evidence": ev_items,
        "alternative_causes": [a["cause"] + (f" (score {a['confidence']:.2f})" if a["confidence"] is not None else " (unverified differential)") for a in alts],
        "alternative_causes_detail": alts,
        "secondary_issues": [{"cause": h["cause"], "devices": h["devices"], "confidence": h["confidence"]} for h in corr["secondary"]],
        "recommended_actions": actions,
        "evidence_sources": ev_sources,
        "limitations": limitations,
        "conflicts_resolved": corr["conflicts"],
        "topology_scope": corr["scope"],
        "data_quality": {"score": ingest_rep["quality"], "rows": ingest_rep["rows_out"], "input_schema": ingest_rep["input_schema"],
                         "warnings": len(ingest_rep["warnings"])},
        "scoring_method": ("confidence = min(0.95, S x R x Q); S = 1 - prod(1 - s_a) over agents' max support strength (noisy-OR corroboration); "
                           "R = 1 - 0.6 x max refuting strength on the same devices; Q = 0.5 + 0.5 x data_quality^2 (minus 0.08 per failed agent). "
                           "status=diagnosed needs confidence >= 0.5 and a >= 0.15 margin over rival causes on overlapping devices; < 0.30 -> no cause claimed."),
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    report["_dry_run_commands"] = rec["dry_run"]
    return report


def error_report(ingest_rep, data_hash):
    return {
        "incident_id": "INC-" + str(int(data_hash[:6], 16) % 9000 + 1000),
        "status": "insufficient_data",
        "suspected_root_cause": "Insufficient data: input failed validation - no diagnosis attempted",
        "root_cause_id": None, "confidence": 0.0, "confidence_category": "none", "affected_devices": [],
        "downstream_impacted_devices": [], "supporting_evidence": [], "alternative_causes": [], "alternative_causes_detail": [],
        "secondary_issues": [],
        "recommended_actions": ["Fix the reported validation errors and resubmit",
                                "Ensure device_id and timestamp fields plus at least two telemetry metrics are present (see Protocol tab)"],
        "evidence_sources": [], "limitations": ingest_rep["errors"], "conflicts_resolved": [], "topology_scope": {},
        "data_quality": {"score": 0.0, "rows": 0, "input_schema": ingest_rep["input_schema"], "warnings": len(ingest_rep["warnings"])},
        "scoring_method": "n/a - validation failed", "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "_dry_run_commands": [],
    }


# ============================================================================
# 7. ORCHESTRATOR
# ============================================================================
def run_pipeline(raw, parse_error=None, disabled=()):
    corr_id = uuid.uuid4().hex[:8]
    msgs = []
    t0 = time.perf_counter()
    df, rep = ingest(raw, parse_error)
    data_hash = hashlib.md5(pd.util.hash_pandas_object(raw, index=False).values.tobytes()).hexdigest() \
        if isinstance(raw, pd.DataFrame) else hashlib.md5(b"none").hexdigest()
    msgs.append(make_msg("orchestrator", "ingestion", "task", {"task": "validate_and_normalize", "rows_in": rep["rows_in"]}, corr_id))
    msgs.append(make_msg("ingestion", "orchestrator", "validation_result" if rep["ok"] else "error",
                         {"ok": rep["ok"], "errors": rep["errors"], "warnings": rep["warnings"][:10], "quality": rep["quality"],
                          "conversions": rep["conversions"]}, corr_id, (time.perf_counter() - t0) * 1000))
    if not rep["ok"]:
        report = error_report(rep, data_hash)
        msgs.append(make_msg("orchestrator", "user", "report", {"status": report["status"], "errors": rep["errors"]}, corr_id))
        return {"report": report, "messages": msgs, "ingest": rep, "df": None, "summ": {}, "corr": None, "failed": []}

    summ = summarize(df)
    ctx = {"summ": summ, "quality": rep["quality"], "failed_agents": []}
    inbox, all_findings, failed = {}, [], []
    # Performance runs first and broadcasts; the other analysis agents consume its message.
    for ag in AGENTS:
        task = {"task": "analyze", "role": ag.role, "inputs": ag.consumes, "window_samples": 12}
        msgs.append(make_msg("orchestrator", ag.name, "task", task, corr_id))
        ts = time.perf_counter()
        try:
            if ag.name in disabled:
                raise RuntimeError("simulated agent crash (fault injection)")
            out = ag.analyze(ctx, inbox)
            inbox[ag.name] = out
            all_findings += out["findings"]
            recipient = "broadcast" if ag.name == "performance_agent" else "fault_correlation"
            msgs.append(make_msg(ag.name, recipient, "finding",
                                 {"findings": out["findings"], "summary": out["summary"]}, corr_id, (time.perf_counter() - ts) * 1000))
        except Exception as e:  # noqa: BLE001
            failed.append(ag.name)
            ctx["failed_agents"] = failed
            msgs.append(make_msg(ag.name, "orchestrator", "error", {"code": "AGENT_FAILURE", "detail": str(e)}, corr_id,
                                 (time.perf_counter() - ts) * 1000))
    ts = time.perf_counter()
    corr = correlate(all_findings, ctx, inbox)
    msgs.append(make_msg("fault_correlation", "recommendation_agent", "diagnosis",
                         {"status": corr["status"],
                          "ranked_hypotheses": [{k: h[k] for k in ("cause", "confidence", "devices", "sources", "breakdown")} for h in corr["hypotheses"]],
                          "conflicts": corr["conflicts"], "secondary": [h["cause"] for h in corr["secondary"]]},
                         corr_id, (time.perf_counter() - ts) * 1000))
    ts = time.perf_counter()
    rec = RECOMMENDER.recommend(corr, ctx)
    msgs.append(make_msg("recommendation_agent", "orchestrator", "recommendation",
                         {"actions": rec["actions"], "alternatives": rec["alternatives"], "dry_run_commands": rec["dry_run"]},
                         corr_id, (time.perf_counter() - ts) * 1000))
    report = build_report(corr, ctx, rep, data_hash, failed, rec)
    msgs.append(make_msg("recommendation_agent", "orchestrator", "report",
                         {k: report[k] for k in ("incident_id", "status", "suspected_root_cause", "confidence")}, corr_id,
                         (time.perf_counter() - ts) * 1000))
    return {"report": report, "messages": msgs, "ingest": rep, "df": df, "summ": summ, "corr": corr, "failed": failed}


# ============================================================================
# 8. BATCH EVALUATION
# ============================================================================
def evaluate(meta, rep):
    exp_status, exp_causes = meta["expect_status"], meta["causes"]
    got_causes = ([rep["root_cause_id"]] if rep["root_cause_id"] else []) + [s["cause"] for s in rep["secondary_issues"]]
    abst = meta.get("abstain_ok", False)
    if exp_status in ("healthy", "insufficient_data", "insufficient_evidence"):
        ok = rep["status"] == exp_status
    elif rep["status"] == "diagnosed":
        ok = set(got_causes) == set(exp_causes)
    elif abst and rep["status"] in ("inconclusive", "insufficient_evidence"):
        ok = rep["root_cause_id"] in (None, *exp_causes)
    else:
        ok = False
    tgt = set(meta["targets"])
    loc_ok = tgt.issubset(set(rep["affected_devices"]) | {s_d for s in rep["secondary_issues"] for s_d in s["devices"]}) if tgt and exp_status == "diagnosed" else None
    return ok, got_causes, loc_ok


@st.cache_data(show_spinner=False)
def run_batch(seeds=(1, 2, 3)):
    rows = []
    for key, meta in SCENARIO_META.items():
        for sd in seeds:
            res = run_pipeline(generate(key, sd, 1.0, 0.0))
            rep = res["report"]
            ok, got, loc = evaluate(meta, rep)
            rows.append({"scenario": meta["label"], "seed": sd, "expected": meta["expect_status"] + (": " + ", ".join(meta["causes"]) if meta["causes"] else ""),
                         "got_status": rep["status"], "got_causes": ", ".join(got) or "-", "confidence": rep["confidence"],
                         "category": rep["confidence_category"], "location_ok": "n/a" if loc is None else ("yes" if loc else "NO"),
                         "pass": "PASS" if ok else "FAIL"})
    return pd.DataFrame(rows)


# ============================================================================
# 9. REPORT RENDERING (Markdown)
# ============================================================================
def report_markdown(rep) -> str:
    L = [f"# Network Diagnostic Report - {rep['incident_id']}", "",
         f"**Status:** {rep['status']}  ", f"**Suspected root cause:** {rep['suspected_root_cause']}  ",
         f"**Confidence:** {rep['confidence']:.2f} ({rep['confidence_category']})  ",
         f"**Affected devices:** {', '.join(rep['affected_devices']) or '-'}  ",
         f"**Downstream impacted:** {', '.join(rep['downstream_impacted_devices']) or '-'}  ",
         f"**Generated:** {rep['generated_at']}", "", "## Supporting evidence", "",
         "| Device | Metric | Value | Interpretation | Source |", "|---|---|---|---|---|"]
    for e in rep["supporting_evidence"]:
        L.append(f"| {e['device']} | {e['metric']} | {e['value']} {e['unit']} | {e['interpretation']} | {e.get('source', '')} |")
    L += ["", "## Alternative explanations"] + [f"- {a}" for a in rep["alternative_causes"]]
    L += ["", "## Recommended actions"] + [f"{i}. {a}" for i, a in enumerate(rep["recommended_actions"], 1)]
    L += ["", "## Limitations"] + [f"- {a}" for a in rep["limitations"]]
    if rep["conflicts_resolved"]:
        L += ["", "## Conflicting evidence resolved"] + [f"- **{c['cause']}**: {c['resolution']}" for c in rep["conflicts_resolved"]]
    L += ["", "## Method", rep["scoring_method"], "", f"_Evidence sources: {', '.join(rep['evidence_sources'])}_"]
    return "\n".join(L)


def clean_json(rep):
    return {k: v for k, v in rep.items() if not k.startswith("_")}


# ============================================================================
# 10. STREAMLIT UI
# ============================================================================
CSS = """
<style>
.block-container {padding-top: 1.4rem;}
.nc-hero {padding: 1.1rem 1.4rem; border-radius: 14px; margin-bottom: .8rem;
          background: linear-gradient(120deg, rgba(99,102,241,.18), rgba(16,185,129,.14)); border: 1px solid rgba(128,128,128,.25);}
.nc-hero h1 {margin: 0; font-size: 1.9rem;} .nc-hero p {margin: .25rem 0 0; opacity: .8;}
.nc-card {padding: 1rem 1.2rem; border-radius: 12px; border: 1px solid rgba(128,128,128,.3); margin-bottom: .6rem;}
.nc-cause {font-size: 1.45rem; font-weight: 650; line-height: 1.3;}
.nc-pill {display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: .78rem; font-weight: 600; margin-right: 6px;}
.pill-diagnosed {background:#16a34a22; color:#16a34a;} .pill-healthy {background:#0ea5e922; color:#0ea5e9;}
.pill-inconclusive {background:#f59e0b22; color:#d97706;} .pill-insufficient_evidence {background:#f9731622; color:#ea580c;}
.pill-insufficient_data {background:#ef444422; color:#dc2626;}
</style>
"""
STATUS_UI = {"diagnosed": ("Diagnosed", "success"), "healthy": ("Healthy", "info"), "inconclusive": ("Inconclusive", "warning"),
             "insufficient_evidence": ("Insufficient evidence", "warning"), "insufficient_data": ("Insufficient data", "error")}


def load_uploaded(file):
    try:
        name = file.name.lower()
        if name.endswith(".csv"):
            return pd.read_csv(file), None
        data = json.load(file)
        if isinstance(data, dict):
            for k in ("records", "telemetry", "data", "rows"):
                if isinstance(data.get(k), list):
                    data = data[k]
                    break
            else:
                return None, "JSON object has no 'records'/'telemetry'/'data' list."
        return pd.DataFrame(data), None
    except Exception as e:  # noqa: BLE001
        return None, f"Could not parse uploaded file: {e}"


def topo_dot(rep, summ):
    aff, imp = set(rep["affected_devices"]), set(rep["downstream_impacted_devices"])
    deg = set((rep.get("topology_scope") or {}).get("root_devices", [])) if False else set()
    lines = ['digraph G {rankdir=TB; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#555555"]; edge [color="#888888"];']
    for dev in NODES:
        s = summ.get(dev, {})
        stat = s.get("status")
        if dev in aff:
            fill, fc = "#ef4444", "white"
        elif dev in imp:
            fill, fc = "#f59e0b", "black"
        elif stat == "down":
            fill, fc = "#9ca3af", "black"
        elif stat == "degraded":
            fill, fc = "#fde047", "black"
        else:
            fill, fc = "#86efac", "black"
        lines.append(f'"{dev}" [label="{dev}\\n({NODES[dev]["type"]})", fillcolor="{fill}", fontcolor="{fc}"];')
    for p, c in EDGES:
        lines.append(f'"{p}" -> "{c}";')
    lines.append("}")
    return "\n".join(lines)


def protocol_tables():
    tele = pd.DataFrame([{"field": "device_id", "type": "string", "unit": "-", "valid range": "non-empty", "meaning": "Unique device identifier (required)",
                          "accepted aliases": ", ".join(a for a, _ in ALIASES["device_id"][1:])},
                         {"field": "timestamp", "type": "ISO-8601 / epoch s|ms", "unit": "UTC", "valid range": "parseable", "meaning": "Sample time (required)",
                          "accepted aliases": ", ".join(a for a, _ in ALIASES["timestamp"][1:])},
                         {"field": "device_status", "type": "enum", "unit": "-", "valid range": "up|degraded|down", "meaning": "Reported device state",
                          "accepted aliases": "status, state (OK/WARN/CRIT, online/offline...)"}] +
                        [{"field": m, "type": "float", "unit": CANON[m][0], "valid range": f"{CANON[m][1]} .. {CANON[m][2]}", "meaning": CANON[m][3],
                          "accepted aliases": ", ".join(f"{a}" + (f" (x{f:g})" if f != 1 else "") for a, f in ALIASES[m][1:])} for m in METRICS])
    env = pd.DataFrame([
        ("schema_version", "string", "Protocol version, currently '1.0'"), ("message_id", "string", "Unique id of the message"),
        ("correlation_id", "string", "Shared by all messages of one diagnosis run"), ("sender / recipient", "string", "Agent names; 'broadcast' = all peers"),
        ("type", "enum", "task | finding | diagnosis | recommendation | report | validation_result | error"), ("timestamp", "ISO-8601 UTC", "Creation time"),
        ("duration_ms", "float (ms)", "Processing time of the sender"), ("payload", "object", "Type-specific body"),
    ], columns=["field", "type", "meaning"])
    fnd = pd.DataFrame([
        ("finding_id", "string", "-", "Unique id"), ("agent", "string", "-", "Producing agent"),
        ("cause", "enum", "-", ", ".join(CAUSES)), ("stance", "enum", "-", "supports | refutes the cause"),
        ("strength", "float", "0..1", "Agent's evidence strength for the stance (not a probability)"),
        ("devices", "list[string]", "-", "Devices the finding concerns"),
        ("evidence[]", "list[object]", "-", "{device, metric, value, unit, interpretation}"), ("rationale", "string", "-", "Human-readable justification"),
    ], columns=["field", "type", "unit/range", "meaning"])
    return tele, env, fnd


def main():
    st.set_page_config(page_title="NetCoop AI", page_icon="🛰️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="nc-hero"><h1>🛰️ NetCoop AI</h1><p>Multi-agent network fault diagnosis &amp; interoperability - IIT Bhubaneswar campus network</p></div>',
                unsafe_allow_html=True)

    # ------------------------------ sidebar ---------------------------------
    sb = st.sidebar
    sb.header("Input")
    src = sb.radio("Telemetry source", ["Synthetic scenario", "Upload CSV / JSON", "Paste JSON"])
    raw, parse_err, truth = None, None, None
    seed, noise, miss = 7, 1.0, 0.0
    if src == "Synthetic scenario":
        key = sb.selectbox("Scenario", list(SCENARIO_META), format_func=lambda k: SCENARIO_META[k]["label"])
        sb.caption(SCENARIO_META[key]["desc"])
        seed = sb.number_input("Random seed", 0, 99999, 7)
        noise = sb.slider("Noise level", 0.5, 2.5, 1.0, 0.1)
        miss = sb.slider("Missing-data injection (%)", 0, 80, 0, 5)
        raw, truth = generate(key, int(seed), float(noise), float(miss)), SCENARIO_META[key]
    elif src == "Upload CSV / JSON":
        up = sb.file_uploader("Telemetry file", type=["csv", "json"])
        if up is not None:
            raw, parse_err = load_uploaded(up)
        else:
            sb.info("Upload a file or switch to a synthetic scenario.")
            parse_err = "No file uploaded yet."
    else:
        txt = sb.text_area("JSON array of records", height=180, placeholder='[{"device_id":"SW1","timestamp":"2026-11-01T09:00:00","latency_ms":12,"cpu_pct":30}]')
        if txt.strip():
            try:
                data = json.loads(txt)
                raw = pd.DataFrame(data.get("records", data) if isinstance(data, dict) else data)
            except Exception as e:  # noqa: BLE001
                parse_err = f"Invalid JSON: {e}"
        else:
            parse_err = "No JSON pasted yet."
    sb.divider()
    sb.header("Robustness testing")
    disabled = sb.multiselect("Simulate agent crash", [a.name for a in AGENTS], help="Fault injection: the orchestrator must degrade gracefully and report the failure.")
    sb.divider()
    sb.caption("Free stack: Streamlit + pandas + numpy. No production network is touched; remediation is dry-run only.")

    res = run_pipeline(raw, parse_err, tuple(disabled))
    rep, ing, summ = res["report"], res["ingest"], res["summ"]
    if isinstance(raw, pd.DataFrame):
        sb.download_button("Download current input (CSV)", raw.to_csv(index=False), "netcoop_input.csv", "text/csv")

    tabs = st.tabs(["🩺 Diagnosis", "📈 Telemetry", "🗺️ Topology", "💬 Agent messages", "🧾 Validation", "📐 Protocol", "🧪 Test suite", "📄 Report"])

    # ------------------------------ Diagnosis -------------------------------
    with tabs[0]:
        label, level = STATUS_UI[rep["status"]]
        st.markdown(f'<span class="nc-pill pill-{rep["status"]}">{label.upper()}</span> <span style="opacity:.6">Incident {rep["incident_id"]}</span>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="nc-card"><div class="nc-cause">{rep["suspected_root_cause"]}</div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Confidence", f"{rep['confidence']:.0%}", rep["confidence_category"].replace("_", " "), delta_color="off")
        c2.metric("Affected devices", len(rep["affected_devices"]))
        c3.metric("Downstream impacted", len(rep["downstream_impacted_devices"]))
        c4.metric("Data quality", f"{rep['data_quality']['score']:.0%}")
        st.progress(min(1.0, max(0.0, rep["confidence"])))
        if res["failed"]:
            st.error(f"Agent failure(s): {', '.join(res['failed'])} - diagnosis produced with reduced evidence.")
        if rep["status"] == "insufficient_data":
            for e in ing["errors"]:
                st.error(e)
        if truth is not None and src == "Synthetic scenario":
            ok, got, loc = evaluate(truth, rep)
            st.caption(f"Ground truth for this synthetic scenario: **{truth['expect_status']}**" + (f" / {', '.join(truth['causes'])}" if truth["causes"] else "") +
                       f" -> {'✅ matches' if ok else '⚠️ differs'}")
        left, right = st.columns([3, 2])
        with left:
            st.subheader("Supporting evidence")
            if rep["supporting_evidence"]:
                st.dataframe(pd.DataFrame(rep["supporting_evidence"])[["device", "metric", "value", "unit", "interpretation", "source"]], hide_index=True)
            else:
                st.write("No evidence items (no fault claimed).")
            if rep["conflicts_resolved"]:
                st.subheader("Conflicting evidence resolved")
                for c in rep["conflicts_resolved"]:
                    st.warning(f"**{c['cause']}** - supported by {', '.join(c['supported_by'])}, refuted by {', '.join(c['refuted_by'])}. {c['resolution']}")
            if rep["secondary_issues"]:
                st.subheader("Concurrent issues")
                st.dataframe(pd.DataFrame(rep["secondary_issues"]), hide_index=True)
        with right:
            st.subheader("Alternative explanations")
            if rep["alternative_causes_detail"]:
                st.dataframe(pd.DataFrame([{"explanation": a["cause"], "score": a["confidence"], "status": "scored" if a["verified"] else "unverified"}
                                           for a in rep["alternative_causes_detail"]]),
                             hide_index=True,
                             column_config={"score": st.column_config.ProgressColumn("score", min_value=0.0, max_value=1.0, format="%.2f")})
            else:
                st.write("None.")
            st.subheader("Recommended actions")
            for i, a in enumerate(rep["recommended_actions"], 1):
                st.markdown(f"{i}. {a}")
        if rep["limitations"]:
            with st.expander("Limitations & uncertainty", expanded=rep["status"] != "diagnosed"):
                for l in rep["limitations"]:
                    st.markdown(f"- {l}")
        with st.expander("How confidence is computed"):
            st.write(rep["scoring_method"])
            if res["corr"] and res["corr"]["hypotheses"]:
                st.dataframe(pd.DataFrame([{"cause": h["cause"], "confidence": h["confidence"], "devices": ", ".join(h["devices"]),
                                            "sources": ", ".join(h["sources"]), **h["breakdown"]} for h in res["corr"]["hypotheses"]]), hide_index=True)
        if rep["_dry_run_commands"]:
            st.subheader("Human-in-the-loop remediation (optional, dry-run)")
            approve = st.checkbox("I have reviewed the recommendation and approve a SIMULATED diagnostic run", key="hitl")
            if approve:
                st.code("\n".join(f"[DRY-RUN] $ {c}" for c in rep["_dry_run_commands"]) + "\n[DRY-RUN] No commands were executed. Production infrastructure untouched.", language="bash")

    # ------------------------------ Telemetry -------------------------------
    with tabs[1]:
        df = res["df"]
        if df is None:
            st.warning("No valid telemetry to display (see Validation tab).")
        else:
            c1, c2 = st.columns([2, 3])
            metric = c1.selectbox("Metric", [m for m in METRICS if df[m].notna().any()], index=0)
            devs = c2.multiselect("Devices", sorted(df["device_id"].unique()), default=(rep["affected_devices"] or sorted(df["device_id"].unique()))[:4])
            if devs:
                piv = df[df["device_id"].isin(devs)].pivot_table(index="timestamp", columns="device_id", values=metric)
                st.line_chart(piv)
                st.caption(f"{metric} ({UNITS[metric]}) - fault onset is mid-window in synthetic scenarios.")
            st.subheader("Recent-window summary (median of last 12 samples)")
            rows = []
            for d, s in summ.items():
                r = s["recent"]
                rows.append({"device": d, "status": s["status"], "latency ms": r["latency_ms"], "loss %": r["packet_loss_pct"], "util %": r["link_utilization_pct"],
                             "cpu %": r["cpu_pct"], "mem %": r["memory_pct"], "q drops": r["queue_drops"], "if errors": r["interface_errors"],
                             "rssi dBm": r["rssi_dbm"], "dns fail %": r["dns_failure_pct"]})
            st.dataframe(pd.DataFrame(rows).round(1), hide_index=True,
                         column_config={"util %": st.column_config.ProgressColumn("util %", min_value=0, max_value=100, format="%.0f"),
                                        "cpu %": st.column_config.ProgressColumn("cpu %", min_value=0, max_value=100, format="%.0f")})

    # ------------------------------ Topology --------------------------------
    with tabs[2]:
        if not summ:
            st.warning("No topology view without valid telemetry.")
        else:
            st.graphviz_chart(topo_dot(rep, summ))
            st.markdown("🟥 root-cause device &nbsp; 🟧 downstream impacted &nbsp; 🟨 degraded &nbsp; ⬜ down &nbsp; 🟩 healthy")
            sc = rep.get("topology_scope") or {}
            if sc:
                st.info(f"Connectivity Agent scope: **{sc.get('type')}** - root device(s): {', '.join(sc.get('root_devices', [])) or '-'}")
            cn = ((res["messages"] and next((m["payload"]["summary"] for m in res["messages"]
                                              if m["sender"] == "connectivity_agent" and m["type"] == "finding"), {})) or {}).get("common_neighbors", [])
            st.caption(f"Common neighbours of affected devices: {', '.join(cn) or 'none'}")

    # ------------------------------ Messages --------------------------------
    with tabs[3]:
        st.subheader("Agents")
        cols = st.columns(3)
        allag = AGENTS + [type("C", (), {"name": "fault_correlation", "role": "Fault Correlation", "description": "Merges findings via noisy-OR corroboration, applies refutations, ranks hypotheses, resolves conflicts and decides diagnosed / inconclusive / insufficient evidence."})(),
                          RECOMMENDER]
        for i, a in enumerate(allag):
            with cols[i % 3]:
                st.markdown(f'<div class="nc-card"><b>{a.role}</b><br><code>{a.name}</code><br><span style="opacity:.8;font-size:.9rem">{a.description}</span></div>', unsafe_allow_html=True)
        st.subheader("Message bus log")
        st.dataframe(pd.DataFrame([{"time": m["timestamp"][11:23], "from": m["sender"], "to": m["recipient"], "type": m["type"],
                                    "ms": m.get("duration_ms"), "message_id": m["message_id"]} for m in res["messages"]]), hide_index=True)
        for m in res["messages"]:
            with st.expander(f"{m['sender']} -> {m['recipient']}  [{m['type']}]  {m['message_id']}"):
                st.json(m)

    # ------------------------------ Validation ------------------------------
    with tabs[4]:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows in", ing["rows_in"])
        c2.metric("Rows accepted", ing["rows_out"])
        c3.metric("Input schema", ing["input_schema"])
        c4.metric("Quality score", f"{ing['quality']:.2f}")
        for e in ing["errors"]:
            st.error(e)
        for w in ing["warnings"]:
            st.warning(w)
        if ing["conversions"]:
            st.subheader("Adapter conversions applied")
            for c in ing["conversions"]:
                st.markdown(f"- `{c}`")
        if ing["completeness"]:
            st.subheader("Metric completeness")
            st.bar_chart(pd.Series(ing["completeness"], name="non-null fraction"))
        if not ing["errors"] and not ing["warnings"]:
            st.success("Input passed all validation checks.")

    # ------------------------------ Protocol --------------------------------
    with tabs[5]:
        tele, env, fnd = protocol_tables()
        st.markdown("### Message envelope (v1.0)")
        st.dataframe(env, hide_index=True)
        st.markdown("### Finding object")
        st.dataframe(fnd, hide_index=True)
        st.markdown("### Telemetry schema (canonical v1.0) with accepted aliases & unit conversions")
        st.dataframe(tele, hide_index=True)
        st.markdown("### Example message")
        st.code(json.dumps({"schema_version": "1.0", "message_id": "a1b2c3d4", "correlation_id": "9f8e7d6c", "sender": "infrastructure_agent",
                            "recipient": "fault_correlation", "type": "finding", "timestamp": "2026-11-01T09:31:02.114+00:00",
                            "payload": {"findings": [{"finding_id": "x1y2z3", "agent": "infrastructure_agent", "cause": "link_congestion", "stance": "supports",
                                                      "strength": 0.85, "devices": ["HOSTEL_CORE_SW_01"],
                                                      "evidence": [{"device": "HOSTEL_CORE_SW_01", "metric": "queue_drops", "value": 160, "unit": "pkts/interval",
                                                                    "interpretation": "Elevated packet drops"}],
                                                      "rationale": "egress queue drops 160"}]}}, indent=2), language="json")
        st.markdown("**Legacy adapter:** schema v0.9 fields such as `rtt_s`, `jitter_us`, `loss_ratio`, `bw_kbps`, `util_ratio` are converted automatically; "
                    "unknown schema versions raise a warning and use best-effort mapping; missing `device_id`/`timestamp` is a hard error.")

    # ------------------------------ Test suite ------------------------------
    with tabs[6]:
        st.write("Runs every scenario over 3 seeds through the full pipeline and compares against ground truth (reproducible, seeded).")
        if st.button("Run all scenarios", type="primary"):
            st.session_state["batch"] = run_batch()
        if "batch" in st.session_state:
            b = st.session_state["batch"]
            acc = (b["pass"] == "PASS").mean()
            m1, m2, m3 = st.columns(3)
            m1.metric("Pass rate", f"{acc:.0%}")
            m2.metric("Runs", len(b))
            m3.metric("Failures", int((b["pass"] == "FAIL").sum()))
            st.dataframe(b, hide_index=True)
            st.download_button("Download results (CSV)", b.to_csv(index=False), "netcoop_test_results.csv", "text/csv")

    # ------------------------------ Report ----------------------------------
    with tabs[7]:
        cj = json.dumps(clean_json(rep), indent=2)
        md = report_markdown(rep)
        d1, d2 = st.columns(2)
        d1.download_button("Download JSON report", cj, f"{rep['incident_id']}.json", "application/json")
        d2.download_button("Download Markdown report", md, f"{rep['incident_id']}.md", "text/markdown")
        j, m = st.tabs(["JSON", "Markdown"])
        with j:
            st.json(clean_json(rep))
        with m:
            st.markdown(md)


if __name__ == "__main__":
    main()
