#!/bin/bash

# Save current working directory
ORIG_DIR=$(pwd)

# Navigate to the folder where mjpg_streamer is located
cd ~/WHOPA/mjpg-streamer/mjpg-streamer-experimental || { echo "Failed to enter mjpg_streamer folder"; exit 1; }

# Start mjpg_streamer in the background using nohup
nohup ./mjpg_streamer -i "./input_uvc.so -r 1920x1080 -f 5" -o "./output_http.so -w ./www -p 8081" > /tmp/mjpg_streamer.log 2>&1 &
PID2=$!
echo "Started mjpg_streamer with PID $PID2"

# Go back to the original directory
cd "$ORIG_DIR"

# Save the PID
echo "$PID2" > /tmp/mjpg_streamer.pid

echo "MJPG Streamer started and running in the background."
