
from uuid import uuid4

from protocol.schemas import (
    AgentMessage,
    MessageType,
    MessageStatus,
)
from topology.network_topology import (
    build_network_graph,
    get_connected_devices,
    find_common_neighbors,
)


def handle(message: AgentMessage) -> AgentMessage:

    def make_response(message_type, payload, status):
        return AgentMessage(
            message_id=str(uuid4()),
            correlation_id=message.correlation_id,
            incident_id=message.incident_id,
            sender="connectivity_agent",
            receiver="fault_correlation_agent",
            message_type=message_type,
            payload=payload,
            status=status,
        )

    if message.message_type != MessageType.TASK:
        return make_response(
            MessageType.ERROR,
            {"error": "Connectivity Agent expects a TASK message."},
            MessageStatus.FAILED,
        )

    try:
        topology = message.payload["topology"]
        affected_devices = message.payload["affected_devices"]

        if not isinstance(affected_devices, list) or not affected_devices:
            raise ValueError(
                "affected_devices must be a non-empty list."
            )

        if not all(
            isinstance(device, str) and device.strip()
            for device in affected_devices
        ):
            raise ValueError(
                "Every affected device must have a valid device ID."
            )

        if len(set(affected_devices)) != len(affected_devices):
            raise ValueError(
                "affected_devices contains duplicate device IDs."
            )

        graph = build_network_graph(topology)

        unknown_devices = [
            device
            for device in affected_devices
            if device not in graph
        ]

        known_devices = [
            device
            for device in affected_devices
            if device in graph
        ]

        connectivity_findings = {}

        for device in known_devices:
            connectivity_findings[device] = (
                get_connected_devices(graph, device)
            )

        # Find devices directly connected to every affected device.
        common_neighbors = []

        if len(known_devices) >= 2:
            neighbor_sets = [
                set(graph.neighbors(device))
                for device in known_devices
            ]

            common_neighbors = sorted(
                set.intersection(*neighbor_sets)
            )

        status = (
            MessageStatus.PARTIAL
            if unknown_devices
            else MessageStatus.COMPLETED
        )

        return make_response(
            MessageType.FINDING,
            {
                "agent": "connectivity_agent",
                "affected_devices": affected_devices,
                "connected_devices": connectivity_findings,
                "common_neighbors": common_neighbors,
                "unknown_devices": unknown_devices,
                "root_cause_determined": False,
            },
            status,
        )

    except (KeyError, TypeError, ValueError) as error:
        return make_response(
            MessageType.ERROR,
            {"error": str(error)},
            MessageStatus.FAILED,
        )
