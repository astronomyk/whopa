#!/bin/bash

# Set VNC display number
VNC_DISPLAY=1

# Set the path to your noVNC directory if you installed via GitHub
NOVNC_DIR="/usr/share/novnc"  # Adjust this path if needed
VNC_PORT=5901
NOVNC_PORT=6080

# Check if VNC is running, and start it if necessary
if ! pgrep -x "Xvnc" > /dev/null; then
    echo "Starting VNC server..."
    nohup vncserver :$VNC_DISPLAY -localhost no > ~/vncserver.log 2>&1 &
else
    echo "VNC server is already running."
fi

# Start noVNC if it's not already running
if ! pgrep -x "websockify" > /dev/null; then
    echo "Starting noVNC..."
    # If using the package-installed version
    nohup websockify --web=$NOVNC_DIR  $NOVNC_PORT 0.0.0.0:$VNC_PORT > ~/novnc.log 2>&1 &
    # Or if using the GitHub version, replace with:
    # $NOVNC_DIR/utils/launch.sh --vnc localhost:$VNC_PORT
else
    echo "noVNC is already running."
fi

echo "Access your desktop at http://$(hostname -I | awk '{print $1}'):$NOVNC_PORT/vnc.html"
