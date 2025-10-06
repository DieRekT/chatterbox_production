## 🛡️ Martins Point Security v2.2

Professional Desktop Security Console with Advanced Motion Detection & AI Analytics

### Key Features
- Dual camera tiles (USB webcam or RTSP via OpenCV)
- Motion detection with sensitivity controls and pre/post-buffer recording
- Optional YOLOv8 AI analytics (disabled by default, graceful fallback)
- Stable viewport engine (letterboxed, flicker-free)
- Live storage usage indicator

## Quick Start

Prereqs: Ubuntu 20.04+, Python 3.10+, webcams or IP cameras

```bash
python3 -m venv idview_env
source idview_env/bin/activate
pip install -r requirements.txt
./run_idview.sh
```

## Configuration

Unified settings with layered config:

```
defaults (config/default_settings.json)
→ user (~/.config/mps/settings.json)
→ env overrides (MPS_RECORDINGS_DIR, MPS_CONFIG)
```

Open the Settings dialog from the app menu (Settings → Open Settings…) to import/export/reset.

## Systemd (optional)

```bash
sudo bash packaging/install_systemd.sh
sudo systemctl status martinspoint.service
journalctl -u martinspoint.service -f
```

See `scripts/print_settings_tree.py` to inspect the resolved tree.

## Notes
- AI analytics requires `ultralytics` and weights; it is optional.
- RTSP URLs can be used in `device` fields directly.
