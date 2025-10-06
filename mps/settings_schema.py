from __future__ import annotations

from typing import Dict, Literal
from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat, field_validator, ConfigDict


class Cam(BaseModel):
    device: str
    resolution: str = Field(pattern=r"^\d+x\d+$")
    fps: PositiveInt = 30
    rotate_deg: Literal[0, 90, 180, 270] = 0
    enabled: bool = True


class Video(BaseModel):
    cams: Dict[str, Cam]
    letterbox: bool = True
    backend: Literal["opencv"] = "opencv"
    rtsp_timeout_s: NonNegativeFloat = 6.0


class Motion(BaseModel):
    enabled: bool = True
    sensitivity: float = Field(0.55, ge=0.0, le=1.0)
    min_area_px: PositiveInt = 900
    prebuffer_s: NonNegativeFloat = 2.0
    postbuffer_s: NonNegativeFloat = 4.0
    cooldown_s: NonNegativeFloat = 2.0


class Analytics(BaseModel):
    yolo_enabled: bool = False
    model: str = "yolov8n.pt"
    confidence: float = Field(0.35, ge=0.05, le=0.95)


class Storage(BaseModel):
    recordings_dir: str
    snapshots_dir: str
    max_days_to_keep: PositiveInt = 14
    free_space_min_gb: NonNegativeFloat = 5.0


class App(BaseModel):
    name: str = "Martins Point Security"
    version: str
    timezone: str = "Australia/Sydney"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    ui_theme: Literal["dark", "light", "auto"] = "dark"


class Telemetry(BaseModel):
    enabled: bool = False


class Flags(BaseModel):
    experimental: bool = False
    dev_tools: bool = False
    low_power_mode: bool = False


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    app: App
    storage: Storage
    video: Video
    motion: Motion
    analytics: Analytics
    telemetry: Telemetry
    flags: Flags

    @field_validator("storage")
    def _paths_not_empty(cls, v: Storage):
        if not v.recordings_dir or not v.snapshots_dir:
            raise ValueError("Storage directories must not be empty")
        return v
