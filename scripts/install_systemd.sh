#!/usr/bin/env bash

# experimental:
# systemd user service generator
# after running this script speaking-eye will automatically turn on after system startup

# stop script if any command fails
set -e

mkdir -p ~/.local/share/systemd/user

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"

cat > ~/.local/share/systemd/user/speaking-eye.service <<EOL
[Unit]
Description=Speaking Eye App

[Service]
ExecStart=${SCRIPTS_DIR}/start.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
EOL

systemctl --user daemon-reload
