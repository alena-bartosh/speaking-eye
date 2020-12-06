test:
	@echo "=== Run unit tests ==="
	@PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests
