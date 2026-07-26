from pathlib import Path

from loguru import logger

from core.config import settings

LOG_FILE = settings.LOG_DIR / "app.log"
ERROR_FILE = settings.LOG_DIR / "error.log"

# Remove default logger
logger.remove()

# Console
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
)

# Application log
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="30 days",
    level="INFO",
)

# Error log
logger.add(
    ERROR_FILE,
    rotation="10 MB",
    retention="30 days",
    level="ERROR",
)

app_logger = logger