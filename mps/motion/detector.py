from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

import cv2
import numpy as np


@dataclass
class MotionSettings:
    sensitivity: int = 25  # threshold (1-255)
    min_area: int = 800  # minimum contour area to consider motion
    erode_iter: int = 1
    dilate_iter: int = 2


@dataclass
class MotionResult:
    motion_detected: bool
    boxes: List[Tuple[int, int, int, int]]  # x, y, w, h
    mask: Optional[np.ndarray]


class MotionDetector:
    def __init__(self, settings: MotionSettings | None = None) -> None:
        self.settings = settings or MotionSettings()
        self._background: Optional[np.ndarray] = None

    def reset(self) -> None:
        self._background = None

    def process(self, frame_bgr: np.ndarray) -> MotionResult:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self._background is None:
            self._background = gray.astype("float32")
            return MotionResult(False, [], None)

        cv2.accumulateWeighted(gray, self._background, 0.05)
        delta = cv2.absdiff(gray, cv2.convertScaleAbs(self._background))
        _, thresh = cv2.threshold(delta, self.settings.sensitivity, 255, cv2.THRESH_BINARY)

        if self.settings.erode_iter > 0:
            thresh = cv2.erode(thresh, None, iterations=self.settings.erode_iter)
        if self.settings.dilate_iter > 0:
            thresh = cv2.dilate(thresh, None, iterations=self.settings.dilate_iter)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes: List[Tuple[int, int, int, int]] = []
        for c in contours:
            if cv2.contourArea(c) < self.settings.min_area:
                continue
            x, y, w, h = cv2.boundingRect(c)
            boxes.append((x, y, w, h))

        return MotionResult(len(boxes) > 0, boxes, thresh)
