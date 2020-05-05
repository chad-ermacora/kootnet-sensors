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
from threading import Thread
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateMonitoredThread, get_file_content, write_file_to_disk
from operations_modules import app_cached_variables
from operations_modules import sqlite_database
from operations_modules import app_config_access
from operations_modules.app_cached_variables import no_sensor_present, command_data_separator
from sensor_modules import sensors_initialization as sensors_direct


def get_operating_system_name():
    """ Returns sensors Operating System Name and version. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_os_name_version()
    return no_sensor_present


def get_hostname():
    """ Returns sensors hostname. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_hostname()
    return no_sensor_present


def get_ip():
    """ Returns sensor IP Address as a String. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_ip()
    return no_sensor_present


def get_disk_usage_gb():
    """ Returns sensor root disk usage as GB's. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_disk_usage_gb()
    return no_sensor_present


def get_disk_usage_percent():
    """ Returns sensor root disk usage as a %. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_disk_usage_percent()
    return no_sensor_present


def get_memory_usage_percent():
    """ Returns sensor RAM usage as a %. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_memory_usage_percent()
    return no_sensor_present


def get_system_datetime():
    """ Returns System DateTime in format YYYY-MM-DD HH:MM as a String. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_sys_datetime_str()
    return no_sensor_present


def get_uptime_minutes():
    """ Returns System UpTime in Minutes as an Integer. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_uptime_raw()
    return no_sensor_present


def get_uptime_str():
    """ Returns System UpTime as a human readable String. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_uptime_str()
    return no_sensor_present


def get_system_reboot_count():
    """ Returns system reboot count from the SQL Database. """
    if app_cached_variables.current_platform == "Linux":
        reboot_count = sensors_direct.operating_system_a.get_sensor_reboot_count()
        return reboot_count
    return no_sensor_present


def get_db_size():
    """ Returns SQL Database size in MB. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_sql_db_size()
    return no_sensor_present


def get_db_notes_count():
    """ Returns Number of Notes in the SQL Database. """
    if app_cached_variables.current_platform == "Linux":
        return sensors_direct.operating_system_a.get_db_notes_count()
    return no_sensor_present


def get_db_first_last_date():
    """ Returns First and Last recorded date in the SQL Database as a String. """
    if app_cached_variables.current_platform == "Linux":
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
    sensor_function_list = [get_cpu_temperature, get_sensor_temperature, get_pressure, get_altitude, get_humidity,
                            get_distance, get_gas_resistance_index, get_gas_oxidised, get_gas_reduced, get_gas_nh3,
                            get_particulate_matter_1, get_particulate_matter_2_5, get_particulate_matter_10,
                            get_lumen, get_ems, get_ultra_violet_index, get_ultra_violet_a, get_ultra_violet_b,
                            get_accelerometer_xyz, get_magnetometer_xyz, get_gyroscope_xyz]
    sensor_names_list = ["cpu_temperature", "environment_temperature", "pressure", "altitude", "humidity",
                         "distance", "gas_resistance_index", "gas_oxidised", "gas_reduced", "gas_nh3",
                         "particulate_matter_1", "particulate_matter_2_5", "particulate_matter_10",
                         "lumen", "colours", "ultra_violet_index", "ultra_violet_a", "ultra_violet_b",
                         "accelerometer_xyz", "magnetometer_xyz", "gyroscope_xyz"]

    sensor_latency_list = []
    for sensor_function in sensor_function_list:
        thing = _get_sensor_latency(sensor_function)
        if thing is None:
            sensor_latency_list.append(None)
        else:
            sensor_latency_list.append(round(thing, 6))
    return [sensor_names_list, sensor_latency_list]


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
        temperature = no_sensor_present
    return temperature


def get_sensor_temperature(temperature_offset=True):
    """ Returns sensors Environmental temperature. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        temperature = sensors_direct.pimoroni_enviro_a.temperature()
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
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        temperature = sensors_direct.dummy_sensors.temperature()
    else:
        temperature = no_sensor_present

    if temperature_offset and temperature != app_cached_variables.no_sensor_present:
        if app_config_access.primary_config.enable_custom_temp:
            try:
                return temperature + app_config_access.primary_config.temperature_offset
            except Exception as error:
                logger.sensors_logger.warning("Invalid Temperature Offset")
                logger.sensors_logger.debug(str(error))
    return temperature


def get_pressure():
    """ Returns sensors pressure. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        pressure = sensors_direct.pimoroni_enviro_a.pressure()
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
        pressure = no_sensor_present
    return pressure


def get_altitude():
    """ Returns sensors altitude. """
    if app_config_access.installed_sensors.pimoroni_bmp280:
        altitude = sensors_direct.pimoroni_bmp280_a.altitude()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        altitude = sensors_direct.pimoroni_enviroplus_a.altitude()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        altitude = sensors_direct.dummy_sensors.altitude()
    else:
        altitude = no_sensor_present
    return altitude


