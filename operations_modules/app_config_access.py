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
from operations_modules import logger
from operations_modules import config_sensor_control
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import sqlite_database
from operations_modules import software_version
from operations_modules import config_trigger_variances
from operations_modules.online_services.weather_underground import CreateWeatherUndergroundConfig
from operations_modules.online_services.luftdaten import CreateLuftdatenConfig
from operations_modules.online_services.open_sense_map import CreateOpenSenseMapConfig

# Creates and loads primary configurations and variables used throughout the program.
sensor_control_config = config_sensor_control.CreateSensorControlConfig()
weather_underground_config = CreateWeatherUndergroundConfig()
luftdaten_config = CreateLuftdatenConfig()
open_sense_map_config = CreateOpenSenseMapConfig()
if software_version.old_version != software_version.version:
    logger.primary_logger.debug("Upgrade detected, Loading default values until upgrade complete")
    installed_sensors = config_installed_sensors.CreateInstalledSensors()
    current_config = config_primary.CreateConfig()
    trigger_variances = config_trigger_variances.CreateTriggerVariances()
else:
    logger.primary_logger.debug("Initializing configurations")
    installed_sensors = config_installed_sensors.get_installed_sensors_from_file()
    installed_sensors.raspberry_pi_name = installed_sensors.get_raspberry_pi_model()
    current_config = config_primary.get_config_from_file()
    trigger_variances = config_trigger_variances.get_triggers_variances_from_file()
    sensor_control_config.set_from_disk()
    weather_underground_config.update_settings_from_file()
    luftdaten_config.update_settings_from_file()
    open_sense_map_config.update_settings_from_file()

current_platform = system()
database_variables = sqlite_database.CreateDatabaseVariables()
command_data_separator = "[new_data_section]"
linux_os_upgrade_ready = True

# Online Service Variables
wu_thread_running = False
luftdaten_thread_running = False
open_sense_map_thread_running = False

# Plotly Configuration Variables
plotly_theme = "plotly_dark"

# Sensor Control Variables
creating_the_reports_zip = False
creating_the_big_zip = False
creating_databases_zip = False
creating_logs_zip = False

# Flask Login Variables
http_flask_user = "Kootnet"
http_flask_password = "sensors"
