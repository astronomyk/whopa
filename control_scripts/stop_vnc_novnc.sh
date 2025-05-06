#!/bin/bash

# Function to stop the VNC server
stop_vnc() {
    # Find the VNC server process (assuming it runs on display :1)
    VNC_PID=$(ps aux | grep 'Xtigervnc' | grep ':1' | awk '{print $2}')

    if [ -n "$VNC_PID" ]; then
        echo "Stopping VNC server (PID: $VNC_PID)..."
        kill -9 $VNC_PID
        echo "VNC server stopped."
    else
        echo "No VNC server running on display :1."
    fi
}

# Function to stop the noVNC server
stop_novnc() {
    # Find the noVNC server process (assuming it listens on port 6080)
    NOVNC_PID=$(ps aux | grep 'websockify' | grep '6080' | awk '{print $2}')

    if [ -n "$NOVNC_PID" ]; then
        echo "Stopping noVNC server (PID: $NOVNC_PID)..."
        kill -9 $NOVNC_PID
        echo "noVNC server stopped."
    else
        echo "No noVNC server running on port 6080."
    fi
}

# Main function to stop both VNC and noVNC servers
stop_servers() {
    stop_vnc
    stop_novnc
}

# Call the stop_servers function
stop_servers

