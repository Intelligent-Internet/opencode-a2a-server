#!/usr/bin/env bash
# Uninstall a single OpenCode + A2A instance created by scripts/deploy.sh.
#
# Safety model (enforced):
# - This script always prints the uninstall actions (preview first).
# - There is NO dry_run=false option.
# - To actually apply destructive actions you must pass confirm=UNINSTALL.
#
# IMPORTANT: This script (and the apply step) never removes systemd template units
# (/etc/systemd/system/opencode@.service, opencode-a2a@.service) because they are
# shared globally across all instances.
#
# Usage:
#   ./scripts/uninstall.sh project=<name> [data_root=/data/projects] [confirm=UNINSTALL]
#
# Examples:
#   ./scripts/uninstall.sh project=alpha
#   ./scripts/uninstall.sh project=alpha confirm=UNINSTALL
set -euo pipefail

PROJECT_NAME=""
DATA_ROOT_INPUT=""
CONFIRM_INPUT=""

for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    key="${arg%%=*}"
    value="${arg#*=}"
  else
    echo "Unknown argument format: $arg (expected key=value)" >&2
    exit 1
  fi

  case "${key,,}" in
    project|project_name)
      PROJECT_NAME="$value"
      ;;
    data_root)
      DATA_ROOT_INPUT="$value"
      ;;
    confirm)
      CONFIRM_INPUT="$value"
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_NAME" ]]; then
  echo "Usage: $0 project=<name> [data_root=/data/projects] [confirm=UNINSTALL]" >&2
  exit 1
fi

DATA_ROOT="${DATA_ROOT_INPUT:-${DATA_ROOT:-/data/projects}}"
PROJECT_DIR="${DATA_ROOT}/${PROJECT_NAME}"
UNIT_OPENCODE="opencode@${PROJECT_NAME}.service"
UNIT_A2A="opencode-a2a@${PROJECT_NAME}.service"

APPLY="false"
if [[ "$CONFIRM_INPUT" == "UNINSTALL" ]]; then
  APPLY="true"
fi

run() {
  echo "+ $*"
  if [[ "$APPLY" == "true" ]]; then
    "$@"
  fi
}

run_ignore() {
  echo "+ $*"
  if [[ "$APPLY" == "true" ]]; then
    "$@" || true
  fi
}

echo "Project: ${PROJECT_NAME}"
echo "DATA_ROOT: ${DATA_ROOT}"
echo "Project dir: ${PROJECT_DIR}"
echo "Note: systemd template units will NOT be removed."
echo "Mode: $([[ "$APPLY" == "true" ]] && echo apply || echo preview)"

# Stop/disable instance units (idempotent).
if command -v systemctl >/dev/null 2>&1; then
  run_ignore sudo systemctl disable --now "${UNIT_A2A}" "${UNIT_OPENCODE}"
  run_ignore sudo systemctl reset-failed "${UNIT_A2A}" "${UNIT_OPENCODE}"
else
  echo "systemctl not found; skipping systemd unit disable/stop." >&2
fi

# Remove project directory.
if [[ -e "${PROJECT_DIR}" ]]; then
  run sudo rm -rf --one-file-system "${PROJECT_DIR}"
else
  echo "Project dir not found; skipping: ${PROJECT_DIR}"
fi

# Remove project user and group.
if id "${PROJECT_NAME}" &>/dev/null; then
  if command -v userdel >/dev/null 2>&1; then
    run_ignore sudo userdel "${PROJECT_NAME}"
  elif command -v deluser >/dev/null 2>&1; then
    run_ignore sudo deluser "${PROJECT_NAME}"
  else
    echo "Neither userdel nor deluser found; cannot remove user ${PROJECT_NAME} automatically." >&2
  fi
else
  echo "User not found; skipping: ${PROJECT_NAME}"
fi

if getent group "${PROJECT_NAME}" >/dev/null 2>&1; then
  if command -v groupdel >/dev/null 2>&1; then
    run_ignore sudo groupdel "${PROJECT_NAME}"
  elif command -v delgroup >/dev/null 2>&1; then
    run_ignore sudo delgroup "${PROJECT_NAME}"
  else
    echo "Neither groupdel nor delgroup found; cannot remove group ${PROJECT_NAME} automatically." >&2
  fi
else
  echo "Group not found; skipping: ${PROJECT_NAME}"
fi

echo "Uninstall completed."
if [[ "$APPLY" != "true" ]]; then
  echo
  echo "Preview only. To apply, re-run with: confirm=UNINSTALL"
fi
