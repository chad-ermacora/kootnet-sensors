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
from os import geteuid
from operations_modules import logger
from operations_modules import config_sensor_control
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import software_version
from operations_modules import config_trigger_variances
from operations_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from operations_modules.config_luftdaten import CreateLuftdatenConfiguration
from operations_modules.config_open_sense_map import CreateOpenSenseMapConfig

# Creates and loads primary configurations and variables used throughout the program.
open_sense_map_config = CreateOpenSenseMapConfig()
open_sense_map_config.update_settings_from_file()

if software_version.old_version != software_version.version and geteuid() == 0:
    logger.primary_logger.debug("Upgrade detected, Loading default values until upgrade complete")
    installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration(load_from_file=False)
    current_config = config_primary.CreatePrimaryConfiguration(load_from_file=False)
    trigger_variances = config_trigger_variances.CreateTriggerVariancesConfiguration(load_from_file=False)
    sensor_control_config = config_sensor_control.CreateSensorControlConfiguration(load_from_file=False)
    weather_underground_config = CreateWeatherUndergroundConfiguration(load_from_file=False)
    luftdaten_config = CreateLuftdatenConfiguration(load_from_file=False)
    open_sense_map_config.open_sense_map_enabled = 0
elif geteuid() != 0:
    logger.primary_logger.warning(" -- Sensors Initialization Skipped - root permissions required for sensors")
    installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration(load_from_file=False)
    current_config = config_primary.CreatePrimaryConfiguration()
    trigger_variances = config_trigger_variances.CreateTriggerVariancesConfiguration()
    sensor_control_config = config_sensor_control.CreateSensorControlConfiguration()
    weather_underground_config = CreateWeatherUndergroundConfiguration()
    luftdaten_config = CreateLuftdatenConfiguration()
    open_sense_map_config.open_sense_map_enabled = 0
else:
    logger.primary_logger.debug("Initializing configurations")
    installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration()
    current_config = config_primary.CreatePrimaryConfiguration()
    trigger_variances = config_trigger_variances.CreateTriggerVariancesConfiguration()
    sensor_control_config = config_sensor_control.CreateSensorControlConfiguration()
    weather_underground_config = CreateWeatherUndergroundConfiguration()
    luftdaten_config = CreateLuftdatenConfiguration()

# Plotly Configuration Variables
plotly_theme = "plotly_dark"
