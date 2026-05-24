"""Structlog configuration."""

import logging
import sys

import structlog

from src.otel_setup import add_otel_context


def setup_logging(dev: bool = False, log_level: str = "INFO") -> None:
    """Configure structlog and route stdlib logging through it."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_otel_context,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer() if dev else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionPrettyPrinter(),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # Quieter third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
