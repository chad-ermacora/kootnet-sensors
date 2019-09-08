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
import psutil
import math
from time import sleep
from datetime import datetime
from threading import Thread
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import os_cli_commands
from operations_modules import app_generic_functions
from operations_modules import sqlite_database
from operations_modules import app_config_access
from operations_modules import software_version
from sensor_modules import sensors_initialization as sensor_direct_access

command_data_separator = app_config_access.command_data_separator
no_sensor_present = "NoSensor"


def get_sensor_readings():
    """
    Returns sensor types and readings for interval and trigger sensors in html table format.
    Used in Control Center Readings Reports.
    """

    interval_readings = get_interval_sensor_readings().split(command_data_separator)

    str_interval_types = interval_readings[0].split(",")
    str_interval_types_data = interval_readings[1].split(",")

    return_data = ""
    return_types = ""
    for interval_type, interval_data in zip(str_interval_types, str_interval_types_data):
        return_types += "<th><span style='background-color: #00ffff;'>" + interval_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + interval_data + "</span></th>"

    return [return_types, return_data]


def get_system_information():
    """ Returns System Information needed for a Control Center 'System Report'. """
    free_disk = psutil.disk_usage("/")[2]

    ip_address = get_ip()
    try:
        str_sensor_data = get_hostname() + \
                          ",<a href='https://" + ip_address + ":10065/Quick' target='_blank'>" + ip_address + "</a>" + \
                          "," + str(get_system_datetime()) + \
                          "," + str(get_uptime_minutes()) + \
                          "," + str(software_version.version) + \
                          "," + str(round(float(get_cpu_temperature()), 2)) + \
                          "," + str(round(free_disk / (2 ** 30), 2)) + \
                          "," + str(get_db_size()) + \
                          "," + str(get_last_updated())
    except Exception as error:
        logger.network_logger.error("Sensor reading failed - " + str(error))
        str_sensor_data = "Sensor, Data Retrieval, Failed, 0, 0, 0, 0, 0"

    return str_sensor_data


def get_config_information():
    """ Opens configuration file and returns it as a comma separated string. """
    str_installed_sensors = app_config_access.installed_sensors.get_installed_names_str()

    try:
        tmp_str_config = str(app_config_access.current_config.enable_interval_recording) + "," + \
                         str(app_config_access.current_config.enable_trigger_recording) + "," + \
                         str(app_config_access.current_config.sleep_duration_interval) + "," + \
                         str(app_config_access.current_config.enable_custom_temp) + "," + \
                         str(app_config_access.current_config.temperature_offset) + "," + \
                         str(str_installed_sensors)

    except Exception as error:
        logger.network_logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, Error"

    return tmp_str_config


