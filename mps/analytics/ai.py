from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

try:
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    YOLO = None  # type: ignore


@dataclass
class AiSettings:
    enabled: bool = False
    confidence: float = 0.25
    stride: int = 3  # analyze every N frames


class AiAnalyzer:
    def __init__(self, settings: AiSettings | None = None):
        self.settings = settings or AiSettings()
        self._model = None
        self._frame_count = 0
        if self.settings.enabled and YOLO is not None:
            try:
                self._model = YOLO("yolov8n.pt")
            except Exception:
                self._model = None
                self.settings.enabled = False

    def analyze(self, frame_bgr: np.ndarray) -> List[Tuple[int, int, int, int, str, float]]:
        # returns boxes with labels
        if not self.settings.enabled or self._model is None:
            return []
        self._frame_count += 1
        if self._frame_count % max(1, self.settings.stride) != 0:
            return []
        # run model
        results = self._model.predict(source=[frame_bgr[:, :, ::-1]], verbose=False, conf=self.settings.confidence)
        detections: List[Tuple[int, int, int, int, str, float]] = []
        if not results:
            return detections
        res = results[0]
        names = res.names if hasattr(res, "names") else {}
        # Boxes in xyxy
        if hasattr(res, "boxes") and hasattr(res.boxes, "xyxy"):
            for i in range(len(res.boxes)):
                xyxy = res.boxes.xyxy[i].cpu().numpy().astype(int)
                x1, y1, x2, y2 = map(int, xyxy)
                cls_id = int(res.boxes.cls[i].item()) if hasattr(res.boxes, "cls") else -1
                conf = float(res.boxes.conf[i].item()) if hasattr(res.boxes, "conf") else 0.0
                label = names.get(cls_id, str(cls_id))
                detections.append((x1, y1, x2, y2, label, conf))
        return detections
