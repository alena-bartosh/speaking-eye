#!/usr/bin/env bash

# NOTE: we need to update TERM env variable since we use colors more than [0-7]
#       based on https://serverfault.com/a/524057
export TERM=xterm-256color

DARK_GREY=$(tput setab 8)
GREEN=$(tput setaf 10)
RED=$(tput setaf 1)

BOLD=$(tput bold)
NC=$(tput sgr0)

export DARK_GREY
export GREEN
export RED

export BOLD
export NC
