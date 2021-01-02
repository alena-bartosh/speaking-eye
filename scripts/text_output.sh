#!/usr/bin/env bash

# Get absolute path for dir with scripts
CURRENT_DIR="$(readlink -f "${BASH_SOURCE%/*}")"

source "${CURRENT_DIR}/assert.sh"
source "${CURRENT_DIR}/colors.sh"

robot_says() {
  local emoji=${1}
  local text=${2}

  assert_argument_should_be_set "${emoji}" "emoji"
  assert_argument_should_be_set "${text}" "text"

  echo
  echo -e "  ${GREEN}🤖 ${emoji} ${text}${NC}"
  echo
}
