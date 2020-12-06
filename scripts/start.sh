#!/usr/bin/env bash

# stop script if any command fails
set -e

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"
REPO_DIR="${SCRIPTS_DIR}/.."

cd "${REPO_DIR}"

make start
