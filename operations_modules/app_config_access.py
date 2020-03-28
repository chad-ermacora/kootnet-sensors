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
from configuration_modules import config_sensor_control
from configuration_modules import config_primary
from configuration_modules import config_installed_sensors
from configuration_modules import config_trigger_variances
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration


if geteuid() != 0:
    logger.primary_logger.warning(" -- Sensors Initialization Skipped - root permissions required for sensors")
    installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration(load_from_file=False)
    current_config = config_primary.CreatePrimaryConfiguration()
    trigger_variances = config_trigger_variances.CreateTriggerVariancesConfiguration()
    sensor_control_config = config_sensor_control.CreateSensorControlConfiguration()
    weather_underground_config = CreateWeatherUndergroundConfiguration()
    luftdaten_config = CreateLuftdatenConfiguration()
    open_sense_map_config = CreateOpenSenseMapConfiguration()
else:
    logger.primary_logger.debug("Initializing configurations")
    installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration()
    current_config = config_primary.CreatePrimaryConfiguration()
    trigger_variances = config_trigger_variances.CreateTriggerVariancesConfiguration()
    sensor_control_config = config_sensor_control.CreateSensorControlConfiguration()
    weather_underground_config = CreateWeatherUndergroundConfiguration()
    luftdaten_config = CreateLuftdatenConfiguration()
    open_sense_map_config = CreateOpenSenseMapConfiguration()

# Plotly Configuration Variables
plotly_theme = "plotly_dark"
