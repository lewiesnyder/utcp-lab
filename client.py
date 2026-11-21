
import asyncio
from utcp.utcp_client import UtcpClient


async def main():
    client = await UtcpClient.create(
        config={
            "manual_call_templates": [
                {
                    "name": "demo",
                    "call_template_type": "http",
                    "url": "http://127.0.0.1:8000/utcp",
                    "http_method": "GET",
                }
            ]
        }
    )

    try:
        # Tools are discovered during client initialization.
        result = await client.call_tool(
            "demo.multiply",
            {"x": 6, "y": 7}
        )

        print(result)
    finally:
        await client.close()


asyncio.run(main())
