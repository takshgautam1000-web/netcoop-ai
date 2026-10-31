
from topology.network_topology import (
    build_network_graph,
    get_connected_devices,
    find_common_neighbors,
)


def test_build_network_graph():
    topology = {
        "nodes": [
            {"device_id": "R1", "device_type": "router"},
            {"device_id": "S1", "device_type": "switch"},
            {"device_id": "S2", "device_type": "switch"},
        ],
        "edges": [
            {"source": "R1", "target": "S1"},
            {"source": "R1", "target": "S2"},
        ],
    }

    graph = build_network_graph(topology)

    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2


def test_connected_devices():
    topology = {
        "nodes": [
            {"device_id": "R1"},
            {"device_id": "S1"},
            {"device_id": "S2"},
        ],
        "edges": [
            {"source": "R1", "target": "S1"},
            {"source": "R1", "target": "S2"},
        ],
    }

    graph = build_network_graph(topology)

    result = get_connected_devices(graph, "S1")

    assert result == ["R1", "S2"]


def test_common_neighbors():
    topology = {
        "nodes": [
            {"device_id": "R1"},
            {"device_id": "S1"},
            {"device_id": "S2"},
        ],
        "edges": [
            {"source": "R1", "target": "S1"},
            {"source": "R1", "target": "S2"},
        ],
    }

    graph = build_network_graph(topology)

    result = find_common_neighbors(graph, "S1", "S2")

    assert result == ["R1"]
