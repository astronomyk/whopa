#!/bin/bash

# Check if the PID file exists
if [ -f /tmp/mjpg_streamer.pid ]; then
    # Read the PID from the file
    MJPG_PID=$(cat /tmp/mjpg_streamer.pid)
    echo "Stopping MJPG Streamer (PID: $MJPG_PID)..."

    # Kill the process
    kill $MJPG_PID

    # Optionally, check if the kill was successful
    if ps -p $MJPG_PID > /dev/null; then
        echo "Failed to stop MJPG Streamer with PID $MJPG_PID"
    else
        echo "MJPG Streamer stopped successfully."
    fi

    # Remove the PID file
    rm -f /tmp/mjpg_streamer.pid
else
    echo "PID file for MJPG Streamer not found, skipping."
fi

echo "Stop MJPG Streamer script finished."

