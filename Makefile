SHELL := /bin/bash

# --- Node / MCP server ---

.PHONY: install
install:
	npm install

.PHONY: build
build:
	npm run build

.PHONY: dev-mcp
dev-mcp:
	npx tsx src/mcp_server/index.ts

# --- Python API ---

.PHONY: venv
venv:
	python -m venv .venv
	@echo "Run: source .venv/bin/activate"

.PHONY: install-python
install-python:
	pip install -r src/python_api/requirements.txt

.PHONY: dev-python
dev-python:
	cd src/python_api && gunicorn -c gunicorn.conf.py app.wsgi:app

# --- Docker / Compose ---

.PHONY: docker-build
docker-build:
	docker compose build

.PHONY: docker-up
docker-up:
	docker compose up

.PHONY: docker-down
docker-down:
	docker compose down

# --- Meta ---

.PHONY: dev
dev: dev-python

.PHONY: all
all: install build