def get_humidity():
    """ Returns sensors humidity. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        humidity = sensors_direct.pimoroni_enviroplus_a.humidity()
    elif app_config_access.installed_sensors.pimoroni_bme680:
        humidity = sensors_direct.pimoroni_bme680_a.humidity()
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        humidity = sensors_direct.rp_sense_hat_a.humidity()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        humidity = sensors_direct.dummy_sensors.humidity()
    else:
        humidity = no_sensor_present
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
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        distance = sensors_direct.pimoroni_enviroplus_a.distance()
    elif app_config_access.installed_sensors.pimoroni_vl53l1x:
        distance = sensors_direct.pimoroni_vl53l1x_a.distance()
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        distance = sensors_direct.pimoroni_ltr_559_a.distance()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        distance = sensors_direct.dummy_sensors.distance()
    else:
        distance = no_sensor_present
    return distance


def get_gas_resistance_index():
    """ Returns sensors gas resistance index for VOC. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        index = sensors_direct.pimoroni_bme680_a.gas_resistance_index()
    elif app_config_access.installed_sensors.pimoroni_sgp30:
        index = sensors_direct.pimoroni_sgp30_a.gas_resistance_index()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        index = sensors_direct.dummy_sensors.gas_resistance_index()
    else:
        index = no_sensor_present
    return index


def get_gas_oxidised():
    """ Returns sensors gas reading for oxidising. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        oxidising = sensors_direct.pimoroni_enviroplus_a.gas_data()[0]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        oxidising = sensors_direct.dummy_sensors.gas_data()[0]
    else:
        oxidising = no_sensor_present
    return oxidising


def get_gas_reduced():
    """ Returns sensors gas reading for reducing. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        reducing = sensors_direct.pimoroni_enviroplus_a.gas_data()[1]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        reducing = sensors_direct.dummy_sensors.gas_data()[1]
    else:
        reducing = no_sensor_present
    return reducing


def get_gas_nh3():
    """ Returns sensors gas reading for NH3. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        nh3_reading = sensors_direct.pimoroni_enviroplus_a.gas_data()[2]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        nh3_reading = sensors_direct.dummy_sensors.gas_data()[2]
    else:
        nh3_reading = no_sensor_present
    return nh3_reading


def get_particulate_matter_1():
    """ Returns sensor reading for PM1. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm1_reading = sensors_direct.pimoroni_enviroplus_a.particulate_matter_data()[0]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pm1_reading = sensors_direct.dummy_sensors.particulate_matter_data()[0]
    else:
        pm1_reading = no_sensor_present
    return pm1_reading


def get_particulate_matter_2_5():
    """ Returns sensor reading for PM2.5. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm2_5_reading = sensors_direct.pimoroni_enviroplus_a.particulate_matter_data()[1]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pm2_5_reading = sensors_direct.dummy_sensors.particulate_matter_data()[1]
    else:
        pm2_5_reading = no_sensor_present
    return pm2_5_reading


def get_particulate_matter_10():
    """ Returns sensor reading for PM10. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm10_reading = sensors_direct.pimoroni_enviroplus_a.particulate_matter_data()[2]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        pm10_reading = sensors_direct.dummy_sensors.particulate_matter_data()[2]
    else:
        pm10_reading = no_sensor_present
    return pm10_reading


