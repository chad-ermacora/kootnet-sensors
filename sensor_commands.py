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
import logging
import os
import pickle
import socket
from logging.handlers import RotatingFileHandler
from shutil import disk_usage
from time import sleep

import operations_config
import operations_sensors
import sensor_modules.Linux_OS as Linux_System
import sensor_modules.RaspberryPi_System as RaspberryPi_Sensors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensor_Commands_log.txt', maxBytes=256000,
                                   backupCount=5)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensor_system = RaspberryPi_Sensors.CreateRPSystem()
sensor_os = Linux_System.CreateLinuxSystem()

version = "Alpha.20.1"


def get_system_information():
    sensor_config = operations_config.get_installed_config()
    free_disk = disk_usage("/")[2]

    try:
        str_sensor_data = str(sensor_os.get_hostname()) + \
                          "," + str(sensor_os.get_ip()) + \
                          "," + str(sensor_os.get_sys_datetime()) + \
                          "," + str(sensor_os.get_uptime()) + \
                          "," + str(round(sensor_system.cpu_temperature(), 2)) + \
                          "," + str(round(free_disk / (2 ** 30), 2)) + \
                          "," + str(sensor_os.get_interval_db_size()) + \
                          "," + str(sensor_os.get_trigger_db_size()) + \
                          "," + str(sensor_config.write_to_db) + \
                          "," + str(sensor_config.enable_custom) + \
                          "," + str(version) + \
                          "," + str(get_last_updated())
    except Exception as error:
        logger.error("Sensor reading failed - " + str(error))
        str_sensor_data = "Sensor Unit, Data Retrieval, Failed, 0, 0, 0, 0, 0, 0, 0"

    return str_sensor_data


def get_last_updated():
    try:
        last_updated_file = open(operations_config.last_updated_file_location, 'r')
        tmp_last_updated = last_updated_file.readlines()
        last_updated_file.close()
        last_updated = str(tmp_last_updated[0]) + str(tmp_last_updated[1])
    except Exception as error:
        logger.error("Unable to Load Last Updated File: " + str(error))
        last_updated = "N/A"

    return last_updated


def get_config_information():
    temp_config = operations_config.get_installed_config()
    try:
        tmp_str_config = str(temp_config.sleep_duration_interval) + \
                         "," + str(temp_config.sleep_duration_trigger) + \
                         "," + str(temp_config.write_to_db) + \
                         "," + str(temp_config.enable_custom) + \
                         "," + str(temp_config.acc_variance) + \
                         "," + str(temp_config.mag_variance) + \
                         "," + str(temp_config.gyro_variance)
    except Exception as error:
        logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, 0, 0"

    return tmp_str_config


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


def get_sensor_readings():
    interval_data = operations_sensors.get_interval_sensor_readings()
    trigger_data = operations_sensors.get_trigger_sensor_readings()

    str_interval_types = interval_data.sensor_types
    str_interval_data = interval_data.sensor_readings
    str_trigger_types = trigger_data.sensor_types
    str_trigger_data = trigger_data.sensor_readings

    return_data = [str_interval_types, str_interval_data, str_trigger_types, str_trigger_data]

    return return_data


def restart_services():
    os.system("systemctl restart SensorInterval")
    os.system("systemctl restart SensorTrigger")
    os.system("systemctl restart SensorCommands")


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
                system_info = get_system_information()
                connection.sendall(pickle.dumps(system_info))
                logger.info('Sensor Data Sent to ' + str(client_address[0]))
            elif connection_command == "inkupg":
                os.system("bash /opt/kootnet-sensors/upgrade/update_programs_e-Ink.sh")
                logger.info('/opt/kootnet-sensors/upgrade/update_programs_e-Ink.sh Finished')
                restart_services()
            elif connection_command == "UpgradeOnline":
                os.system("bash /opt/kootnet-sensors/upgrade/update_programs_online.sh")
                logger.info('/opt/kootnet-sensors/upgrade/update_programs_online.sh Finished')
                restart_services()
            elif connection_command == "UpgradeSMB":
                os.system("bash /opt/kootnet-sensors/upgrade/update_programs_smb.sh")
                logger.info('/opt/kootnet-sensors/upgrade/update_programs_smb.sh Finished')
                restart_services()
            elif connection_command == "RebootSystem":
                logger.info('Rebooting System')
                os.system("reboot")
            elif connection_command == "ShutdownSystem":
                logger.info('Shutting Down System')
                os.system("shutdown -h now")
            elif connection_command == "RestartServices":
                logger.info('Sensor Termination sent by ' + str(client_address[0]))
                restart_services()
            elif connection_command == "UpgradeSystemOS":
                logger.info('Updating Operating System & rebooting')
                os.system("apt-get update && apt-get upgrade -y && reboot")
            elif connection_command == "GetConfiguration":
                str_config = get_config_information()
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
                except Exception as error_msg:
                    logger.info("Hostname Change Failed - " + str(error_msg))
            elif tmp_connection_data.decode()[:11] == "SetDateTime":
                logger.info('Setting System DateTime')
                new_datetime = tmp_connection_data.decode()[11:]
                os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[10:])
            elif connection_command == "GetSensorReadings":
                logger.info('Sending Sensor Readings')
                sensor_data = get_sensor_readings()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetHostName":
                logger.info('Sending Sensor HostName')
                sensor_data = operations_sensors.get_hostname()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetSystemUptime":
                logger.info('Sending Sensor System Uptime')
                sensor_data = operations_sensors.get_system_uptime()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetCPUTemperature":
                logger.info('Sending Sensor CPU Temperature')
                sensor_data = operations_sensors.get_cpu_temperature()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetEnvTemperature":
                logger.info('Sending Sensor Temperature')
                sensor_data = operations_sensors.get_sensor_temperature()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetPressure":
                logger.info('Sending Sensor Pressure')
                sensor_data = operations_sensors.get_pressure()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetHumidity":
                logger.info('Sending Sensor Humidity')
                sensor_data = operations_sensors.get_humidity()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetLumen":
                logger.info('Sending Sensor Lumen')
                sensor_data = operations_sensors.get_lumen()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetRGB":
                logger.info('Sending Sensor RGB')
                sensor_data = operations_sensors.get_rgb()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            else:
                logger.info("Invalid command sent:" + connection_data)

            connection.close()

    except Exception as error_msg:
        logger.warning('Socket Failed trying again in 5 Seconds - ' + str(error_msg))
        sleep(2)
