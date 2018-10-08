#!/bin/bash

sudo systemctl restart monitor.service
ssh btnode1 'sudo systemctl restart monitor.service'
ssh btnode2 'sudo systemctl restart monitor.service'
