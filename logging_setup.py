import logging
from logging.handlers import RotatingFileHandler
import threading
import inspect
from typing import Optional, Dict, Any


def get_log_level(level_str: str) -> int:
    """Convert log level string to logging level constant."""
    level_str = level_str.upper()
    if level_str == "DEBUG":
        return logging.DEBUG
    elif level_str == "INFO":
        return logging.INFO
    elif level_str == "WARNING":
        return logging.WARNING
    elif level_str == "ERROR":
        return logging.ERROR
    elif level_str == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO  # Default level


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Configure logging with professional formatting and handlers."""
    logger = logging.getLogger(__name__)

    # Get log levels from config with defaults
    log_level = get_log_level(config.get("logging", {}).get("level", "INFO"))
    file_level = get_log_level(config.get("logging", {}).get("file_level", "DEBUG"))
    console_level = get_log_level(
        config.get("logging", {}).get("console_level", "INFO")
    )

    logger.setLevel(log_level)

    # Create formatter with detailed information
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [Thread: %(threadName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler for persistent logs
    file_handler = RotatingFileHandler(
        "anki_automator.log",
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    # Console handler for real-time feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Suppress logs from external libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("deepl").setLevel(logging.WARNING)

    return logger


def log_debug(logger: logging.Logger, message: str):
    """Log a debug message with caller information."""
    caller_frame = inspect.currentframe().f_back
    caller_function = caller_frame.f_code.co_name
    caller_line = caller_frame.f_lineno
    logger.debug(f"[{caller_function}:{caller_line}] {message}")


def log_info(logger: logging.Logger, message: str):
    """Log an info message with caller information."""
    caller_frame = inspect.currentframe().f_back
    caller_function = caller_frame.f_code.co_name
    caller_line = caller_frame.f_lineno
    logger.info(f"[{caller_function}:{caller_line}] {message}")


def log_warning(logger: logging.Logger, message: str):
    """Log a warning message with caller information."""
    caller_frame = inspect.currentframe().f_back
    caller_function = caller_frame.f_code.co_name
    caller_line = caller_frame.f_lineno
    logger.warning(f"[{caller_function}:{caller_line}] {message}")


def log_error(logger: logging.Logger, message: str, exc: Optional[Exception] = None):
    """Log an error message with caller information and optional exception."""
    caller_frame = inspect.currentframe().f_back
    caller_function = caller_frame.f_code.co_name
    caller_line = caller_frame.f_lineno

    if exc:
        logger.error(f"[{caller_function}:{caller_line}] {message}", exc_info=exc)
    else:
        logger.error(f"[{caller_function}:{caller_line}] {message}")
