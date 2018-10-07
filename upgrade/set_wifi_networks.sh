printf 'Updating Wireless Networks to Auto Connect to'
cat > /etc/wpa_supplicant/wpa_supplicant.conf << "EOF"
# Be sure to update to your wireless network
#
# Which ever wireless network has more signal strength
# Is the one that will connect, assuming settings are correct
#
# To add additional wireless network connections
# Copy one of the network blocks, including both { } and
# Paste it at the bottom of the file & Modify as needed

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CA

network={
        ssid="SensorWifi"
        psk="2505512335"
        key_mgmt=WPA-PSK
}
network={
        ssid="KI-WiFi"
        psk="2505510208"
        key_mgmt=WPA-PSK
}
EOF