def get_interval_sensor_readings():
    """
    Returns Interval formatted sensor readings based on installed sensors.
    Format = 'CSV String Installed Sensor Types' + special separator + 'CSV String Sensor Readings'
    """

    sensor_types = [app_config_access.database_variables.all_tables_datetime]
    sensor_readings = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
    if app_config_access.installed_sensors.linux_system:
        sensor_types += [app_config_access.database_variables.sensor_name,
                         app_config_access.database_variables.ip,
                         app_config_access.database_variables.sensor_uptime]
        sensor_readings += [get_hostname(),
                                get_ip(),
                                get_uptime_minutes()]
    if app_config_access.installed_sensors.raspberry_pi:
        sensor_types.append(app_config_access.database_variables.system_temperature)
        sensor_readings.append(get_cpu_temperature())
    if app_config_access.installed_sensors.has_env_temperature:
        sensor_types.append(app_config_access.database_variables.env_temperature)
        sensor_types.append(app_config_access.database_variables.env_temperature_offset)
        sensor_readings.append(get_sensor_temperature())
        if app_config_access.current_config.enable_custom_temp:
            sensor_readings.append(app_config_access.current_config.temperature_offset)
        else:
            sensor_readings.append("0.0")
    if app_config_access.installed_sensors.has_pressure:
        sensor_types.append(app_config_access.database_variables.pressure)
        sensor_readings.append(get_pressure())
    if app_config_access.installed_sensors.has_altitude:
        sensor_types.append(app_config_access.database_variables.altitude)
        sensor_readings.append(get_altitude())
    if app_config_access.installed_sensors.has_humidity:
        sensor_types.append(app_config_access.database_variables.humidity)
        sensor_readings.append(get_humidity())
    if app_config_access.installed_sensors.has_distance:
        sensor_types.append(app_config_access.database_variables.distance)
        sensor_readings.append(get_distance())
    if app_config_access.installed_sensors.has_gas:
        gas_index = get_gas_resistance_index()
        gas_oxidised = get_gas_oxidised()
        gas_reduced = get_gas_reduced()
        gas_nh3 = get_gas_nh3()

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
        pm1_reading = get_particulate_matter_1()
        pm2_5_reading = get_particulate_matter_2_5()
        pm10_reading = get_particulate_matter_10()

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
        sensor_readings.append(get_lumen())
    if app_config_access.installed_sensors.has_red:
        ems_colours = get_ems()

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
        uva_reading = get_ultra_violet_a()
        uvb_reading = get_ultra_violet_b()

        if valid_sensor_reading(uva_reading):
            sensor_types.append(app_config_access.database_variables.ultra_violet_a)
            sensor_readings.append(get_ultra_violet_a())
        if valid_sensor_reading(uvb_reading):
            sensor_types.append(app_config_access.database_variables.ultra_violet_b)
            sensor_readings.append(get_ultra_violet_b())
    if app_config_access.installed_sensors.has_acc:
        accelerometer_readings = get_accelerometer_xyz()

        sensor_types += [app_config_access.database_variables.acc_x,
                         app_config_access.database_variables.acc_y,
                         app_config_access.database_variables.acc_z]
        sensor_readings += [accelerometer_readings[0],
                                accelerometer_readings[1],
                                accelerometer_readings[2]]
    if app_config_access.installed_sensors.has_mag:
        magnetometer_readings = get_magnetometer_xyz()

        sensor_types += [app_config_access.database_variables.mag_x,
                         app_config_access.database_variables.mag_y,
                         app_config_access.database_variables.mag_z]
        sensor_readings += [magnetometer_readings[0],
                                magnetometer_readings[1],
                                magnetometer_readings[2]]
    if app_config_access.installed_sensors.has_gyro:
        gyroscope_readings = get_gyroscope_xyz()

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


def valid_sensor_reading(reading):
    if reading == no_sensor_present:
        return False
    return True


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


def get_operating_system_name():
    """ Returns sensors Operating System Name and version. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_os_name_version()
    else:
        return no_sensor_present


def get_hostname():
    """ Returns sensors hostname. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_hostname()
    else:
        return no_sensor_present


def get_ip():
    """ Returns sensor IP Address as a String. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_ip()
    else:
        return no_sensor_present


def get_disk_usage_percent():
    """ Returns sensor root disk usage as a %. """
    try:
        drive_information = psutil.disk_usage("/")
        return_disk_usage = drive_information[3]
    except Exception as error:
        logger.sensors_logger.error("Get Memory Usage Error: " + str(error))
        return_disk_usage = "Error"
    return return_disk_usage


def get_memory_usage_percent():
    """ Returns sensor RAM usage as a %. """
    try:
        mem = psutil.virtual_memory()
        return_mem = mem[2]
    except Exception as error:
        logger.sensors_logger.error("Get Memory Usage Error: " + str(error))
        return_mem = "Error"
    return return_mem


def get_system_datetime():
    """ Returns System DateTime in format YYYY-MM-DD HH:MM as a String. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_sys_datetime_str()
    else:
        return no_sensor_present


