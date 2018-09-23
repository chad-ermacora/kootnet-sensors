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


class InstalledSensors:
    def __init__(self):
        self.rp_system = True
        self.rp_sense_hat = False
        self.pimoroni_bh1745 = False
        self.pimoroni_bme680 = False
        self.pimoroni_enviro = False
        self.pimoroni_lsm303d = False
        self.pimoroni_vl53l1x = False


class SensorDatabaseData:

    def __init__(self):
        self.sensor_types = ""
        self.sensor_readings = ""


def get_installed_sensors():
    installed_sensors_var = InstalledSensors()
    try:
        sensor_list_file = open(sensor_ver_file, 'r')
        sensor_list = sensor_list_file.readlines()

        if int(sensor_list[1][:1]):
            installed_sensors_var.rp_system = True
        else:
            installed_sensors_var.rp_system = False

        if int(sensor_list[2][:1]):
            installed_sensors_var.rp_sense_hat = True
        else:
            installed_sensors_var.rp_sense_hat = False

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
            logger.debug("COLUMN SensorName - Created")
        except Exception as error:
            logger.debug("COLUMN SensorName - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='UpTime', ct='TEXT'))
            logger.debug("COLUMN UpTime - Created")
        except Exception as error:
            logger.debug("COLUMN UpTime - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='IP', ct='TEXT'))
            logger.debug("COLUMN IP - Created")
        except Exception as error:
            logger.debug("COLUMN IP - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='CPUtemp', ct='TEXT'))
            logger.debug("COLUMN CPUtemp -  Created")
        except Exception as error:
            logger.debug("COLUMN CPUtemp - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='EnvironmentTemp', ct='TEXT'))
            logger.debug("COLUMN EnvironmentTemp - Created")
        except Exception as error:
            logger.debug("COLUMN EnvironmentTemp - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Pressure', ct='TEXT'))
            logger.debug("COLUMN Pressure - Created")
        except Exception as error:
            logger.debug("COLUMN Pressure - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Humidity', ct='TEXT'))
            logger.debug("COLUMN Humidity - Created")
        except Exception as error:
            logger.debug("COLUMN Humidity - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Lumen', ct='TEXT'))
            logger.debug("COLUMN Lumen - Created")
        except Exception as error:
            logger.debug("COLUMN Lumen - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Red', ct='TEXT'))
            logger.debug("COLUMN Red - Created")
        except Exception as error:
            logger.debug("COLUMN Red - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Green', ct='TEXT'))
            logger.debug("COLUMN Green - Created")
        except Exception as error:
            logger.debug("COLUMN Green - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='Blue', ct='TEXT'))
            logger.debug("COLUMN Blue - Created")
        except Exception as error:
            logger.debug("COLUMN Blue - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='mg_X', ct='TEXT'))
            logger.debug("COLUMN mg_X - Created")
        except Exception as error:
            logger.debug("COLUMN mg_X - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='mg_Y', ct='TEXT'))
            logger.debug("COLUMN mg_Y - Created")
        except Exception as error:
            logger.debug("COLUMN mg_Y - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData', cn='mg_Z', ct='TEXT'))
            logger.debug("COLUMN mg_Z - Created")
        except Exception as error:
            logger.debug("COLUMN mg_Z - " + str(error))

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
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='IP', ct='TEXT'))
            logger.debug("Column 'IP' - Created")
        except Exception as error:
            logger.debug("Column 'IP' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='SensorName', ct='TEXT'))
            logger.debug("Column 'SensorName' - Created")
        except Exception as error:
            logger.debug("Column 'SensorName' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='acc_X', ct='BLOB'))
            logger.debug("Column 'acc_X' - Created")
        except Exception as error:
            logger.debug("Column 'acc_X' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='acc_Y', ct='BLOB'))
            logger.debug("Column 'acc_Y' - Created")
        except Exception as error:
            logger.debug("Column 'acc_Y' - " + str(error))

        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData', cn='acc_Z', ct='BLOB'))
            logger.debug("Column 'acc_Z' - Created")
        except Exception as error:
            logger.debug("Column 'acc_Z' - " + str(error))

        c.close()
        conn.close()
    except Exception as error:
        logger.error("DB Connection Failed: " + str(error))


def write_to_sql_database(sql_command, sensor_db_location):
    logger.debug("SQL String to execute: " + str(sql_command))
    try:
        db_connection = sqlite3.connect(sensor_db_location)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_command)
        db_connection.commit()
        db_connection.close()
        logger.info("SQL Write to DataBase - OK - " + str(sensor_db_location))
    except Exception as error:
        logger.error("SQL Write to DataBase - Failed - " + str(error))
