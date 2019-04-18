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
from shutil import disk_usage
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import variables
from operations_modules import sqlite_database
from operations_modules import configuration_main
from operations_modules import software_version
from sensor_modules import linux_os
from sensor_modules import pimoroni_as7262
from sensor_modules import pimoroni_bh1745
from sensor_modules import pimoroni_bme680
from sensor_modules import pimoroni_enviro
from sensor_modules import pimoroni_lsm303d
from sensor_modules import pimoroni_ltr_559
from sensor_modules import pimoroni_vl53l1x
from sensor_modules import raspberry_pi_sensehat
from sensor_modules import raspberry_pi_system

if software_version.old_version == software_version.version:
    # Initialize sensor access, based on installed sensors file
    if configuration_main.installed_sensors.linux_system:
        os_sensor_access = linux_os.CreateLinuxSystem()
    if configuration_main.installed_sensors.raspberry_pi_zero_w or \
            configuration_main.installed_sensors.raspberry_pi_3b_plus:
        system_sensor_access = raspberry_pi_system.CreateRPSystem()
    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
    if configuration_main.installed_sensors.pimoroni_bh1745:
        pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
    if configuration_main.installed_sensors.pimoroni_as7262:
        pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
    if configuration_main.installed_sensors.pimoroni_bme680:
        pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
    if configuration_main.installed_sensors.pimoroni_enviro:
        pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
    if configuration_main.installed_sensors.pimoroni_lsm303d:
        pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
    if configuration_main.installed_sensors.pimoroni_ltr_559:
        pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
    if configuration_main.installed_sensors.pimoroni_vl53l1x:
        pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
else:
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    pass

command_data_separator = "[new_data_section]"


def get_sensor_readings():
    """ Returns sensor types and readings for interval and trigger sensors in html table format. """

    return_data = ""
    return_types = ""
    interval_data = get_interval_sensor_readings()

    str_interval_types = interval_data.sensor_types.split(",")
    str_interval_data = interval_data.sensor_readings.split(",")

    count = 0
    for interval_type in str_interval_types:
        return_types += "<th><span style='background-color: #00ffff;'>" + interval_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + str_interval_data[count] + "</span></th>"
        count = count + 1

    return [return_types, return_data]


def get_system_information():
    """ Returns System Information needed for a Control Center 'System Report'. """
    free_disk = disk_usage("/")[2]

    try:
        str_sensor_data = get_hostname() + \
                          "," + get_ip() + \
                          "," + str(get_system_datetime()) + \
                          "," + str(get_system_uptime()) + \
                          "," + str(software_version.version) + \
                          "," + str(round(float(get_cpu_temperature()), 2)) + \
                          "," + str(round(free_disk / (2 ** 30), 2)) + \
                          "," + str(get_db_size()) + \
                          "," + str(get_last_updated())
    except Exception as error:
        logger.network_logger.error("Sensor reading failed - " + str(error))
        str_sensor_data = "Sensor, Data Retrieval, Failed, 0, 0, 0, 0, 0, 0, 0, 0, 0"

    return str_sensor_data


def get_config_information():
    """ Opens configuration file and returns it as a comma separated string. """
    str_installed_sensors = configuration_main.installed_sensors.get_installed_names_str()

    try:
        tmp_str_config = str(configuration_main.current_config.enable_interval_recording) + \
                         "," + str(configuration_main.current_config.enable_trigger_recording) + \
                         "," + str(configuration_main.current_config.sleep_duration_interval) + \
                         "," + str(configuration_main.current_config.enable_custom_temp) + \
                         "," + str(configuration_main.current_config.temperature_offset) + \
                         "," + str(str_installed_sensors)

    except Exception as error:
        logger.network_logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, 0, 0"

    return tmp_str_config


