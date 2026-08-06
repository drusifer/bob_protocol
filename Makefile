.DEFAULT_GOAL := help

# Build/test/package targets for developing bobp itself.
# Everything for installing/updating/diffing the Bob Protocol into other
# projects now lives in the `bobp` CLI (bobp install/update/pull/diff/clean) —
# see bobp/templates/Makefile for what gets installed there.

.PHONY: install test build clean help

install: ## Install bobp in editable mode with dev dependencies
	pip install -e ".[dev]"

test: ## Run the test suite
	pytest tests/ -q

build: ## Build the sdist and wheel into dist/
	python -m build

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
