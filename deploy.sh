#!/usr/bin/env bash

git add .
git commit -m "deploy"
git push origin master


SSH="ssh -i ~/vium/keys/prod_ecs_host.pem ubuntu@10.204.1.139" 

PID=$($SSH ps ax | grep 'nohup ./fira_server.py' | awk '{print $1}')
$SSH sudo kill -9 $PID

PID=$($SSH ps ax | grep 'fira_server.py' | awk '{print $1}')
$SSH sudo kill -9 $PID

$SSH "cd /home/ubuntu/fira/; printenv > env; git pull origin master; sudo -E nohup ./fira_server.py >fira.log 2>&1 &"
