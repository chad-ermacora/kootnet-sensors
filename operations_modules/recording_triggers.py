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
from operations_modules.app_generic_functions import CreateMonitoredThread as CreateMT
from operations_modules import app_cached_variables as app_cv
from operations_modules.variance_checks import check_gyroscope_xyz, check_accelerometer_xyz, check_altitude, \
    check_cpu_temperature, check_distance, check_ems, check_env_temperature, check_humidity, check_lumen, \
    check_magnetometer_xyz, check_pressure, check_sensor_uptime


def start_trigger_recording():
    """ Starts recording all enabled sensors to the SQL database based on set trigger variances (set in config). """
    logger.primary_logger.debug("Trigger Thread(s) Starting")

    app_cv.trigger_thread_sensor_uptime = CreateMT(check_sensor_uptime, thread_name="Trigger - Sensor Uptime")
    app_cv.trigger_thread_cpu_temp = CreateMT(check_cpu_temperature, thread_name="Trigger - CPU Temperature")
    app_cv.trigger_thread_env_temp = CreateMT(check_env_temperature, thread_name="Trigger - Env Temperature")
    app_cv.trigger_thread_pressure = CreateMT(check_pressure, thread_name="Trigger - Pressure")
    app_cv.trigger_thread_altitude = CreateMT(check_altitude, thread_name="Trigger - Altitude")
    app_cv.trigger_thread_humidity = CreateMT(check_humidity, thread_name="Trigger - Humidity")
    app_cv.trigger_thread_distance = CreateMT(check_distance, thread_name="Trigger - Distance")
    app_cv.trigger_thread_lumen = CreateMT(check_lumen, thread_name="Trigger - Lumen")
    app_cv.trigger_thread_visible_ems = CreateMT(check_ems, thread_name="Trigger - Visible EMS")
    app_cv.trigger_thread_accelerometer = CreateMT(check_accelerometer_xyz, thread_name="Trigger - Accelerometer")
    app_cv.trigger_thread_magnetometer = CreateMT(check_magnetometer_xyz, thread_name="Trigger - Magnetometer")
    app_cv.trigger_thread_gyroscope = CreateMT(check_gyroscope_xyz, thread_name="Trigger - Gyroscope")

    logger.primary_logger.info(" -- All Enabled Trigger Recording Threads Started")
