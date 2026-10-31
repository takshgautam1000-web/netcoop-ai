
def score_hypotheses(evidence: list[dict]) -> dict:
    scores = {
        "congestion": 0,
        "cpu_overload": 0,
        "interface_or_hardware_fault": 0,
        "dns_failure": 0,
        "dhcp_failure": 0,
    }

    for item in evidence:
        metric = item.get("metric")
        value = item.get("value")

        if value is None:
            continue

        # Network performance
        if metric == "latency_ms" and value >= 100:
            scores["congestion"] += 1

        elif metric == "link_utilization_percent" and value >= 85:
            scores["congestion"] += 2

        elif metric == "packet_loss_percent" and value >= 1:
            scores["congestion"] += 1

        elif metric == "queue_drops" and value >= 50:
            scores["congestion"] += 1
        elif metric == "jitter_ms" and value >= 30:
            scores["congestion"] += 1

        # Infrastructure
        elif metric == "cpu_percent" and value >= 80:
            scores["cpu_overload"] += 2

        elif metric == "interface_errors":
            if value >= 100:
                scores["interface_or_hardware_fault"] += 6
            elif value >= 10:
                scores["interface_or_hardware_fault"] += 2

        # DNS health
        elif metric == "dns_resolution_success_percent" and value < 95:
            scores["dns_failure"] += 2

        elif metric == "dns_response_time_ms" and value > 200:
            scores["dns_failure"] += 1

        elif metric == "dns_timeout_count" and value > 5:
            scores["dns_failure"] += 2

        # DHCP health
        elif metric == "dhcp_success_percent" and value < 95:
            scores["dhcp_failure"] += 2

        elif metric == "dhcp_response_time_ms" and value > 500:
            scores["dhcp_failure"] += 1

        elif metric == "dhcp_failure_count" and value > 5:
            scores["dhcp_failure"] += 2

    return scores
