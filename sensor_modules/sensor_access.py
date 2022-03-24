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
import math
import time
from datetime import datetime
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables import database_variables as db_v, latency_variables
from configuration_modules import app_config_access
from sensor_modules import sensors_initialization
from sensor_modules.system_access import get_uptime_minutes

sensors_direct = sensors_initialization.CreateSensorAccess(first_start=True)


def get_sensors_latency():
    """ Returns sensors latency in seconds as a dictionary. """
    sensor_function_list = [
        get_cpu_temperature, get_environment_temperature, get_pressure, get_altitude, get_humidity,
        get_distance, get_gas, get_particulate_matter, get_lumen, get_ems_colors,
        get_ultra_violet, get_accelerometer_xyz, get_magnetometer_xyz, get_gyroscope_xyz, get_gps_data
    ]
    sensor_names_list = latency_variables.get_all_latency_as_list()

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
        return None


def get_all_available_sensor_readings(include_system_info=False):
    """ Returns ALL sensor readings in a dictionary. """
    utc_0_date_time_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    env_temp_raw = get_environment_temperature(temperature_correction=False)
    env_temp_corrected = get_environment_temperature()

    return_dictionary = {}
    if env_temp_raw is not None and env_temp_corrected is not None:
        env_temp_raw = env_temp_raw[db_v.env_temperature]
        env_temp_corrected = env_temp_corrected[db_v.env_temperature]
        temp_correction = round((env_temp_corrected - env_temp_raw), 5)
        return_dictionary.update({db_v.env_temperature: env_temp_corrected,
                                  db_v.env_temperature_offset: temp_correction})

    if include_system_info:
        uptime = get_uptime_minutes()
        if uptime is not None:
            return_dictionary.update({db_v.sensor_uptime: uptime[db_v.sensor_uptime]})
        return_dictionary.update({db_v.all_tables_datetime: utc_0_date_time_now,
                                  db_v.sensor_name: app_cached_variables.hostname,
                                  db_v.ip: app_cached_variables.ip})

    functions_list = [
        get_cpu_temperature, get_environment_temperature, get_pressure, get_altitude, get_humidity, get_dew_point,
        get_distance, get_gas, get_particulate_matter, get_lumen, get_ems_colors, get_ultra_violet,
        get_accelerometer_xyz, get_magnetometer_xyz, get_gyroscope_xyz, get_gps_data
    ]

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
    elif app_config_access.installed_sensors.pimoroni_bme280:
        temperature = sensors_direct.pimoroni_bme280_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        temperature = sensors_direct.pimoroni_bmp280_a.temperature()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        temperature = sensors_direct.rp_sense_hat_a.temperature()
    elif app_config_access.installed_sensors.w1_therm_sensor:
        temperature = sensors_direct.w1_therm_sensor_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_weather_hat:
        temperature = sensors_direct.pimoroni_weather_hat_a.temperature()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.temperature()
    else:
        return None

    if temperature_correction:
        temperature = _apply_environment_temperature_correction(temperature)
    return {db_v.env_temperature: temperature}


def _apply_environment_temperature_correction(temperature):
    enable_custom_temp = app_config_access.sensor_offsets.enable_temp_offset
    temperature_offset = app_config_access.sensor_offsets.temperature_offset
    new_temp = temperature
    if enable_custom_temp:
        try:
            new_temp = round(temperature + temperature_offset, 6)
        except Exception as error:
            logger.sensors_logger.warning("Invalid Environment Temperature Offset")
            logger.sensors_logger.debug(str(error))

    cpu_temp = get_cpu_temperature()
    enable_temperature_comp_factor = app_config_access.sensor_offsets.enable_temperature_comp_factor
    temperature_comp_factor = app_config_access.sensor_offsets.temperature_comp_factor
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
    elif app_config_access.installed_sensors.pimoroni_bme280:
        pressure = sensors_direct.pimoroni_bme280_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        pressure = sensors_direct.pimoroni_bmp280_a.pressure()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        pressure = sensors_direct.rp_sense_hat_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_weather_hat:
        pressure = sensors_direct.pimoroni_weather_hat_a.pressure()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pressure = sensors_direct.dummy_sensors.pressure()
    else:
        return None
    return {db_v.pressure: pressure}


def get_altitude(get_latency=False):
    """ Returns sensors altitude in a dictionary. """
    if app_config_access.installed_sensors.pimoroni_pa1010d:
        if get_latency:
            return sensors_direct.pimoroni_pa1010d_a.sensor_latency
        sensor_reading = sensors_direct.pimoroni_pa1010d_a.altitude()
    elif get_latency:
        return _get_sensor_latency(get_altitude)
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        sensor_reading = sensors_direct.pimoroni_bmp280_a.altitude()
    elif app_config_access.installed_sensors.pimoroni_enviro:
        sensor_reading = sensors_direct.pimoroni_enviro_a.altitude()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        sensor_reading = sensors_direct.dummy_sensors.altitude()
    else:
        sensor_reading = _get_self_calculated_altitude()
        if sensor_reading is None:
            return None
    return {db_v.altitude: sensor_reading}


