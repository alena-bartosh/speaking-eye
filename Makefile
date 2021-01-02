SHELL = /usr/bin/env bash

VENV_DIR = .env
ACTIVATE_VENV = . $(VENV_DIR)/bin/activate
LOAD_TEXT_OUTPUT = . scripts/text_output.sh

DARK_GREY = \033[1;30m
GREEN = \033[1;32m
NC = \033[0m

default:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Supported commands"
	@echo "      $(DARK_GREY)-$(NC) make test"
	@echo "      $(DARK_GREY)-$(NC) make coverage"
	@echo "      $(DARK_GREY)-$(NC) make start"
	@echo "      $(DARK_GREY)-$(NC) make typecheck"
	@echo "      $(DARK_GREY)-$(NC) make lint"
	@echo "      $(DARK_GREY)-$(NC) make install"
	@echo "      $(DARK_GREY)-$(NC) make install/systemd"
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
	@echo
	@echo "  $(GREEN)🤖 💬 Done! Next step:$(NC)"
	@echo "      $(DARK_GREY)-$(NC) make install/systemd"
	@echo

install: env/create

install/systemd:
	@$(LOAD_TEXT_OUTPUT); robot_says "💬" "Create systemd user unit & reload systemd"
	@./scripts/install_systemd.sh
	@echo
	@echo "  $(GREEN)🤖 💬 Done! Choose a next step for Speaking Eye auto start:$(NC)"
	@echo "      $(DARK_GREY)-$(NC) systemctl --user start speaking-eye.service $(DARK_GREY)# run now$(NC)"
	@echo "      $(DARK_GREY)-$(NC) reboot $(DARK_GREY)# will automatically run after reboot$(NC)"
	@echo
