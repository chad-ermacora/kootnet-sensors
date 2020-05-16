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
import time
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function
from operations_modules.sqlite_database import check_database_structure
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_mqtt_broker import CreateMQTTBrokerConfiguration
from configuration_modules.config_mqtt_publisher import CreateMQTTPublisherConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration


def run_program_start_checks():
    """
    This function is used before most of the program has started.
    Sets file permissions, checks the database and generates the HTTPS certificates if not present.
    """
    logger.primary_logger.info(" -- Starting Programs Checks ...")
    _set_file_permissions()
    check_database_structure()
    _check_ssl_files()
    if software_version.old_version != software_version.version:
        thread_function(_run_upgrade_checks)
        # Sleep before loading anything due to needed updates
        # The update function will automatically restart the service
        while True:
            time.sleep(30)


def _set_file_permissions():
    """ Re-sets program file permissions. """
    if app_cached_variables.running_with_root:
        _change_permissions_recursive(file_locations.sensor_data_dir, 0o755, 0o744)
        _change_permissions_recursive(file_locations.sensor_config_dir, 0o755, 0o744)
        _change_permissions_recursive(file_locations.program_root_dir, 0o755, 0o755)
        if os.path.isfile(file_locations.http_auth):
            os.chmod(file_locations.http_auth, 0o700)


def _change_permissions_recursive(path, folder_mode, files_mode):
    root = ""
    files = []
    try:
        os.chmod(path, folder_mode)
        for root, dirs, files in os.walk(path, topdown=False):
            for directory in [os.path.join(root, d) for d in dirs]:
                os.chmod(directory, folder_mode)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, files_mode)
    except Exception as error:
        logger.primary_logger.error("Error setting permissions: " + str(error))


def _check_ssl_files():
    """ Checks for, and if missing, creates the HTTPS SSL certificate files. """
    logger.primary_logger.debug("Running SSL Certificate & Key Checks")
    if not os.path.isdir(file_locations.http_ssl_folder):
        os.mkdir(file_locations.http_ssl_folder)

    if os.path.isfile(file_locations.http_ssl_key):
        logger.primary_logger.debug("SSL Key Found")
    else:
        logger.primary_logger.info("SSL Key not Found - Generating Key")
        os.system("openssl genrsa -out " + file_locations.http_ssl_key + " 2048")

    if os.path.isfile(file_locations.http_ssl_csr):
        logger.primary_logger.debug("SSL CSR Found")
    else:
        logger.primary_logger.info("SSL CSR not Found - Generating CSR")
        terminal_command_part1 = "openssl req -new -key " + file_locations.http_ssl_key
        terminal_command_part2 = " -out " + file_locations.http_ssl_csr + " -subj"
        terminal_command_part3 = " '/C=CA/ST=BC/L=Castlegar/O=Kootenay Networks I.T./OU=Kootnet Sensors/CN=kootnet.ca'"
        os.system(terminal_command_part1 + terminal_command_part2 + terminal_command_part3)

    if os.path.isfile(file_locations.http_ssl_crt):
        logger.primary_logger.debug("SSL Certificate Found")
    else:
        logger.primary_logger.info("SSL Certificate not Found - Generating Certificate")
        terminal_command_part1 = "openssl x509 -req -days 3650 -in " + file_locations.http_ssl_csr
        terminal_command_part2 = " -signkey " + file_locations.http_ssl_key + " -out " + file_locations.http_ssl_crt
        os.system(terminal_command_part1 + terminal_command_part2)


def _run_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    logger.primary_logger.info(" -- Starting Upgrade Checks ...")
    previous_version = software_version.CreateRefinedVersion(software_version.old_version)
    no_changes = True

    if previous_version.major_version == "New_Install":
        logger.primary_logger.info("New Install Detected")
        reset_primary_config(log_reset=False)
        reset_installed_sensors(log_reset=False)
        reset_variance_config(log_reset=False)
        reset_display_config(log_reset=False)
        reset_mqtt_broker_config(log_reset=False)
        reset_mqtt_publisher_config(log_reset=False)
        reset_weather_underground_config(log_reset=False)
        reset_luftdaten_config(log_reset=False)
        reset_open_sense_map_config(log_reset=False)
        reset_sensor_control_config(log_reset=False)
        no_changes = False
    else:
        msg = "Old Version: " + software_version.old_version + " || New Version: " + software_version.version
        logger.primary_logger.info(msg)
        if previous_version.major_version == "Beta":
            if previous_version.feature_version == 30:
                if previous_version.minor_version < 34:
                    no_changes = False
                    reset_display_config()
            if previous_version.feature_version == 29:
                if previous_version.minor_version < 13:
                    no_changes = False
                    reset_installed_sensors()
                    reset_variance_config()
        elif previous_version.major_version == "Alpha":
            no_changes = False
            reset_installed_sensors()
            reset_primary_config()
            reset_variance_config()
        else:
            no_changes = False
            msg = "Bad or Missing Previous Version Detected - Resetting Config and Installed Sensors"
            logger.primary_logger.error(msg)
            reset_installed_sensors()
            reset_primary_config()

    if no_changes:
        logger.primary_logger.info("No configuration changes detected")

    software_version.write_program_version_to_file()
    if file_locations.program_root_dir == "/opt/kootnet-sensors":
        logger.primary_logger.info("Upgrade Complete - Restarting the Sensor service")
        os.system(app_cached_variables.bash_commands["RestartService"])
    else:
        logger.primary_logger.info("Upgrade Complete - Please restart the Sensor program")


def reset_primary_config(log_reset=True):
    """ Writes a default main configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Main Configuration Reset ****")
    CreatePrimaryConfiguration(load_from_file=False).save_config_to_file()


def reset_installed_sensors(log_reset=True):
    """ Writes a default installed sensor configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Installed Sensors Configuration Reset ****")
    CreateInstalledSensorsConfiguration(load_from_file=False).save_config_to_file()


def reset_variance_config(log_reset=True):
    """ Writes a default Trigger Variance configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Trigger Variances Configuration Reset ****")
    CreateTriggerVariancesConfiguration(load_from_file=False).save_config_to_file()


def reset_display_config(log_reset=True):
    """ Writes a default Display configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Display Configuration Reset ****")
    CreateDisplayConfiguration(load_from_file=False).save_config_to_file()


def reset_mqtt_broker_config(log_reset=True):
    """ Writes a default MQTT Broker configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** MQTT Broker Configuration Reset ****")
    CreateMQTTBrokerConfiguration(load_from_file=False).save_config_to_file()


def reset_mqtt_publisher_config(log_reset=True):
    """ Writes a default MQTT Publisher configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** MQTT Publisher Configuration Reset ****")
    CreateMQTTPublisherConfiguration(load_from_file=False).save_config_to_file()


def reset_weather_underground_config(log_reset=True):
    """ Writes a default Weather Underground configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Weather Underground Configuration Reset ****")
    CreateWeatherUndergroundConfiguration(load_from_file=False).save_config_to_file()


def reset_luftdaten_config(log_reset=True):
    """ Writes a default Luftdaten configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Luftdaten Configuration Reset ****")
    CreateLuftdatenConfiguration(load_from_file=False).save_config_to_file()


def reset_open_sense_map_config(log_reset=True):
    """ Writes a default Open Sense Map configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Open Sense Map Configuration Reset ****")
    CreateOpenSenseMapConfiguration(load_from_file=False).save_config_to_file()


def reset_sensor_control_config(log_reset=True):
    """ Writes a default Sensor Control configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Sensor Control Configuration Reset ****")
    CreateSensorControlConfiguration(load_from_file=False).save_config_to_file()
