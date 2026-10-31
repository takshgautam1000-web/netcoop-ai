from external_agent.legacy_adapter import adapt_legacy_telemetry


def test_legacy_conversion():
    external_data = {
        "schema_version": "0.9",
        "device": "SW_CAMPUS_1",
        "observed_at": "2026-10-31T12:00:00Z",
        "device_status": "Warning",
        "measurements": {
            "cpu_pct": 55,
            "link_pct": 75,
            "packet_loss_pct": 1.0,
            "latency_seconds": 0.25,
            "jitter_seconds": 0.05,
            "queue_drop_count": 25,
        },
    }

    result = adapt_legacy_telemetry(external_data)

    assert result.device_id == "SW_CAMPUS_1"
    assert result.metrics.latency_ms == 250
    assert result.metrics.jitter_ms == 50
    assert result.metrics.cpu_percent == 55