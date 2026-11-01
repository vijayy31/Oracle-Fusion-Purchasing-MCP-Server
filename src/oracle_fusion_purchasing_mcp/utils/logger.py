import logging
from pathlib import Path

LOG_DIR = Path.home()/'.oracle_mcp'
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR/"oracle_mcp.log"

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("oracle.mcp")