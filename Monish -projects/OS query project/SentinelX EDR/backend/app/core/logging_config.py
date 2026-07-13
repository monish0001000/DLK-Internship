"""
SentinelX EDR - Structured Logging Configuration
=================================================
Configures structured logging with consistent formatting across all modules.
Supports both console (development) and JSON (production) output formats.
"""

import logging
import sys
from datetime import datetime, timezone

from app.config import get_settings


class SentinelXFormatter(logging.Formatter):
    """
    Custom formatter that produces structured, readable log output.
    
    Format:
        2024-01-15 10:14:32 | INFO     | app.services.detection | Sigma rule matched: T1059.001
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        color = self.COLORS.get(level, "")
        reset = self.RESET

        # Truncate module name for readability
        module = record.name
        if len(module) > 35:
            module = "..." + module[-32:]

        return (
            f"{timestamp} | {color}{level:<8}{reset} | "
            f"{module:<35} | {record.getMessage()}"
        )


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Called once during app startup in main.py lifespan handler.
    Sets log level from config (LOG_LEVEL env var, default: INFO).
    """
    settings = get_settings()
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers to prevent duplicate output
    root_logger.handlers.clear()

    # Console handler with our custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(SentinelXFormatter())
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.getLogger("app").info(
        f"Logging initialized | level={settings.LOG_LEVEL} | debug={settings.DEBUG}"
    )
