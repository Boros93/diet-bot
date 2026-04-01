.PHONY: setup run start-diet-bot

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python -m app.bot

start-diet-bot: setup run
