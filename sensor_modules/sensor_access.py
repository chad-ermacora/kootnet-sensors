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
import time
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk, thread_function
from operations_modules.app_cached_variables import no_sensor_present, command_data_separator, database_variables, \
    current_platform, bash_commands
from operations_modules import sqlite_database
from configuration_modules import app_config_access
from sensor_modules import sensors_initialization

sensors_direct = sensors_initialization.CreateSensorAccess(first_start=True)


def get_operating_system_name():
    """ Returns sensors Operating System Name and version. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_os_name_version()
    return no_sensor_present


def get_hostname():
    """ Returns sensors hostname. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_hostname()
    return no_sensor_present


def get_ip():
    """ Returns sensor IP Address as a String. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_ip()
    return no_sensor_present


def get_disk_usage_gb():
    """ Returns sensor root disk usage as GB's. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_disk_usage_gb()
    return no_sensor_present


def get_disk_usage_percent():
    """ Returns sensor root disk usage as a %. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_disk_usage_percent()
    return no_sensor_present


def get_memory_usage_percent():
    """ Returns sensor RAM usage as a %. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_memory_usage_percent()
    return no_sensor_present


def get_system_datetime():
    """ Returns System DateTime in format YYYY-MM-DD HH:MM as a String. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_sys_datetime_str()
    return no_sensor_present


def get_uptime_minutes():
    """ Returns System UpTime in Minutes as an Integer. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_uptime_raw()
    return no_sensor_present


def get_uptime_str():
    """ Returns System UpTime as a human readable String. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_uptime_str()
    return no_sensor_present


def get_system_reboot_count():
    """ Returns system reboot count from the SQL Database. """
    if current_platform == "Linux":
        reboot_count = sensors_direct.operating_system_a.get_sensor_reboot_count()
        return reboot_count
    return no_sensor_present


def get_db_size():
    """ Returns SQL Database size in MB. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_sql_db_size()
    return no_sensor_present


def get_db_notes_count():
    """ Returns Number of Notes in the SQL Database. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_db_notes_count()
    return no_sensor_present


def get_db_first_last_date():
    """ Returns First and Last recorded date in the SQL Database as a String. """
    if current_platform == "Linux":
        return sensors_direct.operating_system_a.get_db_first_last_date()
    return no_sensor_present


def get_last_updated():
    """ Returns when the sensor programs were last updated and how in a String. """
    last_updated = ""
    if not os.path.isfile(file_locations.program_last_updated):
        logger.sensors_logger.debug("Previous version file not found - Creating version file")
        last_updated_text = "No Update Detected"
        write_file_to_disk(file_locations.program_last_updated, last_updated_text)
        return last_updated_text
    last_updated_file = get_file_content(file_locations.program_last_updated)
    try:
        last_updated_lines = last_updated_file.split("\n")
        for line in last_updated_lines:
            last_updated += str(line)
    except Exception as error:
        logger.sensors_logger.warning("Invalid Kootnet Sensor's Last Updated File: " + str(error))
    return last_updated.strip()


def get_sensors_latency():
    """ Returns sensors latency in seconds as a dictionary. """
    sensor_function_list = [
        get_cpu_temperature, get_sensor_temperature, get_pressure, get_altitude, get_humidity,
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
        thing = _get_sensor_latency(sensor_function)
        if thing is None:
            sensor_latency_dic[sensor_name] = None
        else:
            sensor_latency_dic[sensor_name] = round(thing, 6)
    return sensor_latency_dic


def _get_sensor_latency(sensor_function):
    try:
        start_time = time.time()
        sensor_reading = sensor_function()
        end_time = time.time()
        if sensor_reading == no_sensor_present:
            return None
        return float(end_time - start_time)
    except Exception as error:
        logger.sensors_logger.warning("Problem getting sensor latency: " + str(error))
        return 0.0


def get_cpu_temperature():
    """ Returns sensors CPU temperature. """
    if app_config_access.installed_sensors.raspberry_pi:
        temperature = sensors_direct.raspberry_pi_a.cpu_temperature()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.cpu_temperature()
    else:
        return no_sensor_present
    return temperature


def get_sensor_temperature(temperature_correction=True, get_both=False):
    """ Returns sensors Environmental temperature. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        temperature = sensors_direct.pimoroni_enviro_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        temperature = sensors_direct.pimoroni_enviro2_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        temperature = sensors_direct.pimoroni_enviroplus_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_mcp9600:
        temperature = sensors_direct.pimoroni_mcp9600_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        temperature = sensors_direct.pimoroni_bmp280_a.temperature()
    elif app_config_access.installed_sensors.pimoroni_bme680:
        temperature = sensors_direct.pimoroni_bme680_a.temperature()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        temperature = sensors_direct.rp_sense_hat_a.temperature()
    elif app_config_access.installed_sensors.w1_therm_sensor:
        temperature = sensors_direct.w1_therm_sensor_a.temperature()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.temperature()
    else:
        if get_both:
            return [no_sensor_present, no_sensor_present]
        return no_sensor_present

    new_temp = temperature
    if temperature_correction and temperature != no_sensor_present or \
            get_both and temperature != no_sensor_present:
        enable_custom_temp = app_config_access.primary_config.enable_custom_temp
        temperature_offset = app_config_access.primary_config.temperature_offset
        new_temp = temperature
        if enable_custom_temp and temperature_offset != 0:
            try:
                new_temp = round(temperature + temperature_offset, 6)
            except Exception as error:
                logger.sensors_logger.warning("Invalid Temperature Offset")
                logger.sensors_logger.debug(str(error))

        cpu_temp = get_cpu_temperature()
        enable_temperature_comp_factor = app_config_access.primary_config.enable_temperature_comp_factor
        temperature_comp_factor = app_config_access.primary_config.temperature_comp_factor
        if enable_temperature_comp_factor and cpu_temp != no_sensor_present and temperature_comp_factor != 0:
            try:
                new_temp = round(new_temp - ((cpu_temp - new_temp) * temperature_comp_factor), 6)
            except Exception as error:
                logger.sensors_logger.warning("Invalid Temperature Factor")
                logger.sensors_logger.debug(str(error))
        if not get_both:
            return new_temp
    if get_both:
        return [temperature, new_temp]
    return temperature


