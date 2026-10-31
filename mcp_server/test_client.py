import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from datetime import datetime, timezone


async def main():

    async with streamable_http_client(
        "http://127.0.0.1:8001/mcp"
    ) as (read_stream, write_stream):

        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            print("\nConnected to NETCOOP MCP Server!")

            tools = await session.list_tools()

            print("\nAvailable MCP Tools:")

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            result = await session.call_tool(
                "get_server_status",
                arguments={}
            )

            print("\nServer Status:")
            print(result.content)

        
            telemetry = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "device_id": "SW_CAMPUS_1",
                "status": "Warning",
                "metrics": {
                    "cpu_utilization_pct": 55.0,
                    "link_utilization_pct": 75.0,
                    "packet_loss_pct": 1.0,
                    "latency_ms": 250.0,
                    "jitter_ms": 50.0,
                    "queue_drops": 25
                }
            }

            diagnosis = await session.call_tool(
                "diagnose_incident",
                arguments={"telemetry": telemetry}
            )

            print("\nRemote Diagnostic Report:")
            print(diagnosis.content)

            if diagnosis.is_error:
                print("\nDiagnosis failed!")

if __name__ == "__main__":
    asyncio.run(main())