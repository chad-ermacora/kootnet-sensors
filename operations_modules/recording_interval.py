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
import datetime
from time import sleep
from operations_modules.app_cached_variables import command_data_separator
from operations_modules import logger
from operations_modules import app_config_access
from operations_modules.app_validation_checks import valid_sensor_reading
from operations_modules import sqlite_database
from sensor_modules import sensor_access


class CreateIntervalRecording:
    logger.primary_logger.debug("Created Interval Recording Server Object")

    def __init__(self):
        self.start_interval_recording()

    @staticmethod
    def start_interval_recording():
        """ Starts recording all Interval sensor readings to the SQL database every X Seconds (set in config). """
        logger.primary_logger.info(" -- Interval Recording Started")
        while True:
            try:
                new_sensor_data = get_interval_sensor_readings()
                new_sensor_data = new_sensor_data.split(command_data_separator)
                interval_sql_execute = "INSERT OR IGNORE INTO IntervalData (" + \
                                       str(new_sensor_data[0]) + \
                                       ") VALUES (" + \
                                       str(new_sensor_data[1]) + ")"

                sqlite_database.write_to_sql_database(interval_sql_execute)
            except Exception as error:
                logger.primary_logger.error("Interval Recording Failure: " + str(error))
            sleep(app_config_access.current_config.sleep_duration_interval)