def get_temperature_correction():
    raw_and_corrected = get_sensor_temperature(get_both=True)
    temp_difference = 0.0
    if raw_and_corrected[0] != no_sensor_present:
        try:
            temp_difference = raw_and_corrected[1] - raw_and_corrected[0]
        except Exception as error:
            logger.sensors_logger.warning("Unable to get Env Temperature Correction amount: " + str(error))
        return round(temp_difference, 5)
    else:
        return temp_difference


def get_pressure():
    """ Returns sensors pressure. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        pressure = sensors_direct.pimoroni_enviro_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_enviro2:
        pressure = sensors_direct.pimoroni_enviro2_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        pressure = sensors_direct.pimoroni_enviroplus_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        pressure = sensors_direct.pimoroni_bmp280_a.pressure()
    elif app_config_access.installed_sensors.pimoroni_bme680:
        pressure = sensors_direct.pimoroni_bme680_a.pressure()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        pressure = sensors_direct.rp_sense_hat_a.pressure()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pressure = sensors_direct.dummy_sensors.pressure()
    else:
        return no_sensor_present
    return pressure


def get_altitude(qnh=1013.25):
    """ Returns sensors altitude. """
    round_decimal_to = 5
    temperature = get_sensor_temperature()
    pressure = get_pressure()
    if pressure == no_sensor_present or temperature == no_sensor_present:
        return no_sensor_present

    try:
        var_altitude = ((pow((qnh / pressure), (1.0 / 5.257)) - 1) * (temperature + 273.15)) / 0.0065
    except Exception as error:
        var_altitude = 0.0
        logger.sensors_logger.error("Altitude Calculation using Temperature & Pressure Failed: " + str(error))
    return round(var_altitude, round_decimal_to)


def get_humidity():
    """ Returns sensors humidity. """
    if app_config_access.installed_sensors.pimoroni_enviro2:
        humidity = sensors_direct.pimoroni_enviro2_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        humidity = sensors_direct.pimoroni_enviroplus_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_bme680:
        humidity = sensors_direct.pimoroni_bme680_a.humidity()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        humidity = sensors_direct.rp_sense_hat_a.humidity()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        humidity = sensors_direct.dummy_sensors.humidity()
    else:
        return no_sensor_present
    return humidity


def get_dew_point():
    """ Returns estimated dew point based on Temperature and Humidity. """
    variable_a = 17.27
    variable_b = 237.7

    env_temp = get_sensor_temperature()
    humidity = get_humidity()
    if env_temp == no_sensor_present or humidity == no_sensor_present:
        return no_sensor_present
    else:
        try:
            alpha = ((variable_a * env_temp) / (variable_b + env_temp)) + math.log(humidity / 100.0)
            return (variable_b * alpha) / (variable_a - alpha)
        except Exception as error:
            logger.sensors_logger.error("Unable to calculate dew point: " + str(error))
    return 0.0


def get_distance():
    """ Returns sensors distance. """
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
        return no_sensor_present
    return distance


def get_gas(return_as_dictionary=False):
    """ Returns sensors gas readings as a list. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        gas_readings = sensors_direct.pimoroni_bme680_a.gas_resistance_index()
        if return_as_dictionary:
            return {database_variables.gas_resistance_index: gas_readings}
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        gas_readings = sensors_direct.pimoroni_enviroplus_a.gas_data()
        if return_as_dictionary:
            return {database_variables.gas_oxidising: gas_readings[0],
                    database_variables.gas_reducing: gas_readings[1],
                    database_variables.gas_nh3: gas_readings[2]}
    elif app_config_access.installed_sensors.pimoroni_sgp30:
        # TODO: Add e-co2 this sensor can do into program (In DB?)
        gas_readings = sensors_direct.pimoroni_sgp30_a.gas_resistance_index()
        if return_as_dictionary:
            return {database_variables.gas_resistance_index: gas_readings}
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        gas_readings = [sensors_direct.dummy_sensors.gas_resistance_index()]
        gas_readings += sensors_direct.dummy_sensors.gas_data()
        if return_as_dictionary:
            return {database_variables.gas_resistance_index: gas_readings[0],
                    database_variables.gas_oxidising: gas_readings[1],
                    database_variables.gas_reducing: gas_readings[2],
                    database_variables.gas_nh3: gas_readings[3]}
    else:
        return no_sensor_present
    return gas_readings


