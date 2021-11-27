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
from platform import system
from os import geteuid, path
from operations_modules.app_generic_classes import CreateDatabaseVariables, CreateNetworkSystemCommands, \
    CreateNetworkGetCommands, CreateNetworkSetCommands, CreateLatencyVariables, CreateEmptyThreadClass

database_variables = CreateDatabaseVariables()
network_system_commands = CreateNetworkSystemCommands()
network_get_commands = CreateNetworkGetCommands()
network_set_commands = CreateNetworkSetCommands()
latency_variables = CreateLatencyVariables()

# Dictionary of Terminal commands
bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_kootnet-sensors_e-ink.sh",
                 "RestartService": "systemctl daemon-reload ; systemctl restart KootnetSensors.service",
                 "EnableService": "systemctl enable KootnetSensors.service",
                 "StartService": "systemctl start KootnetSensors.service",
                 "DisableService": "systemctl disable KootnetSensors.service",
                 "StopService": "systemctl stop KootnetSensors.service",
                 "UpgradeSystemOS": "apt-get update && apt-get -y upgrade",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now"}

# The following variables are populated at runtime (Up until the next blank line)
# This helps lessen disk reads by caching commonly used variables
current_platform = system()
running_with_root = True
if geteuid():
    # root has UID of 0
    running_with_root = False
running_as_service = False

program_root_dir = ""
try:
    split_location = path.dirname(path.realpath(__file__)).split("/")[:-1]
    for section in split_location:
        program_root_dir += "/" + str(section)
    program_root_dir = program_root_dir[1:]
except Exception as error:
    print("App Cached Variables - Script Location Error: " + str(error))

if program_root_dir == "/opt/kootnet-sensors":
    running_as_service = True
operating_system_name = ""
program_last_updated = ""
reboot_count = ""
total_ram_memory = 0.0
total_disk_space = 0.0
tmp_sensor_id = ""

# Names of all the uploaded databases for graphing (Only names, no directory path)
uploaded_databases_list = []

# Names of all the backed-up main databases (Only names, no directory path)
zipped_db_backup_list = []

# Is filled with Currently available online Stable / Developmental versions
standard_version_available = "Retrieving"
developmental_version_available = "Retrieving"
software_update_available = False
software_update_dev_available = False

# Update Files found on Update Server. They will be set to either True or False
update_server_file_present_md5 = None
update_server_file_present_version = None
update_server_file_present_full_installer = None
update_server_file_present_upgrade_installer = None

# Static variables
command_data_separator = "[new_data_section]"

# Plotly Configuration Variables
plotly_theme = "plotly_dark"

# Network Variables
hostname = "Loading ..."
ip = "Loading ..."
ip_subnet = ""
gateway = ""
dns1 = ""
dns2 = ""

# Wifi Variables
wifi_country_code = ""
wifi_ssid = ""
wifi_security_type = ""
wifi_psk = ""

# Flask App Login Variables (Web Portal Login)
http_flask_user = "Kootnet"
http_flask_password_hash = b''
http_flask_password_salt = b''
# Place holder for logged in http users {user_id: datetime.utcnow()}
http_flask_login_session_ids = {}
# Failed login IPs are stored here, {IP: [last_failed_login_date, number_of_failed_login_attempts]}
failed_flask_logins_dic = {}

# Sensor Check-in View Variables
checkin_search_sensor_id = ""
checkin_search_sensor_installed_sensors = ""
checkin_sensor_info = ""
checkin_search_primary_log = ""
checkin_search_network_log = ""
checkin_search_sensors_log = ""
# Checkin Cached Table Variables
checkins_sensors_html_list_last_updated = "Please Refresh Information || Datetime is displayed in "
checkins_db_sensors_count = 0
checkins_db_sensors_count_from_past_days = 0
checkins_sensors_html_table_list = ""

# MQTT Subscriber Variables
mqtt_subscriber_sensors_html_list_last_updated = "Please Refresh Table Content || Datetime is displayed in "
mqtt_subscriber_sensors_count = 0
mqtt_subscriber_sensors_html_list = ""

