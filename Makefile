SHELL := /bin/bash

setup:
	@echo "Initializing the environment"
	@uv sync --all-extras --all-groups

build:
	@echo "Building the project"
	@uv tool run maturin develop

test:
	@echo "Running tests"
	@uv run pytest tests/*.py -v -s --log-cli-level=INFO --cov=lakeops --cov-report=xml

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
