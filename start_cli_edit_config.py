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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from http_server import server_http_auth


logger.primary_logger.debug("CLI Edit Configurations Starting")
installed_sensors = CreateInstalledSensorsConfiguration()
primary_config = CreatePrimaryConfiguration()
trigger_variances = CreateTriggerVariancesConfiguration()
sensor_control_config = CreateSensorControlConfiguration()
weather_underground_config = CreateWeatherUndergroundConfiguration()
luftdaten_config = CreateLuftdatenConfiguration()
open_sense_map_config = CreateOpenSenseMapConfiguration()


def start_script():
    running = True
    while running:
        os.system("clear")
        print("Please Select an Option\n")
        print("1. View/Edit Primary/Installed Sensors/Trigger Variance Configurations")
        print("2. Change Web Login Credentials")
        print("3. Update Python Modules")
        print("4. Upgrade Kootnet Sensors (Standard HTTP)")
        print("5. Upgrade Kootnet Sensors (Development HTTP)")
        print("6. Create New Self Signed SSL Certificate")
        print("7. Enable & Start KootnetSensors")
        print("8. Disable & Start KootnetSensors")
        print("9. Restart KootnetSensors Service")
        print("10. Exit")

        selection = input("Enter Number: ")

        try:
            selection = int(selection)
            if selection == 1:
                os.system("nano " + file_locations.primary_config)
                os.system("nano " + file_locations.installed_sensors_config)
                os.system("nano " + file_locations.trigger_variances_config)
                logger.primary_logger.info("Configurations Viewed or Edited Locally")
            elif selection == 2:
                change_https_auth()
                logger.primary_logger.warning("Web Credentials Edited Locally")
            elif selection == 3:
                print("\nUpgrading all Python pip modules can take awhile.  Please wait ...\n")
                _pip_upgrades()
            elif selection == 4:
                os.system(app_cached_variables.bash_commands["UpgradeOnline"])
            elif selection == 5:
                os.system(app_cached_variables.bash_commands["UpgradeOnlineDEV"])
            elif selection == 6:
                os.system("rm -f -r " + file_locations.http_ssl_folder)
            elif selection == 7:
                os.system(app_cached_variables.bash_commands["EnableService"])
                os.system(app_cached_variables.bash_commands["StartService"])
                logger.primary_logger.info("Kootnet Sensors Enabled Locally")
            elif selection == 8:
                os.system(app_cached_variables.bash_commands["DisableService"])
                os.system(app_cached_variables.bash_commands["StopService"])
                logger.primary_logger.info("Kootnet Sensors Disabled Locally")
            elif selection == 9:
                os.system(app_cached_variables.bash_commands["RestartService"])
            elif selection == 10:
                print("\nYou will have to restart KootnetSensors for changes to take effect.")
                running = False
        except Exception as error:
            print("Invalid Selection: " + str(error))


def change_https_auth():
    """ Terminal app that asks for and replaces Kootnet Sensors Web Portal Login. """
    print("Please enter in a Username and Password for Sensor Web Management")
    new_user = input("New Username: ")
    new_password = input("New Password: ")

    server_http_auth.save_http_auth_to_file(new_user, new_password)
    input("New Username and Password set.  Press enter to continue.")


def _pip_upgrades():
    requirements_text = app_generic_functions.get_file_content(file_locations.program_root_dir + "/requirements.txt")
    for line in requirements_text:
        if line[0] != "#":
            command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + line.strip()
            os.system(command)
    logger.primary_logger.info("Python3 Module Upgrades Complete")


if __name__ == '__main__':
    start_script()
