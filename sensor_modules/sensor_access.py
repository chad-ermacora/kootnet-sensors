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
import os
import math
import psutil
import time
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables import command_data_separator, database_variables as db_v, \
    current_platform, bash_commands
from operations_modules import sqlite_database
from configuration_modules import app_config_access
from sensor_modules import sensors_initialization

sensors_direct = sensors_initialization.CreateSensorAccess(first_start=True)


def get_ram_space(return_type=0):
    """
    return_type options: 0 = Free Space, 1 = Used Space, 2 = Total Space, 3 = Percent Space Used
    Default option = 0, all returns are in GB(s)
    """
    ram_space = None
    try:
        if return_type == 0:
            ram_space = psutil.virtual_memory().free
        elif return_type == 1:
            ram_space = psutil.virtual_memory().used
        elif return_type == 2:
            ram_space = app_cached_variables.total_ram_memory
        elif return_type == 3:
            ram_space = psutil.virtual_memory().percent

        if ram_space is not None:
            ram_space = round((ram_space / 1024 / 1024 / 1024), 3)
    except Exception as error:
        logger.primary_logger.warning("Get RAM Space: " + str(error))
    return ram_space


def get_disk_space(return_type=0):
    """
    return_type options: 0 = Free Space, 1 = Used Space, 2 = Total Space, 3 = Percent Space Used
    Default option = 0, all returns are in GB(s)
    """
    disk_space = None
    try:
        if return_type == 0:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).free
        elif return_type == 1:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).used
        elif return_type == 2:
            disk_space = app_cached_variables.total_disk_space
        elif return_type == 3:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).percent

        if disk_space is not None:
            disk_space = round((disk_space / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.primary_logger.warning("Get Disk Space: " + str(error))
    return disk_space


def get_system_datetime():
    """ Returns System DateTime in format YYYY-MM-DD HH:MM - timezone as a String. """
    return time.strftime("%Y-%m-%d %H:%M - %Z")


def get_uptime_minutes():
    """ Returns System UpTime in Minutes as an Integer. """
    if current_platform == "Linux":
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            return int(uptime_seconds / 60)
        except Exception as error:
            logger.sensors_logger.warning("Get Sensor Up Time - Failed: " + str(error))
    return None


def get_db_first_last_date():
    """ Returns First and Last recorded date in the SQL Database as a String. """
    sql_query = "SELECT Min(" + str(db_v.all_tables_datetime) + ") AS First, Max(" + \
                str(db_v.all_tables_datetime) + ") AS Last FROM " + str(db_v.table_interval)

    textbox_db_dates = "DataBase Error"
    try:
        db_datetime_column = sqlite_database.sql_execute_get_data(sql_query)
        for item in db_datetime_column:
            textbox_db_dates = item[0] + " < -- > " + item[1]
    except Exception as error:
        logger.sensors_logger.error("Get First & Last DateTime from Interval Recording DB Failed: " + str(error))
    return textbox_db_dates


def get_sensors_latency():
    """ Returns sensors latency in seconds as a dictionary. """
    sensor_function_list = [
        get_cpu_temperature, get_environment_temperature, get_pressure, get_altitude, get_humidity,
        get_distance, get_gas, get_particulate_matter, get_lumen, get_ems_colors,
        get_ultra_violet, get_accelerometer_xyz, get_magnetometer_xyz, get_gyroscope_xyz
    ]
    sensor_names_list = [
        "cpu_temperature", "environment_temperature", "pressure", "altitude", "humidity",
        "distance", "gas", "particulate_matter", "lumen", "colours", "ultra_violet",
        "accelerometer_xyz", "magnetometer_xyz", "gyroscope_xyz"
    ]

    sensor_latency_dic = {}
    for sensor_function, sensor_name in zip(sensor_function_list, sensor_names_list):
        latency = sensor_function(get_latency=True)
        if latency is not None:
            sensor_latency_dic[sensor_name] = round(latency, 6)
    return sensor_latency_dic


def _get_sensor_latency(sensor_function):
    try:
        start_time = time.time()
        sensor_reading = sensor_function()
        end_time = time.time()
        if sensor_reading is None:
            return None
        return float(end_time - start_time)
    except Exception as error:
        logger.sensors_logger.warning("Problem getting sensor latency: " + str(error))
        return 0.0


def get_all_available_sensor_readings(skip_system_info=False):
    """ Returns ALL sensor readings in a dictionary. """
    utc_0_date_time_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    env_temp_raw = get_environment_temperature(temperature_correction=False)
    env_temp_corrected = get_environment_temperature()

    temp_correction = 0
    if env_temp_raw is not None and env_temp_corrected is not None:
        env_temp_raw = env_temp_raw[db_v.env_temperature]
        env_temp_corrected = env_temp_corrected[db_v.env_temperature]
        temp_correction = round((env_temp_corrected - env_temp_raw), 5)

    if skip_system_info:
        return_dictionary = {}
    else:
        return_dictionary = {db_v.all_tables_datetime: utc_0_date_time_now,
                             db_v.sensor_name: app_cached_variables.hostname,
                             db_v.ip: app_cached_variables.ip,
                             db_v.sensor_uptime: get_uptime_minutes(),
                             db_v.env_temperature_offset: temp_correction}

    functions_list = [get_cpu_temperature, get_environment_temperature, get_pressure, get_altitude, get_humidity,
                      get_dew_point, get_distance, get_gas, get_particulate_matter, get_lumen, get_ems_colors,
                      get_ultra_violet, get_accelerometer_xyz, get_magnetometer_xyz, get_gyroscope_xyz]

    for function in functions_list:
        try:
            readings_dic = function()
            if readings_dic is not None:
                return_dictionary.update(readings_dic)
        except Exception as error:
            logger.primary_logger.error("Get all sensor readings Failure: " + str(error))
    return return_dictionary


def get_cpu_temperature(get_latency=False):
    """ Returns sensors CPU temperature in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_cpu_temperature)
    if app_config_access.installed_sensors.raspberry_pi:
        temperature = sensors_direct.raspberry_pi_a.cpu_temperature()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.cpu_temperature()
    else:
        return None
    return {db_v.system_temperature: temperature}


def get_environment_temperature(temperature_correction=True, get_latency=False):
    """ Returns sensors Environmental temperature in a dictionary. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        if get_latency:
            return sensors_direct.pimoroni_bme680_a.sensor_latency
        temperature = sensors_direct.pimoroni_bme680_a.temperature()
    elif get_latency:
        return _get_sensor_latency(get_environment_temperature)
    elif app_config_access.installed_sensors.pimoroni_enviro:
        temperature = sensors_direct.pimoroni_enviro_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        temperature = sensors_direct.pimoroni_enviro2_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        temperature = sensors_direct.pimoroni_enviroplus_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_mcp9600:
        temperature = sensors_direct.pimoroni_mcp9600_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        temperature = sensors_direct.pimoroni_bmp280_a.temperature()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        temperature = sensors_direct.rp_sense_hat_a.temperature()
    elif app_config_access.installed_sensors.w1_therm_sensor:
        temperature = sensors_direct.w1_therm_sensor_a.temperature()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.temperature()
    else:
        return None

    if temperature_correction:
        temperature = _apply_environment_temperature_correction(temperature)
    return {db_v.env_temperature: temperature}


def _apply_environment_temperature_correction(temperature):
    enable_custom_temp = app_config_access.primary_config.enable_custom_temp
    temperature_offset = app_config_access.primary_config.temperature_offset
    new_temp = temperature
    if enable_custom_temp:
        try:
            new_temp = round(temperature + temperature_offset, 6)
        except Exception as error:
            logger.sensors_logger.warning("Invalid Environment Temperature Offset")
            logger.sensors_logger.debug(str(error))

    cpu_temp = get_cpu_temperature()
    enable_temperature_comp_factor = app_config_access.primary_config.enable_temperature_comp_factor
    temperature_comp_factor = app_config_access.primary_config.temperature_comp_factor
    if enable_temperature_comp_factor and cpu_temp is not None and temperature_comp_factor != 0:
        try:
            cpu_temp = cpu_temp[db_v.system_temperature]
            new_temp = round(new_temp - ((cpu_temp - new_temp) * temperature_comp_factor), 6)
        except Exception as error:
            logger.sensors_logger.warning("Invalid Environment Temperature Factor")
            logger.sensors_logger.debug(str(error))
    return new_temp


def get_pressure(get_latency=False):
    """ Returns sensors pressure in a dictionary. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        if get_latency:
            return sensors_direct.pimoroni_bme680_a.sensor_latency
        pressure = sensors_direct.pimoroni_bme680_a.pressure()
    elif get_latency:
        return _get_sensor_latency(get_pressure)
    elif app_config_access.installed_sensors.pimoroni_enviro:
        pressure = sensors_direct.pimoroni_enviro_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        pressure = sensors_direct.pimoroni_enviro2_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        pressure = sensors_direct.pimoroni_enviroplus_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        pressure = sensors_direct.pimoroni_bmp280_a.pressure()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        pressure = sensors_direct.rp_sense_hat_a.pressure()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pressure = sensors_direct.dummy_sensors.pressure()
    else:
        return None
    return {db_v.pressure: pressure}


def get_altitude(qnh=1013.25, get_latency=False):
    """ Returns sensors altitude in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_altitude)
    round_decimal_to = 5
    temperature = get_environment_temperature()
    pressure = get_pressure()
    if pressure is None or temperature is None:
        return None

    try:
        temperature = temperature[db_v.env_temperature]
        pressure = pressure[db_v.pressure]
        var_altitude = ((pow((qnh / pressure), (1.0 / 5.257)) - 1) * (temperature + 273.15)) / 0.0065
    except Exception as error:
        var_altitude = 0.0
        logger.sensors_logger.error("Altitude Calculation using Temperature & Pressure Failed: " + str(error))

    return {db_v.altitude: round(var_altitude, round_decimal_to)}


def get_humidity(get_latency=False):
    """ Returns sensors humidity in a dictionary. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        if get_latency:
            return sensors_direct.pimoroni_bme680_a.sensor_latency
        humidity = sensors_direct.pimoroni_bme680_a.humidity()
    elif get_latency:
        return _get_sensor_latency(get_humidity)
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        humidity = sensors_direct.pimoroni_enviro2_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        humidity = sensors_direct.pimoroni_enviroplus_a.humidity()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        humidity = sensors_direct.rp_sense_hat_a.humidity()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        humidity = sensors_direct.dummy_sensors.humidity()
    else:
        return None
    return {db_v.humidity: humidity}


def get_dew_point(get_latency=False):
    """ Returns estimated dew point based on Temperature and Humidity in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_dew_point)
    variable_a = 17.27
    variable_b = 237.7

    env_temp = get_environment_temperature()
    humidity = get_humidity()
    if env_temp is None or humidity is None:
        return None

    try:
        env_temp = env_temp[db_v.env_temperature]
        humidity = humidity[db_v.humidity]
        alpha = ((variable_a * env_temp) / (variable_b + env_temp)) + math.log(humidity / 100.0)
        dew_point = (variable_b * alpha) / (variable_a - alpha)
    except Exception as error:
        logger.sensors_logger.error("Unable to calculate dew point: " + str(error))
        dew_point = 0.0
    return {db_v.dew_point: round(dew_point, 5)}


