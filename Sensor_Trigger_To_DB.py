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
sleep_duration = 0.250
# Acceleration Variance to Ignore
acc_variance = 0.045
# Magnetic Variance to Ignore
mag_variance = 0.045
# Gyroscopic Variance to Ignore
gyro_variance = 0.045


def check_mag(new_mag, old_mag):
    write_to_db = False
    now_x = round(float(new_mag[0]), 3)
    now_y = round(float(new_mag[1]), 3)
    now_z = round(float(new_mag[2]), 3)

    old_x = round(float(old_mag[0]), 3)
    old_y = round(float(old_mag[1]), 3)
    old_z = round(float(old_mag[2]), 3)

    if (now_x - mag_variance) > old_x > (now_x + mag_variance):
        write_to_db = True
    elif (now_y - mag_variance) > old_y > (now_y + mag_variance):
        write_to_db = True
    elif (now_z - mag_variance) > old_z > (now_z + mag_variance):
        write_to_db = True

    return write_to_db


def check_acc(new_acc, old_acc):
    write_to_db = False
    now_x = round(float(new_acc[0]), 3)
    now_y = round(float(new_acc[1]), 3)
    now_z = round(float(new_acc[2]), 3)

    old_x = round(float(old_acc[0]), 3)
    old_y = round(float(old_acc[1]), 3)
    old_z = round(float(old_acc[2]), 3)

    if (now_x - acc_variance) > old_x > (now_x + acc_variance):
        write_to_db = True
    elif (now_y - acc_variance) > old_y > (now_y + acc_variance):
        write_to_db = True
    elif (now_z - acc_variance) > old_z > (now_z + acc_variance):
        write_to_db = True

    return write_to_db


def check_gyro(new_gyro, old_gyro):
    write_to_db = False
    now_x = round(float(new_gyro[0]), 3)
    now_y = round(float(new_gyro[1]), 3)
    now_z = round(float(new_gyro[2]), 3)

    old_x = round(float(old_gyro[0]), 3)
    old_y = round(float(old_gyro[1]), 3)
    old_z = round(float(old_gyro[2]), 3)

    if (now_x - gyro_variance) > old_x > (now_x + gyro_variance):
        write_to_db = True
    elif (now_y - gyro_variance) > old_y > (now_y + gyro_variance):
        write_to_db = True
    elif (now_z - gyro_variance) > old_z > (now_z + gyro_variance):
        write_to_db = True

    return write_to_db


