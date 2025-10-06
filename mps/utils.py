from __future__ import annotations

import logging
import os
import shutil

from .settings_schema import Settings


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def ensure_storage(s: Settings) -> None:
    for p in (s.storage.recordings_dir, s.storage.snapshots_dir):
        os.makedirs(os.path.expanduser(p), exist_ok=True)


def health_check(s: Settings) -> list[str]:
    issues: list[str] = []
    rec = os.path.expanduser(s.storage.recordings_dir)
    total, used, free = shutil.disk_usage(rec)
    if free < s.storage.free_space_min_gb * (1024 ** 3):
        issues.append("Low free space for recordings")
    for name, cam in s.video.cams.items():
        if cam.enabled and cam.device.startswith("/dev/") and not os.path.exists(cam.device):
            issues.append(f"{name}: device {cam.device} not found")
    return issues

from __future__ import annotations

import logging
import os
import shutil
from loguru import logger

from .settings_schema import Settings


def setup_logging(level: str = "INFO") -> None:
    # Bridge to loguru for consistency with existing codebase
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=level.upper())


essential_dirs = ("storage.recordings_dir", "storage.snapshots_dir")


def ensure_storage(settings: Settings) -> None:
    for key in essential_dirs:
        section, name = key.split(".")
        path = getattr(getattr(settings, section), name)  # type: ignore[attr-defined]
        os.makedirs(os.path.expanduser(path), exist_ok=True)


def health_check(settings: Settings) -> list[str]:
    issues: list[str] = []
    rec = os.path.expanduser(settings.storage.recordings_dir)
    try:
        total, used, free = shutil.disk_usage(rec)
        if free < settings.storage.free_space_min_gb * (1024 ** 3):
            issues.append("Low free space for recordings")
    except FileNotFoundError:
        issues.append("Recordings directory does not exist")

    for cam_name, cam in settings.video.cams.items():
        if cam.enabled and cam.device.startswith("/dev/") and not os.path.exists(cam.device):
            issues.append(f"{cam_name}: device {cam.device} not found")
    return issues
