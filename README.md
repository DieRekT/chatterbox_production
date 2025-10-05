## 🛡️ Martins Point Security v2.1

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

Edit `config/camera_settings.json`:

```json
{
  "cam0": { "device": "/dev/video0", "resolution": "1280x720", "fps": 30 },
  "cam1": { "device": "/dev/video2", "resolution": "1280x720", "fps": 30 }
}
```

Environment variables:
- `MPS_CONFIG`: path to camera JSON
- `MPS_RECORDINGS_DIR`: directory for snapshots/recordings

## Systemd (optional)

```bash
sudo bash packaging/install_systemd.sh
sudo systemctl status martinspoint.service
journalctl -u martinspoint.service -f
```

The service sets `MPS_CONFIG` and `MPS_RECORDINGS_DIR` to `/opt/martinspoint/...`.

## Notes
- AI analytics requires `ultralytics` and weights; it is optional.
- RTSP URLs can be used in `device` fields directly.
