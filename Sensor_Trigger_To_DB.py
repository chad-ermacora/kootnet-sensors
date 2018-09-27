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

logger.setLevel(logging.INFO)
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
sleep_duration = .15


class CreateTriggerDatabaseData:
    def __init__(self):
        self.num_sensors_installed = 0
        self.acc_variance = 0.03
        self.mag_variance = 250
        self.gyro_variance = 0.045
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


def check_acc(new_data, old_data):
    logger.debug("new_acc - X:" + str(new_data.acc_x) + " Y:" + str(new_data.acc_y) + " Z:" + str(new_data.acc_z))
    write_to_db = False

    if (old_data.acc_x - new_data.acc_variance) > new_data.acc_x or \
            new_data.acc_x > (old_data.acc_x + new_data.acc_variance):
        write_to_db = True
    elif (old_data.acc_y - new_data.acc_variance) > new_data.acc_y or \
            new_data.acc_y > (old_data.acc_y + new_data.acc_variance):
        write_to_db = True
    elif (old_data.acc_z - new_data.acc_variance) > new_data.acc_z or \
            new_data.acc_z > (old_data.acc_z + new_data.acc_variance):
        write_to_db = True

    return write_to_db


def check_mag(new_data, old_data):
    logger.debug("new_mag - X:" + str(new_data.mag_x) + " Y:" + str(new_data.mag_y) + " Y:" + str(new_data.mag_z))
    write_to_db = False

    if (old_data.mag_x - new_data.mag_variance) > new_data.mag_x or \
            new_data.mag_x > (old_data.mag_x + new_data.mag_variance):
        write_to_db = True
    elif (old_data.mag_y - new_data.mag_variance) > new_data.mag_y or \
            new_data.mag_y > (old_data.mag_y + new_data.mag_variance):
        write_to_db = True
    elif (old_data.mag_z - new_data.mag_variance) > new_data.mag_z or \
            new_data.mag_z > (old_data.mag_z + new_data.mag_variance):
        write_to_db = True

    return write_to_db


def check_gyro(new_data, old_data):
    logger.debug("new_gyro - X:" + str(new_data.gyro_x) + " Y:" + str(new_data.gyro_y) + " Z:" + str(new_data.gyro_z))
    write_to_db = False

    if (old_data.gyro_x - new_data.gyro_variance) > new_data.gyro_x or \
            new_data.gyro_x > (old_data.gyro_x + new_data.gyro_variance):
        write_to_db = True
    elif (old_data.gyro_y - new_data.gyro_variance) > new_data.gyro_y or \
            new_data.gyro_y > (old_data.gyro_y + new_data.gyro_variance):
        write_to_db = True
    elif (old_data.gyro_z - new_data.gyro_variance) > new_data.gyro_z or \
            new_data.gyro_z > (old_data.gyro_z + new_data.gyro_variance):
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
        trigger_data.acc_variance = 0.3
        trigger_data.mag_variance = 1.0
        trigger_data.gyro_variance = 0.01

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
        trigger_data.acc_variance = 0.03
        trigger_data.mag_variance = 200.0

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
        trigger_data.acc_variance = 0.02
        trigger_data.mag_variance = 0.02

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
    var_installed_sensors = Operations_Config.get_installed_sensors()
    old_trigger_data = CreateTriggerDatabaseData()
    new_trigger_data = CreateTriggerDatabaseData()

    get_sensors_data(old_trigger_data)
    sleep(sleep_duration)
    get_sensors_data(new_trigger_data)

    if var_installed_sensors.has_acc and check_acc(new_trigger_data, old_trigger_data):
        logger.debug("Accelerometer Triggered - X:" + str(new_trigger_data.acc_x) +
                    " Y:" + str(new_trigger_data.acc_y) + " Z:" + str(new_trigger_data.acc_z))
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
    elif var_installed_sensors.has_mag and check_mag(new_trigger_data, old_trigger_data):
        logger.debug("Magnetometer Triggered - X:" + str(new_trigger_data.mag_x) +
                    " Y:" + str(new_trigger_data.mag_y) + " Z:" + str(new_trigger_data.mag_z))
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
    elif var_installed_sensors.has_gyro and check_gyro(new_trigger_data, old_trigger_data):
        logger.debug("Gyroscope Triggered - X:" + str(new_trigger_data.gyro_x) +
                    " Y:" + str(new_trigger_data.gyro_y) + " Z:" + str(new_trigger_data.gyro_z))
        write_to_database(old_trigger_data)
        write_to_database(new_trigger_data)
