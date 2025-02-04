SHELL := /bin/bash

setup:
	@echo "Initializing the environment"
	@brew install uv

build:
	@echo "Building the project"
	@uv build --wheel

test:
	@echo "Running tests"
	@uv run pytest tests/ -v -s --log-cli-level=INFO

lint:
	@echo "Linting the project"
	@uv tool run ruff check src/ --fix