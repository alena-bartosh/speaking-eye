VENV_DIR = .env
ACTIVATE_VENV = . $(VENV_DIR)/bin/activate

DARK_GREY = \033[1;30m
GREEN = \033[1;32m
NC = \033[0m

default:
	@echo
	@echo "  $(GREEN)🤖 💬 Supported commands$(NC)"
	@echo
	@echo "      $(DARK_GREY)-$(NC) make test"
	@echo "      $(DARK_GREY)-$(NC) make coverage"
	@echo "      $(DARK_GREY)-$(NC) make start"
	@echo "      $(DARK_GREY)-$(NC) make typecheck"
	@echo "      $(DARK_GREY)-$(NC) make lint"
	@echo "      $(DARK_GREY)-$(NC) make install"
	@echo "      $(DARK_GREY)-$(NC) make install/systemd"
	@echo

test:
	@echo
	@echo "  $(GREEN)🤖 💬 Run unit tests$(NC)"
	@echo
	@$(ACTIVATE_VENV) && PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests

coverage:
	@echo
	@echo "  $(GREEN)🤖 💬 Show test coverage$(NC)"
	@echo
	@$(ACTIVATE_VENV) && coverage report -m

start:
	@echo
	@echo "  $(GREEN)🤖 💬 One-time start$(NC)"
	@echo
	@$(ACTIVATE_VENV) && python3 ./src/speaking_eye.py $(SE_ARGS)

typecheck:
	@echo
	@echo "  $(GREEN)🤖 💬 Type checking with mypy$(NC)"
	@echo
	@$(ACTIVATE_VENV) && mypy --show-error-codes --warn-unused-ignores ./src/speaking_eye.py

lint:
	@echo
	@echo "  $(GREEN)🤖 💬 Lint with flake8$(NC)"
	@echo
	@$(ACTIVATE_VENV) && flake8 . --show-source --statistics

env/create:
	@echo
	@echo "  $(GREEN)🤖 💬 Setup virtual env & install requirements$(NC)"
	@echo
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@$(ACTIVATE_VENV) && pip install --upgrade pip && pip install -r requirements.txt

install: env/create

install/systemd:
	@echo
	@echo "  $(GREEN)🤖 💬 Create systemd user unit & reload systemd$(NC)"
	@echo
	@./scripts/install_systemd.sh
