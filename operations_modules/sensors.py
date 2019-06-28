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
from datetime import datetime
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_variables
from operations_modules import sqlite_database
from operations_modules import configuration_main
from operations_modules import software_version
from sensor_modules import linux_os
from sensor_modules import pimoroni_as7262
from sensor_modules import pimoroni_bh1745
from sensor_modules import pimoroni_bme680
from sensor_modules import pimoroni_bmp280
from sensor_modules import pimoroni_enviro
from sensor_modules import pimoroni_enviroplus
from sensor_modules import pimoroni_lsm303d
from sensor_modules import pimoroni_icm20948
from sensor_modules import pimoroni_ltr_559
from sensor_modules import pimoroni_vl53l1x
from sensor_modules import pimoroni_veml6075
from sensor_modules import raspberry_pi_sensehat
from sensor_modules import raspberry_pi_system

if software_version.old_version == software_version.version:
    # Initialize sensor access, based on installed sensors file
    if configuration_main.installed_sensors.linux_system:
        try:
            os_sensor_access = linux_os.CreateLinuxSystem()
        except Exception as sensor_error:
            logger.primary_logger.error("Linux OS Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.raspberry_pi_zero_w or \
            configuration_main.installed_sensors.raspberry_pi_3b_plus:
        try:
            system_sensor_access = raspberry_pi_system.CreateRPSystem()
        except Exception as sensor_error:
            logger.primary_logger.warning("Raspberry Pi Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                system_sensor_access = raspberry_pi_system.CreateRPSystem()
                logger.primary_logger.info("Raspberry Pi Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Raspberry Pi Sensor Attempt 2 Failed Skipping Sensor - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        try:
            rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
        except Exception as sensor_error:
            logger.primary_logger.warning("RP SenseHAT Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
                logger.primary_logger.info("RP SenseHAT Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("RP SenseHAT Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bh1745:
        try:
            pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BH1745 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
                logger.primary_logger.info("Pimoroni BH1745 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BH1745 Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_as7262:
        try:
            pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni AS7262 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
                logger.primary_logger.info("Pimoroni AS7262 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni AS7262 Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bme680:
        try:
            pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BME680 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
                logger.primary_logger.info("Pimoroni BME680 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BME680 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bmp280:
        try:
            pimoroni_bmp280_sensor_access = pimoroni_bmp280.CreateBMP280()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BMP280 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bmp280_sensor_access = pimoroni_bmp280.CreateBMP280()
                logger.primary_logger.info("Pimoroni BMP280 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BMP280 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviro:
        try:
            pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni EnviroPHAT Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
                logger.primary_logger.info("Pimoroni EnviroPHAT Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni EnviroPHAT Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviroplus:
        try:
            pimoroni_enviroplus_sensor_access = pimoroni_enviroplus.CreateEnviroPlus()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni Enviro+ Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_enviroplus_sensor_access = pimoroni_enviroplus.CreateEnviroPlus()
                logger.primary_logger.info("Pimoroni Enviro+ Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni Enviro+ Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        try:
            pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LSM303D Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
                logger.primary_logger.info("Pimoroni LSM303D Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni LSM303D Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_icm20948:
        try:
            pimoroni_icm20948_sensor_access = pimoroni_icm20948.CreateICM20948()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni ICM20948 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_icm20948_sensor_access = pimoroni_icm20948.CreateICM20948()
                logger.primary_logger.info("Pimoroni ICM20948 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni ICM20948 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_ltr_559:
        try:
            pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LTR559 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
                logger.primary_logger.info("Pimoroni LTR559 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni LTR559 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_vl53l1x:
        try:
            pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VL53L1X Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
                logger.primary_logger.info("Pimoroni VL53L1X Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni VL53L1X Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_veml6075:
        try:
            pimoroni_veml6075_sensor_access = pimoroni_veml6075.CreateVEML6075()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VEML6075 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_veml6075_sensor_access = pimoroni_veml6075.CreateVEML6075()
                logger.primary_logger.info("Pimoroni VEML6075 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni VEML6075 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))
else:
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    pass

database_columns_and_tables = app_variables.CreateDatabaseVariables()
command_data_separator = "[new_data_section]"


def get_sensor_readings():
    """ Returns sensor types and readings for interval and trigger sensors in html table format. """

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
                          ",<a href='http://" + ip_address + ":10065/Quick' target='_blank'>" + ip_address + "</a>" + \
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
        tmp_str_config = str(configuration_main.current_config.enable_interval_recording) + "," + \
                         str(configuration_main.current_config.enable_trigger_recording) + "," + \
                         str(configuration_main.current_config.sleep_duration_interval) + "," + \
                         str(configuration_main.current_config.enable_custom_temp) + "," + \
                         str(configuration_main.current_config.temperature_offset) + "," + \
                         str(str_installed_sensors)

    except Exception as error:
        logger.network_logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, 0, 0"

    return tmp_str_config


def get_interval_sensor_readings():
    """ Returns Interval sensor readings from installed sensors (set in installed sensors file). """
    interval_data = sqlite_database.CreateIntervalDatabaseData()

    interval_data.sensor_types = configuration_main.database_variables.all_tables_datetime + ", "
    interval_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if configuration_main.installed_sensors.linux_system:
        interval_data.sensor_types += configuration_main.database_variables.sensor_name + ", " + \
                                      configuration_main.database_variables.ip + ", " + \
                                      configuration_main.database_variables.sensor_uptime + ", " + \
                                      configuration_main.database_variables.system_temperature + ", "

        if configuration_main.installed_sensors.raspberry_pi_3b_plus or \
                configuration_main.installed_sensors.raspberry_pi_zero_w:
            cpu_temp = str(get_cpu_temperature())
        else:
            cpu_temp = None

        interval_data.sensor_readings += "'" + get_hostname() + "', " + \
                                         "'" + get_ip() + "', " + \
                                         "'" + str(get_uptime_str()) + "', " + \
                                         "'" + str(cpu_temp) + "', "

    if configuration_main.installed_sensors.has_env_temperature:
        interval_data.sensor_types += configuration_main.database_variables.env_temperature + ", "
        interval_data.sensor_readings += "'" + str(get_sensor_temperature()) + "', "

    if configuration_main.installed_sensors.has_pressure:
        interval_data.sensor_types += configuration_main.database_variables.pressure + ", "
        interval_data.sensor_readings += "'" + str(get_pressure()) + "', "

    if configuration_main.installed_sensors.has_altitude:
        interval_data.sensor_types += configuration_main.database_variables.altitude + ", "
        interval_data.sensor_readings += "'" + str(get_altitude()) + "', "

    if configuration_main.installed_sensors.has_humidity:
        interval_data.sensor_types += configuration_main.database_variables.humidity + ", "
        interval_data.sensor_readings += "'" + str(get_humidity()) + "', "

    if configuration_main.installed_sensors.has_distance:
        interval_data.sensor_types += configuration_main.database_variables.distance + ", "
        interval_data.sensor_readings += "'" + str(get_distance()) + "', "

    if configuration_main.installed_sensors.has_gas:
        gas_index = get_gas_resistance_index()
        gas_oxidised = get_gas_oxidised()
        gas_reduced = get_gas_reduced()
        gas_nh3 = get_gas_nh3()

        if gas_index != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.gas_resistance_index + ", "
            interval_data.sensor_readings += "'" + str(get_gas_resistance_index()) + "', "
        if gas_oxidised != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.gas_oxidising + ", "
            interval_data.sensor_readings += "'" + str(get_gas_oxidised()) + "', "
        if gas_reduced != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.gas_reducing + ", "
            interval_data.sensor_readings += "'" + str(get_gas_reduced()) + "', "
        if gas_nh3 != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.gas_nh3 + ", "
            interval_data.sensor_readings += "'" + str(get_gas_nh3()) + "', "

    if configuration_main.installed_sensors.has_particulate_matter:
        pm1_reading = get_particulate_matter_1()
        pm2_5_reading = get_particulate_matter_2_5()
        pm10_reading = get_particulate_matter_10()

        if pm1_reading != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.particulate_matter_1 + ", "
            interval_data.sensor_readings += "'" + str(get_particulate_matter_1()) + "', "
        if pm2_5_reading != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.particulate_matter_2_5 + ", "
            interval_data.sensor_readings += "'" + str(get_particulate_matter_2_5()) + "', "
        if pm10_reading != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.particulate_matter_10 + ", "
            interval_data.sensor_readings += "'" + str(get_particulate_matter_10()) + "', "

    if configuration_main.installed_sensors.has_lumen:
        interval_data.sensor_types += configuration_main.database_variables.lumen + ", "
        interval_data.sensor_readings += "'" + str(get_lumen()) + "', "

    if configuration_main.installed_sensors.has_red:
        ems_colours = get_ems()

        if len(ems_colours) == 3:
            interval_data.sensor_types += configuration_main.database_variables.red + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[0]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.green + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[1]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.blue + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[2]) + "', "

        elif len(ems_colours) == 6:
            interval_data.sensor_types += configuration_main.database_variables.red + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[0]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.orange + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[1]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.yellow + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[2]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.green + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[3]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.blue + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[4]) + "', "

            interval_data.sensor_types += configuration_main.database_variables.violet + ", "
            interval_data.sensor_readings += "'" + str(ems_colours[5]) + "', "

    if configuration_main.installed_sensors.has_ultra_violet:
        uva_reading = get_ultra_violet_a()
        uvb_reading = get_ultra_violet_b()

        if uva_reading != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.ultra_violet_a + ", "
            interval_data.sensor_readings += "'" + str(get_ultra_violet_a()) + "', "
        if uvb_reading != "NoSensor":
            interval_data.sensor_types += configuration_main.database_variables.ultra_violet_b + ", "
            interval_data.sensor_readings += "'" + str(get_ultra_violet_b()) + "', "

    if configuration_main.installed_sensors.has_acc:
        accelerometer_readings = get_accelerometer_xyz()

        interval_data.sensor_types += configuration_main.database_variables.acc_x + ", "
        interval_data.sensor_readings += "'" + str(accelerometer_readings[0]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.acc_y + ", "
        interval_data.sensor_readings += "'" + str(accelerometer_readings[1]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.acc_z + ", "
        interval_data.sensor_readings += "'" + str(accelerometer_readings[2]) + "', "

    if configuration_main.installed_sensors.has_mag:
        magnetometer_readings = get_magnetometer_xyz()

        interval_data.sensor_types += configuration_main.database_variables.mag_x + ", "
        interval_data.sensor_readings += "'" + str(magnetometer_readings[0]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.mag_y + ", "
        interval_data.sensor_readings += "'" + str(magnetometer_readings[1]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.mag_z + ", "
        interval_data.sensor_readings += "'" + str(magnetometer_readings[2]) + "', "

    if configuration_main.installed_sensors.has_gyro:
        gyroscope_readings = get_gyroscope_xyz()

        interval_data.sensor_types += configuration_main.database_variables.gyro_x + ", "
        interval_data.sensor_readings += "'" + str(gyroscope_readings[0]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.gyro_y + ", "
        interval_data.sensor_readings += "'" + str(gyroscope_readings[1]) + "', "

        interval_data.sensor_types += configuration_main.database_variables.gyro_z + ", "
        interval_data.sensor_readings += "'" + str(gyroscope_readings[2]) + "', "

    return_interval_data = interval_data.sensor_types[:-2] + command_data_separator + interval_data.sensor_readings[:-2]

    return return_interval_data


def get_trigger_sensor_readings():
    """ Returns Trigger sensor readings from installed sensors (set in installed sensors file). """
    trigger_data = sqlite_database.CreateTriggerDatabaseData()
    trigger_data.sensor_types = configuration_main.database_variables.all_tables_datetime + ", "
    trigger_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if configuration_main.installed_sensors.linux_system:
        sensor_types = configuration_main.database_variables.sensor_name + ", " + \
                       configuration_main.database_variables.ip + ", "
        sensor_readings = "'" + str(get_hostname()) + "', '" + str(get_ip()) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        sensor_types = configuration_main.database_variables.acc_x + ", " + \
                       configuration_main.database_variables.acc_y + ", " + \
                       configuration_main.database_variables.acc_z + ", " + \
                       configuration_main.database_variables.mag_x + ", " + \
                       configuration_main.database_variables.mag_y + ", " + \
                       configuration_main.database_variables.mag_z + ", " + \
                       configuration_main.database_variables.gyro_x + ", " + \
                       configuration_main.database_variables.gyro_y + ", " + \
                       configuration_main.database_variables.gyro_z + ", "

        acc_x, acc_y, acc_z = get_accelerometer_xyz()
        mag_x, mag_y, mag_z = get_magnetometer_xyz()
        gyro_x, gyro_y, gyro_z = get_gyroscope_xyz()

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
        sensor_types = configuration_main.database_variables.acc_x + ", " + \
                       configuration_main.database_variables.acc_y + ", " + \
                       configuration_main.database_variables.acc_z + ", " + \
                       configuration_main.database_variables.mag_x + ", " + \
                       configuration_main.database_variables.mag_y + ", " + \
                       configuration_main.database_variables.mag_z + ", "

        acc_x, acc_y, acc_z = get_accelerometer_xyz()
        mag_x, mag_y, mag_z = get_magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        sensor_types = configuration_main.database_variables.acc_x + ", " + \
                       configuration_main.database_variables.acc_y + ", " + \
                       configuration_main.database_variables.acc_z + ", " + \
                       configuration_main.database_variables.mag_x + ", " + \
                       configuration_main.database_variables.mag_y + ", " + \
                       configuration_main.database_variables.mag_z + ", "

        acc_x, acc_y, acc_z = get_accelerometer_xyz()
        mag_x, mag_y, mag_z = get_magnetometer_xyz()

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

    if trigger_data.sensor_types != configuration_main.database_variables.all_tables_datetime:
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


def get_disk_usage_percent():
    """ Returns sensor root disk usage. """
    try:
        drive_information = psutil.disk_usage("/")
        return_disk_usage = drive_information[3]
    except Exception as error:
        logger.sensors_logger.error("Get Memory Usage Error: " + str(error))
        return_disk_usage = "Error"
    return return_disk_usage


def get_memory_usage_percent():
    """ Returns sensor RAM usage. """
    try:
        mem = psutil.virtual_memory()
        return_mem = mem[2]
    except Exception as error:
        logger.sensors_logger.error("Get Memory Usage Error: " + str(error))
        return_mem = "Error"
    return return_mem


def get_system_datetime():
    """ Returns sensor current DateTime. """
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
    """ Returns sensor SQLite Database size in MB. """
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
    elif configuration_main.installed_sensors.pimoroni_enviroplus:
        temperature = pimoroni_enviroplus_sensor_access.temperature()
        return temperature
    elif configuration_main.installed_sensors.pimoroni_bmp280:
        temperature = pimoroni_bmp280_sensor_access.temperature()
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
    elif configuration_main.installed_sensors.pimoroni_enviroplus:
        pressure = pimoroni_enviroplus_sensor_access.pressure()
        return pressure
    elif configuration_main.installed_sensors.pimoroni_bmp280:
        pressure = pimoroni_bmp280_sensor_access.pressure()
        return pressure
    elif configuration_main.installed_sensors.pimoroni_bme680:
        pressure = pimoroni_bme680_sensor_access.pressure()
        return pressure
    elif configuration_main.installed_sensors.raspberry_pi_sense_hat:
        pressure = rp_sense_hat_sensor_access.pressure()
        return pressure
    else:
        return "NoSensor"


def get_altitude():
    """ Returns sensors altitude. """
    if configuration_main.installed_sensors.pimoroni_bmp280:
        altitude = pimoroni_bmp280_sensor_access.altitude()
        return altitude
    else:
        return "NoSensor"


def get_humidity():
    """ Returns sensors humidity. """
    if configuration_main.installed_sensors.pimoroni_enviroplus:
        humidity = pimoroni_enviroplus_sensor_access.humidity()
        return humidity
    elif configuration_main.installed_sensors.pimoroni_bme680:
        humidity = pimoroni_bme680_sensor_access.humidity()
        return humidity
    elif configuration_main.installed_sensors.raspberry_pi_sense_hat:
        humidity = rp_sense_hat_sensor_access.humidity()
        return humidity
    else:
        return "NoSensor"


def get_distance():
    """ Returns sensors distance. """
    if configuration_main.installed_sensors.pimoroni_enviroplus:
        distance = pimoroni_enviroplus_sensor_access.distance()
        return distance
    elif configuration_main.installed_sensors.pimoroni_vl53l1x:
        distance = pimoroni_vl53l1x_sensor_access.distance()
        return distance
    elif configuration_main.installed_sensors.pimoroni_ltr_559:
        distance = pimoroni_ltr_559_sensor_access.distance()
        return distance
    else:
        return "NoSensor"


def get_gas_resistance_index():
    """ Returns sensors gas resistance index. """
    if configuration_main.installed_sensors.pimoroni_bme680:
        index = pimoroni_bme680_sensor_access.gas_resistance_index()
        return index
    else:
        return "NoSensor"


def get_gas_oxidised():
    """ Returns sensors gas reading for oxidising. """
    if configuration_main.installed_sensors.pimoroni_enviroplus:
        oxidising = pimoroni_enviroplus_sensor_access.gas_data()[0]
        return oxidising
    else:
        return "NoSensor"


def get_gas_reduced():
    """ Returns sensors gas reading for reducing. """
    if configuration_main.installed_sensors.pimoroni_enviroplus:
        reducing = pimoroni_enviroplus_sensor_access.gas_data()[1]
        return reducing
    else:
        return "NoSensor"


def get_gas_nh3():
    """ Returns sensors gas reading for NH3. """
    if configuration_main.installed_sensors.pimoroni_enviroplus:
        nh3_reading = pimoroni_enviroplus_sensor_access.gas_data()[2]
        return nh3_reading
    else:
        return "NoSensor"


def get_particulate_matter_1():
    """ Returns sensor reading for PM1. """
    if configuration_main.installed_sensors.pimoroni_enviroplus and \
            configuration_main.installed_sensors.pimoroni_pms5003:
        pm1_reading = pimoroni_enviroplus_sensor_access.particulate_matter_data()[0]
        return pm1_reading
    else:
        return "NoSensor"


def get_particulate_matter_2_5():
    """ Returns sensor reading for PM2.5. """
    if configuration_main.installed_sensors.pimoroni_enviroplus and \
            configuration_main.installed_sensors.pimoroni_pms5003:
        pm2_5_reading = pimoroni_enviroplus_sensor_access.particulate_matter_data()[1]
        return pm2_5_reading
    else:
        return "NoSensor"


def get_particulate_matter_10():
    """ Returns sensor reading for PM10. """
    if configuration_main.installed_sensors.pimoroni_enviroplus and \
            configuration_main.installed_sensors.pimoroni_pms5003:
        pm10_reading = pimoroni_enviroplus_sensor_access.particulate_matter_data()[2]
        return pm10_reading
    else:
        return "NoSensor"


def get_lumen():
    """ Returns sensors lumen. """
    if configuration_main.installed_sensors.pimoroni_enviro:
        lumen = pimoroni_enviro_sensor_access.lumen()
        return lumen
    elif configuration_main.installed_sensors.pimoroni_enviroplus:
        lumen = pimoroni_enviroplus_sensor_access.lumen()
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
    if configuration_main.installed_sensors.pimoroni_as7262:
        six_chan = pimoroni_as7262_sensor_access.spectral_six_channel()
        return six_chan
    elif configuration_main.installed_sensors.pimoroni_enviro:
        rgb = pimoroni_enviro_sensor_access.ems()
        return rgb
    elif configuration_main.installed_sensors.pimoroni_bh1745:
        rgb = pimoroni_bh1745_sensor_access.ems()
        return rgb
    else:
        return "NoSensor"


def get_ultra_violet_a():
    """ Returns Ultra Violet A (UVA). """
    if configuration_main.installed_sensors.pimoroni_veml6075:
        uva_reading = pimoroni_veml6075_sensor_access.ultra_violet()[0]
        return uva_reading


def get_ultra_violet_b():
    """ Returns Ultra Violet B (UVB). """
    if configuration_main.installed_sensors.pimoroni_veml6075:
        uvb_reading = pimoroni_veml6075_sensor_access.ultra_violet()[1]
        return uvb_reading


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
    elif configuration_main.installed_sensors.pimoroni_icm20948:
        xyz = pimoroni_icm20948_sensor_access.accelerometer_xyz()
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
    elif configuration_main.installed_sensors.pimoroni_icm20948:
        xyz = pimoroni_icm20948_sensor_access.magnetometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.gyroscope_xyz()
        return xyz
    if configuration_main.installed_sensors.pimoroni_icm20948:
        xyz = pimoroni_icm20948_sensor_access.gyroscope_xyz()
        return xyz
    else:
        return "NoSensor"


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(app_variables.restart_sensor_services_command)


def get_db_notes():
    sql_query = "SELECT " + \
                database_columns_and_tables.other_table_column_notes + \
                " FROM " + \
                database_columns_and_tables.table_other

    sql_db_notes = sqlite_database.sql_execute_get_data(sql_query)

    return _create_str_from_list(sql_db_notes)


def get_db_note_dates():
    sql_query_notes = "SELECT " + \
                      database_columns_and_tables.all_tables_datetime + \
                      " FROM " + \
                      database_columns_and_tables.table_other

    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)

    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    sql_query_user_datetime = "SELECT " + \
                              database_columns_and_tables.other_table_column_user_date_time + \
                              " FROM " + \
                              database_columns_and_tables.table_other

    sql_data_user_datetime = sqlite_database.sql_execute_get_data(sql_query_user_datetime)

    return _create_str_from_list(sql_data_user_datetime)


def _create_str_from_list(sql_data_notes):
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
    """ Takes the provided DateTime and Note as a list and writes it to the SQLite Database. """
    sql_data = sqlite_database.CreateOtherDataEntry()
    user_date_and_note = datetime_note.split(command_data_separator)

    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]

        sql_data.sensor_types = configuration_main.database_variables.all_tables_datetime + ", " + \
                                configuration_main.database_variables.other_table_column_user_date_time + ", " + \
                                configuration_main.database_variables.other_table_column_notes
        sql_data.sensor_readings = "'" + current_datetime + "','" + custom_datetime + "','" + note + "'"

        sql_execute = (sql_data.sql_query_start + sql_data.sensor_types +
                       sql_data.sql_query_values_start + sql_data.sensor_readings +
                       sql_data.sql_query_values_end)

        sqlite_database.sql_execute(sql_execute)
        logger.sensors_logger.warn(str(sql_execute))
    else:
        logger.sensors_logger.error("Unable to add bad Note.")


def update_note_in_database(datetime_note):
    """ Takes the provided DateTime and Note as a list and updates the note in the SQLite Database. """
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
    sql_query = "DELETE FROM " + \
                str(database_columns_and_tables.table_other) + \
                " WHERE " + \
                str(database_columns_and_tables.all_tables_datetime) + \
                " = '" + note_datetime + "'"

    sqlite_database.sql_execute(sql_query)
