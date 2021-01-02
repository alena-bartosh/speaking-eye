#!/usr/bin/env bash

source ./assert.sh
source ./colors.sh

robot_says() {
  local emoji=${1}
  local text=${2}

  assert_argument_should_be_set "${emoji}" "emoji"
  assert_argument_should_be_set "${text}" "text"

  echo
  echo -e "  ${GREEN}🤖 ${emoji} ${text}${NC}"
  echo
}
