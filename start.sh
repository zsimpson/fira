#!/usr/bin/env bash
source secret.sh
sudo -E nohup ./fira_server.py >fira.log 2>&1 &
echo "Started $?"