# Running "Service" Threads
http_server_thread = CreateEmptyThreadClass()
sensor_checkin_thread = CreateEmptyThreadClass()
automatic_upgrades_thread = CreateEmptyThreadClass()
interval_recording_thread = CreateEmptyThreadClass()
report_email_thread = CreateEmptyThreadClass()
graph_email_thread = CreateEmptyThreadClass()
mini_display_thread = CreateEmptyThreadClass()
interactive_sensor_thread = CreateEmptyThreadClass()
mqtt_broker_dummy_thread = CreateEmptyThreadClass()
mqtt_publisher_thread = CreateEmptyThreadClass()
mqtt_subscriber_thread = CreateEmptyThreadClass()
weather_underground_thread = CreateEmptyThreadClass()
luftdaten_thread = CreateEmptyThreadClass()
open_sense_map_thread = CreateEmptyThreadClass()

# Running High/Low Trigger Recording Threads
trigger_high_low_cpu_temp = CreateEmptyThreadClass()
trigger_high_low_env_temp = CreateEmptyThreadClass()
trigger_high_low_pressure = CreateEmptyThreadClass()
trigger_high_low_altitude = CreateEmptyThreadClass()
trigger_high_low_humidity = CreateEmptyThreadClass()
trigger_high_low_distance = CreateEmptyThreadClass()
trigger_high_low_lumen = CreateEmptyThreadClass()
trigger_high_low_visible_colours = CreateEmptyThreadClass()
trigger_high_low_ultra_violet = CreateEmptyThreadClass()
trigger_high_low_gas = CreateEmptyThreadClass()
trigger_high_low_particulate_matter = CreateEmptyThreadClass()
trigger_high_low_accelerometer = CreateEmptyThreadClass()
trigger_high_low_magnetometer = CreateEmptyThreadClass()
trigger_high_low_gyroscope = CreateEmptyThreadClass()

# Trigger Variance threads. Re-Work? at least re-name.
trigger_variance_thread_cpu_temp = CreateEmptyThreadClass()
trigger_variance_thread_env_temp = CreateEmptyThreadClass()
trigger_variance_thread_pressure = CreateEmptyThreadClass()
trigger_variance_thread_altitude = CreateEmptyThreadClass()
trigger_variance_thread_humidity = CreateEmptyThreadClass()
trigger_variance_thread_distance = CreateEmptyThreadClass()
trigger_variance_thread_lumen = CreateEmptyThreadClass()
trigger_variance_thread_visible_ems = CreateEmptyThreadClass()
trigger_variance_thread_ultra_violet = CreateEmptyThreadClass()
trigger_variance_thread_gas = CreateEmptyThreadClass()
trigger_variance_thread_particulate_matter = CreateEmptyThreadClass()
trigger_variance_thread_accelerometer = CreateEmptyThreadClass()
trigger_variance_thread_magnetometer = CreateEmptyThreadClass()
trigger_variance_thread_gyroscope = CreateEmptyThreadClass()

# If these variables are set to True, it will restart the corresponding thread
# After the thread restarts, it sets this back to False
restart_sensor_checkin_thread = False
restart_automatic_upgrades_thread = False
restart_interval_recording_thread = False
restart_all_trigger_threads = False
restart_report_email_thread = False
restart_graph_email_thread = False
restart_mini_display_thread = False
restart_mqtt_publisher_thread = False
restart_weather_underground_thread = False
restart_luftdaten_thread = False
restart_open_sense_map_thread = False

# Checked before running OS or pip3 upgrades
# Set to False when stating a upgrade, returns to True after program restarts
sensor_ready_for_upgrade = True

# Variables to make sure the same zip is not being generated multiple times at the same time
creating_zip_main_db = False
creating_zip_checkin_db = False
creating_zip_mqtt_sub_db = False

# HTML Sensor Notes Variables
notes_total_count = 0
note_current = 1
cached_notes_as_list = []
