#!/usr/bin/env bash
CONFIG_DIR="/etc/kootnet"
# Update script that is run when the E-Ink upgrade command is sent
EINK_HTTP_URL='http://192.168.10.5:8009'
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
clear
printf 'Starting E-Ink sensor upgrade\n'
# Create temporary directories in root and copy things over
rm -R /root/eInkUpgrade 2>/dev/null
mkdir /root/eInkUpgrade 2>/dev/null
cd /root/eInkUpgrade
wget -r -np -nH -R "index.html*" ${EINK_HTTP_URL}/
cp -f -R /root/eInkUpgrade/* /opt/kootnet-sensors/
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/upgrade/copy_shortcuts.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/upgrade/set_autostart.sh
bash /opt/kootnet-sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - EInk' >> ${CONFIG_DIR}/last_updated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands
