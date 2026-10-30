from oracle_mcp.utils.logger import logger
from oracle_mcp.utils.exception import ConfigurationError, OracleAPIError
import os, sys
from dotenv import load_dotenv
load_dotenv(override=True)

def get_env_variable():

    required_config = {
        "username": os.getenv("ORA_USERNAME"),
        "password": os.getenv("ORA_PASSWORD"),
        "base_url": os.getenv("ORA_BASEURL")
    }

    logger.info("Validating the ENV variables")
    missing = [name for name, value in required_config.items() if not value or not value.strip()]

    if missing:
        logger.error(f"Missing required env variables: {','.join(missing)}")
        raise ConfigurationError(f"Configuration Error: Missing required env variables: {','.join(missing)}")
    
    required_config = {
        key: value.strip()
        for key, value in required_config.items()
    }

    if not required_config["base_url"].startswith("https://"):
        logger.error("ORA_BASEURL must use HTTPS")
        raise ConfigurationError("Configuration Error: ORA_BASEURL must use HTTPS")

    logger.info("Setting up the ENV variables")
    return required_config


def status_code_error_msg(status_code):

    if status_code == 401:
        message = "Oracle Fusion authentication failed. Check credentials."
    elif status_code == 403:
        message = "Access denied. Check Oracle Fusion user permissions."
    elif status_code == 404:
        message = "Oracle Fusion resource or endpoint was not found."
    else:
        message = "Oracle Fusion API request failed with HTTP"

    return message

def add(a):
    return a+5