default:
	@echo "=== Supported commands ==="
	@echo "make test"
	@echo "make coverage"
	@echo "make start"

test:
	@echo "=== Run unit tests ==="
	@PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests

coverage:
	@echo "=== Show test coverage ==="
	@coverage report -m

start:
	@echo "=== One-time start ==="
	@python3 ./src/speaking_eye.py
