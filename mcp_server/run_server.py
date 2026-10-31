import asyncio

from mcp_server.server import server


if __name__ == "__main__":
    asyncio.run(
        server.run_streamable_http_async(
            host="127.0.0.1",
            port=8001,
            streamable_http_path="/mcp",
        )
    )