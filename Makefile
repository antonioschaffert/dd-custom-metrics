.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=dd_custom_metrics --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 dd_custom_metrics tests examples
	mypy dd_custom_metrics

format: ## Format code with black
	black dd_custom_metrics tests examples

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python setup.py sdist bdist_wheel

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

check: ## Run all checks (lint, test, format check)
	black --check dd_custom_metrics tests examples
	flake8 dd_custom_metrics tests examples
	mypy dd_custom_metrics
	pytest

dev-setup: ## Set up development environment
	pip install -e ".[dev]"
	pre-commit install

run-examples: ## Run the example scripts
	python examples/basic_usage.py
	python examples/airflow_integration.py 