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
from operations_modules import app_config_access
from sensor_modules import sensor_access


def scroll_interval_readings_on_display():
    logger.primary_logger.info(" -- Sensor Display Server Started")
    sensor_access.display_message("KS-Sensors Recording Started")
    sleep(app_config_access.primary_config.sleep_duration_interval)
    while True:
        message = "CPU: " + str(sensor_access.get_cpu_temperature()) + "°C "
        message += "ENV: " + str(sensor_access.get_sensor_temperature()) + "°C "
        sensor_access.display_message(message)
        sleep(app_config_access.primary_config.sleep_duration_interval)