def get_distance(get_latency=False):
    """ Returns sensors distance in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_distance)
    if app_config_access.installed_sensors.pimoroni_enviro2:
        distance = sensors_direct.pimoroni_enviro2_a.distance()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        distance = sensors_direct.pimoroni_enviroplus_a.distance()
    elif app_config_access.installed_sensors.pimoroni_vl53l1x:
        distance = sensors_direct.pimoroni_vl53l1x_a.distance()
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        distance = sensors_direct.pimoroni_ltr_559_a.distance()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        distance = sensors_direct.dummy_sensors.distance()
    else:
        return None
    return {db_v.distance: distance}


def get_gas(get_latency=False):
    """ Returns sensors gas readings in a dictionary. """
    gas_dic = {}
    if app_config_access.installed_sensors.pimoroni_bme680:
        if get_latency:
            return sensors_direct.pimoroni_bme680_a.sensor_latency
        gas_reading = sensors_direct.pimoroni_bme680_a.gas_resistance_index()
        gas_dic.update({db_v.gas_resistance_index: gas_reading})
    elif app_config_access.installed_sensors.pimoroni_sgp30:
        # TODO: Add e-co2 this sensor can do into program (In DB?)
        if get_latency:
            return sensors_direct.pimoroni_sgp30_a.sensor_latency
        gas_reading = sensors_direct.pimoroni_sgp30_a.gas_resistance_index()
        gas_dic.update({db_v.gas_resistance_index: gas_reading})
    elif get_latency:
        return _get_sensor_latency(get_gas)
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        gas_readings = sensors_direct.pimoroni_enviroplus_a.gas_data()
        gas_dic.update({db_v.gas_oxidising: gas_readings[0],
                        db_v.gas_reducing: gas_readings[1],
                        db_v.gas_nh3: gas_readings[2]})
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        gas_readings = [sensors_direct.dummy_sensors.gas_resistance_index()]
        gas_readings += sensors_direct.dummy_sensors.gas_data()
        gas_dic.update({db_v.gas_resistance_index: gas_readings[0],
                        db_v.gas_oxidising: gas_readings[1],
                        db_v.gas_reducing: gas_readings[2],
                        db_v.gas_nh3: gas_readings[3]})
    else:
        return None
    return gas_dic


def get_particulate_matter(get_latency=False):
    """ Returns selected Particulate Matter readings in a dictionary. """
    pm_dic = {}
    if app_config_access.installed_sensors.pimoroni_pms5003:
        if get_latency:
            return sensors_direct.pimoroni_pms5003_a.sensor_latency
        pm_readings = sensors_direct.pimoroni_pms5003_a.particulate_matter_data()
        pm_dic.update({db_v.particulate_matter_1: pm_readings[0],
                       db_v.particulate_matter_2_5: pm_readings[1],
                       db_v.particulate_matter_10: pm_readings[2]})
    elif app_config_access.installed_sensors.sensirion_sps30:
        if get_latency:
            return sensors_direct.sensirion_sps30_a.sensor_latency
        pm_readings = sensors_direct.sensirion_sps30_a.particulate_matter_data()
        pm_dic.update({db_v.particulate_matter_1: pm_readings[0],
                       db_v.particulate_matter_2_5: pm_readings[1],
                       db_v.particulate_matter_4: pm_readings[2],
                       db_v.particulate_matter_10: pm_readings[3]})
    elif get_latency:
        return _get_sensor_latency(get_particulate_matter)
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pm_readings = sensors_direct.dummy_sensors.particulate_matter_data()
        pm_dic.update({db_v.particulate_matter_1: pm_readings[0],
                       db_v.particulate_matter_2_5: pm_readings[1],
                       db_v.particulate_matter_4: pm_readings[2],
                       db_v.particulate_matter_10: pm_readings[3]})
    else:
        return None
    return pm_dic


def get_lumen(get_latency=False):
    """ Returns sensors lumen in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_lumen)
    if app_config_access.installed_sensors.pimoroni_enviro:
        lumen = sensors_direct.pimoroni_enviro_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        lumen = sensors_direct.pimoroni_enviro2_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        lumen = sensors_direct.pimoroni_enviroplus_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        lumen = sensors_direct.pimoroni_bh1745_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        lumen = sensors_direct.pimoroni_ltr_559_a.lumen()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        lumen = sensors_direct.dummy_sensors.lumen()
    else:
        return None
    return {db_v.lumen: lumen}


