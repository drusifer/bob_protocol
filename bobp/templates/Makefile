.DEFAULT_GOAL := help

# ── Bob Protocol Configuration ───────────────────────────────────────────────
# Installing/updating/pulling/diffing/cleaning a Bob Protocol install is done
# with the `bobp` CLI directly (bobp install/update/pull/diff/clean) — see
# https://github.com/drusifer/bob_protocol. This Makefile only provides this
# project's own local dev conveniences: chat/chat_diagram, tldr, and the mkf
# build-output-filter wrapper.

# Detect if this file is being run directly as Makefile.bob
_IS_BOB_ENTRY := $(filter %Makefile.bob,$(firstword $(MAKEFILE_LIST)))

ifdef MKF_ACTIVE

# ── Re-invocation Layer ──────────────────────────────────────────────────────
# Included by mkf.py to run the actual target.

# Include the project's original targets.
# We try Makefile.prj (legacy) and Makefile (if we are running as Makefile.bob).
ifneq ($(firstword $(MAKEFILE_LIST)),Makefile)
-include Makefile
endif
-include Makefile.prj

# ── Bob Protocol Targets ─────────────────────────────────────────────────────

.PHONY: tldr test via_index

tldr: ## Show TL;DR summaries from all project files (quick orientation for agents)
	@rg --no-heading "TL;DR:" --glob "*.md" -N | sed 's|^\./||' | sort

test: ## Run unit tests
	@python -m unittest discover -s tests

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

else

# ── Interception layer ───────────────────────────────────────────────────────
# All targets except help, chat, and chat_diagram route through mkf
# (bobp.tools.mkf via `bobp mkf`). mkf captures output to build/build.out,
# posts status to CHAT.md, and prints the last 10 lines on exit.
#
# Verbosity (set V=):
#   make tldr              silent  — exit code only, full log in build/build.out
#   make tldr V=-v         stderr to terminal
#   make tldr V=-vv        stderr + filtered failures to terminal
#   make tldr V=-vvv       stderr + full stdout to terminal

.PHONY: help chat chat_diagram test via_index

help: ## Show available make targets
	@echo ""
	@echo "  Build output filter (mkf) is active. All targets route through 'bobp mkf'."
	@echo "  Full log: build/build.out   Status posted to: agents/CHAT.md"
	@echo ""
	@echo "  Verbosity: append V=-v | V=-vv | V=-vvv to any target"
	@echo "    (none)   silent — exit code only"
	@echo "    -v       stderr to terminal"
	@echo "    -vv      stderr + failures/errors to terminal"
	@echo "    -vvv     stderr + full stdout to terminal"
	@echo ""
	@echo "  Installing/updating/pulling/diffing/cleaning a Bob Protocol install"
	@echo "  is done with the bobp CLI directly, not make:"
	@echo "    bobp install <target> | update <target> | pull <src> | diff <target> | clean"
	@echo ""
	@echo "  Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@if [ -f Makefile.prj ]; then \
		echo ""; \
		echo "  Project targets (Makefile.prj):"; \
		grep -E '^[a-zA-Z][a-zA-Z0-9_-]*:' Makefile.prj | \
		awk 'BEGIN {FS = ":.*?## "}; /##/ {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2} !/##/ {split($$0,a,":"); printf "    \033[36m%-22s\033[0m\n", a[1]}'; \
	fi
	@echo ""

chat: ## Post a message to CHAT.md (usage: make chat MSG="<msg>" [PERSONA="<name>"] [CMD="<cmd>"] [TO="<recipient>"])
	@[ -n "$(MSG)" ] || { echo "Usage: make chat MSG=\"<message>\" [PERSONA=\"<name>\"] [CMD=\"<cmd>\"] [TO=\"<recipient>\"]"; exit 1; }
	@bobp chat "$(MSG)" \
		$(if $(PERSONA),--persona "$(PERSONA)") \
		$(if $(CMD),--cmd "$(CMD)") \
		$(if $(TO),--to "$(TO)")

chat_diagram: ## Regenerate agents/CHAT.diagram.md, a Mermaid sequence diagram of CHAT.md (usage: make chat_diagram [INCLUDE_BUILDS=1])
	@bobp chat-diagram $(if $(INCLUDE_BUILDS),--include-builds)

test: ## Run unit tests
	@bobp mkf $(V) $@

via_index: ## Build the via index required by the via MCP server
	@bobp mkf $(V) $@

# Interception logic:
# If we are the entry point (direct make call), intercept everything.
# If we are included, we only provide targets, unless specified.
ifeq ($(MKF_ACTIVE),)
ifdef _IS_BOB_ENTRY
%:
	@bobp mkf $(V) $@
endif
endif

endif
