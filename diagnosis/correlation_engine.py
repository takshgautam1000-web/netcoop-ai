
from diagnosis.hypothesis_engine import score_hypotheses
from protocol.schemas import AgentMessage, MessageType

HYPOTHESIS_METRICS = {
    "congestion": [
        "latency_ms",
        "link_utilization_percent",
        "packet_loss_percent",
        "queue_drops",
    ],
    "cpu_overload": [
        "cpu_percent",
    ],
    "interface_or_hardware_fault": [
        "interface_errors",
    ],
    "dns_failure": [
        "dns_resolution_success_percent",
        "dns_response_time_ms",
        "dns_timeout_count",
    ],
    "dhcp_failure": [
        "dhcp_success_percent",
        "dhcp_response_time_ms",
        "dhcp_failure_count",
    ],
}



def detect_conflicts(agent_findings: list[dict], all_evidence: list[dict]) -> list[dict]:

    conflicts = []

    reported_status = None

    for finding in agent_findings:
        if finding.get("agent") == "infrastructure_agent":
            reported_status = finding.get("reported_device_status")
            break

    if not reported_status:
        return conflicts

    reported_status = str(reported_status).strip().lower()

    warning_thresholds = {
        "cpu_percent": 70,
        "link_utilization_percent": 60,
        "packet_loss_percent": 0.1,
        "latency_ms": 100,
        "jitter_ms": 20,
        "queue_drops": 1,
        "interface_errors": 1,
    }

    critical_thresholds = {
        "cpu_percent": 95,
        "link_utilization_percent": 95,
        "packet_loss_percent": 10,
        "latency_ms": 500,
        "queue_drops": 5000,
        "interface_errors": 100,
    }

    warning_evidence = []
    critical_evidence = []

    for item in all_evidence:
        metric = item["metric"]
        value = item["value"]

        if metric in warning_thresholds and value >= warning_thresholds[metric]:
            warning_evidence.append(item)

        if metric in critical_thresholds and value >= critical_thresholds[metric]:
            critical_evidence.append(item)

    description = None
    contradicting_evidence = []

    if reported_status == "healthy" and warning_evidence:
        description = (
            "Device reports Healthy, but available measurements "
            "indicate elevated network conditions."
        )
        contradicting_evidence = warning_evidence

    elif reported_status == "warning" and critical_evidence:
        description = (
            "Device reports Warning, but available measurements "
            "indicate critical conditions."
        )
        contradicting_evidence = critical_evidence

    elif reported_status == "warning" and all_evidence and not warning_evidence:
        description = (
            "Device reports Warning, but available measurements "
            "do not show elevated conditions."
        )
        contradicting_evidence = all_evidence

    elif reported_status == "critical" and all_evidence and not critical_evidence:
        description = (
            "Device reports Critical, but available measurements "
            "do not corroborate critical conditions."
        )
        contradicting_evidence = all_evidence

    if description:
        conflicts.append({
            "type": "status_metric_mismatch",
            "reported_status": reported_status,
            "description": description,
            "contradicting_evidence": contradicting_evidence,
        })

    return conflicts


def normalize_agent_finding(finding: dict) -> dict:
    """
    Converts different agent output formats into
    one common format for the Correlation Engine.
    """

    normalized = finding.copy()

    # Performance and Infrastructure use 'findings'.
    # Service Health uses 'evidence'.
    if "evidence" not in normalized:
        normalized["evidence"] = normalized.get("findings", [])

    # Performance and Infrastructure use 'missing_metrics'.
    # Service Health uses 'missing_data'.
    if "missing_data" not in normalized:
        normalized["missing_data"] = normalized.get(
            "missing_metrics", []
        )

    return normalized


def agent_message_to_finding(message: AgentMessage) -> dict:
    """
    Extracts an agent's findings from its AgentMessage envelope.
    Converts them into the format expected by the Correlation Engine.
    """

    if message.message_type != MessageType.FINDING:
        raise ValueError("Expected a FINDING message.")

    payload = message.payload

    finding = {
        "agent": payload.get("agent", message.sender),
        "status": message.status.value,
        "evidence": payload.get(
            "evidence",
            payload.get("findings", [])
        ),
        "missing_data": payload.get(
            "missing_data",
            payload.get("missing_metrics", [])
        ),
    }

    # Preserve the device status for conflict detection.
    if "reported_device_status" in payload:
        finding["reported_device_status"] = (
            payload["reported_device_status"]
        )

    # Preserve topology information for future correlation.
    for key in (
        "connected_devices",
        "common_neighbors",
        "unknown_devices",
    ):
        if key in payload:
            finding[key] = payload[key]

    return finding


