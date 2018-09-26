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
import sqlite3
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Operations_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensor_ver_file = "/home/pi/KootNetSensors/installed_sensors.txt"


class SensorData:
    def __init__(self):
        self.sensor_types = ""
        self.sensor_readings = ""


class SQLCommandData:
    def __init__(self):
        self.database_location = ""
        self.sql_execute = ""


class InstalledSensors:
    def __init__(self):
        self.linux_system = True
        self.raspberry_pi_sense_hat = False
        self.pimoroni_bh1745 = False
        self.pimoroni_bme680 = False
        self.pimoroni_enviro = False
        self.pimoroni_lsm303d = False
        self.pimoroni_vl53l1x = False


def get_installed_sensors():
    installed_sensors_var = InstalledSensors()
    try:
        sensor_list_file = open(sensor_ver_file, 'r')
        sensor_list = sensor_list_file.readlines()

        if int(sensor_list[1][:1]):
            installed_sensors_var.linux_system = True
        else:
            installed_sensors_var.linux_system = False

        if int(sensor_list[2][:1]):
            installed_sensors_var.raspberry_pi_sense_hat = True
        else:
            installed_sensors_var.raspberry_pi_sense_hat = False

        if int(sensor_list[3][:1]):
            installed_sensors_var.pimoroni_bh1745 = True
        else:
            installed_sensors_var.pimoroni_bh1745 = False

        if int(sensor_list[4][:1]):
            installed_sensors_var.pimoroni_bme680 = True
        else:
            installed_sensors_var.pimoroni_bme680 = False

        if int(sensor_list[5][:1]):
            installed_sensors_var.pimoroni_enviro = True
        else:
            installed_sensors_var.pimoroni_enviro = False

        if int(sensor_list[6][:1]):
            installed_sensors_var.pimoroni_lsm303d = True
        else:
            installed_sensors_var.pimoroni_lsm303d = False

        if int(sensor_list[7][:1]):
            installed_sensors_var.pimoroni_vl53l1x = True
        else:
            installed_sensors_var.pimoroni_vl53l1x = False

        return installed_sensors_var
    except Exception as error:
        logger.error("Unable to open: " + sensor_ver_file + " - " + str(error))


def check_any_sensors_installed():
    installed_sensors = get_installed_sensors()
    sensors_installed = False

    if installed_sensors.pimoroni_lsm303d:
        sensors_installed = True
    elif installed_sensors.raspberry_pi_sense_hat:
        sensors_installed = True
    elif installed_sensors.pimoroni_enviro:
        sensors_installed = True
    elif installed_sensors.linux_system:
        sensors_installed = True
    elif installed_sensors.pimoroni_bme680:
        sensors_installed = True
    elif installed_sensors.pimoroni_bh1745:
        sensors_installed = True
    elif installed_sensors.pimoroni_vl53l1x:
        sensors_installed = True

    return sensors_installed


def check_interval_db(sensor_db_location):
    try:
        db_connection = sqlite3.connect(sensor_db_location)
        db_cursor = db_connection.cursor()

        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='IntervalData', nf='DateTime', ft='TEXT'))
            logger.debug("Table 'IntervalData' - Created")
        except Exception as error:
            logger.debug("Table 'IntervalData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='SensorName', ct='TEXT'))
            logger.debug("COLUMN 'SensorName' - Created")
        except Exception as error:
            logger.debug("COLUMN 'SensorName' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='IP', ct='TEXT'))
            logger.debug("COLUMN 'IP' - Created")
        except Exception as error:
            logger.debug("COLUMN 'IP' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='SensorUpTime', ct='TEXT'))
            logger.debug("COLUMN 'SensorUpTime' - Created")
        except Exception as error:
            logger.debug("COLUMN 'SensorUpTime' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='SystemTemp', ct='TEXT'))
            logger.debug("COLUMN 'SystemTemp' -  Created")
        except Exception as error:
            logger.debug("COLUMN 'SystemTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='EnvironmentTemp', ct='TEXT'))
            logger.debug("COLUMN 'EnvironmentTemp' - Created")
        except Exception as error:
            logger.debug("COLUMN 'EnvironmentTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Pressure', ct='TEXT'))
            logger.debug("COLUMN 'Pressure' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Pressure' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Humidity', ct='TEXT'))
            logger.debug("COLUMN 'Humidity' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Humidity' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Lumen', ct='TEXT'))
            logger.debug("COLUMN 'Lumen' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Lumen' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Red', ct='TEXT'))
            logger.debug("COLUMN 'Red' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Red' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Green', ct='TEXT'))
            logger.debug("COLUMN 'Green' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Green' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Blue', ct='TEXT'))
            logger.debug("COLUMN 'Blue' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Blue' - " + str(error))

        db_connection.commit()
        db_connection.close()
    except Exception as error:
        logger.error("DB Connection Failed: " + str(error))


def check_trigger_db(db_location):
    try:
        conn = sqlite3.connect(db_location)
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='TriggerData', nf='DateTime', ft='TEXT'))
            logger.debug("Table 'TriggerData' - Created")
        except Exception as error:
            logger.debug("Table 'TriggerData' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='SensorName', ct='TEXT'))
            logger.debug("Column 'SensorName' - Created")
        except Exception as error:
            logger.debug("Column 'SensorName' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='IP', ct='TEXT'))
            logger.debug("Column 'IP' - Created")
        except Exception as error:
            logger.debug("Column 'IP' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Acc_X', ct='TEXT'))
            logger.debug("Column 'acc_X' - Created")
        except Exception as error:
            logger.debug("Column 'acc_X' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Acc_Y', ct='TEXT'))
            logger.debug("Column 'acc_Y' - Created")
        except Exception as error:
            logger.debug("Column 'acc_Y' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Acc_Z', ct='TEXT'))
            logger.debug("Column 'acc_Z' - Created")
        except Exception as error:
            logger.debug("Column 'acc_Z' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Mag_X', ct='TEXT'))
            logger.debug("COLUMN 'mg_X' - Created")
        except Exception as error:
            logger.debug("COLUMN 'mg_X' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Mag_Y', ct='TEXT'))
            logger.debug("COLUMN 'mg_Y' - Created")
        except Exception as error:
            logger.debug("COLUMN 'mg_Y' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Mag_Z', ct='TEXT'))
            logger.debug("COLUMN 'mg_Z' - Created")
        except Exception as error:
            logger.debug("COLUMN 'mg_Z' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Gyro_X', ct='TEXT'))
            logger.debug("COLUMN 'Gyro_X' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Gyro_X' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Gyro_Y', ct='TEXT'))
            logger.debug("COLUMN 'Gyro_Y' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Gyro_Y' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='Gyro_Z', ct='TEXT'))
            logger.debug("COLUMN 'Gyro_Z' - Created")
        except Exception as error:
            logger.debug("COLUMN 'Gyro_Z' - " + str(error))

        c.close()
        conn.close()
    except Exception as error:
        logger.error("DB Connection Failed: " + str(error))


def write_to_sql_database(sql_data):
    sensors_installed = check_any_sensors_installed()

    if sensors_installed:
        logger.debug("SQL String to execute: " + str(sql_data.sql_execute))
        try:
            db_connection = sqlite3.connect(sql_data.database_location)
            db_cursor = db_connection.cursor()
            db_cursor.execute(sql_data.sql_execute)
            db_connection.commit()
            db_connection.close()
            logger.info("SQL Write to DataBase - OK - " + str(sql_data.database_location))
        except Exception as error:
            logger.error("SQL Write to DataBase - Failed - " + str(error))
    else:
        logger.warning("SQL Write to DataBase - Failed - No Sensors Selected in Config")
