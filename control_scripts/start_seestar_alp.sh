#!/bin/bash

# Save current working directory
ORIG_DIR=$(pwd)

# Navigate to the folder where seestar_alp is located
cd ~/WHOPA/seestar_alp/ || { echo "Failed to enter seestar_alp folder"; exit 1; }

# Start seestar_alp in the background using nohup
nohup ./seestar_alp > /tmp/seestar_alp.log 2>&1 &
PID1=$!
echo "Started seestar_alp with PID $PID1"

# Go back to the original directory
cd "$ORIG_DIR"

# Save the PID
echo "$PID1" > /tmp/seestar_alp.pid

echo "Seestar ALP started and running in the background."
