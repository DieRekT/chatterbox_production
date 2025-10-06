from __future__ import annotations

from mps.settings_loader import resolve_settings


def test_resolve_settings() -> None:
    s = resolve_settings()
    assert s.storage.recordings_dir
    assert "cam0" in s.video.cams

from mps.settings_loader import resolve_settings

def test_resolve_settings():
    s = resolve_settings()
    assert s.storage.recordings_dir
    assert "cam0" in s.video.cams