def get_ems_colors(get_latency=False):
    """ Returns Electromagnetic Spectrum Wavelengths (colors) in a dictionary. """
    colors_dic = {}
    if app_config_access.installed_sensors.pimoroni_as7262:
        if get_latency:
            return sensors_direct.pimoroni_as7262_a.sensor_latency
        colours = sensors_direct.pimoroni_as7262_a.spectral_six_channel()
        colors_dic.update({db_v.red: colours[0],
                           db_v.orange: colours[1],
                           db_v.yellow: colours[2],
                           db_v.green: colours[3],
                           db_v.blue: colours[4],
                           db_v.violet: colours[5]})
    elif get_latency:
        return _get_sensor_latency(get_ems_colors)
    elif app_config_access.installed_sensors.pimoroni_enviro:
        colours = sensors_direct.pimoroni_enviro_a.ems()
        colors_dic.update({db_v.red: colours[0],
                           db_v.green: colours[1],
                           db_v.blue: colours[2]})
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        colours = sensors_direct.pimoroni_bh1745_a.ems()
        colors_dic.update({db_v.red: colours[0],
                           db_v.green: colours[1],
                           db_v.blue: colours[2]})
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        colours = sensors_direct.dummy_sensors.spectral_six_channel()
        colors_dic.update({db_v.red: colours[0],
                           db_v.orange: colours[1],
                           db_v.yellow: colours[2],
                           db_v.green: colours[3],
                           db_v.blue: colours[4],
                           db_v.violet: colours[5]})
    else:
        return None
    return colors_dic


