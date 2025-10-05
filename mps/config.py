from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def get_config_path() -> Path:
    env = os.getenv("MPS_CONFIG")
    if env:
        p = Path(env)
        if p.exists():
            return p
    candidates = [
        Path.cwd() / "config" / "camera_settings.json",
        Path(__file__).resolve().parent.parent / "config" / "camera_settings.json",
        Path("/opt/martinspoint/config/camera_settings.json"),
        Path("/workspace/config/camera_settings.json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    # default path even if missing
    return candidates[0]


def get_recordings_dir() -> Path:
    env = os.getenv("MPS_RECORDINGS_DIR")
    if env:
        return Path(env)
    return Path.cwd() / "recordings"
