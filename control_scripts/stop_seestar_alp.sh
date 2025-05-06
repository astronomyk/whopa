#!/bin/bash

# Check if the PID file exists
if [ -f /tmp/seestar_alp.pid ]; then
    # Read the PID from the file
    SEESTAR_PID=$(cat /tmp/seestar_alp.pid)
    echo "Stopping Seestar ALP (PID: $SEESTAR_PID)..."

    # Kill the process
    kill $SEESTAR_PID

    # Optionally, check if the kill was successful
    if ps -p $SEESTAR_PID > /dev/null; then
        echo "Failed to stop Seestar ALP with PID $SEESTAR_PID"
    else
        echo "Seestar ALP stopped successfully."
    fi

    # Remove the PID file
    rm -f /tmp/seestar_alp.pid
else
    echo "PID file for Seestar ALP not found, skipping."
fi

echo "Stop Seestar ALP script finished."
