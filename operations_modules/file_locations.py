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

    This file contains the location of files on the host system.
"""
import os
from getpass import getuser

running_with_root = True
if os.geteuid():
    # root has UID of 0
    running_with_root = False


def _get_user():
    """Try to find the user who called sudo."""
    try:
        user = os.environ['USER']
    except KeyError:
        # possibly a systemd service. no sudo was used
        return getuser()

    if user == 'root':
        try:
            return os.environ['SUDO_USER']
        except KeyError:
            # no sudo was used
            pass
    return user


def _check_directories():
    create_directories = [
        sensor_data_dir, sensor_config_dir, custom_ip_lists_folder, ks_generated_folder, uploaded_databases_folder,
        log_directory, database_backup_folder, upgrade_scripts_folder, http_ssl_folder, downloads_folder
    ]

    if running_with_root:
        create_directories.append(smb_mount_dir)
        current_directory = ""
        for found_dir in mosquitto_configuration.split("/")[1:-1]:
            current_directory += "/" + str(found_dir)
            create_directories.append(current_directory)

    for directory in create_directories:
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except Exception as dir_error:
                print(" -- Make Directory Error: " + str(dir_error))


program_root_dir = ""
try:
    split_location = os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]
    for section in split_location:
        program_root_dir += "/" + str(section)
    program_root_dir = program_root_dir[1:]
except Exception as error:
    print("File Locations - Script Location Error: " + str(error))

# Holds the location of databases, configurations and extra resources
sensor_data_dir = "/home/kootnet_data"
sensor_config_dir = "/etc/kootnet"
# If not running as a service or the root user, locations changes to the user's home directory + /kootnet_data
if program_root_dir != "/opt/kootnet-sensors" or not running_with_root:
    system_user = _get_user()
    sensor_data_dir = "/home/" + system_user + "/kootnet_data"
    sensor_config_dir = "/home/" + system_user + "/kootnet_data/config"

smb_mount_dir = "/mnt/kootnet_sensors_smb/"
downloads_folder = sensor_data_dir + "/downloads"
upgrade_scripts_folder = sensor_data_dir + "/scripts"
ks_generated_folder = sensor_data_dir + "/ks_generated"
uploaded_databases_folder = sensor_data_dir + "/uploaded_databases"
database_backup_folder = sensor_data_dir + "/database_backups"
custom_ip_lists_folder = sensor_config_dir + "/ip_lists"

upgrade_running_file_location = upgrade_scripts_folder + "/upgrade_running.conf"
display_font = program_root_dir + "/extras/alphanumeric_lcd.ttf"
dhcpcd_config_file = "/etc/dhcpcd.conf"
dhcpcd_config_file_template = program_root_dir + "/extras/dhcpcd_template.conf"
wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"
wifi_config_file_template = program_root_dir + "/extras/wpa_supplicant_template.conf"
mosquitto_configuration = "/etc/mosquitto/conf.d/kootnet_mosquitto.conf"

sensor_database = sensor_data_dir + "/SensorRecordingDatabase.sqlite"
mqtt_subscriber_database = sensor_data_dir + "/MQTTSubscriberDatabase.sqlite"
sensor_checkin_database = sensor_data_dir + "/SensorCheckinDatabase.sqlite"
database_zipped = sensor_data_dir + "/MainDatabaseZipped.zip"
mqtt_database_zipped = sensor_data_dir + "/MQTTDatabaseZipped.zip"
checkin_database_zipped = sensor_data_dir + "/CheckinDatabaseZipped.zip"

log_directory = sensor_data_dir + "/logs/"
primary_log = log_directory + "primary_log.txt"
network_log = log_directory + "network_log.txt"
sensors_log = log_directory + "sensors_log.txt"
mqtt_subscriber_log = log_directory + "mqtt_subscriber_log.txt"
log_zip_file = log_directory + "all_logs.zip"

http_ssl_folder = sensor_data_dir + "/ssl_files"
http_ssl_key = http_ssl_folder + "/kootnet_default.key"
http_ssl_csr = http_ssl_folder + "/kootnet_default.csr"
http_ssl_crt = http_ssl_folder + "/kootnet_default.crt"

flask_login_user = sensor_config_dir + "/auth_http_user.conf"
flask_login_hash = sensor_config_dir + "/auth_http_hash.scrypt"
flask_login_hash_salt = sensor_config_dir + "/auth_http_hash_salt.scrypt"

sensor_id = sensor_config_dir + "/sensor_id.txt"
old_version_file = sensor_config_dir + "/installed_version.txt"
program_last_updated = sensor_config_dir + "/last_updated.txt"

html_sensor_control_config = sensor_config_dir + "/html_sensor_control.conf"
primary_config = sensor_config_dir + "/main_config.conf"
upgrades_config = sensor_config_dir + "/upgrades_config.conf"
urls_configuration = sensor_config_dir + "/urls_config.conf"
installed_sensors_config = sensor_config_dir + "/installed_sensors.conf"
sensor_offsets_config = sensor_config_dir + "/sensor_offsets.conf"
display_config = sensor_config_dir + "/display_config.conf"
checkin_configuration = sensor_config_dir + "/checkin_config.conf"
interval_config = sensor_config_dir + "/interval_recording.conf"
trigger_variances_config = sensor_config_dir + "/trigger_variances.conf"
trigger_high_low_config = sensor_config_dir + "/trigger_high_low.conf"
email_reports_config = sensor_config_dir + "/email_reports.conf"
email_db_graph_config = sensor_config_dir + "/email_db_graphs.conf"
email_config = sensor_config_dir + "/email_config.conf"
mqtt_broker_config = sensor_config_dir + "/mqtt_broker_config.conf"
mqtt_subscriber_config = sensor_config_dir + "/mqtt_subscriber_config.conf"
mqtt_publisher_config = sensor_config_dir + "/mqtt_publisher_config.conf"
weather_underground_config = sensor_config_dir + "/online_services_weather_underground.conf"
luftdaten_config = sensor_config_dir + "/online_services_luftdaten.conf"
osm_config = sensor_config_dir + "/online_services_open_sense_map.conf"

live_graphs_config = sensor_config_dir + "/live_graphs.conf"
db_graphs_config = sensor_config_dir + "/database_graphs.conf"

plotly_graph_interval = ks_generated_folder + "/IntervalPlotlyGraph.html"
plotly_graph_triggers = ks_generated_folder + "/TriggersPlotlyGraph.html"
plotly_graph_mqtt = ks_generated_folder + "/MQTTPlotlyGraph.html"
plotly_graph_custom = ks_generated_folder + "/CustomPlotlyGraph.html"

atpro_reports_folder = program_root_dir + "/http_server/templates/ATPro_admin/page_templates/"
atpro_reports_folder += "remote_management/report_templates/"
html_combo_report = atpro_reports_folder + "report-combo.html"
html_sensor_control_reports_zip = ks_generated_folder + "/ReportsZip.zip"
html_sensor_control_databases_zip = ks_generated_folder + "/DatabasesZip.zip"
html_sensor_control_logs_zip = ks_generated_folder + "/OtherSensorsLogsZip.zip"
html_sensor_control_big_zip = ks_generated_folder + "/TheBigZip.zip"

_check_directories()
