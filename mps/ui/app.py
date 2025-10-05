from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from loguru import logger
from PyQt6 import QtCore, QtGui, QtWidgets

from mps.ui.camera_tile import CameraTile
from mps.config import get_config_path


@dataclass
class CameraConfig:
    device: str
    resolution: str
    fps: int


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, cameras: Dict[str, CameraConfig]):
        super().__init__()
        self.setWindowTitle("Martins Point Security v2.1")
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


def load_config(path: Path) -> Dict[str, CameraConfig]:
    if not path.exists():
        logger.warning(f"Config not found at {path}, using defaults")
        return {
            "cam0": CameraConfig("/dev/video0", "1280x720", 30),
            "cam1": CameraConfig("/dev/video2", "1280x720", 30),
        }
    data = json.loads(path.read_text())
    out: Dict[str, CameraConfig] = {}
    for key, entry in data.items():
        out[key] = CameraConfig(
            device=entry.get("device", "/dev/video0"),
            resolution=entry.get("resolution", "1280x720"),
            fps=int(entry.get("fps", 30)),
        )
    return out


def run_app() -> None:
    app = QtWidgets.QApplication([])

    config = load_config(get_config_path())
    win = MainWindow(config)
    win.show()

    app.exec()
