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
from configuration_modules import app_config_access

installed_sensors = app_config_access.installed_sensors


def check_installed_sensors_compatibility():
    if installed_sensors.pimoroni_bme680:
        installed_sensors.pimoroni_bme280 = 0
        installed_sensors.pimoroni_bmp280 = 0
    elif installed_sensors.pimoroni_bme280:
        installed_sensors.pimoroni_bmp280 = 0

    # ToDo: Add log entry with incompatible sensors and action taken
    if False:
        logger.sensors_logger.warning("Some sensor(s) are trying to use the same port, sensor(s) disabled")
        installed_sensors.update_configuration_settings_list()
        installed_sensors.save_config_to_file()
