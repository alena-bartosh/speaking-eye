#!/usr/bin/env bash

source ./colors.sh

echo_error() {
  echo >&2 -e "${RED}"
  echo >&2 -e "$@"
  echo >&2 -e "${NC}"
}
