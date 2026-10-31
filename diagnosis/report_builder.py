
def generate_diagnosis_explanation(diagnosis: dict) -> str:
    primary = diagnosis.get("primary_hypothesis")

    if not primary:
        if diagnosis.get("diagnosis_status") == "no_fault_detected":
            return (
                "No known fault signature was detected in the available "
                "core telemetry. This does not guarantee that every "
                "network service is healthy."
            )

        return (
            "Available evidence is insufficient to identify a probable "
            "root cause."
        )

    hypothesis = primary.get("hypothesis")
    score = primary.get("score")
    evidence = primary.get("supporting_evidence", [])

    explanation = (
        f"The leading hypothesis is {hypothesis}, "
        f"supported by {len(evidence)} evidence item(s) "
        f"and a heuristic score of {score} points."
    )

    if diagnosis.get("alternative_causes"):
        alternatives = [
            item.get("hypothesis")
            for item in diagnosis["alternative_causes"]
        ]
        explanation += (
            " Other possible causes include: "
            + ", ".join(alternatives)
            + "."
        )

    return explanation


def identify_additional_data_needed(diagnosis: dict) -> list[str]:
    missing = diagnosis.get("missing_data", [])

    additional_data = []

    for item in missing:
        additional_data.append(
            f"Collect missing measurement: {item}."
        )

    primary = diagnosis.get("primary_hypothesis")

    if not primary:
        if diagnosis.get("diagnosis_status") == "insufficient_evidence":
            additional_data.append(
                "Collect CPU, link utilization, packet loss and latency measurements."
            )

        return additional_data

    hypothesis = primary.get("hypothesis")

    if hypothesis == "interface_or_hardware_fault":
        additional_data.extend([
            "Collect interface error-counter trends.",
            "Inspect cable, transceiver and physical interface health.",
            "Collect device logs and hardware diagnostics.",
        ])

    elif hypothesis == "congestion":
        additional_data.extend([
            "Collect traffic volume and bandwidth-usage breakdowns.",
            "Collect queue-depth and queue-drop trends.",
            "Inspect QoS policies and interface capacity.",
        ])

    elif hypothesis == "cpu_overload":
        additional_data.extend([
            "Collect per-process CPU utilization.",
            "Inspect device logs and CPU utilization trends.",
        ])

    elif hypothesis == "dns_failure":
        additional_data.extend([
            "Collect DNS server availability and resolution test results.",
            "Collect DNS response-time and timeout trends.",
        ])

    elif hypothesis == "dhcp_failure":
        additional_data.extend([
            "Collect DHCP lease allocation and pool utilization.",
            "Collect DHCP server availability and failure logs.",
        ])

    return list(dict.fromkeys(additional_data))

def build_diagnostic_report(
    incident_id: str,
    diagnosis: dict,
    recommendations: list[dict] | list[str],
    connectivity_findings: dict | None = None,
) -> dict:
    """
    Combines diagnosis, evidence, connectivity and recommendations
    into one unified diagnostic report.
    """

    if not isinstance(diagnosis, dict):
        raise ValueError("diagnosis must be a dictionary.")

    if not incident_id:
        raise ValueError("incident_id is required.")

    if not isinstance(recommendations, list):
        raise ValueError("recommendations must be a list.")

    primary = diagnosis.get("primary_hypothesis")

    if primary is not None and not isinstance(primary, dict):
        raise ValueError("primary_hypothesis must be a dictionary or None.")

    connectivity_findings = connectivity_findings or {}

    if not isinstance(connectivity_findings, dict):
        raise ValueError("connectivity_findings must be a dictionary.")

    if primary:
        suspected_root_cause = primary.get("hypothesis")
        diagnostic_score = primary.get("score")
    else:
        suspected_root_cause = None
        diagnostic_score = None

    limitations = []

    if diagnosis.get("diagnosis_status") == "insufficient_evidence":
        limitations.append(
            "Insufficient telemetry to determine a probable root cause."
        )

    if diagnosis.get("missing_data"):
        limitations.append(
            "Some telemetry or service-health measurements are missing."
        )

    if connectivity_findings.get("unknown_devices"):
        limitations.append(
            "Some affected devices are missing from the supplied topology."
        )

    if not connectivity_findings.get("connected_devices"):
        limitations.append(
            "No usable network topology relationships were available "
            "to determine the wider impact."
        )
    diagnosis_explanation = generate_diagnosis_explanation(diagnosis)
    additional_data_needed = identify_additional_data_needed(diagnosis)

    return {
        "incident_id": incident_id,
        "status": diagnosis.get("diagnosis_status", "unknown"),
        "suspected_root_cause": suspected_root_cause,
        "confidence": {
            "value": diagnostic_score,
            "type": diagnosis.get("score_type", "heuristic_points"),
        },
        "affected_devices": connectivity_findings.get(
            "affected_devices", []
        ),
        "connected_devices": connectivity_findings.get(
            "connected_devices", {}
        ),
        "supporting_evidence": (
            primary.get("supporting_evidence", []) if primary else []
        ),
        "alternative_causes": diagnosis.get("alternative_causes", []),
        "recommended_actions": recommendations,
        "evidence_sources": diagnosis.get("agent_statuses", {}),
        "conflicts": diagnosis.get("conflicts", []),
        "limitations": limitations,
        "diagnosis_explanation": diagnosis_explanation,
        "additional_data_needed": additional_data_needed,
    }

