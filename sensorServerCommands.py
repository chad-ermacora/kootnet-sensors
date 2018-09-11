'''
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
'''
import os
import socket
import pickle
import sensor_modules.pimoroni_enviro
import sensor_modules.RP_system
from time import sleep


def get_sensor_data():
    try:
        sensor_data = str(sensor_modules.RP_system.get_hostname())
        sensor_data = sensor_data + "," + \
            str(sensor_modules.RP_system.get_ip())
        sensor_data = sensor_data + "," + \
            str(sensor_modules.RP_system.get_sys_datetime())
        sensor_data = sensor_data + "," + \
            str(sensor_modules.RP_system.get_uptime())
        sensor_data = sensor_data + "," + \
            str(round(sensor_modules.RP_system.cpu_temperature(),2))
        sensor_data = sensor_data + "," + \
            str(sensor_modules.RP_system.get_primary_db_size())
        sensor_data = sensor_data + "," + \
            str(sensor_modules.RP_system.get_motion_db_size())
        sensor_data = sensor_data + "\n"
    except:
        print("\n\nSensor reading failed\n\n")

    return sensor_data

network_wait = 0
while network_wait == 0:
    try:
        # Create a TCP/IP socket and Bind the socket to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('', 10065)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        network_wait = 1
    except:
        sleep(5)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('\nWaiting for a Connection ... \n')
    connection, client_address = sock.accept()

    try:
        print("Connection from " + str(client_address[0]) + \
              " Port: " + str(client_address[1]))
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
            os.system("sudo bash /home/sensors/upgrade/" +
                      "update_progs_e-Ink.sh")
            print('/home/sensors/upgrade/update_progs_e-Ink.sh Finished')
        elif connection_command == "online":
            os.system("sudo bash /home/sensors/upgrade/update_progs_online.sh")
            print('/home/sensors/upgrade/update_progs_online.sh Finished')
        elif connection_command == "nasupg":
            os.system("sudo bash /home/sensors/upgrade/" +
                      "install_update_sensor_nas.sh")
            print('/home/sensors/upgrade/install_update_sensor_nas.sh Finished')
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
            except:
                print("Hostname Change Failed - Null hostname?")
        else:
            print("This didn't work - " + connection_data)
    finally:
        # Clean up the connection
        connection.close()
        print("Socket Closed")
