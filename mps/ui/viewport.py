from __future__ import annotations

from datetime import datetime
from typing import Optional

import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
from mps.config import get_recordings_dir
from mps.settings_loader import resolve_settings
from pathlib import Path
import os


class ViewportWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._frame: Optional[np.ndarray] = None
        self.setMinimumSize(320, 240)

    def set_frame(self, frame: np.ndarray) -> None:
        self._frame = frame
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # type: ignore[override]
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("black"))
        if self._frame is None:
            return
        h, w = self._frame.shape[:2]
        target = self.rect()
        scale = min(target.width() / w, target.height() / h)
        new_w, new_h = int(w * scale), int(h * scale)
        x = target.x() + (target.width() - new_w) // 2
        y = target.y() + (target.height() - new_h) // 2
        rgb = cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)
        qimg = QtGui.QImage(rgb.data, w, h, rgb.strides[0], QtGui.QImage.Format.Format_RGB888)
        qpix = QtGui.QPixmap.fromImage(qimg).scaled(new_w, new_h, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(x, y, qpix)

    def save_snapshot(self, name: str) -> None:
        if self._frame is None:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Prefer snapshots_dir from unified settings; fallback to recordings
        try:
            s = resolve_settings()
            outdir = Path(os.path.expanduser(s.storage.snapshots_dir))
        except Exception:
            outdir = get_recordings_dir()
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / f"{name}_{ts}.jpg"
        cv2.imwrite(str(path), self._frame)
