
import networkx as nx


def build_network_graph(topology: dict) -> nx.Graph:
    """
    Build a network graph from nodes and connections.
    """

    graph = nx.Graph()

    for node in topology.get("nodes", []):
        graph.add_node(
            node["device_id"],
            device_type=node.get("device_type", "unknown"),
        )

    for edge in topology.get("edges", []):
        graph.add_edge(
            edge["source"],
            edge["target"],
            link_id=edge.get("link_id"),
        )

    return graph


def get_connected_devices(
    graph: nx.Graph,
    device_id: str,
) -> list[str]:
    """
    Return all devices in the same connected component.
    """

    if device_id not in graph:
        return []

    component = nx.node_connected_component(graph, device_id)

    return sorted(component - {device_id})


def find_common_neighbors(
    graph: nx.Graph,
    device_a: str,
    device_b: str,
) -> list[str]:
    """
    Find devices directly connected to both devices.
    """

    if device_a not in graph or device_b not in graph:
        return []

    common = (
        set(graph.neighbors(device_a))
        & set(graph.neighbors(device_b))
    )

    return sorted(common)
