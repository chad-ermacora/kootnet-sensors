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
from operations_modules import program_start_checks
# Ensure files, database & configurations are OK
program_start_checks.run_program_start_checks()
running_with_root = False
if os.geteuid() == 0:
    running_with_root = True
try:
    from sensor_modules import sensor_access
except Exception as import_error_raw:
    import_error_msg = str(import_error_raw)
    log_message = "--- Failed to Start Kootnet Sensors - Problem Loading Sensor Access: "
    logger.primary_logger.critical(log_message + import_error_msg)
    while True:
        sleep(3600)
from http_server import server_http
from operations_modules.app_generic_functions import CreateMonitoredThread, thread_function
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from operations_modules import server_display
from sensor_recording_modules import recording_interval
from sensor_recording_modules import recording_triggers
from online_services_modules.luftdaten import start_luftdaten
from online_services_modules.weather_underground import start_weather_underground as start_wu
from online_services_modules.open_sense_map import start_open_sense_map

logger.primary_logger.info(" -- Kootnet Sensor Programs Starting ...")
if running_with_root and app_config_access.installed_sensors.no_sensors is False:
    # Start up special Sensor Access Service like SenseHat Joystick
    sensor_access.start_special_sensor_interactive_services()

    # If there is a display installed, start up the display server
    if app_config_access.current_config.enable_display:
        if app_config_access.installed_sensors.has_display:
            pass
            # This currently only displays sensor readings every interval recording. Disabled for now.
            text_name = "Display"
            function = server_display.scroll_interval_readings_on_display
            app_cached_variables.mini_display_thread = CreateMonitoredThread(function, thread_name=text_name)
        else:
            logger.primary_logger.warning("No Compatible Displays Installed")

    # Start up Interval Sensor Recording
    if app_config_access.current_config.enable_interval_recording:
        text_name = "Interval Recording"
        function = recording_interval.start_interval_recording
        app_cached_variables.interval_recording_thread = CreateMonitoredThread(function, thread_name=text_name)
    else:
        logger.primary_logger.debug("Interval Recording Disabled in Config")

    # Start up Trigger Sensor Recording
    if app_config_access.current_config.enable_trigger_recording:
        app_cached_variables.trigger_recording_thread = thread_function(recording_triggers.start_trigger_recording)
    else:
        logger.primary_logger.debug("Trigger Recording Disabled in Config")

    # Start up all enabled Online Services
    if app_config_access.weather_underground_config.weather_underground_enabled:
        text_name = "Weather Underground"
        app_cached_variables.weather_underground_thread = CreateMonitoredThread(start_wu, thread_name=text_name)
    if app_config_access.luftdaten_config.luftdaten_enabled:
        text_name = "Luftdaten"
        app_cached_variables.luftdaten_thread = CreateMonitoredThread(start_luftdaten, thread_name=text_name)
    if app_config_access.open_sense_map_config.open_sense_map_enabled:
        text_name = "Open Sense Map"
        app_cached_variables.open_sense_map_thread = CreateMonitoredThread(start_open_sense_map, thread_name=text_name)
    sensor_access.display_message("KS-Sensors Recording Started")
else:
    if running_with_root:
        logger.primary_logger.warning("No Sensors in Installed Sensors Configuration file")

# Start the HTTP Server for remote access
thread_function(server_http.https_start_and_watch)
logger.primary_logger.debug(" -- Kootnet Sensor Programs Initializations Done")
while True:
    sleep(3600)