def has_sufficient_core_telemetry(all_evidence: list[dict]) -> bool:
    """
    Checks whether enough core performance measurements
    are available to make a preliminary health assessment.
    """

    available_metrics = {
        item["metric"]
        for item in all_evidence
        if item.get("value") is not None
    }

    required_metrics = {
        "cpu_percent",
        "link_utilization_percent",
        "packet_loss_percent",
        "latency_ms",
    }

    return required_metrics.issubset(available_metrics)


def correlate_findings(agent_findings: list[dict]) -> dict:

    if not isinstance(agent_findings, list):
        raise ValueError("agent_findings must be a list.")

    all_evidence = []
    missing_data = []
    agent_statuses = {}
    prepared_findings = []

    # 1. Collect evidence from all agents
    for original_finding in agent_findings:

        # Convert AgentMessage into a dictionary first
        if isinstance(original_finding, AgentMessage):
            original_finding = agent_message_to_finding(original_finding)

        # Validate the converted result
        if not isinstance(original_finding, dict):
            raise ValueError("Each agent finding must be a dictionary.")

        finding = normalize_agent_finding(original_finding)
        prepared_findings.append(finding)

        if not isinstance(finding, dict):
            raise ValueError("Each agent finding must be a dictionary.")

        agent_name = finding.get("agent", "unknown")
        agent_statuses[agent_name] = finding.get("status", "UNKNOWN")

        evidence = finding.get("evidence", [])

        if not isinstance(evidence, list):
            raise ValueError("Agent evidence must be a list.")

        for item in evidence:
            if not isinstance(item, dict):
                raise ValueError("Each evidence item must be a dictionary.")

            if "metric" not in item or "value" not in item:
                raise ValueError("Evidence must contain metric and value.")

            if item["value"] is not None:
                all_evidence.append(item)

        missing = finding.get("missing_data", [])

        if not isinstance(missing, list):
            raise ValueError("missing_data must be a list.")

        missing_data.extend(missing)

    # 2. Calculate hypothesis scores
    scores = score_hypotheses(all_evidence)

    conflicts = detect_conflicts(prepared_findings, all_evidence)

    # 3. Identify evidence supporting each hypothesis
    supporting_evidence = {}

    for hypothesis, metrics in HYPOTHESIS_METRICS.items():

        supporting_evidence[hypothesis] = [
            item
            for item in all_evidence
            if item["metric"] in metrics
        ]

    # 4. Rank hypotheses
    ranked_hypotheses = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    ranked_hypotheses = [
        {
            "hypothesis": hypothesis,
            "score": score,
            "supporting_evidence": supporting_evidence[hypothesis],
        }
        for hypothesis, score in ranked_hypotheses
        if score > 0
    ]

    # 5. Identify primary and alternative causes
    primary_hypothesis = (
        ranked_hypotheses[0]
        if ranked_hypotheses
        else None
    )

    alternative_causes = ranked_hypotheses[1:]

    # 6. Determine diagnosis status
    has_core_telemetry = has_sufficient_core_telemetry(all_evidence)

    if not all_evidence:
        diagnosis_status = "insufficient_evidence"

    elif not ranked_hypotheses:
        if has_core_telemetry:
            diagnosis_status = "no_fault_detected"
        else:
            diagnosis_status = "insufficient_evidence"

    elif missing_data or not has_core_telemetry:
        diagnosis_status = "partial"

    else:
        diagnosis_status = "diagnosed"

    return {
        "diagnosis_status": diagnosis_status,
        "primary_hypothesis": primary_hypothesis,
        "ranked_hypotheses": ranked_hypotheses,
        "alternative_causes": alternative_causes,
        "all_evidence": all_evidence,
        "missing_data": sorted(set(missing_data)),
        "agent_statuses": agent_statuses,
        "score_type": "heuristic_points",
        "conflicts": conflicts
    }
