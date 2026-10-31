from diagnosis.hypothesis_engine import score_hypotheses
def test_dns_failure_scoring():
    evidence = [
        {"metric": "dns_resolution_success_percent", "value": 65},
        {"metric": "dns_response_time_ms", "value": 450},
        {"metric": "dns_timeout_count", "value": 35},
    ]

    scores = score_hypotheses(evidence)

    assert scores["dns_failure"] == 5


def test_dhcp_failure_scoring():
    evidence = [
        {"metric": "dhcp_success_percent", "value": 70},
        {"metric": "dhcp_response_time_ms", "value": 800},
        {"metric": "dhcp_failure_count", "value": 20},
    ]

    scores = score_hypotheses(evidence)

    assert scores["dhcp_failure"] == 5


def test_healthy_dns_dhcp():
    evidence = [
        {"metric": "dns_resolution_success_percent", "value": 99},
        {"metric": "dns_response_time_ms", "value": 50},
        {"metric": "dns_timeout_count", "value": 0},
        {"metric": "dhcp_success_percent", "value": 99},
        {"metric": "dhcp_response_time_ms", "value": 100},
        {"metric": "dhcp_failure_count", "value": 0},
    ]

    scores = score_hypotheses(evidence)

    assert scores["dns_failure"] == 0
    assert scores["dhcp_failure"] == 0
