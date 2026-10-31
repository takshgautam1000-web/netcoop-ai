
from diagnosis.report_builder import build_diagnostic_report


def test_builds_complete_report():
    diagnosis = {
        "diagnosis_status": "partial",
        "primary_hypothesis": {
            "hypothesis": "interface_or_hardware_fault",
            "score": 5,
            "supporting_evidence": [
                {
                    "metric": "interface_errors",
                    "value": 250,
                    "unit": "count",
                }
            ],
        },
        "alternative_causes": [],
        "missing_data": ["dns", "dhcp"],
        "agent_statuses": {
            "infrastructure_agent": "COMPLETED"
        },
        "score_type": "heuristic_points",
        "conflicts": [],
    }

    recommendations = [
        "Inspect network interfaces and physical connections."
    ]

    report = build_diagnostic_report(
        incident_id="INC-001",
        diagnosis=diagnosis,
        recommendations=recommendations,
        connectivity_findings={
            "affected_devices": ["SW_1", "SW_2"],
            "connected_devices": {
                "SW_1": ["SW_1", "SW_2"],
                "SW_2": ["SW_1", "SW_2"],
            },
            "unknown_devices": [],
        },
    )

    assert report["incident_id"] == "INC-001"
    assert report["suspected_root_cause"] == "interface_or_hardware_fault"
    assert report["confidence"]["value"] == 5
    assert report["confidence"]["type"] == "heuristic_points"
    assert len(report["supporting_evidence"]) == 1
    assert report["affected_devices"] == ["SW_1", "SW_2"]
    assert len(report["limitations"]) > 0


def test_report_handles_insufficient_evidence():
    diagnosis = {
        "diagnosis_status": "insufficient_evidence",
        "primary_hypothesis": None,
        "alternative_causes": [],
        "missing_data": ["latency_ms", "packet_loss_percent"],
        "agent_statuses": {},
        "score_type": "heuristic_points",
        "conflicts": [],
    }

    report = build_diagnostic_report(
        incident_id="INC-002",
        diagnosis=diagnosis,
        recommendations=["Collect additional telemetry."],
    )

    assert report["suspected_root_cause"] is None
    assert report["confidence"]["value"] is None
    assert report["supporting_evidence"] == []
    assert report["status"] == "insufficient_evidence"


def test_rejects_invalid_diagnosis():
    try:
        build_diagnostic_report(
            incident_id="INC-003",
            diagnosis=[],
            recommendations=[],
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
