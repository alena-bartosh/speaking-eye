#!/usr/bin/env bash

# stop script if any command fails
set -e

REPO_DIR="$(dirname "$(readlink -f "$0")")"
SRC_DIR="${REPO_DIR}/src"

source ${REPO_DIR}/.env/bin/activate

export PYTHONPATH=${SRC_DIR}
python3 -m unittest discover ./tests
