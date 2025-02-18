
help:	## Show Help
	@grep --no-filename -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

format: ## Format project
	poetry run black .
	poetry run ruff --select I --fix .

lint: 	## Lint project
	poetry run black . --check
	poetry run ruff .

test: 	## Run test
	poetry run pytest

server: ## Start app server
	poetry run uvicorn tinygen.app:app --reload

notebook: ## Start notebook
	poetry run jupyter notebook --notebook-dir=notebooks
