from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Deque, Optional, Tuple

import cv2
import numpy as np
from loguru import logger


@dataclass
class RecordingSettings:
    enabled: bool = True
    prebuffer_seconds: float = 2.0
    postbuffer_seconds: float = 3.0


class SimpleRecorder:
    def __init__(self, out_dir: Path, camera_name: str):
        self.out_dir = out_dir
        self.camera_name = camera_name
        self.writer: Optional[cv2.VideoWriter] = None
        self.file_path: Optional[Path] = None
        self._fourccs = [cv2.VideoWriter_fourcc(*"mp4v"), cv2.VideoWriter_fourcc(*"XVID")]
        self._exts = [".mp4", ".avi"]

    def start(self, frame_size: Tuple[int, int], fps: float) -> bool:
        self.stop()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for idx, fourcc in enumerate(self._fourccs):
            ext = self._exts[idx]
            candidate = self.out_dir / f"{self.camera_name}_{ts}{ext}"
            writer = cv2.VideoWriter(str(candidate), fourcc, fps if fps > 0 else 25.0, frame_size)
            if writer.isOpened():
                self.writer = writer
                self.file_path = candidate
                logger.info(f"Recording started: {candidate}")
                return True
        logger.error("Failed to open any video writer")
        return False

    def write(self, frame_bgr: np.ndarray) -> None:
        if self.writer is not None:
            self.writer.write(frame_bgr)

    def is_recording(self) -> bool:
        return self.writer is not None

    def stop(self) -> Optional[Path]:
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            logger.info(f"Recording stopped: {self.file_path}")
        path = self.file_path
        self.file_path = None
        return path


class MotionTriggeredRecorder:
    def __init__(self, out_dir: Path, camera_name: str, settings: RecordingSettings, fps_hint: float = 30.0):
        self.settings = settings
        self._rec = SimpleRecorder(out_dir, camera_name)
        self._fps: float = fps_hint
        self._frame_size: Optional[Tuple[int, int]] = None
        self._buffer: Deque[np.ndarray] = deque(maxlen=self._prebuffer_frames())
        self._last_motion_time: Optional[float] = None

    def _prebuffer_frames(self) -> int:
        return max(1, int(self.settings.prebuffer_seconds * max(1.0, self._fps)))

    def set_fps(self, fps: float) -> None:
        if fps <= 0:
            return
        self._fps = fps
        # resize buffer to new fps
        old = self._buffer
        self._buffer = deque(list(old)[-self._prebuffer_frames():], maxlen=self._prebuffer_frames())

    def update(self, frame_bgr: np.ndarray, motion: bool) -> None:
        h, w = frame_bgr.shape[:2]
        self._frame_size = (w, h)
        # Always keep prebuffer
        self._buffer.append(frame_bgr.copy())

        now = time.time()
        if motion:
            self._last_motion_time = now
            if self.settings.enabled and not self._rec.is_recording():
                if self._rec.start(self._frame_size, self._fps):
                    # dump prebuffer frames first
                    for fb in list(self._buffer):
                        self._rec.write(fb)
        # While recording, write current frame
        if self._rec.is_recording():
            self._rec.write(frame_bgr)
            # Stop if postbuffer elapsed and no motion
            if self._last_motion_time and (now - self._last_motion_time) > self.settings.postbuffer_seconds:
                self._rec.stop()

    def stop(self) -> Optional[Path]:
        return self._rec.stop()
