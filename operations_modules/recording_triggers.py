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
from operations_modules import app_generic_functions
from operations_modules import variance_checks


def start_trigger_recording():
    """ Starts recording all enabled sensors to the SQL database based on set trigger variances (set in config). """
    logger.primary_logger.debug("Trigger Thread(s) Starting")

    function_and_name = [[variance_checks.check_sensor_uptime, "Trigger - Sensor Uptime"],
                         [variance_checks.check_cpu_temperature, "Trigger - CPU Temperature"],
                         [variance_checks.check_env_temperature, "Trigger - Env Temperature"],
                         [variance_checks.check_pressure, "Trigger - Pressure"],
                         [variance_checks.check_altitude, "Trigger - Altitude"],
                         [variance_checks.check_humidity, "Trigger - Humidity"],
                         [variance_checks.check_distance, "Trigger - Distance"],
                         [variance_checks.check_lumen, "Trigger - Lumen"],
                         [variance_checks.check_ems, "Trigger - Visible EMS"],
                         [variance_checks.check_accelerometer_xyz, "Trigger - Accelerometer"],
                         [variance_checks.check_magnetometer_xyz, "Trigger - Magnetometer"],
                         [variance_checks.check_gyroscope_xyz, "Trigger - Gyroscope"]]

    for trigger_monitor in function_and_name:
        app_generic_functions.CreateMonitoredThread(trigger_monitor[0], thread_name=trigger_monitor[1])
    logger.primary_logger.info(" -- Trigger Recording Started")
    sleep(3600)
