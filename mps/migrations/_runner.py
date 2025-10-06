import copy


def migrate_settings(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    # Example migration: old top-level record_dir -> storage.recordings_dir
    if "record_dir" in out:
        storage = out.get("storage", {})
        storage.setdefault("recordings_dir", out.pop("record_dir"))
        storage.setdefault("snapshots_dir", "~/.local/share/mps/snapshots")
        out["storage"] = storage

    # Example migration: video.cams as list -> dict
    if isinstance(out.get("video", {}).get("cams"), list):
        cams_list = out["video"]["cams"]
        out["video"]["cams"] = {f"cam{i}": c for i, c in enumerate(cams_list)}

    return out

import copy


def migrate_settings(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    # Example migration: old "record_dir" → storage.recordings_dir
    if "record_dir" in out and "storage" not in out:
        out["storage"] = {
            "recordings_dir": out.pop("record_dir"),
            "snapshots_dir": "~/.local/share/mps/snapshots",
        }
    # Example migration: cam list → dict
    if isinstance(out.get("video", {}).get("cams"), list):
        cams_dict = {f"cam{i}": c for i, c in enumerate(out["video"]["cams"])}
        out["video"]["cams"] = cams_dict
    return out
