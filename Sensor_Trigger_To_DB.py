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

acc_variance = 0.045


def check_mag():
    pass


def check_acc():
    pass


def check_gyro():
    pass


# Have readings passed to checks, that set do_db_write
def check_trigger_sensors():
    installed_sensors_var = Operations_DB.get_installed_sensors()
    trigger_sql_data = Operations_DB.SensorData()
    trigger_sql_command_data = Operations_DB.SQLCommandData()

    trigger_sql_command_data.database_location = trigger_db_location
    Operations_DB.check_trigger_db(trigger_db_location)
    do_db_write = True

    count = 0
    if installed_sensors_var.linux_system:
        sensor_access = sensor_modules.Linux_OS.CreateLinuxSystem()

        tmp_sensor_types = "SensorName, IP"

        tmp_sensor_readings = "'" + str(sensor_access.get_hostname()) + "', '" + str(sensor_access.get_ip()) + "'"

        trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + tmp_sensor_types
        trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + ", "
            trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + ", "

        tmp_sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, Gyro_X, Gyro_Y, Gyro_Z"

        tmp_mg_xyz = sensor_access.magnetometer_xyz()
        tmp_acc_xyz = sensor_access.accelerometer_xyz()
        tmp_gyro_xyz = sensor_access.gyroscope_xyz()

        tmp_sensor_readings = "'" + str(tmp_mg_xyz[0]) + "', '" + \
                              str(tmp_mg_xyz[1]) + "', '" + \
                              str(tmp_mg_xyz[2]) + "', '" + \
                              str(tmp_acc_xyz[0]) + "', '" + \
                              str(tmp_acc_xyz[1]) + "', '" + \
                              str(tmp_acc_xyz[2]) + "', '" + \
                              str(tmp_gyro_xyz[0]) + "', '" + \
                              str(tmp_gyro_xyz[1]) + "', '" + \
                              str(tmp_gyro_xyz[2]) + "'"

        trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + tmp_sensor_types
        trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + ", "
            trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + ", "

        tmp_sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        tmp_mg_xyz = sensor_access.magnetometer_xyz()
        tmp_acc_xyz = sensor_access.accelerometer_xyz()

        tmp_sensor_readings = "'" + str(tmp_mg_xyz[0]) + "', '" + \
                              str(tmp_mg_xyz[1]) + "', '" + \
                              str(tmp_mg_xyz[2]) + "', '" + \
                              str(tmp_acc_xyz[0]) + "', '" + \
                              str(tmp_acc_xyz[1]) + "', '" + \
                              str(tmp_acc_xyz[2]) + "'"

        trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + tmp_sensor_types
        trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()

        if count > 0:
            trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + ", "
            trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + ", "

        tmp_sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        tmp_mg_xyz = sensor_access.magnetometer_xyz()
        tmp_acc_xyz = sensor_access.accelerometer_xyz()

        tmp_sensor_readings = "'" + str(tmp_mg_xyz[0]) + "', '" + \
                              str(tmp_mg_xyz[1]) + "', '" + \
                              str(tmp_mg_xyz[2]) + "', '" + \
                              str(tmp_acc_xyz[0]) + "', '" + \
                              str(tmp_acc_xyz[1]) + "', '" + \
                              str(tmp_acc_xyz[2]) + "'"

        trigger_sql_data.sensor_types = trigger_sql_data.sensor_types + tmp_sensor_types
        trigger_sql_data.sensor_readings = trigger_sql_data.sensor_readings + tmp_sensor_readings

    if do_db_write:
        Operations_DB.write_to_sql_database(trigger_sql_data)
        print("Types: " + trigger_sql_data.sensor_types)
        print("Readings: " + trigger_sql_data.sensor_readings)


# var_real = motion.accelerometer()
# database_write(var_real)
# var_acc_last_x = round(float(var_real[0]), 3)
# var_acc_last_y = round(float(var_real[1]), 3)
# var_acc_last_z = round(float(var_real[2]), 3)
#
# while True:
#     sleep(0.25)
#     var_real = motion.accelerometer()
#     var_acc_now_x = round(float(var_real[0]), 3)
#     var_acc_now_y = round(float(var_real[1]), 3)
#     var_acc_now_z = round(float(var_real[2]), 3)
#
#     if var_acc_last_x > (var_acc_now_x + var_motion_variance):
#         database_write(var_real)
#     elif var_acc_last_x < (var_acc_now_x - var_motion_variance):
#         database_write(var_real)
#     elif var_acc_last_y > (var_acc_now_y + var_motion_variance):
#         database_write(var_real)
#     elif var_acc_last_y < (var_acc_now_y - var_motion_variance):
#         database_write(var_real)
#     elif var_acc_last_z > (var_acc_now_z + var_motion_variance):
#         database_write(var_real)
#     elif var_acc_last_z < (var_acc_now_z - var_motion_variance):
#         database_write(var_real)
#
#     var_acc_last_x = var_acc_now_x
#     var_acc_last_y = var_acc_now_y
#     var_acc_last_z = var_acc_now_z

while True:
    check_trigger_sensors()
    sleep(300)
