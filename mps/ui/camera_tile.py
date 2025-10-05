from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
from loguru import logger
from PyQt6 import QtCore, QtGui, QtWidgets

from mps.ui.viewport import ViewportWidget
from mps.motion.detector import MotionDetector, MotionSettings
from mps.recording.recorder import MotionTriggeredRecorder, RecordingSettings
from mps.analytics.ai import AiAnalyzer, AiSettings
from mps.config import get_recordings_dir


@dataclass
class CameraConfig:
    device: str
    resolution: str
    fps: int


class CameraWorker(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(np.ndarray)
    motion = QtCore.pyqtSignal(bool)

    def __init__(self, name: str, cfg: Optional[CameraConfig]):
        super().__init__()
        self.name = name
        self.cfg = cfg
        self._running = True

    def run(self) -> None:
        if not self.cfg:
            logger.warning(f"{self.name}: no camera configured")
            return
        source = self.cfg.device
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logger.error(f"{self.name}: failed to open {source}")
            return
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if fps <= 1:
            fps = 30.0
        motion = MotionDetector(MotionSettings())
        recorder = MotionTriggeredRecorder(get_recordings_dir(), self.name, RecordingSettings(), fps_hint=fps)
        ai = AiAnalyzer(AiSettings())
        while self._running:
            ok, frame = cap.read()
            if not ok:
                self.msleep(10)
                continue
            # motion detection
            mres = motion.process(frame)
            self.motion.emit(mres.motion_detected)
            recorder.update(frame, mres.motion_detected)
            # optional AI (non-blocking stride)
            _ = ai.analyze(frame)

            self.frame_ready.emit(frame)
        cap.release()
        recorder.stop()

    def stop(self) -> None:
        self._running = False


class CameraTile(QtWidgets.QWidget):
    def __init__(self, name: str, cfg: Optional[CameraConfig]):
        super().__init__()
        self.name = name
        self.cfg = cfg

        layout = QtWidgets.QVBoxLayout(self)

        toolbar = QtWidgets.QToolBar()
        self.btn_play = toolbar.addAction("⏯️")
        self.btn_snapshot = toolbar.addAction("📸")
        layout.addWidget(toolbar)

        self.viewport = ViewportWidget()
        layout.addWidget(self.viewport, 1)

        self.worker = CameraWorker(name, cfg)
        self.worker.frame_ready.connect(self._on_frame)
        self.worker.motion.connect(self._on_motion)
        self.btn_play.triggered.connect(self._toggle)
        self.btn_snapshot.triggered.connect(self._snapshot)

        self.worker.start()

    def _on_frame(self, frame: np.ndarray) -> None:
        self.viewport.set_frame(frame)

    def _on_motion(self, is_motion: bool) -> None:
        # Could flash border or update an indicator; keep minimal for now
        if is_motion:
            self.setStyleSheet("border: 2px solid #ff9800;")
        else:
            self.setStyleSheet("")

    def _toggle(self) -> None:
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(200)
        else:
            self.worker = CameraWorker(self.name, self.cfg)
            self.worker.frame_ready.connect(self._on_frame)
            self.worker.motion.connect(self._on_motion)
            self.worker.start()

    def _snapshot(self) -> None:
        self.viewport.save_snapshot(self.name)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # type: ignore[override]
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(500)
        super().closeEvent(event)