def get_particulate_matter(return_as_dictionary=False):
    """ Returns selected Particulate Matter readings in a Dictionary. """
    if app_config_access.installed_sensors.pimoroni_pms5003:
        pm_readings = sensors_direct.pimoroni_pms5003_a.particulate_matter_data()
    elif app_config_access.installed_sensors.sensirion_sps30:
        pm_readings = sensors_direct.sensirion_sps30_a.particulate_matter_data()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pm_readings = sensors_direct.dummy_sensors.particulate_matter_data()
    else:
        if return_as_dictionary:
            return {database_variables.particulate_matter_1: no_sensor_present,
                    database_variables.particulate_matter_2_5: no_sensor_present,
                    database_variables.particulate_matter_4: no_sensor_present,
                    database_variables.particulate_matter_10: no_sensor_present}
        return no_sensor_present
    if return_as_dictionary:
        return pm_readings
    return_list = []
    if pm_readings[database_variables.particulate_matter_1] != no_sensor_present:
        return_list.append(pm_readings[database_variables.particulate_matter_1])
    if pm_readings[database_variables.particulate_matter_2_5] != no_sensor_present:
        return_list.append(pm_readings[database_variables.particulate_matter_2_5])
    if pm_readings[database_variables.particulate_matter_4] != no_sensor_present:
        return_list.append(pm_readings[database_variables.particulate_matter_4])
    if pm_readings[database_variables.particulate_matter_10] != no_sensor_present:
        return_list.append(pm_readings[database_variables.particulate_matter_10])
    return return_list


def get_lumen():
    """ Returns sensors lumen. """
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
        return no_sensor_present
    return lumen


