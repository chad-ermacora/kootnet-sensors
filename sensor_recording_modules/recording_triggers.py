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
from operations_modules.app_generic_functions import thread_function
from configuration_modules.app_config_access import primary_config, installed_sensors, trigger_variances
from operations_modules.app_cached_variables import database_variables
from operations_modules import app_cached_variables
from sensor_recording_modules.variance_checks import CreateTriggerVarianceThread, CreateTriggerVarianceData
from sensor_modules import sensor_access


def start_trigger_recording_server():
    if primary_config.enable_trigger_recording:
        thread_function(_trigger_recording)
    else:
        logger.primary_logger.debug("Trigger Recording Disabled in Primary Configuration")


def _trigger_recording():
    """ Starts recording all enabled sensors to the SQL database based on set trigger variances (set in config). """
    logger.primary_logger.debug("Trigger Thread(s) Starting")
    try:
        sensor_uptime_data = CreateTriggerVarianceData(sensor_access.get_uptime_minutes,
                                                       database_variables.sensor_uptime,
                                                       enabled=trigger_variances.sensor_uptime_enabled,
                                                       thread_name="Trigger - Sensor Uptime",
                                                       sensor_wait_seconds=trigger_variances.sensor_uptime_wait_seconds)
        cpu_temp_data = CreateTriggerVarianceData(sensor_access.get_cpu_temperature,
                                                  database_variables.system_temperature,
                                                  enabled=trigger_variances.cpu_temperature_enabled,
                                                  thread_name="Trigger - CPU Temperature",
                                                  variance=trigger_variances.cpu_temperature_variance,
                                                  sensor_wait_seconds=trigger_variances.cpu_temperature_wait_seconds)
        env_temp_data = CreateTriggerVarianceData(sensor_access.get_sensor_temperature,
                                                  database_variables.env_temperature,
                                                  thread_name="Trigger - ENV Temperature",
                                                  enabled=trigger_variances.env_temperature_enabled,
                                                  variance=trigger_variances.env_temperature_variance,
                                                  sensor_wait_seconds=trigger_variances.env_temperature_wait_seconds)
        pressure_data = CreateTriggerVarianceData(sensor_access.get_pressure,
                                                  database_variables.pressure,
                                                  thread_name="Trigger - Pressure",
                                                  enabled=trigger_variances.pressure_enabled,
                                                  variance=trigger_variances.pressure_variance,
                                                  sensor_wait_seconds=trigger_variances.pressure_wait_seconds)
        altitude_data = CreateTriggerVarianceData(sensor_access.get_altitude,
                                                  database_variables.altitude,
                                                  thread_name="Trigger - Altitude",
                                                  enabled=trigger_variances.altitude_enabled,
                                                  variance=trigger_variances.altitude_variance,
                                                  sensor_wait_seconds=trigger_variances.altitude_wait_seconds)
        humidity_data = CreateTriggerVarianceData(sensor_access.get_humidity,
                                                  database_variables.humidity,
                                                  thread_name="Trigger - Humidity",
                                                  enabled=trigger_variances.humidity_enabled,
                                                  variance=trigger_variances.humidity_variance,
                                                  sensor_wait_seconds=trigger_variances.humidity_wait_seconds)
        distance_data = CreateTriggerVarianceData(sensor_access.get_distance,
                                                  database_variables.distance,
                                                  thread_name="Trigger - Distance",
                                                  enabled=trigger_variances.distance_enabled,
                                                  variance=trigger_variances.distance_variance,
                                                  sensor_wait_seconds=trigger_variances.distance_wait_seconds)
        lumen_data = CreateTriggerVarianceData(sensor_access.get_lumen,
                                               database_variables.lumen,
                                               thread_name="Trigger - Lumen",
                                               enabled=trigger_variances.lumen_enabled,
                                               variance=trigger_variances.lumen_variance,
                                               sensor_wait_seconds=trigger_variances.lumen_wait_seconds)

        ems_database_sensor_variable = database_variables.red + "," + \
                                       database_variables.green + "," + \
                                       database_variables.blue + ","
        ems_variances_list = [trigger_variances.red_variance,
                              trigger_variances.green_variance,
                              trigger_variances.blue_variance]
        number_of_readings = 3
        if installed_sensors.pimoroni_as7262:
            number_of_readings = 6
            ems_database_sensor_variable = database_variables.red + "," + \
                                           database_variables.orange + "," + \
                                           database_variables.yellow + "," + \
                                           database_variables.green + "," + \
                                           database_variables.blue + "," + \
                                           database_variables.violet
            ems_variances_list = [trigger_variances.red_variance,
                                  trigger_variances.orange_variance,
                                  trigger_variances.yellow_variance,
                                  trigger_variances.green_variance,
                                  trigger_variances.blue_variance,
                                  trigger_variances.violet_variance]
        visible_ems_data = CreateTriggerVarianceData(sensor_access.get_ems_colors,
                                                     ems_database_sensor_variable,
                                                     thread_name="Trigger - Visible Electromagnetic Spectrum",
                                                     enabled=trigger_variances.colour_enabled,
                                                     variance=ems_variances_list,
                                                     sensor_wait_seconds=trigger_variances.colour_wait_seconds,
                                                     num_of_readings=number_of_readings)

        acc_database_sensor_variable = database_variables.acc_x + "," + \
                                       database_variables.acc_y + "," + \
                                       database_variables.acc_z
        acc_variances_list = [trigger_variances.accelerometer_x_variance,
                              trigger_variances.accelerometer_y_variance,
                              trigger_variances.accelerometer_z_variance]
        accelerometer_data = CreateTriggerVarianceData(sensor_access.get_accelerometer_xyz,
                                                       acc_database_sensor_variable,
                                                       thread_name="Trigger - Accelerometer",
                                                       enabled=trigger_variances.accelerometer_enabled,
                                                       variance=acc_variances_list,
                                                       sensor_wait_seconds=trigger_variances.accelerometer_wait_seconds,
                                                       num_of_readings=3)

        mag_database_sensor_variable = database_variables.mag_x + "," + \
                                       database_variables.mag_y + "," + \
                                       database_variables.mag_z
        mag_variances_list = [trigger_variances.magnetometer_x_variance,
                              trigger_variances.magnetometer_y_variance,
                              trigger_variances.magnetometer_z_variance]
        magnetometer_data = CreateTriggerVarianceData(sensor_access.get_magnetometer_xyz,
                                                      mag_database_sensor_variable,
                                                      thread_name="Trigger - Magnetometer",
                                                      enabled=trigger_variances.magnetometer_enabled,
                                                      variance=mag_variances_list,
                                                      sensor_wait_seconds=trigger_variances.magnetometer_wait_seconds,
                                                      num_of_readings=3)

        gyro_database_sensor_variable = database_variables.gyro_x + "," + \
                                        database_variables.gyro_y + "," + \
                                        database_variables.gyro_z
        gyro_variances_list = [trigger_variances.gyroscope_x_variance,
                               trigger_variances.gyroscope_y_variance,
                               trigger_variances.gyroscope_z_variance]
        gyroscope_data = CreateTriggerVarianceData(sensor_access.get_gyroscope_xyz,
                                                   gyro_database_sensor_variable,
                                                   thread_name="Trigger - Gyroscope",
                                                   enabled=trigger_variances.gyroscope_enabled,
                                                   variance=gyro_variances_list,
                                                   sensor_wait_seconds=trigger_variances.gyroscope_wait_seconds,
                                                   num_of_readings=3)

        sensor_uptime = CreateTriggerVarianceThread(sensor_uptime_data, sensor_uptime=True)
        cpu_temp = CreateTriggerVarianceThread(cpu_temp_data)
        env_temp = CreateTriggerVarianceThread(env_temp_data)
        pressure = CreateTriggerVarianceThread(pressure_data)
        altitude = CreateTriggerVarianceThread(altitude_data)
        humidity = CreateTriggerVarianceThread(humidity_data)
        distance = CreateTriggerVarianceThread(distance_data)
        lumen = CreateTriggerVarianceThread(lumen_data)
        visible_ems = CreateTriggerVarianceThread(visible_ems_data)
        accelerometer = CreateTriggerVarianceThread(accelerometer_data)
        magnetometer = CreateTriggerVarianceThread(magnetometer_data)
        gyroscope = CreateTriggerVarianceThread(gyroscope_data)

        app_cached_variables.trigger_thread_sensor_uptime = sensor_uptime.monitored_thread
        app_cached_variables.trigger_thread_cpu_temp = cpu_temp.monitored_thread
        app_cached_variables.trigger_thread_env_temp = env_temp.monitored_thread
        app_cached_variables.trigger_thread_pressure = pressure.monitored_thread
        app_cached_variables.trigger_thread_altitude = altitude.monitored_thread
        app_cached_variables.trigger_thread_humidity = humidity.monitored_thread
        app_cached_variables.trigger_thread_distance = distance.monitored_thread
        app_cached_variables.trigger_thread_lumen = lumen.monitored_thread
        app_cached_variables.trigger_thread_visible_ems = visible_ems.monitored_thread
        app_cached_variables.trigger_thread_accelerometer = accelerometer.monitored_thread
        app_cached_variables.trigger_thread_magnetometer = magnetometer.monitored_thread
        app_cached_variables.trigger_thread_gyroscope = gyroscope.monitored_thread

        logger.primary_logger.info(" -- All Enabled Trigger Recording Threads Started")
    except Exception as error:
        logger.primary_logger.error("Problem Starting Triggers: " + str(error))