# Have readings passed to checks, that set do_db_write
def check_trigger_sensors():
    installed_sensors = Operations_Config.get_installed_sensors()
    old_sql_command_data = Operations_DB.CreateSQLCommandData()
    new_sql_command_data = Operations_DB.CreateSQLCommandData()

    old_sql_command_data.database_location = trigger_db_location
    Operations_DB.check_trigger_db(trigger_db_location)

    do_db_write = False
    count = 0
    if installed_sensors.linux_system:
        sensor_access = sensor_modules.Linux_OS.CreateLinuxSystem()

        sensor_types = "SensorName, IP"

        old_sensor_readings = "'" + str(sensor_access.get_hostname()) + "', '" + str(sensor_access.get_ip()) + "'"

        old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + sensor_types
        old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + old_sensor_readings
        new_sql_command_data.sensor_types = new_sql_command_data.sensor_types + sensor_types
        new_sql_command_data.sensor_readings = new_sql_command_data.sensor_readings + old_sensor_readings
        count = count + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + ", "
            old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, Gyro_X, Gyro_Y, Gyro_Z"

        acc_xyz_old = sensor_access.accelerometer_xyz()
        mag_xyz_old = sensor_access.magnetometer_xyz()
        gyro_xyz_old = sensor_access.gyroscope_xyz()

        sleep(sleep_duration)

        mag_xyz_new = sensor_access.magnetometer_xyz()
        acc_xyz_new = sensor_access.accelerometer_xyz()
        gyro_xyz_new = sensor_access.gyroscope_xyz()

        acc_change = check_acc(acc_xyz_old, acc_xyz_new)
        mag_change = check_mag(mag_xyz_old, mag_xyz_new)
        gyro_change = check_gyro(gyro_xyz_old, gyro_xyz_new)

        if acc_change or mag_change or gyro_change:
            do_db_write = True

        old_sensor_readings = "'" + str(mag_xyz_old[0]) + "', '" + \
                              str(mag_xyz_old[1]) + "', '" + \
                              str(mag_xyz_old[2]) + "', '" + \
                              str(acc_xyz_old[0]) + "', '" + \
                              str(acc_xyz_old[1]) + "', '" + \
                              str(acc_xyz_old[2]) + "', '" + \
                              str(gyro_xyz_old[0]) + "', '" + \
                              str(gyro_xyz_old[1]) + "', '" + \
                              str(gyro_xyz_old[2]) + "'"

        new_sensor_readings = "'" + str(mag_xyz_new[0]) + "', '" + \
                              str(mag_xyz_new[1]) + "', '" + \
                              str(mag_xyz_new[2]) + "', '" + \
                              str(acc_xyz_new[0]) + "', '" + \
                              str(acc_xyz_new[1]) + "', '" + \
                              str(acc_xyz_new[2]) + "', '" + \
                              str(gyro_xyz_new[0]) + "', '" + \
                              str(gyro_xyz_new[1]) + "', '" + \
                              str(gyro_xyz_new[2]) + "'"

        old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + sensor_types
        old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + old_sensor_readings
        new_sql_command_data.sensor_types = new_sql_command_data.sensor_types + sensor_types
        new_sql_command_data.sensor_readings = new_sql_command_data.sensor_readings + new_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + ", "
            old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        acc_xyz_old = sensor_access.accelerometer_xyz()
        mag_xyz_old = sensor_access.magnetometer_xyz()

        sleep(sleep_duration)

        mag_xyz_new = sensor_access.magnetometer_xyz()
        acc_xyz_new = sensor_access.accelerometer_xyz()

        acc_change = check_acc(acc_xyz_old, acc_xyz_new)
        mag_change = check_mag(mag_xyz_old, mag_xyz_new)

        if acc_change or mag_change:
            do_db_write = True

        old_sensor_readings = "'" + str(mag_xyz_old[0]) + "', '" + \
                              str(mag_xyz_old[1]) + "', '" + \
                              str(mag_xyz_old[2]) + "', '" + \
                              str(acc_xyz_old[0]) + "', '" + \
                              str(acc_xyz_old[1]) + "', '" + \
                              str(acc_xyz_old[2]) + "'"

        new_sensor_readings = "'" + str(mag_xyz_new[0]) + "', '" + \
                              str(mag_xyz_new[1]) + "', '" + \
                              str(mag_xyz_new[2]) + "', '" + \
                              str(acc_xyz_new[0]) + "', '" + \
                              str(acc_xyz_new[1]) + "', '" + \
                              str(acc_xyz_new[2]) + "'"

        old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + sensor_types
        old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + old_sensor_readings
        new_sql_command_data.sensor_types = new_sql_command_data.sensor_types + sensor_types
        new_sql_command_data.sensor_readings = new_sql_command_data.sensor_readings + new_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()

        if count > 0:
            old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + ", "
            old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        acc_xyz_old = sensor_access.accelerometer_xyz()
        mag_xyz_old = sensor_access.magnetometer_xyz()

        sleep(sleep_duration)

        mag_xyz_new = sensor_access.magnetometer_xyz()
        acc_xyz_new = sensor_access.accelerometer_xyz()

        acc_change = check_acc(acc_xyz_old, acc_xyz_new)
        mag_change = check_mag(mag_xyz_old, mag_xyz_new)

        if acc_change or mag_change:
            do_db_write = True

        old_sensor_readings = "'" + str(mag_xyz_old[0]) + "', '" + \
                              str(mag_xyz_old[1]) + "', '" + \
                              str(mag_xyz_old[2]) + "', '" + \
                              str(acc_xyz_old[0]) + "', '" + \
                              str(acc_xyz_old[1]) + "', '" + \
                              str(acc_xyz_old[2]) + "'"

        new_sensor_readings = "'" + str(mag_xyz_new[0]) + "', '" + \
                              str(mag_xyz_new[1]) + "', '" + \
                              str(mag_xyz_new[2]) + "', '" + \
                              str(acc_xyz_new[0]) + "', '" + \
                              str(acc_xyz_new[1]) + "', '" + \
                              str(acc_xyz_new[2]) + "'"

        old_sql_command_data.sensor_types = old_sql_command_data.sensor_types + sensor_types
        old_sql_command_data.sensor_readings = old_sql_command_data.sensor_readings + old_sensor_readings
        new_sql_command_data.sensor_types = new_sql_command_data.sensor_types + sensor_types
        new_sql_command_data.sensor_readings = new_sql_command_data.sensor_readings + new_sensor_readings

    if do_db_write:
        old_sql_command_data.sql_execute = sql_query_start + old_sql_command_data.sensor_types + \
            sql_query_values_start + old_sql_command_data.sensor_readings + sql_query_values_end
        new_sql_command_data.sql_execute = sql_query_start + new_sql_command_data.sensor_types + \
            sql_query_values_start + new_sql_command_data.sensor_readings + sql_query_values_end

        Operations_DB.write_to_sql_database(old_sql_command_data)
        Operations_DB.write_to_sql_database(new_sql_command_data)
    else:
        logger.warning("No Trigger Sensors Selected in Config - Skipping Trigger Database Write")


# Check Database & start monitoring / recording
Operations_DB.check_trigger_db(trigger_db_location)

while True:
    check_trigger_sensors()
