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
    sensor_data_dir = "/home/" + str(getuser()).strip() + "/kootnet_data"
    sensor_config_dir = "/home/" + str(getuser()).strip() + "/kootnet_data/config"

    directory_list = [sensor_data_dir, sensor_config_dir, sensor_data_dir + "/logs", sensor_data_dir + "/scripts"]
    for directory in directory_list:
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except Exception as error:
                print("Make Directory Error: " + str(error))

sensor_database = sensor_data_dir + "/SensorRecordingDatabase.sqlite"
sensor_html_help = program_root_dir + "/extras/SensorUnitHelp.html"
database_zipped = sensor_data_dir + "/MainDatabaseZipped.zip"

log_directory = sensor_data_dir + "/logs/"
primary_log = log_directory + "Primary_log.txt"
network_log = log_directory + "Network_log.txt"
sensors_log = log_directory + "Sensors_log.txt"
log_zip_file = log_directory + "all_logs.zip"

old_version_file = sensor_config_dir + "/installed_version.txt"
program_last_updated = sensor_config_dir + "/last_updated.txt"

primary_config = sensor_config_dir + "/main_config.conf"
mqtt_broker_config = sensor_config_dir + "/mqtt_broker_config.conf"
mqtt_publisher_config = sensor_config_dir + "/mqtt_publisher_config.conf"
display_config = sensor_config_dir + "/display_config.conf"
installed_sensors_config = sensor_config_dir + "/installed_sensors.conf"
trigger_variances_config = sensor_config_dir + "/trigger_variances.conf"

http_auth = sensor_config_dir + "/auth.conf"

html_sensor_control_config = sensor_config_dir + "/html_sensor_control.conf"
html_sensor_control_reports_zip = sensor_data_dir + "/ReportsZip.zip"
html_sensor_control_databases_zip = sensor_data_dir + "/DatabasesZip.zip"
html_sensor_control_logs_zip = sensor_data_dir + "/OtherSensorsLogsZip.zip"
html_sensor_control_big_zip = sensor_data_dir + "/TheBigZip.zip"

weather_underground_config = sensor_config_dir + "/online_services_weather_underground.conf"
luftdaten_config = sensor_config_dir + "/online_services_luftdaten.conf"
osm_config = sensor_config_dir + "/online_services_open_sense_map.conf"

plotly_graph_interval = sensor_data_dir + "/IntervalPlotlySensorGraph.html"
plotly_graph_triggers = sensor_data_dir + "/TriggersPlotlySensorGraph.html"

dhcpcd_config_file = "/etc/dhcpcd.conf"
wifi_config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

display_font = program_root_dir + "/extras/DejaVuSans-Bold.ttf"
dhcpcd_config_file_template = program_root_dir + "/extras/dhcpcd_template.conf"
wifi_config_file_template = program_root_dir + "/extras/wpa_supplicant_template.conf"

http_ssl_folder = program_root_dir + "/http_server/ssl_files"
http_ssl_key = http_ssl_folder + "/kootnet_default.key"
http_ssl_csr = http_ssl_folder + "/kootnet_default.csr"
http_ssl_crt = http_ssl_folder + "/kootnet_default.crt"

j_query_js = program_root_dir + "/http_server/extras/jquery-3.4.1.min.js"
mui_min_css = program_root_dir + "/http_server/extras/mui.min-ver-0.9.43.css"
mui_colors_min_css = program_root_dir + "/http_server/extras/mui-colors.min-ver-0.9.43.css"
mui_min_js = program_root_dir + "/http_server/extras/mui.min-ver-0.9.43.js"
menu_script = program_root_dir + "/http_server/extras/menu.js"
menu_css_style = program_root_dir + "/http_server/extras/style.css"
html_icon = program_root_dir + "/extras/icon.ico"

tinymce_min_js = program_root_dir + "/http_server/extras/tinymce/tinymce.min.js"
tinymce_theme_min_js = program_root_dir + "/http_server/extras/tinymce/themes/silver/theme.min.js"
tinymce_jquery_min_js = program_root_dir + "/http_server/extras/tinymce/jquery.tinymce.min.js"
tinymce_skin_min_css = program_root_dir + "/http_server/extras/tinymce/skins/ui/oxide-dark/skin.min.css"
tinymce_ui_content_min_css = program_root_dir + "/http_server/extras/tinymce/skins/ui/oxide-dark/content.min.css"
tinymce_content_min_css = program_root_dir + "/http_server/extras/tinymce/skins/content/dark/content.min.css"

tinymce_plugin_link = program_root_dir + "/http_server/extras/tinymce/plugins/link/plugin.min.js"
tinymce_plugin_autolink = program_root_dir + "/http_server/extras/tinymce/plugins/autolink/plugin.min.js"
tinymce_plugin_lists = program_root_dir + "/http_server/extras/tinymce/plugins/lists/plugin.min.js"
tinymce_plugin_print = program_root_dir + "/http_server/extras/tinymce/plugins/print/plugin.min.js"
tinymce_plugin_wordcount = program_root_dir + "/http_server/extras/tinymce/plugins/wordcount/plugin.min.js"
tinymce_plugin_code = program_root_dir + "/http_server/extras/tinymce/plugins/code/plugin.min.js"
tinymce_plugin_insertdatetime = program_root_dir + "/http_server/extras/tinymce/plugins/insertdatetime/plugin.min.js"
tinymce_plugin_fullscreen = program_root_dir + "/http_server/extras/tinymce/plugins/fullscreen/plugin.min.js"
tinymce_plugin_spellchecker = program_root_dir + "/http_server/extras/tinymce/plugins/spellchecker/plugin.min.js"
tinymce_plugin_help = program_root_dir + "/http_server/extras/tinymce/plugins/help/plugin.min.js"

html_combo_report = program_root_dir + "/http_server/templates/non-flask/report_3_combo.html"

html_report_system1_start = program_root_dir + "/http_server/templates/non-flask/report_system1_start.html"
html_report_system2_sensor = program_root_dir + "/http_server/templates/non-flask/report_system2_sensor.html"
html_report_system3_end = program_root_dir + "/http_server/templates/non-flask/report_system3_end.html"

html_report_config1_start = program_root_dir + "/http_server/templates/non-flask/report_config1_start.html"
html_report_config2_sensor = program_root_dir + "/http_server/templates/non-flask/report_config2_sensor.html"
html_report_config3_end = program_root_dir + "/http_server/templates/non-flask/report_config3_end.html"

html_report_sensors_test1_start = program_root_dir + "/http_server/templates/non-flask/report_sensors_test1_start.html"
html_report_sensors_test2_sensor = program_root_dir + "/http_server/templates/non-flask/report_sensors_test2_sensor.html"
html_report_sensors_test3_end = program_root_dir + "/http_server/templates/non-flask/report_sensors_test3_end.html"

html_report_sensors_latency1_start = program_root_dir + "/http_server/templates/non-flask/report_sensors_latency1_start.html"
html_report_sensors_latency2_sensor = program_root_dir + "/http_server/templates/non-flask/report_sensors_test2_sensor.html"
