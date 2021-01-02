SHELL = /usr/bin/env bash

VENV_DIR = .env
ACTIVATE_VENV = . $(VENV_DIR)/bin/activate
LOAD_TEXT_OUTPUT = . scripts/text_output.sh

default:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Supported commands"
	@$(LOAD_TEXT_OUTPUT); print_list_item "make checks" "# includes:"
	@$(LOAD_TEXT_OUTPUT); print_list_item "  make typecheck"
	@$(LOAD_TEXT_OUTPUT); print_list_item "  make lint"
	@$(LOAD_TEXT_OUTPUT); print_list_item "  make test"
	@$(LOAD_TEXT_OUTPUT); print_list_item "  make coverage"
	@$(LOAD_TEXT_OUTPUT); print_list_item "make start"
	@$(LOAD_TEXT_OUTPUT); print_list_item "make install"
	@$(LOAD_TEXT_OUTPUT); print_list_item "make install/systemd"
	@echo

test:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Run unit tests"
	@$(ACTIVATE_VENV) && PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests
	@$(LOAD_TEXT_OUTPUT); robot_says "👍" "All good!"

coverage:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Show test coverage"
	@$(ACTIVATE_VENV) && coverage report -m
	@$(LOAD_TEXT_OUTPUT); robot_says "👍" "All good!"

start:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "One-time start"
	@$(ACTIVATE_VENV) && python3 ./src/speaking_eye.py $(SE_ARGS)

typecheck:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Type checking with mypy"
	@$(ACTIVATE_VENV) && mypy --show-error-codes --warn-unused-ignores ./src/speaking_eye.py
	@$(LOAD_TEXT_OUTPUT); robot_says "👍" "All good!"

lint:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Lint with flake8"
	@$(ACTIVATE_VENV) && flake8 . --show-source --statistics
	@$(LOAD_TEXT_OUTPUT); robot_says "👍" "All good!"

env/create:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Setup virtual env & install requirements"
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@$(ACTIVATE_VENV) && pip install --upgrade pip && pip install -r requirements.txt
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Done! Next step:"
	@$(LOAD_TEXT_OUTPUT); print_list_item "make install/systemd"
	@echo

install: env/create

install/systemd:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Create systemd user unit & reload systemd"
	@./scripts/install_systemd.sh
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Done! Choose a next step for Speaking Eye auto start:"
	@$(LOAD_TEXT_OUTPUT); print_list_item "systemctl --user start speaking-eye.service" "# run now"
	@$(LOAD_TEXT_OUTPUT); print_list_item "reboot" "# will automatically run after reboot"
	@echo

install/ci:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Prepare system dependencies for CI"
	@sudo apt install -y libgirepository1.0-dev
	make install
	@pip install flake8
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Done!"

checks: typecheck lint test coverage
