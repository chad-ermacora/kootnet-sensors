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
from upgrade_modules.upgrade_functions import start_kootnet_sensors_upgrade, download_type_smb
from operations_modules.software_version import version
from http_server.server_http_generic_functions import save_http_auth_to_file
imports_ok = False
try:
    import requests
    imports_ok = True
except Exception as import_error:
    logger.primary_logger.error("Terminal Configuration Tool - Import: " + str(import_error))

logging.captureWarnings(True)
logger.primary_logger.debug("Terminal Configuration Tool Starting")

remote_get = app_cached_variables.CreateNetworkGetCommands()

options_menu = """Kootnet Sensors {{ Version }} - Terminal Configuration Tool\n
1. View/Edit Primary Config & Installed Sensors
2. Reset ALL Configurations to Default
3. Change Web Login Credentials
4. Update Python Modules
5. Upgrade Kootnet Sensors (Standard HTTP)
6. Upgrade Kootnet Sensors (Development HTTP)
7. Re-Install Kootnet Sensors (Latest Standard HTTP)
8. Create New Self Signed SSL Certificate
9. Enable & Start KootnetSensors
10. Disable & Stop KootnetSensors
11. Restart KootnetSensors Service
12. Run Sensor Local Tests
13. Exit
""".replace("{{ Version }}", version)

any_key_shutdown = "\nThe TCT must be restarted\n\nPress enter to close"
msg_service_not_installed = "Operation Cancelled - Not Running as Installed Service"
msg_requests_missing = "Unable to start update - Python requests module required"


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
            elif selection == 3:
                _change_https_auth()
            elif selection == 4:
                if app_cached_variables.running_as_service:
                    _pip_upgrades()
                else:
                    print(msg_service_not_installed)
            elif selection == 5:
                if app_cached_variables.running_as_service:
                    if imports_ok:
                        start_kootnet_sensors_upgrade()
                        input(any_key_shutdown)
                        running = False
                    else:
                        print(msg_requests_missing)
                else:
                    print(msg_service_not_installed)
            elif selection == 6:
                if app_cached_variables.running_as_service:
                    if imports_ok:
                        start_kootnet_sensors_upgrade(dev_upgrade=True)
                        input(any_key_shutdown)
                        running = False
                    else:
                        print(msg_requests_missing)
                else:
                    print(msg_service_not_installed)
            elif selection == 7:
                if app_cached_variables.running_as_service:
                    if imports_ok:
                        start_kootnet_sensors_upgrade(clean_upgrade=True)
                        input(any_key_shutdown)
                        running = False
                    else:
                        print(msg_requests_missing)
                else:
                    print(msg_service_not_installed)
            elif selection == 8:
                os.system("rm -f -r " + file_locations.http_ssl_folder)
                if app_cached_variables.running_as_service:
                    _restart_service(msg="SSL Certificate Removed, Restarting Service to Create a New Certificate")
                else:
                    print("SSL Certificate Removed")
            elif selection == 9:
                if app_cached_variables.running_as_service:
                    os.system(app_cached_variables.bash_commands["EnableService"])
                    os.system(app_cached_variables.bash_commands["StartService"])
                    logger.primary_logger.info("TCT - Kootnet Sensors Enabled")
                else:
                    print(msg_service_not_installed)
            elif selection == 10:
                if app_cached_variables.running_as_service:
                    os.system(app_cached_variables.bash_commands["DisableService"])
                    os.system(app_cached_variables.bash_commands["StopService"])
                    logger.primary_logger.info("TCT - Kootnet Sensors Disabled")
                else:
                    print(msg_service_not_installed)
            elif selection == 11:
                if app_cached_variables.running_as_service:
                    _restart_service(msg="Kootnet Sensors Restarting")
                else:
                    print(msg_service_not_installed)
            elif selection == 12:
                if imports_ok:
                    _test_sensors()
                    print("Testing Complete")
                else:
                    print(msg_requests_missing)
            elif selection == 13:
                running = False
            elif selection == 22:
                print("Starting SMB Dev Upgrade")
                start_kootnet_sensors_upgrade(dev_upgrade=True, download_type=download_type_smb)
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


def _pip_upgrades():
    print("Upgrading all Python pip modules can take awhile.  Please wait ...\n")
    try:
        with open(file_locations.program_root_dir + "/requirements.txt") as file:
            requirements_text_lines_list = file.readlines()
        for line in requirements_text_lines_list:
            if line[0] != "#":
                command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + line.strip()
                os.system(command)
        logger.primary_logger.info("TCT - Python3 Module Upgrades Complete\n")
        _restart_service()
    except Exception as error:
        logger.primary_logger.error("TCT - Python3 Module Upgrades: " + str(error))


def _test_sensors():
    print("*** Starting Sensor Data test ***\n")
    try:
        interval_data = _get_interval_sensor_data()
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
        _display_text_on_sensor("Display Test Message")
    except Exception as error:
        logger.primary_logger.error("TCT - Tests Failed: " + str(error))


def _get_interval_sensor_data():
    """ Returns local sensor Interval data. """
    try:
        url = "https://127.0.0.1:10065/" + remote_get.sensor_readings
        tmp_return_data = requests.get(url=url, verify=False)
        return_data = tmp_return_data.text.split(app_cached_variables.command_data_separator)
        return [str(return_data[0]), str(return_data[1])]
    except Exception as error:
        logger.primary_logger.warning("TCT - Get Sensor Data - Unable to connect to localhost: " + str(error))
    return ["error", "error"]


def _display_text_on_sensor(text_message):
    """ Displays text on local sensors display (if any). """
    try:
        url = "https://127.0.0.1:10065/DisplayText"
        requests.put(url=url, data={'command_data': text_message}, verify=False)
    except Exception as error:
        logger.primary_logger.warning("TCT - Display - Unable to connect to localhost: " + str(error))


def _restart_service(msg="Restarting Kootnet Sensors service to apply changes"):
    print(msg)
    os.system(app_cached_variables.bash_commands["RestartService"])


if __name__ == '__main__':
    start_script()
