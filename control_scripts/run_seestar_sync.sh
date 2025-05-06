#!/bin/bash
cd /home/ingo/WHOPA/git_repo/whopa/control_scripts
source ~/.bashrc                    # Optional: load virtualenvs or PATHs if needed

echo "[$(date)] Starting Seestar sync..." >> /var/log/seestar_sync.log
/usr/bin/python3 seestar_sync.py >> /var/log/seestar_sync.log 2>&1
