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
import sensor_modules.RaspberryPi_Sensors as RaspberryPi_Sensors
import sensor_modules.Linux_System as Linux_System
from time import sleep


def get_sensor_data():
    str_sensor_data = ""
    try:
        str_sensor_data = str(Linux_System.get_hostname())
        str_sensor_data = str_sensor_data + "," + str(Linux_System.get_ip())
        str_sensor_data = str_sensor_data + "," + str(Linux_System.get_sys_datetime())
        str_sensor_data = str_sensor_data + "," + str(Linux_System.get_uptime())
        str_sensor_data = str_sensor_data + "," + str(round(RaspberryPi_Sensors.cpu_temperature(), 2))
        str_sensor_data = str_sensor_data + "," + str(Linux_System.get_primary_db_size())
        str_sensor_data = str_sensor_data + "," + str(Linux_System.get_motion_db_size())
        str_sensor_data = str_sensor_data + "\n"
    except Exception as error_msg:
        print("Sensor reading  failed - " + str(error_msg))

    return str_sensor_data


while True:
    try:
        # Create a TCP/IP socket and Bind the socket to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('', 10065)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        sock.listen(1)
        while True:
            print('\nWaiting for a Connection ... \n')
            connection, client_address = sock.accept()
            print("Connection from " + str(client_address[0]) + " Port: " + str(client_address[1]))
            connection_data = connection.recv(512)
            connection_data = str(connection_data)
            connection_command = connection_data[2:8]

            if connection_command == "checks":
                print('Sensor Checked')
            elif connection_command == "datagt":
                sensor_data = get_sensor_data()
                connection.sendall(pickle.dumps(sensor_data))
                print('Sensor Data Sent to ' + str(client_address[0]))
            elif connection_command == "inkupg":
                os.system("sudo bash /home/sensors/upgrade/update_programs_e-Ink.sh")
                print('/home/sensors/upgrade/update_programs_e-Ink.sh Finished')
            elif connection_command == "online":
                os.system("sudo bash /home/sensors/upgrade/update_programs_online.sh")
                print('/home/sensors/upgrade/update_programs_online.sh Finished')
            elif connection_command == "nasupg":
                os.system("sudo bash /home/sensors/upgrade/update_programs_smb.sh")
                print('/home/sensors/upgrade/update_programs_smb.sh Finished')
            elif connection_command == "reboot":
                os.system("sudo reboot")
            elif connection_command == "shutdn":
                os.system("sudo shutdown -h now")
            elif connection_command == "killpg":
                print('Sensor Termination sent by ' + str(client_address[0]))
                os.system("sudo killall python3")
            elif connection_command == "hostch":
                try:
                    new_host = connection_data[8:-1]
                    os.system("sudo hostnamectl set-hostname " + new_host)
                    print("Hostname Changed to " + new_host + " - OK")
                except Exception as error:
                    print("Hostname Change Failed - " + str(error))
            else:
                print("This didn't work - " + connection_data)
    except Exception as error:
        print('Socket Failed trying again in 5 Seconds - ' + str(error))
        sleep(5)
