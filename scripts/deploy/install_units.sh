#!/usr/bin/env bash
# Install systemd template units for OpenCode and A2A.
# Requires env: OPENCODE_A2A_DIR, OPENCODE_CORE_DIR, UV_PYTHON_DIR.
# Requires sudo to write /etc/systemd/system.
set -euo pipefail

: "${OPENCODE_A2A_DIR:?}"
: "${OPENCODE_CORE_DIR:?}"
: "${UV_PYTHON_DIR:?}"

UNIT_DIR="/etc/systemd/system"
OPENCODE_UNIT="${UNIT_DIR}/opencode@.service"
A2A_UNIT="${UNIT_DIR}/opencode-a2a@.service"

sudo install -d -m 755 "$UNIT_DIR"

cat <<UNIT | sudo tee "$OPENCODE_UNIT" >/dev/null
[Unit]
Description=OpenCode serve for %i
After=network.target

[Service]
Type=simple
User=%i
Group=%i
WorkingDirectory=%h
Environment=OPENCODE_CORE_DIR=${OPENCODE_CORE_DIR}
Environment=OPENCODE_A2A_DIR=${OPENCODE_A2A_DIR}
Environment=UV_PYTHON_DIR=${UV_PYTHON_DIR}
Environment=PATH=${OPENCODE_CORE_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
EnvironmentFile=%h/config/opencode.env
EnvironmentFile=-%h/config/opencode.secret.env
Environment=HOME=%h

ExecStart=${OPENCODE_A2A_DIR}/scripts/deploy/run_opencode.sh
Restart=on-failure
RestartSec=2
UMask=0077

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=%h
ReadOnlyPaths=${OPENCODE_CORE_DIR}
ReadOnlyPaths=${OPENCODE_A2A_DIR}
ReadOnlyPaths=${UV_PYTHON_DIR}
ReadOnlyPaths=/usr/bin/gh

[Install]
WantedBy=multi-user.target
UNIT

cat <<UNIT | sudo tee "$A2A_UNIT" >/dev/null
[Unit]
Description=OpenCode A2A for %i
After=network.target opencode@%i.service
Requires=opencode@%i.service

[Service]
Type=simple
User=%i
Group=%i
WorkingDirectory=%h
Environment=OPENCODE_A2A_DIR=${OPENCODE_A2A_DIR}
Environment=OPENCODE_CORE_DIR=${OPENCODE_CORE_DIR}
Environment=UV_PYTHON_DIR=${UV_PYTHON_DIR}
EnvironmentFile=%h/config/a2a.env
Environment=HOME=%h

ExecStart=${OPENCODE_A2A_DIR}/scripts/deploy/run_a2a.sh
Restart=on-failure
RestartSec=2
UMask=0077

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=%h
ReadOnlyPaths=${OPENCODE_A2A_DIR}
ReadOnlyPaths=${OPENCODE_CORE_DIR}
ReadOnlyPaths=${UV_PYTHON_DIR}

[Install]
WantedBy=multi-user.target
UNIT
