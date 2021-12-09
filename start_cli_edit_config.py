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
import logging
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules.config_primary import CreatePrimaryConfiguration
from upgrade_modules.upgrade_functions import start_kootnet_sensors_upgrade, download_type_smb
from operations_modules.software_version import version
from operations_modules.http_generic_network import get_http_sensor_reading, send_http_command
from upgrade_modules.generic_upgrade_functions import upgrade_python_pip_modules, upgrade_linux_os
from http_server.server_http_generic_functions import save_http_auth_to_file

logging.captureWarnings(True)
logger.primary_logger.debug("Terminal Configuration Tool Starting")
primary_config = CreatePrimaryConfiguration()
local_sensor_address = "127.0.0.1:" + str(primary_config.web_portal_port)

options_menu = """Kootnet Sensors {{ Version }} - Terminal Configuration Tool\n
1. View/Edit Primary & Installed Sensors Configurations
2. Change Web Login Credentials
3. Update Python Modules
4. Upgrade Operating System
5. Upgrade Kootnet Sensors (Standard HTTP)
6. Re-Install Kootnet Sensors (Latest Standard HTTP)
7. Create New Self Signed SSL Certificate
8. Restart KootnetSensors Service
9. Run Sensor Local Tests
10. View Logs
11. Advanced Menu
12. Exit
""".replace("{{ Version }}", version)

extra_options_menu = """Advanced Menu\n
21. Upgrade Kootnet Sensors (Development HTTP)
22. Re-Install Kootnet Sensors (Latest Development HTTP)
23. Enable & Start KootnetSensors
24. Disable & Stop KootnetSensors
25. Reset ALL Configurations to Default
26. Upgrade Kootnet Sensors (Standard SMB)
27. Upgrade Kootnet Sensors (Development SMB)
28. Re-Install Kootnet Sensors (Latest Standard SMB)
29. Re-Install Kootnet Sensors (Latest Developmental SMB)
"""
remote_get_commands = app_cached_variables.network_get_commands
msg_service_not_installed = "Operation Cancelled - Not Running as Installed Service"
msg_upgrade_started = "Kootnet Sensors upgrade has started\nCheck Logs for more Info /home/kootnet_data/logs/"
view_log_system_command = "tail -n 50 "


def start_script():
    running = True
    while running:
        os.system("clear")
        print(options_menu)
        selection = input("Enter Number: ")

        try:
            selection = int(selection)
            os.system("clear")
            if selection == 1:
                os.system("nano " + file_locations.primary_config)
                os.system("nano " + file_locations.installed_sensors_config)
                if app_cached_variables.running_as_service:
                    _restart_service()
            elif selection == 2:
                _change_https_auth()
            elif selection == 3:
                if app_cached_variables.running_as_service:
                    upgrade_python_pip_modules(python_location="/home/kootnet_data/env/bin/python")
                else:
                    print(msg_service_not_installed)
            elif selection == 4:
                if app_cached_variables.running_with_root:
                    print("Starting Operating System Upgrade\n")
                    upgrade_linux_os(thread_the_function=False)
                else:
                    print("OS Upgrade Cancelled - Not Running as root")
            elif selection == 5:
                if app_cached_variables.running_as_service:
                    print("Starting HTTP Standard Upgrade\n")
                    start_kootnet_sensors_upgrade(thread=False)
                    print(msg_upgrade_started)
                else:
                    print(msg_service_not_installed)
            elif selection == 6:
                if app_cached_variables.running_as_service:
                    print("Starting HTTP Standard Re-Install\n")
                    start_kootnet_sensors_upgrade(clean_upgrade=True, thread=False)
                    print(msg_upgrade_started)
                else:
                    print(msg_service_not_installed)
            elif selection == 7:
                os.system("rm -f -r " + file_locations.http_ssl_folder)
                if app_cached_variables.running_as_service:
                    _restart_service(msg="SSL Certificate Removed\nRestarting Service to Create a New Certificate")
                else:
                    print("SSL Certificate Removed")
            elif selection == 8:
                if app_cached_variables.running_as_service:
                    _restart_service(msg="Kootnet Sensors Restarting")
                else:
                    print(msg_service_not_installed)
            elif selection == 9:
                _test_sensors()
                print("Testing Complete")
            elif selection == 10:
                os.system("clear")
                print("Primary Log\n\n")
                os.system(view_log_system_command + file_locations.primary_log)
                input("\nPress enter for the next log")
                os.system("clear")
                print("Network Log\n\n")
                os.system(view_log_system_command + file_locations.network_log)
                input("\nPress enter for the next log")
                os.system("clear")
                print("Sensors Log\n\n")
                os.system(view_log_system_command + file_locations.sensors_log)
                print("\nEnd of Logs")
            elif selection == 11:
                print(extra_options_menu)
            elif selection == 12:
                running = False
            elif selection == 21:
                if app_cached_variables.running_as_service:
                    print("Starting HTTP Developmental Upgrade\n")
                    start_kootnet_sensors_upgrade(dev_upgrade=True, thread=False)
                    print(msg_upgrade_started)
                else:
                    print(msg_service_not_installed)
            elif selection == 22:
                if app_cached_variables.running_as_service:
                    print("Starting HTTP Developmental Re-Install\n")
                    start_kootnet_sensors_upgrade(dev_upgrade=True, clean_upgrade=True, thread=False)
                    print(msg_upgrade_started)
                else:
                    print(msg_service_not_installed)
            elif selection == 23:
                if app_cached_variables.running_as_service:
                    os.system(app_cached_variables.bash_commands["EnableService"])
                    os.system(app_cached_variables.bash_commands["StartService"])
                    logger.primary_logger.info("TCT - Kootnet Sensors Enabled")
                else:
                    print(msg_service_not_installed)
            elif selection == 24:
                if app_cached_variables.running_as_service:
                    os.system(app_cached_variables.bash_commands["DisableService"])
                    os.system(app_cached_variables.bash_commands["StopService"])
                    logger.primary_logger.info("TCT - Kootnet Sensors Disabled")
                else:
                    print(msg_service_not_installed)
            elif selection == 25:
                if input("Are you sure you want to reset ALL configurations? (y/n): ").lower() == "y":
                    os.system("clear")
                    config_list = [file_locations.primary_config, file_locations.installed_sensors_config,
                                   file_locations.display_config, file_locations.checkin_configuration,
                                   file_locations.interval_config, file_locations.trigger_high_low_config,
                                   file_locations.trigger_variances_config, file_locations.email_config,
                                   file_locations.mqtt_publisher_config, file_locations.mqtt_subscriber_config,
                                   file_locations.osm_config, file_locations.weather_underground_config,
                                   file_locations.luftdaten_config]
                    for config in config_list:
                        os.remove(config)
                    if app_cached_variables.running_as_service:
                        _restart_service()
                else:
                    print("Configuration Reset Cancelled")
            elif selection == 26:
                print("Starting SMB Standard Upgrade\n")
                start_kootnet_sensors_upgrade(download_type=download_type_smb, thread=False)
                print(msg_upgrade_started)
            elif selection == 27:
                print("Starting SMB Developmental Upgrade\n")
                start_kootnet_sensors_upgrade(download_type=download_type_smb, dev_upgrade=True, thread=False)
                print(msg_upgrade_started)
            elif selection == 28:
                print("Starting SMB Standard Re-Install\n")
                start_kootnet_sensors_upgrade(download_type=download_type_smb, clean_upgrade=True, thread=False)
                print(msg_upgrade_started)
            elif selection == 29:
                print("Starting SMB Developmental Re-Install\n")
                start_kootnet_sensors_upgrade(
                    download_type=download_type_smb, dev_upgrade=True, clean_upgrade=True, thread=False
                )
                print(msg_upgrade_started)
            else:
                os.system("clear")
                print("Invalid Selection: " + str(selection))
        except ValueError:
            os.system("clear")
            print("Invalid Selection: " + str(selection))
        except Exception as error:
            os.system("clear")
            print("Invalid Selection: " + str(selection) + " - " + str(error))
        if running:
            input("\nPress enter to continue")


