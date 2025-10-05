#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/martinspoint
SERVICE_NAME=martinspoint.service

if [[ ${EUID:-} -ne 0 ]]; then
  echo "Please run as root" >&2
  exit 1
fi

mkdir -p "$APP_DIR"
rsync -a --delete ./ "$APP_DIR"/

cd "$APP_DIR"
python3 -m venv idview_env
source idview_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

install -m 644 packaging/systemd/martinspoint.service /etc/systemd/system/$SERVICE_NAME
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Installed and started $SERVICE_NAME"
