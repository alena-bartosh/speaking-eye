#!/usr/bin/env bash

CURRENT_DIR="$(readlink -f "${BASH_SOURCE%/*}")"

source "${CURRENT_DIR}/colors.sh"

echo_error() {
  echo >&2 "${RED}"
  echo >&2 "$@"
  echo >&2 "${NC}"
}
