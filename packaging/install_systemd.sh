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

install -m 644 packaging/martinspoint.service /etc/systemd/system/$SERVICE_NAME
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
echo "Installed $SERVICE_NAME. Start with: systemctl start $SERVICE_NAME"
