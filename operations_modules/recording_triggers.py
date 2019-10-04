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
from threading import Thread
from operations_modules import logger
from operations_modules import variance_checks


def start_trigger_recording(sensor_access):
    """ Starts recording all enabled sensors to the SQL database based on set trigger variances (set in config). """
    logger.primary_logger.debug("Trigger Thread(s) Starting")
    sensor_variance_checks = variance_checks.CreateVarianceRecording(sensor_access)

    threads = [Thread(target=sensor_variance_checks.check_sensor_uptime),
               Thread(target=sensor_variance_checks.check_cpu_temperature),
               Thread(target=sensor_variance_checks.check_env_temperature),
               Thread(target=sensor_variance_checks.check_pressure),
               Thread(target=sensor_variance_checks.check_altitude),
               Thread(target=sensor_variance_checks.check_humidity),
               Thread(target=sensor_variance_checks.check_distance),
               Thread(target=sensor_variance_checks.check_lumen),
               Thread(target=sensor_variance_checks.check_ems),
               Thread(target=sensor_variance_checks.check_accelerometer_xyz),
               Thread(target=sensor_variance_checks.check_magnetometer_xyz),
               Thread(target=sensor_variance_checks.check_gyroscope_xyz)]

    for thread in threads:
        thread.daemon = True
        thread.start()
    logger.primary_logger.info(" -- Trigger Recording Started")
