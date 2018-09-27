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
import Operations_DB
import Operations_Config
import sensor_modules.Linux_OS
import sensor_modules.RaspberryPi_SenseHAT
import sensor_modules.Pimoroni_Enviro
import sensor_modules.Pimoroni_LSM303D
import logging
from logging.handlers import RotatingFileHandler
from time import sleep

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Trigger_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

trigger_db_location = '/home/pi/KootNetSensors/data/SensorTriggerDatabase.sqlite'
sql_query_start = "INSERT OR IGNORE INTO TriggerData (DateTime, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"

# Sleep Duration between sensor readings
sleep_duration = 0.25
# Acceleration Variance to Ignore
acc_variance = 0.045
# Magnetic Variance to Ignore
mag_variance = 0.045
# Gyroscopic Variance to Ignore
gyro_variance = 0.045


class CreateTriggerDatabaseData:
    def __init__(self):
        self.num_sensors_installed = 0
        self.sensor_types = ""
        self.sensor_readings = ""
        self.write_to_db = False

        self.acc_x = 0.0
        self.acc_y = 0.0
        self.acc_z = 0.0

        self.mag_x = 0.0
        self.mag_y = 0.0
        self.mag_z = 0.0

        self.gyro_x = 0.0
        self.gyro_y = 0.0
        self.gyro_z = 0.0


def check_acc(new_acc, old_acc):
    logger.debug("new_acc - " + str(new_acc))
    logger.debug("old_acc - " + str(old_acc))
    write_to_db = False
    now_x = round(float(new_acc), 3)
    now_y = round(float(new_acc), 3)
    now_z = round(float(new_acc), 3)

    old_x = round(float(old_acc), 3)
    old_y = round(float(old_acc), 3)
    old_z = round(float(old_acc), 3)

    if (now_x - acc_variance) > old_x > (now_x + acc_variance):
        write_to_db = True
    elif (now_y - acc_variance) > old_y > (now_y + acc_variance):
        write_to_db = True
    elif (now_z - acc_variance) > old_z > (now_z + acc_variance):
        write_to_db = True

    return write_to_db


def check_mag(new_mag, old_mag):
    logger.debug("new_mag - " + str(new_mag))
    logger.debug("old_mag - " + str(old_mag))
    write_to_db = False
    now_x = round(float(new_mag), 3)
    now_y = round(float(new_mag), 3)
    now_z = round(float(new_mag), 3)

    old_x = round(float(old_mag), 3)
    old_y = round(float(old_mag), 3)
    old_z = round(float(old_mag), 3)

    if (now_x - mag_variance) > old_x > (now_x + mag_variance):
        write_to_db = True
    elif (now_y - mag_variance) > old_y > (now_y + mag_variance):
        write_to_db = True
    elif (now_z - mag_variance) > old_z > (now_z + mag_variance):
        write_to_db = True

    return write_to_db


def check_gyro(new_gyro, old_gyro):
    logger.debug("new_gyro - " + str(new_gyro))
    logger.debug("old_gyro - " + str(old_gyro))
    write_to_db = False
    now_x = round(float(new_gyro), 3)
    now_y = round(float(new_gyro), 3)
    now_z = round(float(new_gyro), 3)

    old_x = round(float(old_gyro), 3)
    old_y = round(float(old_gyro), 3)
    old_z = round(float(old_gyro), 3)

    if (now_x - gyro_variance) > old_x > (now_x + gyro_variance):
        write_to_db = True
    elif (now_y - gyro_variance) > old_y > (now_y + gyro_variance):
        write_to_db = True
    elif (now_z - gyro_variance) > old_z > (now_z + gyro_variance):
        write_to_db = True

    return write_to_db


def get_sensors_data(trigger_data):
    installed_sensors = Operations_Config.get_installed_sensors()

    if installed_sensors.linux_system:
        sensor_access = sensor_modules.Linux_OS.CreateLinuxSystem()

        sensor_types = "SensorName, IP"
        sensor_readings = "'" + str(sensor_access.get_hostname()) + "', '" + str(sensor_access.get_ip()) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        trigger_data.num_sensors_installed = trigger_data.num_sensors_installed + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if trigger_data.num_sensors_installed > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, Gyro_X, Gyro_Y, Gyro_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()
        trigger_data.gyro_x, trigger_data.gyro_y, trigger_data.gyro_z = sensor_access.gyroscope_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "', '" + \
                          str(trigger_data.gyro_x) + "', '" + \
                          str(trigger_data.gyro_y) + "', '" + \
                          str(trigger_data.gyro_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        trigger_data.num_sensors_installed = trigger_data.num_sensors_installed + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if trigger_data.num_sensors_installed > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        trigger_data.num_sensors_installed = trigger_data.num_sensors_installed + 1

    if installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()

        if trigger_data.num_sensors_installed > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        trigger_data.num_sensors_installed = trigger_data.num_sensors_installed + 1

        return trigger_data


def write_to_database(trigger_data):

    Operations_DB.check_trigger_db(trigger_db_location)

    sql_command = Operations_DB.CreateSQLCommandData()

    sql_command.database_location = trigger_db_location

    sql_command.sql_execute = sql_query_start + trigger_data.sensor_types + \
        sql_query_values_start + trigger_data.sensor_readings + sql_query_values_end

    logger.debug("SQL Command - " + str(sql_command.sql_execute))
    Operations_DB.write_to_sql_database(sql_command)


while True:
    default_trigger_data = CreateTriggerDatabaseData()

    old_trigger_data = get_sensors_data(default_trigger_data)
    sleep(sleep_duration)
    new_trigger_data = get_sensors_data(default_trigger_data)

    if check_acc(new_trigger_data, old_trigger_data):
        logger.debug("Accelerometer Triggered")
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
    elif check_mag(new_trigger_data, old_trigger_data):
        logger.debug("Magnetometer Triggered")
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
    elif check_gyro(new_trigger_data, old_trigger_data):
        logger.debug("Gyroscope Triggered")
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
