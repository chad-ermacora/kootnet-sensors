"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
debug_file_location = "/etc/kootnet/enable_debug_logging.conf"
sensor_database_location = "/home/kootnet_data/SensorRecordingDatabase.sqlite"
config_file_location = "/etc/kootnet/sql_recording.conf"
sensors_installed_file_location = "/etc/kootnet/installed_sensors.conf"
trigger_variances_file_location = "/etc/kootnet/trigger_variances.conf"
wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"
quick_links_file_location = "/opt/kootnet-sensors/extras/quick.html"

old_version_file_location = "/etc/kootnet/installed_version.txt"
last_updated_file_location = "/etc/kootnet/last_updated.txt"

log_directory = "/home/kootnet_data/logs/"
primary_log = log_directory + "Primary_log.txt"
sensors_log = log_directory + "Sensors_log.txt"
network_log = log_directory + "Network_log.txt"
