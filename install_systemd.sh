#!/usr/bin/env bash

# experimental:
# systemd user service and timer generator
# after running this script speaking-eye will turn on in 2 minutes after reboot

# stop script if any command fails
set -e

mkdir -p ~/.local/share/systemd/user

REPO_DIR="$(dirname "$(readlink -f "$0")")"

cat > ~/.local/share/systemd/user/speaking-eye.service <<EOL
[Unit]
Description=Speaking Eye App

[Service]
ExecStart=${REPO_DIR}/start.sh

[Install]
WantedBy=default.target
EOL

cat > ~/.local/share/systemd/user/speaking-eye.timer <<EOL
[Unit]
Description=Speaking Eye App Timer

[Timer]
OnBootSec=2min
Unit=speaking-eye.service

[Install]
WantedBy=default.target
EOL

systemctl --user daemon-reload
systemctl --user enable speaking-eye.timer
