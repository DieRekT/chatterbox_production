from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from loguru import logger
from PyQt6 import QtCore, QtGui, QtWidgets

from mps.ui.camera_tile import CameraTile
from mps.settings_loader import resolve_settings
from mps.settings_schema import Settings
try:
    from mps.settings_ui import SettingsDialog  # PyQt settings dialog
except Exception:
    SettingsDialog = None  # type: ignore


@dataclass
class CameraConfig:
    device: str
    resolution: str
    fps: int


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, cameras: Dict[str, CameraConfig]):
        super().__init__()
        try:
            s = resolve_settings()
            self.setWindowTitle(f"{s.app.name} {s.app.version}")
        except Exception:
            self.setWindowTitle("Martins Point Security")
        self.resize(1280, 800)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QGridLayout(central)

        # Two camera tiles
        keys = list(sorted(cameras.keys()))
        cam0 = cameras.get(keys[0]) if keys else None
        cam1 = cameras.get(keys[1]) if len(keys) > 1 else None

        self.tile0 = CameraTile("cam0", cam0)
        self.tile1 = CameraTile("cam1", cam1)

        layout.addWidget(self.tile0, 0, 0)
        layout.addWidget(self.tile1, 0, 1)

        # Menubar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        if SettingsDialog is not None:
            act_open = settings_menu.addAction("Open Settings…")
            act_open.triggered.connect(self._open_settings)

        # Status bar entries
        self.storage_label = QtWidgets.QLabel("Storage: ...")
        self.statusBar().addPermanentWidget(self.storage_label)

        # Timer to update storage info
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._update_storage)
        self.timer.start(2000)

    def _update_storage(self) -> None:
        try:
            statvfs = os.statvfs("/")
            total = statvfs.f_frsize * statvfs.f_blocks
            available = statvfs.f_frsize * statvfs.f_bavail
            used = total - available
            pct = used / total * 100 if total > 0 else 0
            self.storage_label.setText(f"Storage used: {pct:0.1f}%")
        except Exception as e:
            logger.debug(f"storage update failed: {e}")

    def _open_settings(self) -> None:
        if SettingsDialog is None:
            return
        dlg = SettingsDialog(self)
        dlg.exec()


def _cams_from_settings(s: Settings) -> Dict[str, CameraConfig]:
    out: Dict[str, CameraConfig] = {}
    for key, cam in s.video.cams.items():
        if not cam.enabled:
            continue
        out[key] = CameraConfig(
            device=cam.device,
            resolution=cam.resolution,
            fps=int(cam.fps),
        )
    return out


def run_app() -> None:
    app = QtWidgets.QApplication([])

    s = resolve_settings()
    config = _cams_from_settings(s)
    win = MainWindow(config)
    win.show()

    app.exec()
