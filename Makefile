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

.PHONY: install-hooks security-scan security-scan-secrets security-scan-python security-scan-npm release install install-evals system-install test test-q lint lint-mermaid build clean distclean help

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

# ── Security scans (owned by Switch; run before release) ───────────────────────
# Each scan exits non-zero on findings. Needs gitleaks, uv, and npm on PATH;
# pip-audit runs through uvx. Mermaid's tools have no lockfile, so they cannot
# be audited reproducibly (documented gap in docs/SDLC.md).
security-scan: security-scan-secrets security-scan-python security-scan-npm ## Scan for leaked secrets and vulnerable dependencies

install-hooks: ## Enable the repo's git hooks (gitleaks pre-commit) via core.hooksPath
	@command -v gitleaks >/dev/null || { echo "gitleaks is not installed: https://github.com/gitleaks/gitleaks#installing"; exit 1; }
	git config core.hooksPath .githooks
	@echo "git hooks enabled: .githooks/pre-commit (gitleaks)"

security-scan-secrets: ## Scan git history for committed secrets (gitleaks, git-aware)
	@command -v gitleaks >/dev/null || { echo "gitleaks is not installed: https://github.com/gitleaks/gitleaks#installing"; exit 1; }
	gitleaks detect --source . --no-banner

security-scan-python: install ## Audit locked Python dependencies for known vulnerabilities (pip-audit)
	@mkdir -p build
	uv export --locked --extra dev --no-hashes --no-emit-project -o build/requirements-audit.txt
	uvx pip-audit -r build/requirements-audit.txt --disable-pip --no-deps

security-scan-npm: ## Audit the packaged persona-eval npm lockfile (high severity and above)
	npm audit --prefix bobp/tools/persona_eval_assets --audit-level=high

# ── Publish to public PyPI via GitHub trusted publishing ───────────────────────
# Creating a GitHub Release triggers .github/workflows/release.yml, which builds
# and publishes to PyPI (OIDC; no token). Needs `gh` authenticated with
# permission to create releases. Version comes from bobp/__init__.py.
VERSION := $(shell sed -n 's/^__version__ = "\(.*\)"/\1/p' bobp/__init__.py)

release: test ## Tag v<version> (if missing), push, and create the GitHub Release that publishes to PyPI
	@test -n "$(VERSION)" || { echo "cannot read version"; exit 1; }
	@test "$$(git rev-parse --abbrev-ref HEAD)" = main || { echo "release must run from main"; exit 1; }
	@git diff --quiet HEAD -- pyproject.toml bobp uv.lock || { echo "uncommitted changes in package files"; exit 1; }
	@git fetch -q origin main && test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || { echo "HEAD must match origin/main (push first)"; exit 1; }
	@git rev-parse -q --verify refs/tags/v$(VERSION) >/dev/null || git tag -a v$(VERSION) -m "bobp $(VERSION)"
	git push origin v$(VERSION)
	@gh release view v$(VERSION) >/dev/null 2>&1 && { echo "release v$(VERSION) already exists"; exit 1; } || true
	gh release create v$(VERSION) --generate-notes --title "bobp $(VERSION)"
