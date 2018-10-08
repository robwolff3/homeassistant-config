#!/bin/bash

sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove
source /srv/homeassistant/bin/activate
python3 -m pip install --upgrade homeassistant
deactivate
sudo systemctl restart home-assistant.service