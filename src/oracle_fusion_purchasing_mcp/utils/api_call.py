from oracle_fusion_purchasing_mcp.utils.exception import ConfigurationError, OracleAPIError, OracleJSONDecodeError
from fastmcp import FastMCP, Context
from oracle_fusion_purchasing_mcp.utils.logger import logger
import httpx
from oracle_fusion_purchasing_mcp.utils.helper import get_env_variable, status_code_error_msg
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(server):

    config = get_env_variable()

    headers = {
        "Accept": "application/json"
    }

    auth = httpx.BasicAuth(
        username=config["username"], password=config["password"]
    )

    logger.info("MCP Server Started...")
    async with httpx.AsyncClient(
        auth=auth,
        headers=headers,
        timeout=30.0
    ) as client:
        yield {
                "http_client": client,
                "base_url": config["base_url"]
        }


async def oracle_get(ctx: Context, endpoint: str, tool_name: str, params: dict | None = None) -> dict:
    try:
        
        client = ctx.lifespan_context["http_client"]
        baseurl =ctx.lifespan_context["base_url"]

        api_url = baseurl.rstrip("/")+ endpoint

        logger.info(f"{tool_name}: Oracle API request STARTED")
        response = await client.get(api_url, params=params)

        response.raise_for_status()

        try:
            return response.json()
        except Exception as exc:
            logger.error(f"Oracle JSON Decode Error: {exc}")
            raise OracleJSONDecodeError("Oracle JSON Decode Error: Unable to parse the API JSON response") from exc
        finally:
            logger.info(f"{tool_name}: Oracle API request FINISHED")
    
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = status_code_error_msg(status_code=status_code)

        logger.warning(f"HTTP Status Code {status_code} Oracle API Error: {message}")
        raise OracleAPIError(f"HTTP Status Code {status_code} Oracle API Error: {message}") from exc

    except httpx.ConnectError as exc:
        logger.error(f"Oracle API Error: {exc}")
        raise OracleAPIError(f"Oracle API Error: Could not connect to Oracle Fusion. Check the instance URL") from exc

    except Exception as exc:
        logger.error(f"Oracle API Error: {exc}")
        raise OracleAPIError(f"Oracle API Error: Unexpected Oracle API error {exc}") from exc