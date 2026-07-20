import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

Path("logs").mkdir(exist_ok=True)

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("smart_home_api")
logger.propagate = False