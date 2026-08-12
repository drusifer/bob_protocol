.DEFAULT_GOAL := help

# Build/test/package targets for developing bobp itself.
# Everything for installing/updating/diffing the Bob Protocol into other
# projects now lives in the `bobp` CLI (bobp install/update/pull/diff/clean) —
# see bobp/templates/Makefile for what gets installed there.
#
# Always runs through the project .venv, never system/PATH python or pip.

VENV := .venv
PYTHON := $(VENV)/bin/python
VENV_STAMP := $(VENV)/.install.stamp

.PHONY: install system-install test build clean help

$(VENV_STAMP): pyproject.toml
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	touch $(VENV_STAMP)

install: $(VENV_STAMP) ## Install bobp in editable mode with dev dependencies (into .venv)
	$(PYTHON) -m pip install -e ".[dev]"

system-install: ## Install bobp globally using pipx (editable mode)
	pipx install --editable . --force

test: $(VENV_STAMP) ## Run the test suite (via .venv)
	$(PYTHON) -m pytest tests/ -q

build: $(VENV_STAMP) ## Build the sdist and wheel into dist/
	$(PYTHON) -m build

clean: ## Remove build artifacts (keeps .venv — use `rm -rf .venv` to drop it too)
	rm -rf dist/ build/ *.egg-info

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