def get_lumen():
    """ Returns sensors lumen. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        lumen = sensors_direct.pimoroni_enviro_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        lumen = sensors_direct.pimoroni_enviroplus_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        lumen = sensors_direct.pimoroni_bh1745_a.lumen()
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        lumen = sensors_direct.pimoroni_ltr_559_a.lumen()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        lumen = sensors_direct.dummy_sensors.lumen()
    else:
        lumen = no_sensor_present
    return lumen


def get_ems():
    """ Returns Electromagnetic Spectrum Wavelengths in the form of Red, Orange, Yellow, Green, Cyan, Blue, Violet. """
    if app_config_access.installed_sensors.pimoroni_as7262:
        colours = sensors_direct.pimoroni_as7262_a.spectral_six_channel()
    elif app_config_access.installed_sensors.pimoroni_enviro:
        colours = sensors_direct.pimoroni_enviro_a.ems()
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        colours = sensors_direct.pimoroni_bh1745_a.ems()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        colours = sensors_direct.dummy_sensors.spectral_six_channel()
    else:
        colours = no_sensor_present
    return colours


def get_ultra_violet_index():
    """ Returns Ultra Violet Index. """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uv_index_reading = sensors_direct.pimoroni_veml6075_a.ultra_violet_index()
    else:
        uv_index_reading = no_sensor_present
    return uv_index_reading


def get_ultra_violet_a():
    """ Returns Ultra Violet A (UVA). """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uva_reading = sensors_direct.pimoroni_veml6075_a.ultra_violet()[0]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        uva_reading = sensors_direct.dummy_sensors.ultra_violet()[0]
    else:
        uva_reading = no_sensor_present
    return uva_reading


def get_ultra_violet_b():
    """ Returns Ultra Violet B (UVB). """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uvb_reading = sensors_direct.pimoroni_veml6075_a.ultra_violet()[1]
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        uvb_reading = sensors_direct.dummy_sensors.ultra_violet()[1]
    else:
        uvb_reading = no_sensor_present
    return uvb_reading


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ. """
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
        xyz = no_sensor_present
    return xyz


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ. """
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
        xyz = no_sensor_present
    return xyz


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensors_direct.rp_sense_hat_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensors_direct.pimoroni_icm20948_a.gyroscope_xyz()
    elif app_config_access.installed_sensors.kootnet_dummy_sensor:
        xyz = sensors_direct.dummy_sensors.gyroscope_xyz()
    else:
        xyz = no_sensor_present
    return xyz


def display_message(text_msg):
    """ If a Supported Display is installed, shows provided text message on it. """
    text_msg = str(text_msg)
    logger.primary_logger.debug("* Displaying Text on LED Screen: " + text_msg)
    message_length = len(text_msg)

    if message_length > 0:
        text_msg = "-- " + text_msg
        if app_config_access.installed_sensors.kootnet_dummy_sensor:
            display_thread = Thread(target=sensors_direct.dummy_sensors.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)
        if app_config_access.installed_sensors.raspberry_pi_sense_hat:
            display_thread = Thread(target=sensors_direct.rp_sense_hat_a.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)
        if app_config_access.installed_sensors.pimoroni_matrix_11x7:
            display_thread = Thread(target=sensors_direct.pimoroni_matrix_11x7_a.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)
        if app_config_access.installed_sensors.pimoroni_st7735:
            display_thread = Thread(target=sensors_direct.pimoroni_st7735_a.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)
        if app_config_access.installed_sensors.pimoroni_mono_oled_luma:
            display_thread = Thread(target=sensors_direct.pimoroni_mono_oled_luma_a.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)
        if app_config_access.installed_sensors.pimoroni_enviroplus:
            display_thread = Thread(target=sensors_direct.pimoroni_enviroplus_a.display_text, args=[text_msg])
            _start_daemon_thread(display_thread)


def _start_daemon_thread(thread):
    thread.daemon = True
    thread.start()


def start_special_sensor_interactive_services():
    """ If available start additional hardware Interaction thread. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        text_name = "Sensor Interactive Service"
        function = sensors_direct.rp_sense_hat_a.start_joy_stick_commands
        app_cached_variables.interactive_sensor_thread = CreateMonitoredThread(function, thread_name=text_name)


def restart_services(sleep_before_restart=1):
    """ Reloads systemd service files & restarts KootnetSensors service. """
    time.sleep(sleep_before_restart)
    os.system(app_cached_variables.bash_commands["RestartService"])


def get_db_notes():
    """ Returns a comma separated string of Notes from the SQL Database. """
    sql_query = "SELECT " + app_cached_variables.database_variables.other_table_column_notes + \
                " FROM " + app_cached_variables.database_variables.table_other
    sql_db_notes = sqlite_database.sql_execute_get_data(sql_query)
    return _create_str_from_list(sql_db_notes)


def get_db_note_dates():
    """ Returns a comma separated string of Note Dates from the SQL Database. """
    sql_query_notes = "SELECT " + app_cached_variables.database_variables.all_tables_datetime + \
                      " FROM " + app_cached_variables.database_variables.table_other
    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)
    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    """ Returns a comma separated string of User Note Dates from the SQL Database. """
    sql_query_user_datetime = "SELECT " + app_cached_variables.database_variables.other_table_column_user_date_time + \
                              " FROM " + app_cached_variables.database_variables.table_other
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
    sql_data = sqlite_database.CreateOtherDataEntry()
    user_date_and_note = datetime_note.split(command_data_separator)

    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]

        sql_data.sensor_types = app_cached_variables.database_variables.all_tables_datetime + ", " + \
                                app_cached_variables.database_variables.other_table_column_user_date_time + ", " + \
                                app_cached_variables.database_variables.other_table_column_notes
        sql_data.sensor_readings = "'" + current_datetime + "','" + custom_datetime + "','" + note + "'"

        sql_execute = (sql_data.sql_query_start + sql_data.sensor_types + sql_data.sql_query_values_start +
                       sql_data.sensor_readings + sql_data.sql_query_values_end)

        sqlite_database.write_to_sql_database(sql_execute)
    else:
        logger.sensors_logger.error("Unable to add bad Note")


def update_note_in_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then updates the note in the SQL Database. """
    data_list = datetime_note.split(command_data_separator)

    try:
        current_datetime = "'" + data_list[0] + "'"
        user_datetime = "'" + data_list[1] + "'"
        note = "'" + data_list[2] + "'"

        sql_execute = "UPDATE OtherData SET " + "Notes = " + note + \
                      ",UserDateTime = " + user_datetime + " WHERE DateTime = " + current_datetime
        sqlite_database.write_to_sql_database(sql_execute)
    except Exception as error:
        logger.primary_logger.error("DB note update error: " + str(error))


def delete_db_note(note_datetime):
    """ Deletes a Note from the SQL Database based on it's DateTime entry. """
    sql_query = "DELETE FROM " + str(app_cached_variables.database_variables.table_other) + \
                " WHERE " + str(app_cached_variables.database_variables.all_tables_datetime) + \
                " = '" + note_datetime + "'"
    sqlite_database.write_to_sql_database(sql_query)
