VENV_DIR = .env
ACTIVATE_VENV = . $(VENV_DIR)/bin/activate

default:
	@echo "=== Supported commands ==="
	@echo "make test"
	@echo "make coverage"
	@echo "make start"
	@echo "make typecheck"
	@echo "make lint"
	@echo "make install"

test:
	@echo "=== Run unit tests ==="
	@$(ACTIVATE_VENV) && PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests

coverage:
	@echo "=== Show test coverage ==="
	@$(ACTIVATE_VENV) && coverage report -m

start:
	@echo "=== One-time start ==="
	@$(ACTIVATE_VENV) && python3 ./src/speaking_eye.py

typecheck:
	@echo "=== Type checking with mypy ==="
	@$(ACTIVATE_VENV) && mypy --show-error-codes --warn-unused-ignores ./src/speaking_eye.py

lint:
	@echo "=== Lint with flake8 ==="
	@$(ACTIVATE_VENV) && flake8 . --show-source --statistics

env/create:
	@echo "=== Setup virtual env and install requirements ==="
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@$(ACTIVATE_VENV) && pip install --upgrade pip && pip install -r requirements.txt

install: env/create
