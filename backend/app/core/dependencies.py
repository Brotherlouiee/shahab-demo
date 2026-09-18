"""Framework dependency providers; business use cases are wired in later tasks."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends

from .config import Settings, get_settings
from .logging import configure_logging


def get_app_logger(settings: Annotated[Settings, Depends(get_settings)]) -> logging.Logger:
    """Expose the configured, redacting application logger to HTTP adapters."""
    return configure_logging(settings.log_level)
