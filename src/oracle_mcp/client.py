from fastmcp import Client
import asyncio
from pathlib import Path
import json
import logging
logging.basicConfig(
    level=logging.INFO,
    filename="oracle_client.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("oracle_client")

async def main():
    
    try:
        server_path = Path(__file__).parent / "server.py"
        print(server_path)
        async with Client(server_path) as client:

            tools = await client.list_tools()

            for tool in tools:
                print(tool.model_dump())

            # Test the purchase order tool
            result = await client.call_tool(
                "get_one_purchase_order",
                {"po_number": "380008505"},
            )
            print(json.dumps(result.structured_content, indent=2))
            
    except Exception as e:
        logger.exception("Connection Failed")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())