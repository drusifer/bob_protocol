.DEFAULT_GOAL := help

# Build/test/package targets for developing bobp itself.
# Everything for installing/updating/diffing the Bob Protocol into other
# projects now lives in the `bobp` CLI (bobp install/update/pull/diff/clean) —
# see bobp/templates/Makefile for what gets installed there.
#
# Python commands run through uv and the project .venv. `.python-version` tracks
# the latest available Python 3.15 patch; `uv.lock` records latest compatible deps.

MERMAID_DIR := tools/mermaid_validate
MERMAID_STAMP := $(MERMAID_DIR)/node_modules/.install.stamp
MERMAID_DIAGRAMS := $(shell find agents -name '*.diagram.md' 2>/dev/null)

.PHONY: install install-evals system-install test test-q lint lint-mermaid build clean distclean help

$(MERMAID_STAMP): $(MERMAID_DIR)/package.json
	cd $(MERMAID_DIR) && npm install
	touch $(MERMAID_STAMP)

install: ## Install bobp and dev dependencies into the uv-managed .venv
	uv sync --python 3.15 --locked --extra dev

install-evals: ## Show how to install global Promptfoo dependencies for persona evaluations
	uv run --python 3.15 --locked --extra dev bobp persona-eval --setup

system-install: ## Install bobp as a uv-managed global tool (editable mode)
	uv tool install --editable . --force

test: install ## Run the test suite with locked dependencies
	uv run --python 3.15 --locked --extra dev pytest --basetemp=build/pytest tests/ -q

test-q: install ## Run a focused test selection (pass ARGS=... to pytest)
	uv run --python 3.15 --locked --extra dev pytest --basetemp=build/pytest tests/ -q $(ARGS)

lint: lint-mermaid ## Run all lint checks

lint-mermaid: $(MERMAID_STAMP) ## Syntax-check every ```mermaid fence in agents/*.diagram.md against mermaid's real parser
	node $(MERMAID_DIR)/validate.mjs $(MERMAID_DIAGRAMS)

build: install ## Build the sdist and wheel into dist/
	uv run --python 3.15 --locked --extra dev python -m build

clean: ## Remove build artifacts (keeps .venv)
	rm -rf dist/ build/ *.egg-info

distclean: clean ## Remove build artifacts and the local Python environment
	rm -rf .venv

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Publish to the pi-patch Forgejo registry (forge.pi-patch.lan) ──────────────
# Credentials: make -C $(PI_PATCH)/cluster forgejo-token
PI_PATCH        ?= $(HOME)/Projects/pi-patch
FORGEJO_PUBLISH := $(PI_PATCH)/cluster/scripts/forgejo-publish.sh
FORGEJO_VERSION ?= $(shell git describe --tags --always --dirty)

.PHONY: deploy-forgejo
deploy-forgejo: build ## Build and publish the bobp wheel/sdist to pi-patch Forgejo PyPI
	$(FORGEJO_PUBLISH) pypi dist
