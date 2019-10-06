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
import os
from time import sleep
from operations_modules import logger
if os.geteuid() != 0:
    log_message = "--- Failed to Start Kootnet Sensors - Elevated (root) permissions required for Hardware Access"
    logger.primary_logger.critical(log_message)
    while True:
        sleep(600)
try:
    from sensor_modules import sensor_access
except Exception as import_error_raw:
    import_error_msg = str(import_error_raw)
    log_message = "--- Failed to Start Kootnet Sensors - Problem Loading Sensor Access: "
    logger.primary_logger.critical(log_message + import_error_msg)
    while True:
        sleep(600)
from threading import Thread
from http_server import server_http
from operations_modules import program_start_checks
from operations_modules import app_config_access
from operations_modules import software_version
from operations_modules import recording_interval
from operations_modules import recording_triggers
# from operations_modules import server_display


# Ensure files, database & configurations are OK
program_start_checks.set_file_permissions()
program_start_checks.check_database_structure()

if software_version.old_version != software_version.version:
    os.system("systemctl start SensorUpgradeChecks")
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    while True:
        sleep(30)

logger.primary_logger.info(" -- Kootnet Sensor Programs Starting ...")

if app_config_access.installed_sensors.no_sensors is False:
    # Start up special Sensor Access Service like SenseHat Joystick
    sensor_access.start_special_sensor_interactive_services()

    # If there is a display installed, start up the display server
    if app_config_access.current_config.enable_display:
        if app_config_access.installed_sensors.has_display:
            pass
            # This currently only displays sensor readings every interval recording. Disabled for now.
            # display_thread = Thread(target=server_display.CreateSensorDisplay, args=[sensor_access])
            # display_thread.daemon = True
            # display_thread.start()
        else:
            logger.primary_logger.warning("No Compatible Displays Installed")

    # Start up Interval Sensor Recording
    if app_config_access.current_config.enable_interval_recording:
        interval_recording_thread = Thread(target=recording_interval.CreateIntervalRecording)
        interval_recording_thread.daemon = True
        interval_recording_thread.start()
    else:
        logger.primary_logger.debug("Interval Recording Disabled in Config")

    # Start up Trigger Sensor Recording
    if app_config_access.current_config.enable_trigger_recording:
        recording_triggers.start_trigger_recording(sensor_access)
    else:
        logger.primary_logger.debug("Trigger Recording Disabled in Config")

    # Start up all enabled Online Services
    if app_config_access.weather_underground_config.weather_underground_enabled:
        app_config_access.weather_underground_config.sensor_access = sensor_access
        wu_thread = Thread(target=app_config_access.weather_underground_config.start_weather_underground)
        wu_thread.daemon = True
        wu_thread.start()
    if app_config_access.luftdaten_config.luftdaten_enabled:
        app_config_access.luftdaten_config.sensor_access = sensor_access
        luftdaten_thread = Thread(target=app_config_access.luftdaten_config.start_luftdaten)
        luftdaten_thread.daemon = True
        luftdaten_thread.start()
    if app_config_access.open_sense_map_config.open_sense_map_enabled:
        app_config_access.open_sense_map_config.sensor_access = sensor_access
        open_sense_map_thread = Thread(target=app_config_access.open_sense_map_config.start_open_sense_map)
        open_sense_map_thread.daemon = True
        open_sense_map_thread.start()
else:
    logger.primary_logger.warning("No Sensors in Installed Sensors Configuration file")

# Make sure SSL Files are there before starting HTTPS Server
program_start_checks.check_ssl_files()
# Start the HTTP Server for remote access
https_server_and_check_thread = Thread(target=server_http.https_start_and_watch)
https_server_and_check_thread.daemon = True
https_server_and_check_thread.start()

logger.primary_logger.debug(" -- Kootnet Sensor Programs Initializations Done")
sensor_access.display_message("KS-Sensors")
while True:
    sleep(600)
