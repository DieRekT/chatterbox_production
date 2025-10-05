#!/usr/bin/env bash
set -euo pipefail

# Activate venv if present
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  :
elif [[ -d "idview_env" ]]; then
  # shellcheck disable=SC1091
  source idview_env/bin/activate
fi

export PYTHONUNBUFFERED=1
export QT_QPA_PLATFORM=xcb

python3 -m mps.main "$@"
