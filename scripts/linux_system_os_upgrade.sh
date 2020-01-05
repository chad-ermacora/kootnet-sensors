#!/bin/bash
# This script runs a system apt-get update and upgrade then reboots the system
# The one prior must succeed before doing the next
apt-get update && apt-get -y upgrade && reboot