def get_interval_sensor_readings():
    """ Returns Interval sensor readings from installed sensors (set in installed sensors file). """
    interval_data = sqlite_database.CreateIntervalDatabaseData()

    interval_data.sensor_types = "DateTime, "
    interval_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if configuration_main.installed_sensors.linux_system:
        interval_data.sensor_types += "SensorName, IP, SensorUpTime, SystemTemp, "

        if configuration_main.installed_sensors.raspberry_pi_3b_plus or \
                configuration_main.installed_sensors.raspberry_pi_zero_w:
            cpu_temp = str(system_sensor_access.cpu_temperature())
        else:
            cpu_temp = None

        interval_data.sensor_readings += "'" + str(os_sensor_access.get_hostname()) + "', '" + \
                                         str(os_sensor_access.get_ip()) + "', '" + \
                                         str(os_sensor_access.get_uptime()) + "', '" + \
                                         cpu_temp + "', "

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        interval_data.sensor_types += "EnvironmentTemp, " \
                                      "EnvTempOffset, " \
                                      "Pressure, " \
                                      "Humidity, " \
                                      "Acc_X, Acc_Y, Acc_Z, Mag_X, Mag_Y, Mag_Z, Gyro_X, Gyro_Y, Gyro_Z, "

        interval_data.sensor_readings += "'" + str(rp_sense_hat_sensor_access.temperature()) + "', '" + \
                                         str(configuration_main.current_config.temperature_offset) + "', '" + \
                                         str(rp_sense_hat_sensor_access.pressure()) + "', '" + \
                                         str(rp_sense_hat_sensor_access.humidity()) + "', "

        acc_x, acc_y, acc_z = rp_sense_hat_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = rp_sense_hat_sensor_access.magnetometer_xyz()
        gyro_x, gyro_y, gyro_z = rp_sense_hat_sensor_access.gyroscope_xyz()

        interval_data.sensor_readings += "'" + str(acc_x) + "', '" + \
                                         str(acc_y) + "', '" + \
                                         str(acc_z) + "', '" + \
                                         str(mag_x) + "', '" + \
                                         str(mag_y) + "', '" + \
                                         str(mag_z) + "', '" + \
                                         str(gyro_x) + "', '" + \
                                         str(gyro_y) + "', '" + \
                                         str(gyro_z) + "', "

    if configuration_main.installed_sensors.pimoroni_bh1745:
        rgb_colour = pimoroni_bh1745_sensor_access.ems()

        interval_data.sensor_types += "Lumen, Red, Green, Blue, "
        interval_data.sensor_readings += "'" + str(pimoroni_bh1745_sensor_access.lumen()) + "', '" + \
                                         str(rgb_colour[0]) + "', '" + \
                                         str(rgb_colour[1]) + "', '" + \
                                         str(rgb_colour[2]) + "', "
    if configuration_main.installed_sensors.pimoroni_as7262:
        ems_colors = pimoroni_as7262_sensor_access.spectral_six_channel()

        interval_data.sensor_types += "Red, Orange, Yellow, Green, Blue, Violet, "
        interval_data.sensor_readings += "'" + str(ems_colors[0]) + "', '" + \
                                         str(ems_colors[1]) + "', '" + \
                                         str(ems_colors[2]) + "', '" + \
                                         str(ems_colors[3]) + "', '" + \
                                         str(ems_colors[4]) + "', '" + \
                                         str(ems_colors[5]) + "', "

    if configuration_main.installed_sensors.pimoroni_bme680:
        interval_data.sensor_types += "EnvironmentTemp, EnvTempOffset, Pressure, Humidity, "

        interval_data.sensor_readings += "'" + str(pimoroni_bme680_sensor_access.temperature()) + "', '" + \
                                         str(configuration_main.current_config.temperature_offset) + "', '" + \
                                         str(pimoroni_bme680_sensor_access.pressure()) + "', '" + \
                                         str(pimoroni_bme680_sensor_access.humidity()) + "', "

    if configuration_main.installed_sensors.pimoroni_enviro:
        rgb_colour = pimoroni_enviro_sensor_access.ems()

        interval_data.sensor_types += \
            "EnvironmentTemp, " \
            "EnvTempOffset, " \
            "Pressure, " \
            "Lumen, " \
            "Red, " \
            "Green, " \
            "Blue, " \
            "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        interval_data.sensor_readings += "'" + str(pimoroni_enviro_sensor_access.temperature()) + "', '" + \
                                         str(configuration_main.current_config.temperature_offset) + "', '" + \
                                         str(pimoroni_enviro_sensor_access.pressure()) + "', '" + \
                                         str(pimoroni_enviro_sensor_access.lumen()) + "', '" + \
                                         str(rgb_colour[0]) + "', '" + \
                                         str(rgb_colour[1]) + "', '" + \
                                         str(rgb_colour[2]) + "', "

        acc_x, acc_y, acc_z = pimoroni_enviro_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_enviro_sensor_access.magnetometer_xyz()

        interval_data.sensor_readings += "'" + str(acc_x) + "', '" + \
                                         str(acc_y) + "', '" + \
                                         str(acc_z) + "', '" + \
                                         str(mag_x) + "', '" + \
                                         str(mag_y) + "', '" + \
                                         str(mag_z) + "', "
    if configuration_main.installed_sensors.pimoroni_ltr_559:
        interval_data.sensor_types += "Lumen, "
        interval_data.sensor_readings += "'" + str(pimoroni_ltr_559_sensor_access.lumen()) + "', "

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        interval_data.sensor_types += "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        acc_x, acc_y, acc_z = pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_lsm303d_sensor_access.magnetometer_xyz()

        interval_data.sensor_readings += "'" + str(acc_x) + "', '" + \
                                         str(acc_y) + "', '" + \
                                         str(acc_z) + "', '" + \
                                         str(mag_x) + "', '" + \
                                         str(mag_y) + "', '" + \
                                         str(mag_z) + "', "

    interval_data.sensor_types = interval_data.sensor_types[:-2]
    interval_data.sensor_readings = interval_data.sensor_readings[:-2]

    if interval_data.sensor_types != "DateTime":
        return interval_data


