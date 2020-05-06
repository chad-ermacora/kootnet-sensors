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
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from operations_modules import sqlite_database
from operations_modules.app_validation_checks import valid_sensor_reading
from sensor_modules import sensor_access


class CreateHasSensorVariables:
    def __init__(self):
        self._update_has_sensor_variables()

    def _update_has_sensor_variables(self):
        self._set_all_has_sensor_states(0)
        if app_config_access.installed_sensors.kootnet_dummy_sensor:
            self._set_all_has_sensor_states(1)
            self.has_real_time_clock = 0
        if app_config_access.installed_sensors.raspberry_pi:
            self.has_cpu_temperature = 1
        if app_config_access.installed_sensors.raspberry_pi_sense_hat:
            self.has_display = 1
            self.has_env_temperature = 1
            self.has_pressure = 1
            self.has_humidity = 1
            self.has_acc = 1
            self.has_mag = 1
            self.has_gyro = 1
        if app_config_access.installed_sensors.pimoroni_bh1745:
            self.has_lumen = 1
            self.has_red = 1
            self.has_green = 1
            self.has_blue = 1
        if app_config_access.installed_sensors.pimoroni_as7262:
            self.has_red = 1
            self.has_orange = 1
            self.has_yellow = 1
            self.has_green = 1
            self.has_blue = 1
            self.has_violet = 1
        if app_config_access.installed_sensors.pimoroni_bmp280:
            self.has_env_temperature = 1
            self.has_pressure = 1
            self.has_altitude = 1
        if app_config_access.installed_sensors.pimoroni_bme680:
            self.has_env_temperature = 1
            self.has_pressure = 1
            self.has_humidity = 1
            self.has_gas = 1
        if app_config_access.installed_sensors.pimoroni_enviro:
            self.has_env_temperature = 1
            self.has_pressure = 1
            self.has_lumen = 1
            self.has_red = 1
            self.has_green = 1
            self.has_blue = 1
            self.has_acc = 1
            self.has_mag = 1
        if app_config_access.installed_sensors.pimoroni_enviroplus:
            self.has_display = 1
            self.has_env_temperature = 1
            self.has_pressure = 1
            self.has_altitude = 1
            self.has_humidity = 1
            self.has_distance = 1
            self.has_lumen = 1
            self.has_gas = 1
        if app_config_access.installed_sensors.pimoroni_pms5003:
            self.has_particulate_matter = 1
        if app_config_access.installed_sensors.pimoroni_lsm303d:
            self.has_acc = 1
            self.has_mag = 1
        if app_config_access.installed_sensors.pimoroni_icm20948:
            self.has_acc = 1
            self.has_mag = 1
            self.has_gyro = 1
        if app_config_access.installed_sensors.pimoroni_vl53l1x:
            self.has_distance = 1
        if app_config_access.installed_sensors.pimoroni_ltr_559:
            self.has_lumen = 1
            self.has_distance = 1
        if app_config_access.installed_sensors.pimoroni_veml6075:
            self.has_ultra_violet = 1
            self.has_ultra_violet_comparator = 1
        if app_config_access.installed_sensors.pimoroni_matrix_11x7:
            self.has_display = 1
        if app_config_access.installed_sensors.pimoroni_st7735:
            self.has_display = 1
        if app_config_access.installed_sensors.pimoroni_mono_oled_luma:
            self.has_display = 1
        if app_config_access.installed_sensors.pimoroni_msa301:
            self.has_acc = 1
        if app_config_access.installed_sensors.pimoroni_sgp30:
            self.has_gas = 1
        if app_config_access.installed_sensors.pimoroni_mcp9600:
            self.has_env_temperature = 1

    def _set_all_has_sensor_states(self, set_sensor_state_as):
        self.has_display = set_sensor_state_as
        self.has_real_time_clock = set_sensor_state_as
        self.has_cpu_temperature = set_sensor_state_as
        self.has_env_temperature = set_sensor_state_as
        self.has_pressure = set_sensor_state_as
        self.has_altitude = set_sensor_state_as
        self.has_humidity = set_sensor_state_as
        self.has_distance = set_sensor_state_as
        self.has_gas = set_sensor_state_as
        self.has_particulate_matter = set_sensor_state_as
        self.has_ultra_violet = set_sensor_state_as
        self.has_ultra_violet_comparator = set_sensor_state_as
        self.has_lumen = set_sensor_state_as
        self.has_red = set_sensor_state_as
        self.has_orange = set_sensor_state_as
        self.has_yellow = set_sensor_state_as
        self.has_green = set_sensor_state_as
        self.has_blue = set_sensor_state_as
        self.has_violet = set_sensor_state_as
        self.has_acc = set_sensor_state_as
        self.has_mag = set_sensor_state_as
        self.has_gyro = set_sensor_state_as


