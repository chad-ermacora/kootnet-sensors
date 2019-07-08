#!/usr/bin/env bash
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
printf '\n\nDoing "Clean" upgrade\nLeaves database & config\nDeletes everything else\nThen re-downloads and installs\n'
cp -f /opt/kootnet-sensors/scripts/remove_services_and_files.sh /root
cp -f /opt/kootnet-sensors/scripts/update_programs_online.sh /root
bash /root/remove_services_and_files.sh
bash /root/update_programs_online.sh
