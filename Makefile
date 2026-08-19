.PHONY: help install install-dev dev build preview check clean clean-all new-week new-notebook status
.DEFAULT_GOAL := help

CONTENT_DIR := src/content/docs
NB_DIR      := notebooks

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (frozen lockfile)
	pnpm install --frozen-lockfile

install-dev: ## Install dependencies (updates lockfile)
	pnpm install

dev: ## Start dev server at localhost:4321
	pnpm run dev

build: ## Build the static site to ./dist/
	pnpm run build

preview: build ## Build then preview
	pnpm run preview

check: ## Type-check the project
	pnpm exec astro check

clean: ## Remove build artifacts
	rm -rf .astro dist

clean-all: clean ## Remove build artifacts and node_modules
	rm -rf node_modules

new-week: ## Scaffold a week page. Usage: make new-week N=07
ifndef N
	$(error N is required. Usage: make new-week N=07)
endif
	@FILE="$(CONTENT_DIR)/weeks/week-$(N).mdx"; \
	if [ -f "$$FILE" ]; then echo "$$FILE already exists"; exit 1; fi; \
	printf '%s\n' '---' 'title: "$(N)주차: 제목"' 'description: 설명' 'week: $(N)' '---' '' \
		'## 이번 주차' '' 'TODO' '' \
		'## 온라인 (2시수)' '' 'TODO' '' \
		'## 대면 (1시수)' '' 'TODO' '' \
		'## 학습활동' '' '**[이론]** TODO' '' '**[구현]** TODO' '' '**[실무]** TODO' \
		> "$$FILE"; \
	echo "Created: $$FILE"

new-notebook: ## Scaffold a practice notebook. Usage: make new-notebook N=03
ifndef N
	$(error N is required. Usage: make new-notebook N=03)
endif
	@FILE="$(NB_DIR)/week-$(N).ipynb"; \
	if [ -f "$$FILE" ]; then echo "$$FILE already exists"; exit 1; fi; \
	sed 's/__WEEK__/$(N)/g' $(NB_DIR)/_template.ipynb > "$$FILE"; \
	echo "Created: $$FILE"

status: ## Show content file counts
	@echo "weeks:     $$(ls $(CONTENT_DIR)/weeks/*.mdx 2>/dev/null | wc -l | tr -d ' ') / 15"
	@echo "notebooks: $$(ls $(NB_DIR)/week-*.ipynb 2>/dev/null | wc -l | tr -d ' ')"
	@echo "submitted: $$(find assignments -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ') folders"
