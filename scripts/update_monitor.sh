#!/bin/bash

sudo systemctl stop monitor.service
cd /home/rob/monitor/
sudo git pull
sudo systemctl start monitor.service
ssh mirrorpi 'sudo systemctl stop monitor.service && sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove && cd /home/rob/monitor/ && sudo git pull && sudo systemctl start monitor.service'
