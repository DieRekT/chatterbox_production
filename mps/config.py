from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    # Unified settings system
    from mps.settings_loader import resolve_settings  # type: ignore
except Exception:  # pragma: no cover - settings layer not yet available
    resolve_settings = None  # type: ignore


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
    """Return the recordings directory from unified settings, with legacy env fallback."""
    env = os.getenv("MPS_RECORDINGS_DIR")
    if env:
        return Path(env)
    if resolve_settings is not None:
        try:
            s = resolve_settings()
            return Path(os.path.expanduser(s.storage.recordings_dir))
        except Exception:
            pass
    return Path.cwd() / "recordings"
