from __future__ import annotations

import os
import sys
from loguru import logger

from mps.ui.app import run_app


def configure_logging() -> None:
    log_level = os.getenv("MPS_LOG_LEVEL", "INFO")
    logger.remove()
    logger.add(sys.stderr, level=log_level)


def main() -> int:
    configure_logging()
    logger.info("Starting Martins Point Security v2.1")
    try:
        run_app()
    except Exception:
        logger.exception("Fatal error in application")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