def get_uptime_minutes():
    """ Returns System UpTime in Minutes as an Integer. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_uptime()
    else:
        return no_sensor_present


def get_uptime_str():
    """ Returns System UpTime as a human readable String. """
    if app_config_access.installed_sensors.linux_system:
        var_minutes = sensor_direct_access.os_sensor_access.get_uptime()
        str_day_hour_min = ""

        try:
            uptime_days = int(float(var_minutes) // 1440)
            uptime_hours = int((float(var_minutes) % 1440) // 60)
            uptime_min = int(float(var_minutes) % 60)
            if uptime_days:
                if uptime_days > 1:
                    str_day_hour_min = str(uptime_days) + " Days, "
                else:
                    str_day_hour_min = str(uptime_days) + " Day, "
            if uptime_hours:
                if uptime_hours > 1:
                    str_day_hour_min += str(uptime_hours) + " Hours & "
                else:
                    str_day_hour_min += str(uptime_hours) + " Hour & "

            str_day_hour_min += str(uptime_min) + " Min"

        except Exception as error:
            logger.sensors_logger.error("Unable to convert Minutes to days/hours.min: " + str(error))
            str_day_hour_min = var_minutes

        return str_day_hour_min
    else:
        return no_sensor_present


def get_system_reboot_count():
    """ Returns system reboot count from the SQL Database. """
    if app_config_access.installed_sensors.linux_system:
        reboot_count = sensor_direct_access.os_sensor_access.get_sensor_reboot_count()
        return reboot_count
    else:
        return no_sensor_present


def get_db_size():
    """ Returns SQL Database size in MB. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_sql_db_size()
    else:
        return no_sensor_present


def get_db_notes_count():
    """ Returns Number of Notes in the SQL Database. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_db_notes_count()
    else:
        return no_sensor_present


def get_db_first_last_date():
    """ Returns First and Last recorded date in the SQL Database as a String. """
    if app_config_access.installed_sensors.linux_system:
        return sensor_direct_access.os_sensor_access.get_db_first_last_date()
    else:
        return no_sensor_present


def get_last_updated():
    """ Returns when the sensor programs were last updated and how in a String. """
    last_updated = ""
    last_updated_file = app_generic_functions.get_file_content(file_locations.program_last_updated)
    try:
        last_updated_lines = last_updated_file.split("\n")
        last_updated += str(last_updated_lines[0]) + str(last_updated_lines[1])
    except Exception as error:
        logger.sensors_logger.warning("Invalid Kootnet Sensor's Last Updated File: " + str(error))
    return last_updated.strip()


def get_cpu_temperature():
    """ Returns sensors CPU temperature. """
    if app_config_access.installed_sensors.raspberry_pi:
        temperature = sensor_direct_access.system_sensor_access.cpu_temperature()
        return temperature
    else:
        return no_sensor_present


def get_sensor_temperature():
    """ Returns sensors Environmental temperature. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        temperature = sensor_direct_access.pimoroni_enviro_sensor_access.temperature()
        return temperature
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        temperature = sensor_direct_access.pimoroni_enviroplus_sensor_access.temperature()
        return temperature
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        temperature = sensor_direct_access.pimoroni_bmp280_sensor_access.temperature()
        return temperature
    elif app_config_access.installed_sensors.pimoroni_bme680:
        temperature = sensor_direct_access.pimoroni_bme680_sensor_access.temperature()
        return temperature
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        temperature = sensor_direct_access.rp_sense_hat_sensor_access.temperature()
        return temperature
    else:
        return no_sensor_present


