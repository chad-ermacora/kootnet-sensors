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
from time import sleep
from operations_modules import logger
from operations_modules.initialization_checks import run_program_start_checks

# Ensure files, database & configurations are OK
run_program_start_checks()

from operations_modules.app_cached_variables import running_with_root

try:
    from sensor_modules import sensor_access
except Exception as import_error_raw:
    import_error_msg = str(import_error_raw)
    log_message = "--- Failed to Start Kootnet Sensors - Problem Loading Sensor Access: "
    logger.primary_logger.critical(log_message + import_error_msg)
    while True:
        sleep(3600)
from operations_modules.software_version import start_new_version_check_server
from configuration_modules import app_config_access
from operations_modules.app_cached_variables_update import start_ip_hostname_refresh
from sensor_recording_modules.recording_interval import start_interval_recording_server
from sensor_recording_modules.recording_high_low_triggers import start_trigger_high_low_recording_server
from sensor_recording_modules.recording_triggers import start_trigger_variance_recording_server
from operations_modules.software_checkin import start_sensor_checkins
from operations_modules.server_hardware_interactive import start_hardware_interactive_server
from operations_modules.server_display import start_display_server
from operations_modules.email_server import start_report_email_server
from operations_modules.email_server import start_graph_email_server
from mqtt.server_mqtt_publisher import start_mqtt_publisher_server
from mqtt.server_mqtt_subscriber import start_mqtt_subscriber_server
from online_services_modules.luftdaten import start_luftdaten_server
from online_services_modules.weather_underground import start_weather_underground_server
from online_services_modules.open_sense_map import start_open_sense_map_server
from mqtt.server_mqtt_broker import start_mqtt_broker_server
from http_server.server_http import start_https_server

logger.primary_logger.debug(" -- Starting Kootnet Sensor Threads")
dummy_sensors_installed = app_config_access.installed_sensors.kootnet_dummy_sensor
if dummy_sensors_installed or running_with_root and app_config_access.installed_sensors.no_sensors is False:
    # Start up Interval & Trigger Sensor Recording
    start_interval_recording_server()
    start_trigger_high_low_recording_server()
    start_trigger_variance_recording_server()

    # Start up Hardware Servers for Interaction and Display
    start_hardware_interactive_server()
    start_display_server()

    # Start up all enabled Online Services
    start_mqtt_publisher_server()
    start_luftdaten_server()
    start_weather_underground_server()
    start_open_sense_map_server()
else:
    if running_with_root:
        logger.primary_logger.warning("No Sensors in Installed Sensors Configuration file")

# Start the HTTPS Web Portal Server
start_https_server()

# Start the MQTT Servers
start_mqtt_broker_server()
start_mqtt_subscriber_server()

# Start the "Call Home" Check-in server.
# Sends Sensor ID and Kootnet Version + sometimes 25 lines of the Primary and Sensors Logs
start_sensor_checkins()

# Start Version Check Server (Checks for updates)
start_new_version_check_server()

# Start Interval Emails
start_report_email_server()
start_graph_email_server()

# Updates IP and hostname cache every hour
start_ip_hostname_refresh()

logger.primary_logger.debug(" -- Thread Initializations Complete")
while True:
    sleep(3600)
