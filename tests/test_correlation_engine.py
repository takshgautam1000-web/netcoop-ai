import pytest
from diagnosis.correlation_engine import correlate_findings
from protocol.schemas import AgentMessage, MessageType, MessageStatus

def test_combines_findings():
    findings = [
        {
            "agent": "performance_agent",
            "evidence": [
                {"metric": "latency_ms", "value": 250},
            ],
            "missing_data": [],
        },
        {
            "agent": "infrastructure_agent",
            "evidence": [
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_data": [],
        },
    ]

    result = correlate_findings(findings)

    assert len(result["all_evidence"]) == 2
    assert result["diagnosis_status"] == "partial"


def test_ranks_hypotheses():
    findings = [
        {
            "agent": "infrastructure_agent",
            "evidence": [
                {"metric": "interface_errors", "value": 250},
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    assert (
        result["ranked_hypotheses"][0]["hypothesis"]
        == "interface_or_hardware_fault"
    )


def test_missing_evidence():
    findings = [
        {
            "agent": "service_health_agent",
            "evidence": [],
            "missing_data": ["DNS health measurements"],
        }
    ]

    result = correlate_findings(findings)

    assert result["diagnosis_status"] == "insufficient_evidence"
    assert "DNS health measurements" in result["missing_data"]


def test_duplicate_missing_data():
    findings = [
        {
            "agent": "performance_agent",
            "evidence": [],
            "missing_data": ["latency_ms"],
        },
        {
            "agent": "infrastructure_agent",
            "evidence": [],
            "missing_data": ["latency_ms"],
        },
    ]

    result = correlate_findings(findings)

    assert result["missing_data"] == ["latency_ms"]

    
def test_primary_hypothesis_has_supporting_evidence():
    findings = [
        {
            "agent": "infrastructure_agent",
            "evidence": [
                {"metric": "interface_errors", "value": 250},
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    primary = result["primary_hypothesis"]

    assert primary["hypothesis"] == "interface_or_hardware_fault"
    assert len(primary["supporting_evidence"]) == 1


def test_alternative_causes_are_returned():
    findings = [
        {
            "agent": "performance_agent",
            "evidence": [
                {"metric": "latency_ms", "value": 250},
                {"metric": "packet_loss_percent", "value": 2},
            ],
            "missing_data": [],
        },
        {
            "agent": "infrastructure_agent",
            "evidence": [
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_data": [],
        },
    ]

    result = correlate_findings(findings)

    assert result["primary_hypothesis"] is not None
    assert len(result["alternative_causes"]) >= 1


def test_malformed_evidence_is_rejected():
    findings = [
        {
            "agent": "performance_agent",
            "evidence": [{"metric": "latency_ms"}],
            "missing_data": [],
        }
    ]

    with pytest.raises(ValueError):
        correlate_findings(findings)


def test_detects_healthy_status_with_high_packet_loss():
    findings = [
        {
            "agent": "infrastructure_agent",
            "reported_device_status": "Healthy",
            "evidence": [
                {"metric": "packet_loss_percent", "value": 20},
                {"metric": "interface_errors", "value": 250},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["type"] == "status_metric_mismatch"


def test_detects_warning_status_with_critical_measurements():
    findings = [
        {
            "agent": "infrastructure_agent",
            "reported_device_status": "Warning",
            "evidence": [
                {"metric": "packet_loss_percent", "value": 20},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["reported_status"] == "warning"


def test_detects_critical_status_without_critical_evidence():
    findings = [
        {
            "agent": "infrastructure_agent",
            "reported_device_status": "Critical",
            "evidence": [
                {"metric": "cpu_percent", "value": 30},
                {"metric": "packet_loss_percent", "value": 0},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["reported_status"] == "critical"


def test_healthy_status_without_elevated_metrics_has_no_conflict():
    findings = [
        {
            "agent": "infrastructure_agent",
            "reported_device_status": "Healthy",
            "evidence": [
                {"metric": "cpu_percent", "value": 30},
                {"metric": "packet_loss_percent", "value": 0},
                {"metric": "latency_ms", "value": 15},
            ],
            "missing_data": [],
        }
    ]

    result = correlate_findings(findings)

    assert result["conflicts"] == []


def test_normalizes_performance_agent_output():
    findings = [
        {
            "agent": "performance_agent",
            "findings": [
                {"metric": "latency_ms", "value": 250},
                {"metric": "packet_loss_percent", "value": 2},
            ],
            "missing_metrics": ["jitter_ms"],
        }
    ]

    result = correlate_findings(findings)

    assert len(result["all_evidence"]) == 2
    assert "jitter_ms" in result["missing_data"]


def test_normalizes_infrastructure_agent_output():
    findings = [
        {
            "agent": "infrastructure_agent",
            "reported_device_status": "Critical",
            "findings": [
                {"metric": "interface_errors", "value": 250},
                {"metric": "cpu_percent", "value": 99.9},
            ],
            "missing_metrics": ["queue_drops"],
        }
    ]

    result = correlate_findings(findings)

    assert len(result["all_evidence"]) == 2
    assert "queue_drops" in result["missing_data"]
    assert result["conflicts"] == []


def test_correlates_actual_agent_message():
    message = AgentMessage(
        message_id="msg-001",
        correlation_id="corr-001",
        incident_id="incident-001",
        sender="performance_agent",
        receiver="orchestrator",
        message_type=MessageType.FINDING,
        status=MessageStatus.PARTIAL,
        payload={
            "agent": "performance_agent",
            "findings": [
                {"metric": "latency_ms", "value": 250},
                {"metric": "packet_loss_percent", "value": 2},
            ],
            "missing_metrics": ["jitter_ms"],
        },
    )

    result = correlate_findings([message])

    assert len(result["all_evidence"]) == 2
    assert "jitter_ms" in result["missing_data"]
    assert result["agent_statuses"]["performance_agent"] == "PARTIAL"
