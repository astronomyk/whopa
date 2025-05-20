# Description: Start WiFi hotspot using wlx7cf17ec63a62
# Make sure the device is disconnected before running
# wlx7cdd900b41e9
# wlx7cf17ec63a62
# wlx98ba5fd03903

SSID="whopa_box"
PASSWORD="HungryJacks"
IFNAME="wlx7cf17ec63a62"

echo "Starting hotspot on $IFNAME with SSID '$SSID'..."
sudo nmcli device wifi hotspot ssid "$SSID" password "$PASSWORD" ifname "$IFNAME" band a channel 48

