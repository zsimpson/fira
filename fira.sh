#!/usr/bin/env bash
sudo kill $(ps aux | grep 'fira' | awk '{print $2}')
sudo nohup ./fira_server.py >fira_server.log 2>&1 &