def get_pressure():
    """ Returns sensors pressure. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        pressure = sensor_direct_access.pimoroni_enviro_sensor_access.pressure()
        return pressure
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        pressure = sensor_direct_access.pimoroni_enviroplus_sensor_access.pressure()
        return pressure
    elif app_config_access.installed_sensors.pimoroni_bmp280:
        pressure = sensor_direct_access.pimoroni_bmp280_sensor_access.pressure()
        return pressure
    elif app_config_access.installed_sensors.pimoroni_bme680:
        pressure = sensor_direct_access.pimoroni_bme680_sensor_access.pressure()
        return pressure
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        pressure = sensor_direct_access.rp_sense_hat_sensor_access.pressure()
        return pressure
    else:
        return no_sensor_present


def get_altitude():
    """ Returns sensors altitude. """
    if app_config_access.installed_sensors.pimoroni_bmp280:
        altitude = sensor_direct_access.pimoroni_bmp280_sensor_access.altitude()
        return altitude
    else:
        return no_sensor_present


def get_humidity():
    """ Returns sensors humidity. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        humidity = sensor_direct_access.pimoroni_enviroplus_sensor_access.humidity()
        return humidity
    elif app_config_access.installed_sensors.pimoroni_bme680:
        humidity = sensor_direct_access.pimoroni_bme680_sensor_access.humidity()
        return humidity
    elif app_config_access.installed_sensors.raspberry_pi_sense_hat:
        humidity = sensor_direct_access.rp_sense_hat_sensor_access.humidity()
        return humidity
    else:
        return no_sensor_present


def get_dew_point():
    """ Returns estimated dew point based on Temperature and Humidity. """
    variable_a = 17.27
    variable_b = 237.7

    env_temp = get_sensor_temperature()
    if app_config_access.current_config.enable_custom_temp:
        env_temp = env_temp + app_config_access.current_config.temperature_offset
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
        distance = sensor_direct_access.pimoroni_enviroplus_sensor_access.distance()
        return distance
    elif app_config_access.installed_sensors.pimoroni_vl53l1x:
        distance = sensor_direct_access.pimoroni_vl53l1x_sensor_access.distance()
        return distance
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        distance = sensor_direct_access.pimoroni_ltr_559_sensor_access.distance()
        return distance
    else:
        return no_sensor_present


def get_gas_resistance_index():
    """ Returns sensors gas resistance index. """
    if app_config_access.installed_sensors.pimoroni_bme680:
        index = sensor_direct_access.pimoroni_bme680_sensor_access.gas_resistance_index()
        return index
    else:
        return no_sensor_present


def get_gas_oxidised():
    """ Returns sensors gas reading for oxidising. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        oxidising = sensor_direct_access.pimoroni_enviroplus_sensor_access.gas_data()[0]
        return oxidising
    else:
        return no_sensor_present


def get_gas_reduced():
    """ Returns sensors gas reading for reducing. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        reducing = sensor_direct_access.pimoroni_enviroplus_sensor_access.gas_data()[1]
        return reducing
    else:
        return no_sensor_present


def get_gas_nh3():
    """ Returns sensors gas reading for NH3. """
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        nh3_reading = sensor_direct_access.pimoroni_enviroplus_sensor_access.gas_data()[2]
        return nh3_reading
    else:
        return no_sensor_present


def get_particulate_matter_1():
    """ Returns sensor reading for PM1. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm1_reading = sensor_direct_access.pimoroni_enviroplus_sensor_access.particulate_matter_data()[0]
        return pm1_reading
    else:
        return no_sensor_present


def get_particulate_matter_2_5():
    """ Returns sensor reading for PM2.5. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm2_5_reading = sensor_direct_access.pimoroni_enviroplus_sensor_access.particulate_matter_data()[1]
        return pm2_5_reading
    else:
        return no_sensor_present


def get_particulate_matter_10():
    """ Returns sensor reading for PM10. """
    if app_config_access.installed_sensors.pimoroni_enviroplus and \
            app_config_access.installed_sensors.pimoroni_pms5003:
        pm10_reading = sensor_direct_access.pimoroni_enviroplus_sensor_access.particulate_matter_data()[2]
        return pm10_reading
    else:
        return no_sensor_present


def get_lumen():
    """ Returns sensors lumen. """
    if app_config_access.installed_sensors.pimoroni_enviro:
        lumen = sensor_direct_access.pimoroni_enviro_sensor_access.lumen()
        return lumen
    elif app_config_access.installed_sensors.pimoroni_enviroplus:
        lumen = sensor_direct_access.pimoroni_enviroplus_sensor_access.lumen()
        return lumen
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        lumen = sensor_direct_access.pimoroni_bh1745_sensor_access.lumen()
        return lumen
    elif app_config_access.installed_sensors.pimoroni_ltr_559:
        lumen = sensor_direct_access.pimoroni_ltr_559_sensor_access.lumen()
        return lumen
    else:
        return no_sensor_present


