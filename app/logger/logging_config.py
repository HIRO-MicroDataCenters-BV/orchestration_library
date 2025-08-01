"""Logging configuration for the orchestration application.
This module sets up logging to both a file and the console, with rotation for the log file.
It ensures that logs from the FastAPI application and Uvicorn server are captured.
"""
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(
    log_file: str = "orchestration_app.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
):
    """    Set up logging configuration.
    Logs will be written to a file and also output to the console.
    Args:
        log_file (str): Path to the log file.
        level (int): Logging level (default: logging.INFO).
        max_bytes (int): Maximum size of the log file before rotation (default: 10 MB).
        backup_count (int): Number of backup files to keep (default: 5).
    """
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # Ensure uvicorn logs go to the same file
    for uvicorn_logger in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(uvicorn_logger)
        logger.handlers = []
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = True
    logger.info("Logging setup complete. Logs will be written to %s", log_file)
