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
import requests
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import thread_function
from operations_modules.software_version import version
from configuration_modules import app_config_access
from sensor_modules import sensor_access

checkin_wait_time_sec = 86400


class CreateCheckinServer:
    def __init__(self):
        logger.primary_logger.debug(" -- Sensor Checkin Server Started")
        sleep(30)

        previous_primary_logs = ""
        previous_sensors_logs = ""
        previous_installed_sensors = ""
        while True:
            try:
                current_installed_sensors = app_config_access.installed_sensors.get_installed_names_str()
                current_primary_logs = logger.get_sensor_log(file_locations.primary_log, max_lines=40)
                current_sensors_logs = logger.get_sensor_log(file_locations.sensors_log, max_lines=40)
                if current_installed_sensors == previous_installed_sensors:
                    current_installed_sensors = ""
                else:
                    previous_installed_sensors = current_installed_sensors

                if current_primary_logs == previous_primary_logs:
                    current_primary_logs = ""
                else:
                    previous_primary_logs = current_primary_logs

                if current_sensors_logs == previous_sensors_logs:
                    current_sensors_logs = ""
                else:
                    previous_sensors_logs = current_sensors_logs

                requests.post(url=app_config_access.primary_config.checkin_url, timeout=5, verify=False,
                              data={"checkin_id": app_config_access.primary_config.sensor_checkin_id,
                                    "program_version": version,
                                    "sensor_uptime": sensor_access.get_uptime_minutes(),
                                    "installed_sensors": current_installed_sensors,
                                    "primary_log": current_primary_logs,
                                    "sensor_log": current_sensors_logs})
            except Exception as error:
                logger.network_logger.debug("Failed to send Checkin ID: " + str(error))
            sleep(checkin_wait_time_sec)


def start_sensor_checkin_server():
    thread_function(CreateCheckinServer)