def get_interval_sensor_readings():
    """
    Returns Interval formatted sensor readings based on installed sensors.
    Format = 'CSV String Installed Sensor Types' + special separator + 'CSV String Sensor Readings'
    """

    sensor_types = [app_config_access.database_variables.all_tables_datetime]
    sensor_readings = [datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
    if app_config_access.installed_sensors.linux_system:
        sensor_types += [app_config_access.database_variables.sensor_name,
                         app_config_access.database_variables.ip,
                         app_config_access.database_variables.sensor_uptime]
        sensor_readings += [sensor_access.get_hostname(),
                            sensor_access.get_ip(),
                            sensor_access.get_uptime_minutes()]
    if app_config_access.installed_sensors.raspberry_pi:
        sensor_types.append(app_config_access.database_variables.system_temperature)
        sensor_readings.append(sensor_access.get_cpu_temperature())
    if app_config_access.installed_sensors.has_env_temperature:
        sensor_types.append(app_config_access.database_variables.env_temperature)
        sensor_types.append(app_config_access.database_variables.env_temperature_offset)
        sensor_readings.append(sensor_access.get_sensor_temperature())
        if app_config_access.current_config.enable_custom_temp:
            sensor_readings.append(app_config_access.current_config.temperature_offset)
        else:
            sensor_readings.append("0.0")
    if app_config_access.installed_sensors.has_pressure:
        sensor_types.append(app_config_access.database_variables.pressure)
        sensor_readings.append(sensor_access.get_pressure())
    if app_config_access.installed_sensors.has_altitude:
        sensor_types.append(app_config_access.database_variables.altitude)
        sensor_readings.append(sensor_access.get_altitude())
    if app_config_access.installed_sensors.has_humidity:
        sensor_types.append(app_config_access.database_variables.humidity)
        sensor_readings.append(sensor_access.get_humidity())
    if app_config_access.installed_sensors.has_distance:
        sensor_types.append(app_config_access.database_variables.distance)
        sensor_readings.append(sensor_access.get_distance())
    if app_config_access.installed_sensors.has_gas:
        gas_index = sensor_access.get_gas_resistance_index()
        gas_oxidised = sensor_access.get_gas_oxidised()
        gas_reduced = sensor_access.get_gas_reduced()
        gas_nh3 = sensor_access.get_gas_nh3()

        if valid_sensor_reading(gas_index):
            sensor_types.append(app_config_access.database_variables.gas_resistance_index)
            sensor_readings.append(gas_index)
        if valid_sensor_reading(gas_oxidised):
            sensor_types.append(app_config_access.database_variables.gas_oxidising)
            sensor_readings.append(gas_oxidised)
        if valid_sensor_reading(gas_reduced):
            sensor_types.append(app_config_access.database_variables.gas_reducing)
            sensor_readings.append(gas_reduced)
        if valid_sensor_reading(gas_nh3):
            sensor_types.append(app_config_access.database_variables.gas_nh3)
            sensor_readings.append(gas_nh3)
    if app_config_access.installed_sensors.has_particulate_matter:
        pm1_reading = sensor_access.get_particulate_matter_1()
        pm2_5_reading = sensor_access.get_particulate_matter_2_5()
        pm10_reading = sensor_access.get_particulate_matter_10()

        if valid_sensor_reading(pm1_reading):
            sensor_types.append(app_config_access.database_variables.particulate_matter_1)
            sensor_readings.append(pm1_reading)
        if valid_sensor_reading(pm2_5_reading):
            sensor_types.append(app_config_access.database_variables.particulate_matter_2_5)
            sensor_readings.append(pm2_5_reading)
        if valid_sensor_reading(pm10_reading):
            sensor_types.append(app_config_access.database_variables.particulate_matter_10)
            sensor_readings.append(pm10_reading)
    if app_config_access.installed_sensors.has_lumen:
        sensor_types.append(app_config_access.database_variables.lumen)
        sensor_readings.append(sensor_access.get_lumen())
    if app_config_access.installed_sensors.has_red:
        ems_colours = sensor_access.get_ems()

        if len(ems_colours) == 3:
            sensor_types += [app_config_access.database_variables.red,
                             app_config_access.database_variables.green,
                             app_config_access.database_variables.blue]
            sensor_readings += [ems_colours[0],
                                ems_colours[1],
                                ems_colours[2]]
        elif len(ems_colours) == 6:
            sensor_types += [app_config_access.database_variables.red,
                             app_config_access.database_variables.orange,
                             app_config_access.database_variables.yellow,
                             app_config_access.database_variables.green,
                             app_config_access.database_variables.blue,
                             app_config_access.database_variables.violet]
            sensor_readings += [ems_colours[0],
                                ems_colours[1],
                                ems_colours[2],
                                ems_colours[3],
                                ems_colours[4],
                                ems_colours[5]]
    if app_config_access.installed_sensors.has_ultra_violet:
        uva_reading = sensor_access.get_ultra_violet_a()
        uvb_reading = sensor_access.get_ultra_violet_b()

        if valid_sensor_reading(uva_reading):
            sensor_types.append(app_config_access.database_variables.ultra_violet_a)
            sensor_readings.append(sensor_access.get_ultra_violet_a())
        if valid_sensor_reading(uvb_reading):
            sensor_types.append(app_config_access.database_variables.ultra_violet_b)
            sensor_readings.append(sensor_access.get_ultra_violet_b())
    if app_config_access.installed_sensors.has_acc:
        accelerometer_readings = sensor_access.get_accelerometer_xyz()

        sensor_types += [app_config_access.database_variables.acc_x,
                         app_config_access.database_variables.acc_y,
                         app_config_access.database_variables.acc_z]
        sensor_readings += [accelerometer_readings[0],
                            accelerometer_readings[1],
                            accelerometer_readings[2]]
    if app_config_access.installed_sensors.has_mag:
        magnetometer_readings = sensor_access.get_magnetometer_xyz()

        sensor_types += [app_config_access.database_variables.mag_x,
                         app_config_access.database_variables.mag_y,
                         app_config_access.database_variables.mag_z]
        sensor_readings += [magnetometer_readings[0],
                            magnetometer_readings[1],
                            magnetometer_readings[2]]
    if app_config_access.installed_sensors.has_gyro:
        gyroscope_readings = sensor_access.get_gyroscope_xyz()

        sensor_types += [app_config_access.database_variables.gyro_x,
                         app_config_access.database_variables.gyro_y,
                         app_config_access.database_variables.gyro_z]
        sensor_readings += [gyroscope_readings[0],
                            gyroscope_readings[1],
                            gyroscope_readings[2]]

    return_interval_data = _list_to_csv_string(sensor_types) + \
                           command_data_separator + \
                           _list_to_csv_string_quoted(sensor_readings)
    return return_interval_data


def _list_to_csv_string(list_to_add):
    if len(list_to_add) > 0:
        text_string = ""
        for entry in list_to_add:
            text_string += str(entry) + ","
        return text_string[:-1]
    return ""


def _list_to_csv_string_quoted(list_to_add):
    if len(list_to_add) > 0:
        text_string = ""
        for entry in list_to_add:
            text_string += "'" + str(entry) + "',"
        return text_string[:-1]
    return ""
