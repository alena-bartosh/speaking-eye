#!/usr/bin/env bash

CURRENT_DIR="$(readlink -f "${BASH_SOURCE%/*}")"

source "${CURRENT_DIR}/echo_error.sh"

assert_die() {
  echo_error "$@"
  exit 1
}

assert_argument_should_be_set() {
  local value="${1}"
  local name="${2}"

  if [[ -z "${name}" ]]; then
    assert_die "Error: Name of argument was not set!"
  fi

  if [[ -z "${value}" ]]; then
    assert_die "Error: Value for [${name}] argument was not set!"
  fi
}
