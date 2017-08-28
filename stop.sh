#!/usr/bin/env bash
sudo kill $(ps aux | grep 'fira' | awk '{print $2}')
