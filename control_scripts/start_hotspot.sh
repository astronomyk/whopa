# Description: Start WiFi hotspot using wlx7cf17ec63a62
# Make sure the device is disconnected before running

SSID="whopa_box"
PASSWORD="H*****J****"
IFNAME="wlx7cf17ec63a62"

echo "Starting hotspot on $IFNAME with SSID '$SSID'..."
sudo nmcli device wifi hotspot ssid "$SSID" password "$PASSWORD" ifname "$IFNAME" band a channel 48
