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
import socket
from time import sleep
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Trigger_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensorDB_Location = '/home/sensors/data/SensorTriggerDatabase.sqlite'
sensor_ver_file = "/home/pi/KootNetSensors/installed_sensors.txt"
sql_query_start = "INSERT OR IGNORE INTO Motion_Data (DateTime, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"

var_motion_variance = 0.045


def get_installed_sensors():
    # See top of file for sensor_list[] order
    try:
        sensor_list_file = open(sensor_ver_file, 'r')
        sensor_list = sensor_list_file.readlines()
        rp_system = sensor_list[1]
        rp_sense_hat = sensor_list[2]
        pimoroni_bh1745 = sensor_list[3]
        pimoroni_bme680 = sensor_list[4]
        pimoroni_enviro = sensor_list[5]
        pimoroni_lsm303d = sensor_list[6]

        sensors_enabled = rp_system[:1], rp_sense_hat[:1], pimoroni_bh1745[:1], \
            pimoroni_bme680[:1], pimoroni_enviro[:1], pimoroni_lsm303d[:1]

        return sensors_enabled
    except Exception as error:
        logger.error("Unable to open: " + sensor_ver_file + " - " + str(error))


def database_write(wvar_motion):
    var1 = float(wvar_motion[0])
    var2 = float(wvar_motion[1])
    var3 = float(wvar_motion[2])
    var_host = str(socket.gethostname())
    testIP = ""
    print(str(var1))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.10.1", 80))
        testIP = (s.getsockname()[0])
        s.close()
    except BaseException:
        testIP = "0.0.0.0"
        
    testIP = str(testIP)
    conn = sqlite3.connect(sensorDB_Location)
    c = conn.cursor()
    print("x: " + str(var1))
    print("y: " + str(var2))
    print("z: " + str(var3))
    c.execute("INSERT OR IGNORE INTO TriggerData (DateTime,IP, X, Y, Z, SensorName) " +
              "VALUES ((CURRENT_TIMESTAMP),?,?,?,?,?)", (testIP, var1, var2, var3, var_host))
    conn.commit()
    c.close()
    conn.close()


var_real = motion.accelerometer()
database_write(var_real)
var_acc_last_x = round(float(var_real[0]), 3)
var_acc_last_y = round(float(var_real[1]), 3)
var_acc_last_z = round(float(var_real[2]), 3)

while True:
    sleep(0.25)
    var_real = motion.accelerometer()
    var_acc_now_x = round(float(var_real[0]), 3)
    var_acc_now_y = round(float(var_real[1]), 3)
    var_acc_now_z = round(float(var_real[2]), 3)

    if var_acc_last_x > (var_acc_now_x + var_motion_variance):
        database_write(var_real)
    elif var_acc_last_x < (var_acc_now_x - var_motion_variance):
        database_write(var_real)
    elif var_acc_last_y > (var_acc_now_y + var_motion_variance):
        database_write(var_real)
    elif var_acc_last_y < (var_acc_now_y - var_motion_variance):
        database_write(var_real)
    elif var_acc_last_z > (var_acc_now_z + var_motion_variance):
        database_write(var_real)
    elif var_acc_last_z < (var_acc_now_z - var_motion_variance):
        database_write(var_real)

    var_acc_last_x = var_acc_now_x
    var_acc_last_y = var_acc_now_y
    var_acc_last_z = var_acc_now_z