def _get_self_calculated_altitude(qnh=1013.25):
    try:
        temperature = get_environment_temperature()
        pressure = get_pressure()
        if pressure is None or temperature is None:
            return None

        temperature = temperature[db_v.env_temperature]
        pressure = pressure[db_v.pressure]
        var_altitude = ((pow((qnh / pressure), (1.0 / 5.257)) - 1) * (temperature + 273.15)) / 0.0065
        return round(var_altitude, 5)
    except Exception as error:
        logger.sensors_logger.error("Altitude Calculation using Temperature & Pressure Failed: " + str(error))
    return None


def get_humidity(get_latency=False):
    """ Returns sensors humidity in a dictionary. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        if get_latency:
            return sensors_direct.pimoroni_bme680_a.sensor_latency
        humidity = sensors_direct.pimoroni_bme680_a.humidity()
    elif get_latency:
        return _get_sensor_latency(get_humidity)
    elif app_config_access.installed_sensors.pimoroni_bme280:
        humidity = sensors_direct.pimoroni_bme280_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        humidity = sensors_direct.pimoroni_enviro2_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        humidity = sensors_direct.pimoroni_enviroplus_a.humidity()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        humidity = sensors_direct.rp_sense_hat_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_weather_hat:
        humidity = sensors_direct.pimoroni_weather_hat_a.humidity()
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
        logger.sensors_logger.warning("Unable to calculate dew point: " + str(error))
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
    elif app_config_access.installed_sensors.pimoroni_weather_hat:
        distance = sensors_direct.pimoroni_weather_hat_a.distance()
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
    elif app_config_access.installed_sensors.pimoroni_mics6814:
        gas_readings = sensors_direct.pimoroni_mics6814_a.gas_data()
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
    elif app_config_access.installed_sensors.pimoroni_weather_hat:
        lumen = sensors_direct.pimoroni_weather_hat_a.lumen()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        lumen = sensors_direct.dummy_sensors.lumen()
    else:
        return None
    return {db_v.lumen: lumen}


def get_ems_colors(get_latency=False):
    """ Returns Electromagnetic Spectrum Wavelengths (colors) in a dictionary. """
    colors_dic = {}
    if get_latency:
        return _get_sensor_latency(get_ems_colors)
    elif app_config_access.installed_sensors.pimoroni_as7262:
        colours = sensors_direct.pimoroni_as7262_a.spectral_six_channel()
        colors_dic.update({db_v.red: colours[0],
                           db_v.orange: colours[1],
                           db_v.yellow: colours[2],
                           db_v.green: colours[3],
                           db_v.blue: colours[4],
                           db_v.violet: colours[5]})
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


def get_gps_data(get_latency=False):
    """
     Returns GPS Data in a dictionary.

     latitude, longitude, altitude, timestamp, number of satellites,
     gps quality, mode fix type, speed over ground, pdop, hdop, vdop
    """
    if app_config_access.installed_sensors.pimoroni_pa1010d:
        if get_latency:
            return sensors_direct.pimoroni_pa1010d_a.sensor_latency
        gps_data = sensors_direct.pimoroni_pa1010d_a.all_gps_data()
    elif get_latency:
        return _get_sensor_latency(get_gps_data)
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        gps_data = sensors_direct.dummy_sensors.all_gps_data()
    else:
        return None
    return {db_v.latitude: gps_data[0],
            db_v.longitude: gps_data[1],
            db_v.altitude: gps_data[2],
            db_v.gps_timestamp: gps_data[3],
            db_v.gps_num_satellites: gps_data[4],
            db_v.gps_quality: gps_data[5],
            db_v.gps_mode_fix_type: gps_data[6],
            db_v.gps_speed_over_ground: gps_data[7],
            db_v.gps_pdop: gps_data[8],
            db_v.gps_hdop: gps_data[9],
            db_v.gps_vdop: gps_data[10]}


def get_reading_unit(reading_type):
    if reading_type == db_v.env_temperature or reading_type == db_v.system_temperature or \
            reading_type == db_v.dew_point or reading_type == db_v.env_temperature_offset:
        return "°C"
    elif reading_type == "Seconds":
        return "Sec"
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
    elif reading_type == db_v.gps_speed_over_ground:
        return "km/hr?"
    elif reading_type == db_v.gps_timestamp:
        return "UTC0"
    return ""


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
