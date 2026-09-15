PYTHON ?= python3

.PHONY: setup test run

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r services/agent/requirements.txt && pip install -r services/scraper/requirements.txt && pip install -r services/codegen/requirements.txt

run:
	docker compose up --build -d

test:
	pytest -q