def get_ems_colors(return_as_dictionary=False):
    """ Returns Electromagnetic Spectrum Wavelengths in the form of Red, Orange, Yellow, Green, Cyan, Blue, Violet. """
    if app_config_access.installed_sensors.pimoroni_as7262:
        colours = sensors_direct.pimoroni_as7262_a.spectral_six_channel()
        if return_as_dictionary:
            return {database_variables.red: colours[0],
                    database_variables.orange: colours[1],
                    database_variables.yellow: colours[2],
                    database_variables.green: colours[3],
                    database_variables.blue: colours[4],
                    database_variables.violet: colours[5]}
    elif app_config_access.installed_sensors.pimoroni_enviro:
        colours = sensors_direct.pimoroni_enviro_a.ems()
        if return_as_dictionary:
            return {database_variables.red: colours[0],
                    database_variables.green: colours[1],
                    database_variables.blue: colours[2]}
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        colours = sensors_direct.pimoroni_bh1745_a.ems()
        if return_as_dictionary:
            return {database_variables.red: colours[0],
                    database_variables.green: colours[1],
                    database_variables.blue: colours[2]}
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        colours = sensors_direct.dummy_sensors.spectral_six_channel()
        if return_as_dictionary:
            return {database_variables.red: colours[0],
                    database_variables.orange: colours[1],
                    database_variables.yellow: colours[2],
                    database_variables.green: colours[3],
                    database_variables.blue: colours[4],
                    database_variables.violet: colours[5]}
    else:
        return no_sensor_present
    return colours


def get_ultra_violet(return_as_dictionary=False):
    """ Returns Ultra Violet Index. """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uv_index = sensors_direct.pimoroni_veml6075_a.ultra_violet_index()
        uv_reading = sensors_direct.pimoroni_veml6075_a.ultra_violet()
        if return_as_dictionary:
            return {database_variables.ultra_violet_index: uv_index,
                    database_variables.ultra_violet_a: uv_reading[0],
                    database_variables.ultra_violet_b: uv_reading[1]}
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        uv_index = sensors_direct.dummy_sensors.ultra_violet_index()
        uv_reading = sensors_direct.dummy_sensors.ultra_violet()
        if return_as_dictionary:
            return {database_variables.ultra_violet_index: uv_index,
                    database_variables.ultra_violet_a: uv_reading[0],
                    database_variables.ultra_violet_b: uv_reading[1]}
    else:
        return no_sensor_present
    return uv_reading


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ as tuple. """
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
        return no_sensor_present
    return xyz


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ as tuple. """
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
        return no_sensor_present
    return xyz


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ as tuple. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensors_direct.rp_sense_hat_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensors_direct.pimoroni_icm20948_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        xyz = sensors_direct.dummy_sensors.gyroscope_xyz()
    else:
        return no_sensor_present
    return xyz


# TODO: Send all sensors in JSON format
def get_all_sensors_as_json():
    """ Returns all sensor readings in JSON format. """
    return "WIP"


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
    sql_query = "SELECT " + database_variables.other_table_column_notes + \
                " FROM " + database_variables.table_other
    sql_db_notes = sqlite_database.sql_execute_get_data(sql_query)
    return _create_str_from_list(sql_db_notes)


def get_db_note_dates():
    """ Returns a comma separated string of Note Dates from the SQL Database. """
    sql_query_notes = "SELECT " + database_variables.all_tables_datetime + \
                      " FROM " + database_variables.table_other
    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)
    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    """ Returns a comma separated string of User Note Dates from the SQL Database. """
    sql_query_user_datetime = "SELECT " + database_variables.other_table_column_user_date_time + \
                              " FROM " + database_variables.table_other
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
            new_entry = str(entry)[2:-3]
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
                      database_variables.all_tables_datetime + "," + \
                      database_variables.other_table_column_user_date_time + "," + \
                      database_variables.other_table_column_notes + ")" + \
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
    sql_query = "DELETE FROM " + str(database_variables.table_other) + \
                " WHERE " + str(database_variables.all_tables_datetime) + \
                " = ?;"
    sql_data = [note_datetime]
    sqlite_database.write_to_sql_database(sql_query, sql_data)
