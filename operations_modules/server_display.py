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


class CreateSensorDisplay:
    logger.primary_logger.debug("Starting Display Server")

    def __init__(self, sensor_access):
        self.sensor_access = sensor_access
        self.scroll_interval_readings_on_display()

    def scroll_interval_readings_on_display(self):
        logger.primary_logger.info("Display Server Started")
        while True:
            message = "CPU: " + str(int(self.sensor_access.get_cpu_temperature())) + "°C "
            message += "ENV: " + str(int(self.sensor_access.get_sensor_temperature())) + "°C "
            self.sensor_access.display_message(message)
            sleep(app_config_access.current_config.sleep_duration_interval)
