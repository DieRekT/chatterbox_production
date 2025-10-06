from __future__ import annotations

import os
import sys
from loguru import logger

from mps.ui.app import run_app
from mps.settings_loader import resolve_settings
from mps.utils import setup_logging, ensure_storage, health_check


def configure_logging() -> None:
    try:
        level = resolve_settings().app.log_level
    except Exception:
        level = os.getenv("MPS_LOG_LEVEL", "INFO")
    setup_logging(level)


def main() -> int:
    configure_logging()
    s = resolve_settings()
    ensure_storage(s)
    issues = health_check(s)
    if issues:
        logger.warning(f"Startup health issues: {issues}")
    try:
        app_name = resolve_settings().app.name
        app_ver = resolve_settings().app.version
    except Exception:
        app_name = "Martins Point Security"
        app_ver = ""
    logger.info(f"Starting {app_name} {app_ver}")
    try:
        run_app()
    except Exception:
        logger.exception("Fatal error in application")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
