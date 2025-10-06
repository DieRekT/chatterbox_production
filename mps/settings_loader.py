from __future__ import annotations

import json
import os
import pathlib
import threading
from typing import Any, Dict, Callable, Optional

from pydantic import ValidationError

from .settings_schema import Settings
from .migrations._runner import migrate_settings


_listeners: list[Callable[[Settings], None]] = []
_lock = threading.RLock()
_cached: Optional[Settings] = None


def _defaults_path() -> str:
    return str(pathlib.Path(__file__).resolve().parents[1] / "config" / "default_settings.json")


def _app_dir() -> str:
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(xdg, "mps")


def _user_settings_path() -> str:
    return os.path.join(_app_dir(), "settings.json")


def _load_json(p: str) -> Dict[str, Any]:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_dirs(settings_like: Dict[str, Any]) -> None:
    rec = os.path.expanduser(settings_like["storage"]["recordings_dir"])
    snap = os.path.expanduser(settings_like["storage"]["snapshots_dir"])  # may be same as recordings_dir
    os.makedirs(rec, exist_ok=True)
    os.makedirs(snap, exist_ok=True)


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)  # type: ignore[index]
        else:
            out[k] = v
    return out


def resolve_settings() -> Settings:
    global _cached
    with _lock:
        base = _load_json(_defaults_path())
        user_settings_file = _user_settings_path()
        if os.path.exists(user_settings_file):
            user = _load_json(user_settings_file)
            user = migrate_settings(user)
            merged = _merge(base, user)
        else:
            merged = base

        env_overrides: Dict[str, Any] = {}
        # Legacy support: MPS_RECORDINGS_DIR
        if (p := os.environ.get("MPS_RECORDINGS_DIR")):
            env_overrides = _merge(env_overrides, {"storage": {"recordings_dir": p}})
        # Legacy support: MPS_CONFIG with camera_settings.json
        if (p := os.environ.get("MPS_CONFIG")):
            try:
                cam_cfg = _load_json(p)
                env_overrides = _merge(env_overrides, {"video": {"cams": cam_cfg}})
            except Exception:
                pass

        merged = _merge(merged, env_overrides)
        _ensure_dirs(merged)

        try:
            _cached = Settings.model_validate(merged)
            return _cached
        except ValidationError as e:
            diag_dir = _app_dir()
            os.makedirs(diag_dir, exist_ok=True)
            diag = os.path.join(diag_dir, "settings.errors.json")
            with open(diag, "w", encoding="utf-8") as f:
                f.write(e.json())
            _cached = Settings.model_validate(_load_json(_defaults_path()))
            return _cached


def save_user_settings(patch: Dict[str, Any]) -> Settings:
    with _lock:
        settings_file = _user_settings_path()
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        current: Dict[str, Any] = {}
        if os.path.exists(settings_file):
            current = _load_json(settings_file)
        updated = _merge(current, patch)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
        s = resolve_settings()
        for cb in list(_listeners):
            try:
                cb(s)
            except Exception:
                pass
        return s


def on_change(callback: Callable[[Settings], None]) -> None:
    _listeners.append(callback)


# import/export/reset helpers

def export_user_settings() -> Dict[str, Any]:
    settings_file = _user_settings_path()
    if os.path.exists(settings_file):
        return _load_json(settings_file)
    return {}


def import_user_settings(data: Dict[str, Any]) -> Settings:
    settings_file = _user_settings_path()
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return resolve_settings()


def reset_user_settings() -> Settings:
    settings_file = _user_settings_path()
    if os.path.exists(settings_file):
        backup = settings_file.replace(".json", ".bak.json")
        try:
            import shutil
            shutil.copy(settings_file, backup)
        except Exception:
            pass
        os.remove(settings_file)
    return resolve_settings()