def get_ultra_violet(get_latency=False):
    """ Returns Ultra Violet readings in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_ultra_violet)
    uv_dic = {}
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uv_index = sensors_direct.pimoroni_veml6075_a.ultra_violet_index()
        uv_reading = sensors_direct.pimoroni_veml6075_a.ultra_violet()
        uv_dic.update({db_v.ultra_violet_index: uv_index,
                       db_v.ultra_violet_a: uv_reading[0],
                       db_v.ultra_violet_b: uv_reading[1]})
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        uv_index = sensors_direct.dummy_sensors.ultra_violet_index()
        uv_reading = sensors_direct.dummy_sensors.ultra_violet()
        uv_dic.update({db_v.ultra_violet_index: uv_index,
                       db_v.ultra_violet_a: uv_reading[0],
                       db_v.ultra_violet_b: uv_reading[1]})
    else:
        return None
    return uv_dic


def get_accelerometer_xyz(get_latency=False):
    """ Returns sensors Accelerometer XYZ in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_accelerometer_xyz)
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensors_direct.rp_sense_hat_a.accelerometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_enviro:
        xyz = sensors_direct.pimoroni_enviro_a.accelerometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_msa301:
        xyz = sensors_direct.pimoroni_msa301_a.accelerometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_lsm303d:
        xyz = sensors_direct.pimoroni_lsm303d_a.accelerometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensors_direct.pimoroni_icm20948_a.accelerometer_xyz()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        xyz = sensors_direct.dummy_sensors.accelerometer_xyz()
    else:
        return None
    return {db_v.acc_x: xyz[0],
            db_v.acc_y: xyz[1],
            db_v.acc_z: xyz[2]}


