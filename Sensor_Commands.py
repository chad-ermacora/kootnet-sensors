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
import sensor_modules.RaspberryPi_System as RaspberryPi_Sensors
import sensor_modules.Linux_OS as Linux_System
from time import sleep
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensor_Commands_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensor_system = RaspberryPi_Sensors.CreateRPSystem()
sensor_os = Linux_System.CreateLinuxSystem


def get_sensor_data():
    str_sensor_data = ""
    try:
        str_sensor_data = str(sensor_os.get_hostname())
        str_sensor_data = str_sensor_data + "," + str(sensor_os.get_ip())
        str_sensor_data = str_sensor_data + "," + str(sensor_os.get_sys_datetime())
        str_sensor_data = str_sensor_data + "," + str(sensor_os.get_uptime())
        str_sensor_data = str_sensor_data + "," + str(round(sensor_system.cpu_temperature(), 2))
        str_sensor_data = str_sensor_data + "," + str(sensor_os.get_interval_db_size())
        str_sensor_data = str_sensor_data + "," + str(sensor_os.get_trigger_db_size())
        str_sensor_data = str_sensor_data + "\n"
    except Exception as error_msg:
        logger.info("Sensor reading failed - " + str(error_msg))

    return str_sensor_data


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
            connection_data = connection.recv(512)
            connection_data = str(connection_data)
            connection_command = connection_data[2:-1]

            if connection_command == "CheckOnlineStatus":
                logger.info('Sensor Checked')
            elif connection_command == "GetSystemData":
                sensor_data = get_sensor_data()
                connection.sendall(pickle.dumps(sensor_data))
                logger.info('Sensor Data Sent to ' + str(client_address[0]))
            elif connection_command == "inkupg":
                os.system("sudo bash /home/sensors/upgrade/update_programs_e-Ink.sh")
                logger.info('/home/sensors/upgrade/update_programs_e-Ink.sh Finished')
            elif connection_command == "UpgradeOnline":
                os.system("sudo bash /home/sensors/upgrade/update_programs_online.sh")
                logger.info('/home/sensors/upgrade/update_programs_online.sh Finished')
            elif connection_command == "UpgradeSMB":
                os.system("sudo bash /home/sensors/upgrade/update_programs_smb.sh")
                logger.info('/home/sensors/upgrade/update_programs_smb.sh Finished')
            elif connection_command == "RebootSystem":
                os.system("sudo reboot")
            elif connection_command == "ShutdownSystem":
                os.system("sudo shutdown -h now")
            elif connection_command == "TerminatePrograms":
                logger.info('Sensor Termination sent by ' + str(client_address[0]))
                os.system("sudo killall python3")
            elif connection_data[2:16] == "ChangeHostName":
                try:
                    new_host = connection_data[16:-1]
                    os.system("sudo hostnamectl set-hostname " + new_host)
                    logger.info("Hostname Changed to " + new_host + " - OK")
                except Exception as error:
                    logger.info("Hostname Change Failed - " + str(error))
            elif connection_command == "UpgradeSystemOS":
                os.system("sudo apt-get update && sudo apt-get upgrade -y && sudo reboot")
            else:
                logger.info("This didn't work - " + connection_data)
            connection.close()
    except Exception as error:
        logger.info('Socket Failed trying again in 5 Seconds - ' + str(error))
        sleep(5)
