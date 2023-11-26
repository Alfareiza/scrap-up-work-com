import os
from pathlib import Path

from loguru import logger

BASE_DIR = Path(__file__).resolve().parent


def get_logger():
    log_dir = BASE_DIR / "logs" / "upwork.log"
    logger.add(BASE_DIR / "logs" / "upwork.log", rotation="10 MB",
               format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
    os.chmod(log_dir, 0o777)
    return logger


log = get_logger()