def get_ems():
    """ Returns Electromagnetic Spectrum Wavelengths in the form of Red, Orange, Yellow, Green, Cyan, Blue, Violet. """
    if app_config_access.installed_sensors.pimoroni_as7262:
        six_chan = sensor_direct_access.pimoroni_as7262_sensor_access.spectral_six_channel()
        return six_chan
    elif app_config_access.installed_sensors.pimoroni_enviro:
        rgb = sensor_direct_access.pimoroni_enviro_sensor_access.ems()
        return rgb
    elif app_config_access.installed_sensors.pimoroni_bh1745:
        rgb = sensor_direct_access.pimoroni_bh1745_sensor_access.ems()
        return rgb
    else:
        return no_sensor_present


def get_ultra_violet_index():
    """ Returns Ultra Violet Index. """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uv_index_reading = sensor_direct_access.pimoroni_veml6075_sensor_access.ultra_violet_index()
        return uv_index_reading
    else:
        return no_sensor_present


def get_ultra_violet_a():
    """ Returns Ultra Violet A (UVA). """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uva_reading = sensor_direct_access.pimoroni_veml6075_sensor_access.ultra_violet()[0]
        return uva_reading
    else:
        return no_sensor_present


def get_ultra_violet_b():
    """ Returns Ultra Violet B (UVB). """
    if app_config_access.installed_sensors.pimoroni_veml6075:
        uvb_reading = sensor_direct_access.pimoroni_veml6075_sensor_access.ultra_violet()[1]
        return uvb_reading
    else:
        return no_sensor_present


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensor_direct_access.rp_sense_hat_sensor_access.accelerometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_enviro:
        xyz = sensor_direct_access.pimoroni_enviro_sensor_access.accelerometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_lsm303d:
        xyz = sensor_direct_access.pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensor_direct_access.pimoroni_icm20948_sensor_access.accelerometer_xyz()
        return xyz
    else:
        return no_sensor_present


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensor_direct_access.rp_sense_hat_sensor_access.magnetometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_enviro:
        xyz = sensor_direct_access.pimoroni_enviro_sensor_access.magnetometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_lsm303d:
        xyz = sensor_direct_access.pimoroni_lsm303d_sensor_access.magnetometer_xyz()
        return xyz
    elif app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensor_direct_access.pimoroni_icm20948_sensor_access.magnetometer_xyz()
        return xyz
    else:
        return no_sensor_present


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        xyz = sensor_direct_access.rp_sense_hat_sensor_access.gyroscope_xyz()
        return xyz
    if app_config_access.installed_sensors.pimoroni_icm20948:
        xyz = sensor_direct_access.pimoroni_icm20948_sensor_access.gyroscope_xyz()
        return xyz
    else:
        return no_sensor_present


def _empty_thread():
    """
    Used to replace a threaded function that is disabled.
    """
    while True:
        sleep(600)


def display_message(text_message):
    """ If a Supported Display is installed, shows provided text message on it. """
    text_message = str(text_message)
    logger.primary_logger.debug("* Displaying Text on LED Screen: " + text_message)
    if app_config_access.installed_sensors.has_display and app_config_access.current_config.enable_display:
        message_length = len(text_message)

        if message_length > 0:
            text_message = "-- " + text_message
            if app_config_access.installed_sensors.raspberry_pi_sense_hat:
                display_thread = Thread(target=sensor_direct_access.rp_sense_hat_sensor_access.display_text,
                                        args=[text_message])
            elif app_config_access.installed_sensors.pimoroni_matrix_11x7:
                display_thread = Thread(target=sensor_direct_access.pimoroni_matrix_11x7_sensor_access.display_text,
                                        args=[text_message])
            elif app_config_access.installed_sensors.pimoroni_st7735:
                display_thread = Thread(target=sensor_direct_access.pimoroni_st7735_sensor_access.display_text,
                                        args=[text_message])
            elif app_config_access.installed_sensors.pimoroni_mono_oled_luma:
                display_thread = Thread(target=sensor_direct_access.pimoroni_mono_oled_luma_sensor_access.display_text,
                                        args=[text_message])
            elif app_config_access.installed_sensors.pimoroni_enviroplus:
                display_thread = Thread(target=sensor_direct_access.pimoroni_enviroplus_sensor_access.display_text,
                                        args=[text_message])
            else:
                display_thread = Thread(target=_empty_thread)
            display_thread.daemon = True
            display_thread.start()
    else:
        logger.primary_logger.debug("* Display Text: Sensor Display Disabled or not installed")


