"""Simple shared logger factory so every module logs consistently."""
import logging
import sys

from src.config import get_settings


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name)
    if not logger.handlers:  # avoid duplicate handlers on repeated calls / Airflow reloads
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(settings.log_level)
    return logger
