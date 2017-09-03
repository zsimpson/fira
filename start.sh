#!/usr/bin/env bash
source secret.sh
git pull origin master
sudo -E nohup ./fira_server.py >fira.log 2>&1 &
echo "Started $?"
