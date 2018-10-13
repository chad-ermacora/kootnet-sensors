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
import socket
import pickle
import operations_config
import sensor_modules.RaspberryPi_System as RaspberryPi_Sensors
import sensor_modules.Linux_OS as Linux_System
from time import sleep
from shutil import disk_usage
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensor_Commands_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensor_system = RaspberryPi_Sensors.CreateRPSystem()
sensor_os = Linux_System.CreateLinuxSystem


def get_sensor_data():
    sensor_config = operations_config.get_installed_config()
    str_sensor_data = ""
    free_disk = disk_usage("/")[2]

    try:
        str_sensor_data = str(sensor_os.get_hostname()) + \
                          "," + str(sensor_os.get_ip()) + \
                          "," + str(sensor_os.get_sys_datetime()) + \
                          "," + str(sensor_os.get_uptime()) + \
                          "," + str(round(sensor_system.cpu_temperature(), 2)) + \
                          "," + str(round(free_disk / (2**30), 2)) + \
                          "," + str(sensor_os.get_interval_db_size()) + \
                          "," + str(sensor_os.get_trigger_db_size()) + \
                          "," + str(sensor_config.write_to_db) + \
                          "," + str(sensor_config.enable_custom)
        print(str_sensor_data)
    except Exception as error_msg:
        logger.error("Sensor reading failed - " + str(error_msg))

    return str_sensor_data


def set_sensor_config(config_data):
    split_config = config_data.split(',')
    new_config = operations_config.CreateConfig()

    try:
        new_config.write_to_db = int(split_config[1])
        if new_config.write_to_db:
            os.system("systemctl enable SensorInterval && systemctl enable SensorTrigger")
            os.system("systemctl start SensorInterval && systemctl start SensorTrigger")
        else:
            os.system("systemctl disable SensorInterval && systemctl disable SensorTrigger")
            os.system("systemctl stop SensorInterval && systemctl stop SensorTrigger")

    except Exception as error1:
        logger.error("Bad config 'Record Sensors to SQL Database' - " + str(error1))

    try:
        new_config.sleep_duration_interval = int(split_config[2])
    except Exception as error1:
        logger.error("Bad config 'Duration between Interval Readings' - " + str(error1))

    try:
        new_config.sleep_duration_trigger = float(split_config[3])
    except Exception as error1:
        logger.error("Bad config 'Duration between Trigger Readings' - " + str(error1))

    try:
        new_config.enable_custom = int(split_config[4])
    except Exception as error1:
        logger.error("Bad config 'Enable Custom Settings' - " + str(error1))

    try:
        new_config.acc_variance = float(split_config[5])
    except Exception as error1:
        logger.error("Bad config 'Accelerometer Variance' - " + str(error1))

    try:
        new_config.mag_variance = float(split_config[6])
    except Exception as error1:
        logger.error("Bad config 'Magnetometer Variance' - " + str(error1))

    try:
        new_config.gyro_variance = float(split_config[7])
    except Exception as error1:
        logger.error("Bad config 'Gyroscope Variance' - " + str(error1))

    operations_config.write_config_to_file(new_config)
    os.system("systemctl restart SensorInterval && systemctl restart SensorTrigger")


while True:
    try:
        # Create a TCP/IP socket and Bind the socket to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('', 10065)
        logger.info('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        sock.listen(12)
        logger.info('Waiting for a Connection ... ')

        while True:
            connection, client_address = sock.accept()
            logger.info("Connection from " + str(client_address[0]) + " Port: " + str(client_address[1]))
            tmp_connection_data = connection.recv(4096)
            connection_data = str(tmp_connection_data)
            connection_command = connection_data[2:-1]

            if connection_command == "CheckOnlineStatus":
                logger.info('Sensor Checked')
            elif connection_command == "GetSystemData":
                sensor_data = get_sensor_data()
                connection.sendall(pickle.dumps(sensor_data))
                logger.info('Sensor Data Sent to ' + str(client_address[0]))
            elif connection_command == "inkupg":
                os.system("bash /home/sensors/upgrade/update_programs_e-Ink.sh")
                logger.info('/home/sensors/upgrade/update_programs_e-Ink.sh Finished')
            elif connection_command == "UpgradeOnline":
                os.system("bash /home/sensors/upgrade/update_programs_online.sh")
                logger.info('/home/sensors/upgrade/update_programs_online.sh Finished')
            elif connection_command == "UpgradeSMB":
                os.system("bash /home/sensors/upgrade/update_programs_smb.sh")
                logger.info('/home/sensors/upgrade/update_programs_smb.sh Finished')
            elif connection_command == "RebootSystem":
                logger.info('Rebooting System')
                os.system("reboot")
            elif connection_command == "ShutdownSystem":
                logger.info('Shutting Down System')
                os.system("shutdown -h now")
            elif connection_command == "RestartServices":
                logger.info('Sensor Termination sent by ' + str(client_address[0]))
                os.system("systemctl restart SensorInterval && " +
                          "systemctl restart SensorTrigger && " +
                          "systemctl restart SensorCommands")
            elif connection_command == "UpgradeSystemOS":
                logger.info('Updating Operating System & rebooting')
                os.system("apt-get update && apt-get upgrade -y && reboot")
            elif connection_command == "GetConfiguration":
                temp_config = operations_config.get_installed_config()
                str_config = str(temp_config.write_to_db) + "," + \
                    str(temp_config.sleep_duration_interval) + "," + \
                    str(temp_config.sleep_duration_trigger) + "," + \
                    str(temp_config.enable_custom) + "," + \
                    str(temp_config.acc_variance) + "," + \
                    str(temp_config.mag_variance) + "," + \
                    str(temp_config.gyro_variance)
                connection.sendall(pickle.dumps(str_config))
                logger.info('Sensor Data Sent to ' + str(client_address[0]))
            elif tmp_connection_data.decode()[:16] == "SetConfiguration":
                logger.info('Setting Sensor Configuration')
                set_sensor_config(tmp_connection_data.decode())
            elif tmp_connection_data.decode()[:14] == "ChangeHostName":
                try:
                    new_host = tmp_connection_data.decode()[14:]
                    os.system("hostnamectl set-hostname " + new_host)
                    logger.info("Hostname Changed to " + new_host + " - OK")
                except Exception as error:
                    logger.info("Hostname Change Failed - " + str(error))
            elif tmp_connection_data.decode()[:11] == "SetDateTime":
                logger.info('Setting System DateTime')
                new_datetime = tmp_connection_data.decode()[11:]
                os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[10:])
            else:
                logger.info("Invalid command sent:" + connection_data)

            connection.close()
    except Exception as error:
        logger.warning('Socket Failed trying again in 5 Seconds - ' + str(error))
        sleep(2)
