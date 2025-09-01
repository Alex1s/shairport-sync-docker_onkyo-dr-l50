import logging
import os
import sys

log_level_str = os.getenv("API_LOG_LEVEL", "DEBUG").upper()
log_level = getattr(logging, log_level_str, logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
