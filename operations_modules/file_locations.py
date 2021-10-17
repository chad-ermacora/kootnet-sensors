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


def _check_directories():
    create_directories = [
        sensor_data_dir, sensor_config_dir, custom_ip_lists_folder, uploaded_databases_folder,
        sensor_data_dir + "/logs", database_backup_folder, sensor_data_dir + "/scripts", http_ssl_folder
    ]

    if os.geteuid() == 0:
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


# Holds the location of required files such as configurations and extra resources
# Locations change to the user's home directory + /kootnet_data if not run with root
program_root_dir = ""
try:
    split_location = os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]
    for section in split_location:
        program_root_dir += "/" + str(section)
    program_root_dir = program_root_dir[1:]
except Exception as error:
    print("Script Location Error: " + str(error))

sensor_data_dir = "/home/kootnet_data"
sensor_config_dir = "/etc/kootnet"

if os.geteuid() != 0:
    system_user = str(getuser()).strip()
    sensor_data_dir = "/home/" + system_user + "/kootnet_data"
    sensor_config_dir = "/home/" + system_user + "/kootnet_data/config"

uploaded_databases_folder = sensor_data_dir + "/uploaded_databases"
database_backup_folder = sensor_data_dir + "/database_backups"
custom_ip_lists_folder = sensor_config_dir + "/ip_lists"

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

checkin_configuration = sensor_config_dir + "/checkin_config.txt"
sensor_id = sensor_config_dir + "/sensor_id.txt"
old_version_file = sensor_config_dir + "/installed_version.txt"
program_last_updated = sensor_config_dir + "/last_updated.txt"

primary_config = sensor_config_dir + "/main_config.conf"
mqtt_broker_config = sensor_config_dir + "/mqtt_broker_config.conf"
mosquitto_configuration = "/etc/mosquitto/conf.d/kootnet_mosquitto.conf"
mqtt_subscriber_config = sensor_config_dir + "/mqtt_subscriber_config.conf"
mqtt_publisher_config = sensor_config_dir + "/mqtt_publisher_config.conf"
email_config = sensor_config_dir + "/email_config.conf"
display_config = sensor_config_dir + "/display_config.conf"
installed_sensors_config = sensor_config_dir + "/installed_sensors.conf"
interval_config = sensor_config_dir + "/interval_recording.conf"
trigger_variances_config = sensor_config_dir + "/trigger_variances.conf"
trigger_high_low_config = sensor_config_dir + "/trigger_high_low.conf"

http_auth = sensor_config_dir + "/auth.conf"

html_sensor_control_config = sensor_config_dir + "/html_sensor_control.conf"
html_sensor_control_reports_zip = sensor_data_dir + "/ReportsZip.zip"
html_sensor_control_databases_zip = sensor_data_dir + "/DatabasesZip.zip"
html_sensor_control_logs_zip = sensor_data_dir + "/OtherSensorsLogsZip.zip"
html_sensor_control_big_zip = sensor_data_dir + "/TheBigZip.zip"

weather_underground_config = sensor_config_dir + "/online_services_weather_underground.conf"
luftdaten_config = sensor_config_dir + "/online_services_luftdaten.conf"
osm_config = sensor_config_dir + "/online_services_open_sense_map.conf"

plotly_graph_interval = sensor_data_dir + "/IntervalPlotlyGraph.html"
plotly_graph_triggers = sensor_data_dir + "/TriggersPlotlyGraph.html"
plotly_graph_mqtt = sensor_data_dir + "/MQTTPlotlyGraph.html"
plotly_graph_custom = sensor_data_dir + "/CustomPlotlyGraph.html"

dhcpcd_config_file = "/etc/dhcpcd.conf"
wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

display_font = program_root_dir + "/extras/alphanumeric_lcd.ttf"
dhcpcd_config_file_template = program_root_dir + "/extras/dhcpcd_template.conf"
wifi_config_file_template = program_root_dir + "/extras/wpa_supplicant_template.conf"

http_ssl_folder = sensor_data_dir + "/ssl_files"
http_ssl_key = http_ssl_folder + "/kootnet_default.key"
http_ssl_csr = http_ssl_folder + "/kootnet_default.csr"
http_ssl_crt = http_ssl_folder + "/kootnet_default.crt"

html_report_css = program_root_dir + "/http_server/templates/ATPro_admin/style.css"
html_report_js = program_root_dir + "/http_server/templates/ATPro_admin/index.js"
html_report_pure_css = program_root_dir + "/http_server/extras/pure-min.css"
html_pure_css_menu = program_root_dir + "/http_server/templates/ATPro_admin/pure-horizontal-menu.css"

atpro_reports_folder = program_root_dir + \
                       "/http_server/templates/ATPro_admin/page_templates/remote_management/report_templates/"

html_report_all_start = atpro_reports_folder + "report-all-start.html"
html_report_all_end = atpro_reports_folder + "report-all-end.html"
html_combo_report = atpro_reports_folder + "report-combo.html"

html_report_template = atpro_reports_folder + "report-template.html"

html_report_sensor_error_template = atpro_reports_folder + "report-sensor-error-template.html"
html_report_system_sensor_template = atpro_reports_folder + "report-system-sensor-template.html"
html_report_config_sensor_template = atpro_reports_folder + "report-configurations-sensor-template.html"
html_report_sensor_readings_latency_template = atpro_reports_folder + "report-readings-latency-sensor-template.html"

_check_directories()
