#!/usr/bin/env sh
set -eu

REPO_URL="${PROJECT_COPILOT_REPO_URL:-https://github.com/Yingxing-AI/project-copilot.git}"
REF="${PROJECT_COPILOT_REF:-v0.3.0-alpha.8}"
PACKAGE_SPEC="git+${REPO_URL}@${REF}"

say() {
  printf '%s\n' "$1"
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

find_python() {
  if need_cmd python3; then
    printf '%s\n' "python3"
  elif need_cmd python; then
    printf '%s\n' "python"
  else
    return 1
  fi
}

PYTHON_BIN="$(find_python || true)"
if [ -z "$PYTHON_BIN" ]; then
  say "Python 3.10+ is required. Please install Python first:"
  say "https://www.python.org/downloads/"
  exit 1
fi

if ! "$PYTHON_BIN" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
then
  say "Python 3.10+ is required. Current version is:"
  "$PYTHON_BIN" --version
  exit 1
fi

say "Installing Project Copilot from ${PACKAGE_SPEC}"

if need_cmd pipx; then
  pipx install --force "$PACKAGE_SPEC"
else
  say "pipx not found. Falling back to user install with pip."
  "$PYTHON_BIN" -m pip install --user "$PACKAGE_SPEC"
fi

if need_cmd project-copilot; then
  say "Project Copilot installed successfully."
  project-copilot --version
  say "Run this next:"
  say "project-copilot doctor"
else
  say "Project Copilot was installed, but 'project-copilot' is not on PATH."
  say "If you used pip, make sure your user scripts directory is on PATH."
  say "On macOS/Linux/WSL, you can usually run:"
  say "export PATH=\"\$HOME/.local/bin:\$PATH\""
  say "Try:"
  say "$PYTHON_BIN -m project_copilot.cli.main doctor"
fi