def get_magnetometer_xyz(get_latency=False):
    """ Returns sensors Magnetometer XYZ in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_magnetometer_xyz)
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensors_direct.rp_sense_hat_a.magnetometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_enviro:
        xyz = sensors_direct.pimoroni_enviro_a.magnetometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_lsm303d:
        xyz = sensors_direct.pimoroni_lsm303d_a.magnetometer_xyz()
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensors_direct.pimoroni_icm20948_a.magnetometer_xyz()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        xyz = sensors_direct.dummy_sensors.magnetometer_xyz()
    else:
        return None
    return {db_v.mag_x: xyz[0],
            db_v.mag_y: xyz[1],
            db_v.mag_z: xyz[2]}


def get_gyroscope_xyz(get_latency=False):
    """ Returns sensors Gyroscope XYZ in a dictionary. """
    if get_latency:
        return _get_sensor_latency(get_gyroscope_xyz)
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensors_direct.rp_sense_hat_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensors_direct.pimoroni_icm20948_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        xyz = sensors_direct.dummy_sensors.gyroscope_xyz()
    else:
        return None
    return {db_v.gyro_x: xyz[0],
            db_v.gyro_y: xyz[1],
            db_v.gyro_z: xyz[2]}


def get_reading_unit(reading_type):
    if reading_type == db_v.env_temperature or reading_type == db_v.system_temperature or \
            reading_type == db_v.dew_point or reading_type == db_v.env_temperature_offset:
        return "°C"
    elif reading_type == db_v.pressure:
        return "hPa"
    elif reading_type == db_v.altitude:
        return "Meters"
    elif reading_type == db_v.humidity:
        return "%RH"
    elif reading_type == db_v.distance:
        return "?"
    elif reading_type == db_v.gas_resistance_index or reading_type == db_v.gas_oxidising or \
            reading_type == db_v.gas_reducing or reading_type == db_v.gas_nh3:
        return "kΩ"
    elif reading_type == db_v.particulate_matter_1 or reading_type == db_v.particulate_matter_2_5 or \
            reading_type == db_v.particulate_matter_4 or reading_type == db_v.particulate_matter_10:
        return "µg/m³"
    elif reading_type == db_v.lumen or reading_type == db_v.red or reading_type == db_v.orange or \
            reading_type == db_v.yellow or reading_type == db_v.green or reading_type == db_v.blue or \
            reading_type == db_v.violet or reading_type == db_v.ultra_violet_a or \
            reading_type == db_v.ultra_violet_b or reading_type == db_v.ultra_violet_index:
        return "lm"
    elif reading_type == db_v.acc_x or reading_type == db_v.acc_y or reading_type == db_v.acc_z:
        return "g"
    elif reading_type == db_v.mag_x or reading_type == db_v.mag_y or reading_type == db_v.mag_z:
        return "μT"
    elif reading_type == db_v.gyro_x or reading_type == db_v.gyro_y or reading_type == db_v.gyro_z:
        return "°/s"
    elif reading_type == db_v.sensor_uptime:
        return "Minutes"
    elif reading_type == db_v.all_tables_datetime or reading_type == db_v.sensor_name or reading_type == db_v.ip:
        return ""
    return "???"


def display_message(text_msg, check_test=False):
    """ If a Supported Display is installed, shows provided text message on it. """
    logger.sensors_logger.debug("* Displaying Text on LED Screen: " + str(text_msg)[:50])

    text_msg = str(text_msg)
    if app_config_access.display_config.enable_display:
        if len(text_msg) > 0 or check_test:
            text_msg = "-- " + text_msg
            display_missing = True
            if app_config_access.installed_sensors.kootnet_dummy_sensor:
                if not check_test:
                    thread_function(sensors_direct.dummy_sensors.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.raspberry_pi_sense_hat:
                if not check_test:
                    thread_function(sensors_direct.rp_sense_hat_a.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.pimoroni_matrix_11x7:
                if not check_test:
                    thread_function(sensors_direct.pimoroni_matrix_11x7_a.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.pimoroni_st7735:
                if not check_test:
                    thread_function(sensors_direct.pimoroni_st7735_a.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.pimoroni_mono_oled_luma:
                if not check_test:
                    thread_function(sensors_direct.pimoroni_mono_oled_luma_a.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.pimoroni_enviroplus:
                if not check_test:
                    thread_function(sensors_direct.pimoroni_enviroplus_a.display_text, args=text_msg)
                display_missing = False
            if app_config_access.installed_sensors.pimoroni_enviro2:
                if not check_test:
                    thread_function(sensors_direct.pimoroni_enviro2_a.display_text, args=text_msg)
                display_missing = False
            if display_missing:
                return False
            return True
    else:
        logger.sensors_logger.debug("* Unable to Display Text: Display disabled in Primary Configuration")
        return False


def restart_services(sleep_before_restart=1):
    """ Reloads systemd service files & restarts KootnetSensors service. """
    time.sleep(sleep_before_restart)
    os.system(bash_commands["RestartService"])


def get_db_notes():
    """ Returns a comma separated string of Notes from the SQL Database. """
    sql_query = "SELECT " + db_v.other_table_column_notes + \
                " FROM " + db_v.table_other
    sql_db_notes = sqlite_database.sql_execute_get_data(sql_query)
    return _create_str_from_list(sql_db_notes)


def get_db_note_dates():
    """ Returns a comma separated string of Note Dates from the SQL Database. """
    sql_query_notes = "SELECT " + db_v.all_tables_datetime + \
                      " FROM " + db_v.table_other
    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)
    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    """ Returns a comma separated string of User Note Dates from the SQL Database. """
    sql_query_user_datetime = "SELECT " + db_v.other_table_column_user_date_time + \
                              " FROM " + db_v.table_other
    sql_data_user_datetime = sqlite_database.sql_execute_get_data(sql_query_user_datetime)
    return _create_str_from_list(sql_data_user_datetime)


def _create_str_from_list(sql_data_notes):
    """
    Takes in a list and returns a comma separated string.
    It also converts any commas located in the values to "[replaced_comma]".
    These converted values will later be converted back to regular commas.
    """
    if len(sql_data_notes) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data_notes:
            new_entry = str(entry[0])
            new_entry = new_entry.replace(",", "[replaced_comma]")
            return_data_string += new_entry + ","
            count += 1
        return_data_string = return_data_string[:-1]
    else:
        return_data_string = "No Data"
    return return_data_string


def add_note_to_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then writes it to the SQL Database. """
    user_date_and_note = datetime_note.split(command_data_separator)
    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]

        sql_execute = "INSERT OR IGNORE INTO OtherData (" + \
                      db_v.all_tables_datetime + "," + \
                      db_v.other_table_column_user_date_time + "," + \
                      db_v.other_table_column_notes + ")" + \
                      " VALUES (?,?,?);"

        data_entries = [current_datetime, custom_datetime, note]

        sqlite_database.write_to_sql_database(sql_execute, data_entries)
    else:
        logger.primary_logger.error("Unable to add Note to DB: Bad Note")


def update_note_in_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then updates the note in the SQL Database. """
    try:
        data_list = datetime_note.split(command_data_separator)

        current_datetime = data_list[0]
        custom_datetime = data_list[1]
        note = data_list[2]

        sql_execute = "UPDATE OtherData SET Notes = ?,UserDateTime = ? WHERE DateTime = ?;"
        data_entries = [note, custom_datetime, current_datetime]
        sqlite_database.write_to_sql_database(sql_execute, data_entries)
    except Exception as error:
        logger.primary_logger.error("DB note update error: " + str(error))


def delete_db_note(note_datetime):
    """ Deletes a Note from the SQL Database based on it's DateTime entry. """
    sql_query = "DELETE FROM " + str(db_v.table_other) + \
                " WHERE " + str(db_v.all_tables_datetime) + \
                " = ?;"
    sql_data = [note_datetime]
    sqlite_database.write_to_sql_database(sql_query, sql_data)