def restart_services():
    """ Reloads systemd service files & restarts KootnetSensors service. """
    os.system(os_cli_commands.restart_sensor_services_command)


def get_db_notes():
    """ Returns a comma separated string of Notes from the SQL Database. """
    sql_query = "SELECT " + \
                app_config_access.database_variables.other_table_column_notes + \
                " FROM " + \
                app_config_access.database_variables.table_other

    sql_db_notes = sqlite_database.sql_execute_get_data(sql_query)

    return _create_str_from_list(sql_db_notes)


def get_db_note_dates():
    """ Returns a comma separated string of Note Dates from the SQL Database. """
    sql_query_notes = "SELECT " + \
                      app_config_access.database_variables.all_tables_datetime + \
                      " FROM " + \
                      app_config_access.database_variables.table_other

    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)

    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    """ Returns a comma separated string of User Note Dates from the SQL Database. """
    sql_query_user_datetime = "SELECT " + \
                              app_config_access.database_variables.other_table_column_user_date_time + \
                              " FROM " + \
                              app_config_access.database_variables.table_other

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

        sql_data.sensor_types = app_config_access.database_variables.all_tables_datetime + ", " + \
                                app_config_access.database_variables.other_table_column_user_date_time + ", " + \
                                app_config_access.database_variables.other_table_column_notes
        sql_data.sensor_readings = "'" + current_datetime + "','" + custom_datetime + "','" + note + "'"

        sql_execute = (sql_data.sql_query_start + sql_data.sensor_types +
                       sql_data.sql_query_values_start + sql_data.sensor_readings +
                       sql_data.sql_query_values_end)

        sqlite_database.sql_execute(sql_execute)
    else:
        logger.sensors_logger.error("Unable to add bad Note")


def update_note_in_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then updates the note in the SQL Database. """
    data_list = datetime_note.split(command_data_separator)

    try:
        current_datetime = "'" + data_list[0] + "'"
        user_datetime = "'" + data_list[1] + "'"
        note = "'" + data_list[2] + "'"

        sql_execute = "UPDATE OtherData SET " + \
                      "Notes = " + note + \
                      ",UserDateTime = " + user_datetime + \
                      " WHERE DateTime = " + current_datetime

        sqlite_database.sql_execute(sql_execute)
    except Exception as error:
        logger.primary_logger.error("DB note update error: " + str(error))


def delete_db_note(note_datetime):
    """ Deletes a Note from the SQL Database based on it's DateTime entry. """
    sql_query = "DELETE FROM " + \
                str(app_config_access.database_variables.table_other) + \
                " WHERE " + \
                str(app_config_access.database_variables.all_tables_datetime) + \
                " = '" + note_datetime + "'"

    sqlite_database.sql_execute(sql_query)


def upgrade_linux_os():
    """ Runs a bash command to upgrade the Linux System with apt-get. """
    try:
        os.system(os_cli_commands.bash_commands["UpgradeSystemOS"])
        app_config_access.linux_os_upgrade_ready = True
        logger.primary_logger.warning("Linux OS Upgrade Done")
    except Exception as error:
        logger.primary_logger.error("Linux OS Upgrade Error: " + str(error))
