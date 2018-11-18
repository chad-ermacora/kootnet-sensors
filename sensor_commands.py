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
import pickle
import socket
from threading import Thread
from time import sleep

import operations_commands
import operations_config
import operations_logger
import operations_sensors
from operations_sensors import rp_sense_hat_sensor_access

installed_sensors = operations_config.get_installed_sensors()

# If installed, start up SenseHAT Joystick program
if installed_sensors.raspberry_pi_sense_hat:
    sense_joy_stick_thread = Thread(target=rp_sense_hat_sensor_access.start_joy_stick_commands)
    sense_joy_stick_thread.daemon = True
    sense_joy_stick_thread.start()

# Starts a socket server and waits for commands
while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('', 10065)
        operations_logger.network_logger.info("starting up on {} port {}".format(*server_address))
        sock.bind(server_address)
        sock.listen(12)

        while True:
            connection, client_address = sock.accept()
            operations_logger.network_logger.debug(
                "Connection from " + str(client_address[0]) + " Port: " + str(client_address[1]))
            tmp_connection_data = connection.recv(4096)
            connection_data = str(tmp_connection_data)
            connection_command = connection_data[2:-1]

            if connection_command == "CheckOnlineStatus":
                operations_logger.network_logger.info("Sensor Checked")
            elif connection_command == "GetSystemData":
                system_info = operations_commands.get_system_information()
                connection.sendall(pickle.dumps(system_info))
                operations_logger.network_logger.info("* Sensor Data Sent to " + str(client_address[0]))
            elif connection_command == "inkupg":
                os.system(operations_commands.bash_commands["inkupg"])
                operations_logger.network_logger.info("* update_programs_e-Ink.sh Complete")
            elif connection_command == "UpgradeOnline":
                os.system(operations_commands.bash_commands["UpgradeOnline"])
                operations_logger.network_logger.info("* update_programs_online.sh Complete")
            elif connection_command == "UpgradeSMB":
                os.system(operations_commands.bash_commands["UpgradeSMB"])
                operations_logger.network_logger.info("* update_programs_smb.sh Complete")
            elif connection_command == "CleanOnline":
                os.system(operations_commands.bash_commands["CleanOnline"])
                operations_logger.network_logger.info("* Started Clean Upgrade - Online")
            elif connection_command == "CleanSMB":
                os.system(operations_commands.bash_commands["CleanSMB"])
                operations_logger.network_logger.info("* Started Clean Upgrade - SMB")
            elif connection_command == "RebootSystem":
                operations_logger.network_logger.info("* Rebooting System")
                os.system(operations_commands.bash_commands["RebootSystem"])
            elif connection_command == "ShutdownSystem":
                operations_logger.network_logger.info("* Shutting Down System")
                os.system(operations_commands.bash_commands["ShutdownSystem"])
            elif connection_command == "RestartServices":
                operations_logger.network_logger.info("* Sensor Restart Services sent by " + str(client_address[0]))
                operations_commands.restart_services()
            elif connection_command == "UpgradeSystemOS":
                operations_logger.network_logger.info("* Updating Operating System & rebooting")
                os.system(operations_commands.bash_commands["UpgradeSystemOS"])
            elif connection_command == "GetConfiguration":
                str_config = operations_commands.get_config_information()
                connection.sendall(pickle.dumps(str_config))
                operations_logger.network_logger.info("* Sensor Data Sent to " + str(client_address[0]))
            elif tmp_connection_data.decode()[:16] == "SetConfiguration":
                operations_logger.network_logger.info("* Setting Sensor Configuration")
                operations_commands.set_sensor_config(tmp_connection_data.decode())
            elif tmp_connection_data.decode()[:14] == "ChangeHostName":
                try:
                    new_host = tmp_connection_data.decode()[14:]
                    os.system("hostnamectl set-hostname " + new_host)
                    operations_logger.network_logger.info("* Hostname Changed to " + new_host + " - OK")
                except Exception as error_msg:
                    operations_logger.network_logger.info("* Hostname Change Failed - " + str(error_msg))
            elif tmp_connection_data.decode()[:11] == "SetDateTime":
                operations_logger.network_logger.info("* Setting System DateTime")
                new_datetime = tmp_connection_data.decode()[11:]
                os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
            elif connection_command == "GetSensorReadings":
                operations_logger.network_logger.info("* Sending Sensor Readings")
                sensor_data = operations_commands.get_sensor_readings()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetHostName":
                operations_logger.network_logger.info("* Sending Sensor HostName")
                sensor_data = operations_sensors.get_hostname()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetSystemUptime":
                operations_logger.network_logger.info("* Sending Sensor System Uptime")
                sensor_data = operations_sensors.get_system_uptime()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetCPUTemperature":
                operations_logger.network_logger.info("* Sending Sensor CPU Temperature")
                sensor_data = operations_sensors.get_cpu_temperature()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetEnvTemperature":
                operations_logger.network_logger.info("* Sending Sensor Temperature")
                sensor_data = operations_sensors.get_sensor_temperature()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetPressure":
                operations_logger.network_logger.info("* Sending Sensor Pressure")
                sensor_data = operations_sensors.get_pressure()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetHumidity":
                operations_logger.network_logger.info("* Sending Sensor Humidity")
                sensor_data = operations_sensors.get_humidity()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetLumen":
                operations_logger.network_logger.info("* Sending Sensor Lumen")
                sensor_data = operations_sensors.get_lumen()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetRGB":
                operations_logger.network_logger.info("* Sending Sensor RGB")
                sensor_data = operations_sensors.get_rgb()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetAccelerometerXYZ":
                operations_logger.network_logger.info("* Sending Sensor Accelerometer XYZ")
                sensor_data = operations_sensors.get_accelerometer_xyz()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetMagnetometerXYZ":
                operations_logger.network_logger.info("* Sending Sensor Magnetometer XYZ")
                sensor_data = operations_sensors.get_magnetometer_xyz()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetGyroscopeXYZ":
                operations_logger.network_logger.info("* Sending Sensor Gyroscope XYZ")
                sensor_data = operations_sensors.get_gyroscope_xyz()
                print(str(sensor_data))
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetPrimaryLog":
                operations_logger.network_logger.info("* Sending Primary Log")
                sensor_data = operations_commands.get_sensor_log(operations_logger.primary_log)
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetSensorsLog":
                operations_logger.network_logger.info("* Sending Sensor Log")
                sensor_data = operations_commands.get_sensor_log(operations_logger.sensors_log)
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetNetworkLog":
                operations_logger.network_logger.info("* Sending Network Log")
                sensor_data = operations_commands.get_sensor_log(operations_logger.network_log)
                connection.sendall(pickle.dumps(sensor_data))
            elif connection_command == "GetInstalledSensors":
                operations_logger.network_logger.info("* Sending Installed Sensors")
                sensor_data = operations_config.get_installed_sensors()
                connection.sendall(pickle.dumps(sensor_data))
            else:
                operations_logger.network_logger.info("Invalid command sent:" + connection_data)

            connection.close()

    except Exception as error_msg:
        operations_logger.network_logger.warning("Socket Failed trying again in 5 Seconds - " + str(error_msg))
        sleep(5)