def start_interval_recording():
    """ Starts recording all sensor readings to the SQL database every X Seconds (set in config). """
    logger.primary_logger.info(" -- Interval Recording Started")
    while True:
        try:
            new_sensor_data = get_interval_sensor_readings()
            new_sensor_data = new_sensor_data.split(app_cached_variables.command_data_separator)
            interval_sql_execute_part1 = "INSERT OR IGNORE INTO IntervalData (" + str(new_sensor_data[0])
            interval_sql_execute_part2 = ") VALUES (" + str(new_sensor_data[1]) + ")"
            sqlite_database.write_to_sql_database(interval_sql_execute_part1 + interval_sql_execute_part2)
        except Exception as error:
            logger.primary_logger.error("Interval Recording Failure: " + str(error))
        sleep(app_config_access.primary_config.sleep_duration_interval)


def get_interval_sensor_readings():
    """
    Returns Interval formatted sensor readings based on installed sensors.
    Format = 'CSV String Installed Sensor Types' + special separator + 'CSV String Sensor Readings'
    """

    sensor_types = [app_cached_variables.database_variables.all_tables_datetime]
    sensor_readings = [datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
    if app_config_access.installed_sensors.linux_system:
        sensor_types += [app_cached_variables.database_variables.sensor_name,
                         app_cached_variables.database_variables.ip,
                         app_cached_variables.database_variables.sensor_uptime]
        sensor_readings += [sensor_access.get_hostname(),
                            sensor_access.get_ip(),
                            sensor_access.get_uptime_minutes()]
    if app_config_access.installed_sensors.raspberry_pi:
        sensor_types.append(app_cached_variables.database_variables.system_temperature)
        sensor_readings.append(sensor_access.get_cpu_temperature())
    if available_sensors.has_env_temperature:
        sensor_types.append(app_cached_variables.database_variables.env_temperature)
        sensor_types.append(app_cached_variables.database_variables.env_temperature_offset)
        sensor_readings.append(sensor_access.get_sensor_temperature())
        if app_config_access.primary_config.enable_custom_temp:
            sensor_readings.append(app_config_access.primary_config.temperature_offset)
        else:
            sensor_readings.append("0.0")
    if available_sensors.has_pressure:
        sensor_types.append(app_cached_variables.database_variables.pressure)
        sensor_readings.append(sensor_access.get_pressure())
    if available_sensors.has_altitude:
        sensor_types.append(app_cached_variables.database_variables.altitude)
        sensor_readings.append(sensor_access.get_altitude())
    if available_sensors.has_humidity:
        sensor_types.append(app_cached_variables.database_variables.humidity)
        sensor_readings.append(sensor_access.get_humidity())
    if available_sensors.has_distance:
        sensor_types.append(app_cached_variables.database_variables.distance)
        sensor_readings.append(sensor_access.get_distance())
    if available_sensors.has_gas:
        gas_index = sensor_access.get_gas_resistance_index()
        gas_oxidised = sensor_access.get_gas_oxidised()
        gas_reduced = sensor_access.get_gas_reduced()
        gas_nh3 = sensor_access.get_gas_nh3()

        if valid_sensor_reading(gas_index):
            sensor_types.append(app_cached_variables.database_variables.gas_resistance_index)
            sensor_readings.append(gas_index)
        if valid_sensor_reading(gas_oxidised):
            sensor_types.append(app_cached_variables.database_variables.gas_oxidising)
            sensor_readings.append(gas_oxidised)
        if valid_sensor_reading(gas_reduced):
            sensor_types.append(app_cached_variables.database_variables.gas_reducing)
            sensor_readings.append(gas_reduced)
        if valid_sensor_reading(gas_nh3):
            sensor_types.append(app_cached_variables.database_variables.gas_nh3)
            sensor_readings.append(gas_nh3)
    if available_sensors.has_particulate_matter:
        pm1_reading = sensor_access.get_particulate_matter_1()
        pm2_5_reading = sensor_access.get_particulate_matter_2_5()
        pm10_reading = sensor_access.get_particulate_matter_10()

        if valid_sensor_reading(pm1_reading):
            sensor_types.append(app_cached_variables.database_variables.particulate_matter_1)
            sensor_readings.append(pm1_reading)
        if valid_sensor_reading(pm2_5_reading):
            sensor_types.append(app_cached_variables.database_variables.particulate_matter_2_5)
            sensor_readings.append(pm2_5_reading)
        if valid_sensor_reading(pm10_reading):
            sensor_types.append(app_cached_variables.database_variables.particulate_matter_10)
            sensor_readings.append(pm10_reading)
    if available_sensors.has_lumen:
        sensor_types.append(app_cached_variables.database_variables.lumen)
        sensor_readings.append(sensor_access.get_lumen())
    if available_sensors.has_red:
        ems_colours = sensor_access.get_ems()

        if len(ems_colours) == 3:
            sensor_types += [app_cached_variables.database_variables.red,
                             app_cached_variables.database_variables.green,
                             app_cached_variables.database_variables.blue]
            sensor_readings += [ems_colours[0],
                                ems_colours[1],
                                ems_colours[2]]
        elif len(ems_colours) == 6:
            sensor_types += [app_cached_variables.database_variables.red,
                             app_cached_variables.database_variables.orange,
                             app_cached_variables.database_variables.yellow,
                             app_cached_variables.database_variables.green,
                             app_cached_variables.database_variables.blue,
                             app_cached_variables.database_variables.violet]
            sensor_readings += [ems_colours[0],
                                ems_colours[1],
                                ems_colours[2],
                                ems_colours[3],
                                ems_colours[4],
                                ems_colours[5]]
    if available_sensors.has_ultra_violet:
        uva_reading = sensor_access.get_ultra_violet_a()
        uvb_reading = sensor_access.get_ultra_violet_b()

        if valid_sensor_reading(uva_reading):
            sensor_types.append(app_cached_variables.database_variables.ultra_violet_a)
            sensor_readings.append(sensor_access.get_ultra_violet_a())
        if valid_sensor_reading(uvb_reading):
            sensor_types.append(app_cached_variables.database_variables.ultra_violet_b)
            sensor_readings.append(sensor_access.get_ultra_violet_b())
    if available_sensors.has_acc:
        accelerometer_readings = sensor_access.get_accelerometer_xyz()

        sensor_types += [app_cached_variables.database_variables.acc_x,
                         app_cached_variables.database_variables.acc_y,
                         app_cached_variables.database_variables.acc_z]
        sensor_readings += [accelerometer_readings[0],
                            accelerometer_readings[1],
                            accelerometer_readings[2]]
    if available_sensors.has_mag:
        magnetometer_readings = sensor_access.get_magnetometer_xyz()

        sensor_types += [app_cached_variables.database_variables.mag_x,
                         app_cached_variables.database_variables.mag_y,
                         app_cached_variables.database_variables.mag_z]
        sensor_readings += [magnetometer_readings[0],
                            magnetometer_readings[1],
                            magnetometer_readings[2]]
    if available_sensors.has_gyro:
        gyroscope_readings = sensor_access.get_gyroscope_xyz()

        sensor_types += [app_cached_variables.database_variables.gyro_x,
                         app_cached_variables.database_variables.gyro_y,
                         app_cached_variables.database_variables.gyro_z]
        sensor_readings += [gyroscope_readings[0],
                            gyroscope_readings[1],
                            gyroscope_readings[2]]

    return_interval_data = _list_to_csv_string(sensor_types) + \
                           app_cached_variables.command_data_separator + \
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


available_sensors = CreateHasSensorVariables()
