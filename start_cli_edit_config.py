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
import requests
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from http_server import server_http_auth

logging.captureWarnings(True)
logger.primary_logger.debug("CLI Edit Configurations Starting")
primary_config = CreatePrimaryConfiguration()
trigger_variances = CreateTriggerVariancesConfiguration()
sensor_control_config = CreateSensorControlConfiguration()
weather_underground_config = CreateWeatherUndergroundConfiguration()
luftdaten_config = CreateLuftdatenConfiguration()
open_sense_map_config = CreateOpenSenseMapConfiguration()

remote_get = app_cached_variables.CreateNetworkGetCommands()


def start_script():
    running = True
    while running:
        os.system("clear")
        print("Please Select an Option\n")
        print("1. View/Edit Primary Config & Installed Sensors")
        print("2. Change Web Login Credentials")
        print("3. Update Python Modules")
        print("4. Upgrade Kootnet Sensors (Standard HTTP)")
        print("5. Upgrade Kootnet Sensors (Development HTTP)")
        print("6. Upgrade Kootnet Sensors (Clean HTTP)")
        print("7. Create New Self Signed SSL Certificate")
        print("8. Enable & Start KootnetSensors")
        print("9. Disable & Stop KootnetSensors")
        print("10. Restart KootnetSensors Service")
        print("11. Run Sensor Local Tests")
        print("12. Exit")
        selection = input("Enter Number: ")

        try:
            selection = int(selection)
            os.system("clear")
            if selection == 1:
                os.system("nano " + file_locations.primary_config)
                os.system("nano " + file_locations.installed_sensors_config)
                print("Restart KootnetSensors service for changes to take effect")
            elif selection == 2:
                change_https_auth()
            elif selection == 3:
                print("Upgrading all Python pip modules can take awhile.  Please wait ...\n")
                _pip_upgrades()
                logger.primary_logger.info("Python3 Module Upgrades Complete")
                print("Restart KootnetSensors service for changes to take effect")
            elif selection == 4:
                os.system(app_cached_variables.bash_commands["UpgradeOnline"])
                print("Standard HTTP Upgrade Started.  The service will automatically restart when complete.")
            elif selection == 5:
                os.system(app_cached_variables.bash_commands["UpgradeOnlineDEV"])
                print("Development HTTP Upgrade Started.  The service will automatically restart when complete.")
            elif selection == 6:
                os.system(app_cached_variables.bash_commands["UpgradeOnlineClean"])
                print("Clean - Standard HTTP Upgrade Started.  The service will automatically restart when complete.")
            elif selection == 7:
                os.system("rm -f -r " + file_locations.http_ssl_folder)
                print("Restart KootnetSensors service to generate a new SSL certificate")
            elif selection == 8:
                os.system(app_cached_variables.bash_commands["EnableService"])
                os.system(app_cached_variables.bash_commands["StartService"])
                logger.primary_logger.info("Kootnet Sensors Enabled")
            elif selection == 9:
                os.system(app_cached_variables.bash_commands["DisableService"])
                os.system(app_cached_variables.bash_commands["StopService"])
                logger.primary_logger.info("Kootnet Sensors Disabled")
            elif selection == 10:
                os.system(app_cached_variables.bash_commands["RestartService"])
                print("Restarting Kootnet Sensors service")
            elif selection == 11:
                _test_sensors()
                print("Testing Complete")
            elif selection == 12:
                running = False
        except Exception as error:
            print("Invalid Selection: " + str(error))
        if running:
            input("\nPress enter to continue")


def change_https_auth():
    """ Terminal app that asks for and replaces Kootnet Sensors Web Portal Login. """
    print("Please enter a new Username and Password for Kootnet Sensor's Web Portal")
    new_user = input("New Username: ")
    new_password = input("New Password: ")
    server_http_auth.save_http_auth_to_file(new_user, new_password)


def _pip_upgrades():
    with open(file_locations.program_root_dir + "/requirements.txt") as file:
        requirements_text_lines_list = file.readlines()
    for line in requirements_text_lines_list:
        if line[0] != "#":
            command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + line.strip()
            os.system(command)


def _test_sensors():
    print("*** Starting Sensor Data test ***\n")
    interval_data = get_interval_sensor_data()
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
    print("Showing Test Message on Installed Display (If Installed)")
    display_text_on_sensor("Display Test Message")


def get_interval_sensor_data():
    """ Returns local sensor Interval data. """
    url = "https://127.0.0.1:10065/" + remote_get.sensor_readings
    tmp_return_data = requests.get(url=url, verify=False)
    return_data = tmp_return_data.text.split(app_cached_variables.command_data_separator)
    return [str(return_data[0]), str(return_data[1])]


def display_text_on_sensor(text_message):
    """ Displays text on local sensors display (if any). """
    url = "https://127.0.0.1:10065/DisplayText"
    requests.put(url=url, data={'command_data': text_message}, verify=False)


if __name__ == '__main__':
    start_script()
