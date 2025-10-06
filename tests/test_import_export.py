from __future__ import annotations

from mps.settings_loader import (
    export_user_settings,
    import_user_settings,
    reset_user_settings,
    resolve_settings,
)


def test_import_export_cycle(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    s1 = resolve_settings()
    data = export_user_settings()
    data.setdefault("app", {})["ui_theme"] = "light"
    import_user_settings(data)
    s2 = resolve_settings()
    assert s2.app.ui_theme == "light"
    reset_user_settings()
    s3 = resolve_settings()
    assert s3.app.ui_theme != "light"

from mps.settings_loader import export_user_settings, import_user_settings, reset_user_settings, resolve_settings

def test_import_export_cycle(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    s1 = resolve_settings()
    data = export_user_settings()
    data.setdefault("app", {})["ui_theme"] = "light"
    import_user_settings(data)
    s2 = resolve_settings()
    assert s2.app.ui_theme == "light"
    reset_user_settings()
    s3 = resolve_settings()
    assert s3.app.ui_theme != "light"
