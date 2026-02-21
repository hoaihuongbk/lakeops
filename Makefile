SHELL := /bin/bash

setup:
	@echo "Initializing the environment"
	@uv sync --all-extras --all-groups

build:
	@echo "Building the project"
	@uv tool run maturin develop

test:
	@echo "Running core tests"
	@uv run pytest tests/*.py -v -s -m "not spark and not spark_connect" --log-cli-level=INFO --cov=lakeops --cov-report=xml
	@echo "Running spark tests"
	@uv run pytest tests/*.py -v -s -m "spark" --log-cli-level=INFO --cov=lakeops --cov-append
	@echo "Running spark-connect tests"
	@uv run pytest tests/*.py -v -s -m "spark_connect" --log-cli-level=INFO --cov=lakeops --cov-append

integration_test:
	@echo "Running integration tests"
	@uv run pytest integration_tests/*.py -v --log-cli-level=INFO

lint:
	@echo "Linting the project"
	@uv tool run ruff check src/ --fix

test_docs:
	@echo "Generating documentation"
	@uv run mkdocs build --clean
	@uv run mkdocs serve

build_wheel:
	@echo "Releasing the project"
	@uv tool run maturin build
