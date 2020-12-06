default:
	@echo "=== Supported commands ==="
	@echo "make test"
	@echo "make coverage"
	@echo "make start"
	@echo "make typecheck"
	@echo "make lint"

test:
	@echo "=== Run unit tests ==="
	@PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests

coverage:
	@echo "=== Show test coverage ==="
	@coverage report -m

start:
	@echo "=== One-time start ==="
	@python3 ./src/speaking_eye.py

typecheck:
	@echo "=== Type checking with mypy ==="
	@mypy --show-error-codes --warn-unused-ignores ./src/speaking_eye.py

lint:
	@echo "=== Lint with flake8 ==="
	@flake8 . --show-source --statistics