def get_trigger_sensor_readings():
    """ Returns Trigger sensor readings from installed sensors (set in installed sensors file). """
    trigger_data = sqlite_database.CreateTriggerDatabaseData()
    trigger_data.sensor_types = "DateTime, "
    trigger_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if configuration_main.installed_sensors.linux_system:
        sensor_types = "SensorName, IP, "
        sensor_readings = "'" + str(os_sensor_access.get_hostname()) + "', '" + str(os_sensor_access.get_ip()) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        sensor_types = "Acc_X, Acc_Y, Acc_Z, Mag_X, Mag_Y, Mag_Z, Gyro_X, Gyro_Y, Gyro_Z, "

        acc_x, acc_y, acc_z = rp_sense_hat_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = rp_sense_hat_sensor_access.magnetometer_xyz()
        gyro_x, gyro_y, gyro_z = rp_sense_hat_sensor_access.gyroscope_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', '" + \
                          str(gyro_x) + "', '" + \
                          str(gyro_y) + "', '" + \
                          str(gyro_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if configuration_main.installed_sensors.pimoroni_enviro:
        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        acc_x, acc_y, acc_z = pimoroni_enviro_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_enviro_sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        acc_x, acc_y, acc_z = pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_lsm303d_sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    trigger_data.sensor_types = trigger_data.sensor_types[:-2]
    trigger_data.sensor_readings = trigger_data.sensor_readings[:-2]

    if trigger_data.sensor_types != "DateTime":
        return trigger_data


def get_hostname():
    """ Returns sensors hostname. """
    if configuration_main.installed_sensors.linux_system:
        return os_sensor_access.get_hostname()
    else:
        return "NoSensor"


def get_ip():
    """ Returns sensor IP Address. """
    if configuration_main.installed_sensors.linux_system:
        return os_sensor_access.get_ip()
    else:
        return "NoSensor"


def get_system_datetime():
    if configuration_main.installed_sensors.linux_system:
        return os_sensor_access.get_sys_datetime()
    else:
        return "NoSensor"


def get_uptime_str():
    """ Converts provided minutes into a human readable string. """
    if configuration_main.installed_sensors.linux_system:
        var_minutes = os_sensor_access.get_uptime()
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
        return "NoSensor"


def get_system_uptime():
    """ Returns sensors system UpTime. """
    if configuration_main.installed_sensors.linux_system:
        sensor_uptime = os_sensor_access.get_uptime()
        return sensor_uptime
    else:
        return "NoSensor"


def get_db_size():
    if configuration_main.installed_sensors.linux_system:
        return os_sensor_access.get_sql_db_size()
    else:
        return "NoSensor"


def get_last_updated():
    """ Returns when the sensor programs were last updated and how. """
    try:
        last_updated_file = open(file_locations.last_updated_file_location, "r")
        tmp_last_updated = last_updated_file.readlines()
        last_updated_file.close()
        last_updated = str(tmp_last_updated[0]) + str(tmp_last_updated[1])
    except Exception as error:
        logger.network_logger.error("Unable to Load Last Updated File: " + str(error))
        last_updated = "N/A"

    return last_updated.strip()


def get_cpu_temperature():
    """ Returns sensors CPU temperature. """
    if configuration_main.installed_sensors.raspberry_pi_zero_w or \
            configuration_main.installed_sensors.raspberry_pi_3b_plus:
        temperature = system_sensor_access.cpu_temperature()
        return temperature
    else:
        return "NoSensor"


