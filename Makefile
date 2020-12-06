test:
	@echo "=== Run unit tests ==="
	@PYTHONPATH=src coverage run --source=./src -m unittest discover ./tests

coverage:
	@echo "=== Show test coverage ==="
	@coverage report -m
