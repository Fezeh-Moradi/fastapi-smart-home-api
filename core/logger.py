import logging
from pathlib import Path


Path("logs").mkdir(exist_ok=True)


logger = logging.getLogger("smart_home_api")
logger.setLevel(logging.INFO)

if not logger.handlers:

    file_handler = logging.FileHandler(
        "logs/app.log",
        encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


logger.propagate = False