def get_sensor_temperature():
    """ Returns sensors Environmental temperature. """
    if configuration_main.installed_sensors.pimoroni_enviro:
        temperature = pimoroni_enviro_sensor_access.temperature()
        return temperature
    elif configuration_main.installed_sensors.pimoroni_bme680:
        temperature = pimoroni_bme680_sensor_access.temperature()
        return temperature
    elif configuration_main.installed_sensors.raspberry_pi_sense_hat:
        temperature = rp_sense_hat_sensor_access.temperature()
        return temperature
    else:
        return "NoSensor"


def get_pressure():
    """ Returns sensors pressure. """
    if configuration_main.installed_sensors.pimoroni_enviro:
        pressure = pimoroni_enviro_sensor_access.pressure()
        return pressure
    elif configuration_main.installed_sensors.pimoroni_bme680:
        pressure = pimoroni_bme680_sensor_access.pressure()
        return pressure
    elif configuration_main.installed_sensors.raspberry_pi_sense_hat:
        pressure = rp_sense_hat_sensor_access.pressure()
        return pressure
    else:
        return "NoSensor"


def get_humidity():
    """ Returns sensors humidity. """
    if configuration_main.installed_sensors.pimoroni_bme680:
        humidity = pimoroni_bme680_sensor_access.humidity()
        return humidity
    elif configuration_main.installed_sensors.raspberry_pi_sense_hat:
        humidity = rp_sense_hat_sensor_access.humidity()
        return humidity
    else:
        return "NoSensor"


def get_lumen():
    """ Returns sensors lumen. """
    if configuration_main.installed_sensors.pimoroni_enviro:
        lumen = pimoroni_enviro_sensor_access.lumen()
        return lumen
    elif configuration_main.installed_sensors.pimoroni_bh1745:
        lumen = pimoroni_bh1745_sensor_access.lumen()
        return lumen
    elif configuration_main.installed_sensors.pimoroni_ltr_559:
        lumen = pimoroni_ltr_559_sensor_access.lumen()
        return lumen
    else:
        return "NoSensor"


def get_ems():
    """ Returns Electromagnetic Spectrum Wavelengths in the form of Red, Orange, Yellow, Green, Cyan, Blue, Violet. """
    if configuration_main.installed_sensors.pimoroni_enviro:
        rgb = pimoroni_enviro_sensor_access.ems()
        return rgb
    elif configuration_main.installed_sensors.pimoroni_bh1745:
        rgb = pimoroni_bh1745_sensor_access.ems()
        return rgb
    elif configuration_main.installed_sensors.pimoroni_as7262:
        six_chan = pimoroni_as7262_sensor_access.spectral_six_channel()
        return six_chan
    else:
        return "NoSensor"


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ. """
    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.accelerometer_xyz()
        return xyz
    elif configuration_main.installed_sensors.pimoroni_enviro:
        xyz = pimoroni_enviro_sensor_access.accelerometer_xyz()
        return xyz
    elif configuration_main.installed_sensors.pimoroni_lsm303d:
        xyz = pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ. """
    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.magnetometer_xyz()
        return xyz
    elif configuration_main.installed_sensors.pimoroni_enviro:
        xyz = pimoroni_enviro_sensor_access.magnetometer_xyz()
        return xyz
    elif configuration_main.installed_sensors.pimoroni_lsm303d:
        xyz = pimoroni_lsm303d_sensor_access.magnetometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.gyroscope_xyz()
        return xyz
    else:
        return "NoSensor"


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(variables.restart_sensor_services_command)


def add_note_to_database(datetime_note):
    sql_data = sqlite_database.CreateOtherDataEntry()
    user_date_and_note = datetime_note.split(command_data_separator)

    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-6] + "000"
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]
    else:
        custom_datetime = "NA"
        note = user_date_and_note[0]

    sql_data.sensor_types = "DateTime, UserDateTime, Notes"
    sql_data.sensor_readings = "'" + current_datetime + "','" + custom_datetime + "','" + note + "'"

    sql_execute = (sql_data.sql_query_start + sql_data.sensor_types +
                   sql_data.sql_query_values_start + sql_data.sensor_readings +
                   sql_data.sql_query_values_end)

    sqlite_database.write_to_sql_database(sql_execute)


def update_note_in_database(datetime_note):
    data_list = datetime_note.split(command_data_separator)

    try:
        current_datetime = "'" + data_list[0] + "'"
        user_datetime = "'" + data_list[1] + "'"
        note = "'" + data_list[2] + "'"

        sql_execute = "UPDATE OtherData SET Notes = " + note + \
                      ",UserDateTime = " + user_datetime + \
                      " WHERE DateTime = " + current_datetime

        sqlite_database.write_to_sql_database(sql_execute)
    except Exception as error:
        logger.primary_logger.error("DB note update error: " + str(error))
