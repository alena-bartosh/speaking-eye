#!/usr/bin/env bash

# stop script if any command fails
set -e

REPO_DIR="$(dirname "$(readlink -f "$0")")"

source ${REPO_DIR}/.env/bin/activate
python3 ${REPO_DIR}/src/main.py
