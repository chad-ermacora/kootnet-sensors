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
from operations_modules import logger
from operations_modules import configuration_files
from operations_modules import software_version
from operations_modules import app_variables
from operations_modules import trigger_variances
from sensor_modules import sensor_variables


def get_sensor_temperature_offset():
    """
     Returns sensors Environmental temperature offset based on system board and sensor.
     This can be override in the main sensor configuration file.
    """

    if installed_sensors.raspberry_pi_3b_plus:
        sensor_temp_offset = sensor_variables.CreateRP3BPlusTemperatureOffsets()
    elif installed_sensors.raspberry_pi_zero_w:
        sensor_temp_offset = sensor_variables.CreateRPZeroWTemperatureOffsets()
    else:
        # All offsets are 0.0 for unselected or unsupported system boards
        sensor_temp_offset = sensor_variables.CreateUnknownTemperatureOffsets()

    if current_config.enable_custom_temp:
        return current_config.temperature_offset
    elif installed_sensors.pimoroni_enviro:
        return sensor_temp_offset.pimoroni_enviro
    elif installed_sensors.pimoroni_bme680:
        return sensor_temp_offset.pimoroni_bme680
    elif installed_sensors.raspberry_pi_sense_hat:
        return sensor_temp_offset.rp_sense_hat
    else:
        return 0.0


# Creates and loads primary configurations and variables used throughout the program.
if software_version.old_version != software_version.version:
    logger.primary_logger.debug("Upgrade detected, Loading default values until upgrade complete")
    installed_sensors = sensor_variables.CreateInstalledSensors()
    current_config = app_variables.CreateConfig()
    trigger_variances = trigger_variances.CreateTriggerVariances()
else:
    logger.primary_logger.debug("Initializing configurations")
    installed_sensors = configuration_files.get_installed_sensors_from_file()
    current_config = configuration_files.get_config_from_file()
    trigger_variances = trigger_variances.get_triggers_variances_from_file()
    current_config.temperature_offset = get_sensor_temperature_offset()
    # trigger_variances.init_trigger_variances(installed_sensors)

database_variables = app_variables.CreateDatabaseVariables()
command_data_separator = "[new_data_section]"
linux_os_upgrade_ready = True

# Plotly Configuration Variables
plotly_theme = "plotly_dark"

# Help lessen disk reads by caching commonly used variables
cache_hostname = ""
cache_ip = ""
cache_program_last_updated = ""
cache_reboot_count = ""
