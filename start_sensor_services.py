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
from operations_modules.app_generic_functions import check_running_as_service
from configuration_modules import app_config_access
from operations_modules.app_cached_variables_update import start_cached_variables_refresh
from sensor_recording_modules.recording_interval import start_interval_recording_server
from sensor_recording_modules.recording_high_low_triggers import start_trigger_high_low_recording_server
from sensor_recording_modules.recording_triggers import start_trigger_variance_recording_server
from operations_modules.software_checkin import start_sensor_checkins
from operations_modules.software_automatic_upgrades import start_automatic_upgrades_server
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
    try:
        # Start Interval SQL Recording
        start_interval_recording_server()
    except Exception as error:
        logger.primary_logger.critical("Interval SQL Recording Server Error: " + str(error))

    try:
        # Start High/Low Trigger SQL Recording
        start_trigger_high_low_recording_server()
    except Exception as error:
        logger.primary_logger.critical("High/Low Trigger SQL Recording Server Error: " + str(error))

    try:
        # Start Variance Trigger SQL Recording
        start_trigger_variance_recording_server()
    except Exception as error:
        logger.primary_logger.critical("Variance Trigger SQL Recording Server Error: " + str(error))

    try:
        # Start Hardware Interactions Server
        start_hardware_interactive_server()
    except Exception as error:
        logger.primary_logger.critical("Hardware Interactions Server Error: " + str(error))

    try:
        # Start Display Server
        start_display_server()
    except Exception as error:
        logger.primary_logger.critical("Display Server Error: " + str(error))

    try:
        # Start Luftdaten Online Service Server
        start_luftdaten_server()
    except Exception as error:
        logger.primary_logger.critical("Luftdaten Server Error: " + str(error))

    try:
        # Start Weather Underground Online Service Server
        start_weather_underground_server()
    except Exception as error:
        logger.primary_logger.critical("Weather Underground Server Error: " + str(error))

    try:
        # Start Open Sense Map Online Service Server
        start_open_sense_map_server()
    except Exception as error:
        logger.primary_logger.critical("Open Sense Map Server Error: " + str(error))
else:
    if running_with_root:
        logger.primary_logger.warning("No Sensors in Installed Sensors Configuration file")

try:
    # Start HTTPS Web Portal Server
    start_https_server()
except Exception as error:
    logger.primary_logger.critical("HTTPS Web Portal Server Error: " + str(error))

try:
    # Start MQTT Broker Server
    start_mqtt_broker_server()
except Exception as error:
    logger.primary_logger.critical("MQTT Broker Server Error: " + str(error))

try:
    # Start MQTT Publisher Server
    start_mqtt_publisher_server()
except Exception as error:
    logger.primary_logger.critical("MQTT Publisher Server Error: " + str(error))

try:
    # Start MQTT Subscriber Server
    start_mqtt_subscriber_server()
except Exception as error:
    logger.primary_logger.critical("MQTT Subscriber Server Error: " + str(error))

try:
    # Start the "Call Home" Check-in server.
    start_sensor_checkins()
except Exception as error:
    logger.primary_logger.critical("Checkins (Sending) Server Error: " + str(error))

try:
    # Start Reports Email Server
    start_report_email_server()
except Exception as error:
    logger.primary_logger.critical("Reports Email Server Error: " + str(error))

try:
    # Start Graph Email Server
    start_graph_email_server()
except Exception as error:
    logger.primary_logger.critical("Graph Email Server Error: " + str(error))

try:
    # Start Automatic Upgrades Server
    if check_running_as_service() and running_with_root:
        start_automatic_upgrades_server()
    else:
        log_msg = "Kootnet Sensors must be running as a service with root privileges"
        logger.primary_logger.info("Automatic Upgrades Server Disabled - " + log_msg)
except Exception as error:
    logger.primary_logger.critical("Automatic Upgrades Server Error: " + str(error))

try:
    # Updates cached variables that may change like IP and hostname every hour
    start_cached_variables_refresh()
except Exception as error:
    logger.primary_logger.critical("Cached Variables Update Server Error: " + str(error))

logger.primary_logger.debug(" -- Thread Initializations Complete")
while True:
    sleep(3600)
