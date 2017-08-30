#!/usr/bin/env bash

SSH="ssh -i ~/vium/keys/prod.pem ubuntu@fira.mousera.com" 

PID=$($SSH ps ax | grep 'nohup ./fira_server.py' | awk '{print $1}')
$SSH sudo kill -9 $PID

PID=$($SSH ps ax | grep 'fira_server.py' | awk '{print $1}')
$SSH sudo kill -9 $PID

#$SSH "cd /home/ubuntu/fira/; git pull origin master; sudo nohup ./fira_server.py >fira.log 2>&1 &"
$SSH "cd /home/ubuntu/fira/; git pull origin master"