def _change_https_auth():
    """ Terminal app that asks for and replaces Kootnet Sensors Web Portal Login. """
    print("Please enter a new Username and Password for Kootnet Sensor's Web Portal")
    new_user = input("New Username: ")
    new_password = input("New Password: ")
    save_http_auth_to_file(new_user, new_password)
    _restart_service()


def _test_sensors():
    print("*** Starting Sensor Data test ***\n")
    try:
        tmp_interval_data = get_http_sensor_reading(local_sensor_address, remote_get_commands.sensor_readings)
        tmp_interval_data = tmp_interval_data.split(app_cached_variables.command_data_separator)
        interval_data = [str(tmp_interval_data[0]), str(tmp_interval_data[1])]
        sensor_types = interval_data[0].split(",")
        sensor_readings = interval_data[1].split(",")

        str_message = ""
        color_readings1 = ""
        color_readings2 = ""
        acc_readings = ""
        mag_readings = ""
        gyro_readings = ""
        for sensor_type, sensor_reading in zip(sensor_types, sensor_readings):
            if sensor_type[:3] == "Red" or sensor_type[:5] == "Green" or sensor_type[:4] == "Blue":
                color_readings1 += str(sensor_type) + ": " + str(sensor_reading) + " || "
            elif sensor_type[:6] == "Orange" or sensor_type[:6] == "Yellow" or sensor_type[:6] == "Violet":
                color_readings2 += str(sensor_type) + ": " + str(sensor_reading) + " || "
            elif sensor_type[:4] == "Acc_":
                acc_readings += str(sensor_type) + ": " + str(sensor_reading) + " || "
            elif sensor_type[:4] == "Mag_":
                mag_readings += str(sensor_type) + ": " + str(sensor_reading) + " || "
            elif sensor_type[:4] == "Gyro":
                gyro_readings += str(sensor_type) + ": " + str(sensor_reading) + " || "
            else:
                str_message = str_message + str(sensor_type) + ": " + str(sensor_reading) + "\n"
        for tmp_readings in [color_readings1, color_readings2, acc_readings, mag_readings, gyro_readings]:
            if len(tmp_readings) > 4:
                str_message += tmp_readings[:-4] + "\n"

        print(str_message)
        print("Showing Test Message on Installed Display (If Installed)\n")
        send_http_command(
            sensor_address=local_sensor_address,
            http_command="DisplayText",
            dic_data={'command_data': "Display Test Message"}
        )
    except Exception as error:
        logger.primary_logger.error("TCT - Tests Failed: " + str(error))


def _restart_service(msg="Restarting Kootnet Sensors service to apply changes"):
    print(msg)
    os.system(app_cached_variables.bash_commands["RestartService"])


if __name__ == '__main__':
    start_script()
