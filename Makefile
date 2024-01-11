.PHONY: init bot notify camera services

init:
	@python3 -m venv .venv
	@.venv/bin/pip install -r requirements.txt

bot:
	@.venv/bin/python3 bot.py

notify:
	@.venv/bin/python3 notify.py

camera:
	@.venv/bin/python3 camera.py

services:
	@cp services/* /etc/systemd/system/