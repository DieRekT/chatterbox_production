from __future__ import annotations

import json
import pathlib

from mps.settings_schema import Settings


def test_defaults_validate() -> None:
    cfg = json.loads((pathlib.Path("config/default_settings.json")).read_text())
    s = Settings.model_validate(cfg)
    assert s.app.name
    assert "cam0" in s.video.cams

from mps.settings_schema import Settings

def test_defaults_validate():
    import json, pathlib
    cfg = json.loads((pathlib.Path("config/default_settings.json")).read_text())
    s = Settings.model_validate(cfg)
    assert s.app.name
