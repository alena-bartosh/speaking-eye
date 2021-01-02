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
  echo "  ${BOLD}${GREEN}🤖 ${emoji} ${text}${NC}"
  echo
}

print_list_item() {
  local item=${1}
  local comment=${2}

  assert_argument_should_be_set "${item}" "item"

  echo "      ${BOLD}${DARK_GREY}-${NC} ${item} ${DARK_GREY}${comment}${NC}"
}
