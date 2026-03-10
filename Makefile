.DEFAULT_GOAL := help

.PHONY: help tldr install clean

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

tldr: ## Show TL;DR summaries from all project files (quick orientation for agents)
	@rg --no-heading "TL;DR:" --glob "*.md" -N | sed 's|^\./||' | sort

install: ## Copy agents into a project and set up skill links (usage: make install TARGET=/path/to/project)
	@[ -n "$(TARGET)" ] || { echo "Usage: make install TARGET=/path/to/project"; exit 1; }
	@[ -d "$(TARGET)" ] || { echo "Error: $(TARGET) does not exist"; exit 1; }
	@echo "Installing BobProtocol into $(TARGET)..."
	@rsync -a \
		--exclude='*.docs/context.md' \
		--exclude='*.docs/current_task.md' \
		--exclude='*.docs/next_steps.md' \
		--exclude='CHAT.md' \
		agents/ $(TARGET)/agents/
	@echo "Initialising agent state files..."
	@for dir in $(TARGET)/agents/*.docs; do \
		cp agents/templates/_template_context.md    $$dir/context.md; \
		cp agents/templates/_template_current_task.md $$dir/current_task.md; \
		cp agents/templates/_template_next_steps.md $$dir/next_steps.md; \
	done
	@cp agents/templates/_template_CHAT.md $(TARGET)/agents/CHAT.md
	@echo "Setting up Claude skill links..."
	@python $(TARGET)/agents/tools/setup_agent_links.py
	@echo ""
	@echo "Done. BobProtocol installed in $(TARGET)"
	@echo "Run 'make tldr' inside $(TARGET) to verify."

update: ## Update agents and skills in a project, preserving state (usage: make update TARGET=/path/to/project)
	@[ -n "$(TARGET)" ] || { echo "Usage: make update TARGET=/path/to/project"; exit 1; }
	@[ -d "$(TARGET)" ] || { echo "Error: $(TARGET) does not exist"; exit 1; }
	@echo "Updating BobProtocol in $(TARGET)..."
	@rsync -a \
		--exclude='*.docs/context.md' \
		--exclude='*.docs/current_task.md' \
		--exclude='*.docs/next_steps.md' \
		--exclude='CHAT.md' \
		--exclude='chat_archive/' \
		agents/ $(TARGET)/agents/
	@echo "Ensuring new agent state files are initialised..."
	@for dir in $(TARGET)/agents/*.docs; do \
		[ -f $$dir/context.md ] || cp agents/templates/_template_context.md $$dir/context.md; \
		[ -f $$dir/current_task.md ] || cp agents/templates/_template_current_task.md $$dir/current_task.md; \
		[ -f $$dir/next_steps.md ] || cp agents/templates/_template_next_steps.md $$dir/next_steps.md; \
	done
	@[ -f $(TARGET)/agents/CHAT.md ] || cp agents/templates/_template_CHAT.md $(TARGET)/agents/CHAT.md
	@echo "Updating Claude skill links..."
	@python $(TARGET)/agents/tools/setup_agent_links.py
	@echo ""
	@echo "Done. BobProtocol updated in $(TARGET)"

clean: ## Remove generated symlinks and reset agent memory/state files
	@echo "Removing generated symlinks..."
	@rm -rf .claude/skills/
	@rm -f AGENTS.md GEMINI.md .cursorrules CHATGPT.md .github/copilot-instructions.md
	@echo "Resetting agent state files to templates..."
	@for dir in agents/*.docs; do \
		cp agents/templates/_template_context.md    $$dir/context.md; \
		cp agents/templates/_template_current_task.md $$dir/current_task.md; \
		cp agents/templates/_template_next_steps.md $$dir/next_steps.md; \
	done
	@cp agents/templates/_template_CHAT.md agents/CHAT.md
	@echo "Done. Environment cleaned and state reset."
