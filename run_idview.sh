#!/usr/bin/env bash
set -euo pipefail

python3 -m venv idview_env || true
# shellcheck disable=SC1091
source idview_env/bin/activate
pip install -U pip wheel
pip install -r requirements.txt

export PYTHONUNBUFFERED=1
export QT_QPA_PLATFORM=xcb
python -c "from mps.main import main; raise SystemExit(main())" "$@"
