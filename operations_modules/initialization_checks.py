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
import random
import string
from threading import Thread
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import write_file_to_disk
from operations_modules.sqlite_database import check_main_database_structure, check_checkin_database_structure
from upgrade_modules.program_upgrade_checks import run_configuration_upgrade_checks

create_directories_for_files = [file_locations.mosquitto_configuration]


def run_program_start_checks():
    """
    This function is used before most of the program has started.
    Sets file permissions, checks the database and generates the HTTPS certificates if not present.
    """
    logger.primary_logger.info(" -- Pre-Start Initializations Started")
    _check_directories()
    _set_file_permissions()
    _check_ssl_files()
    _check_sensor_id()
    if software_version.old_version != software_version.version:
        db_check_threads = [Thread(target=check_main_database_structure),
                            Thread(target=check_checkin_database_structure)]
        for thread in db_check_threads:
            thread.daemon = True
            thread.start()
        for thread in db_check_threads:
            thread.join()
        run_configuration_upgrade_checks()
    logger.primary_logger.info(" -- Pre-Start Initializations Complete")


def _check_directories():
    try:
        if app_cached_variables.running_with_root:
            for directory_check in create_directories_for_files:
                current_directory = ""
                for found_dir in directory_check.split("/")[1:-1]:
                    current_directory += "/" + str(found_dir)
                    if not os.path.isdir(current_directory):
                        os.mkdir(current_directory)
    except Exception as error:
        logger.primary_logger.error("Problem Checking Program Directories: " + str(error))


def _check_sensor_id():
    """
    Checks for Sensor Checkin ID file, if missing, creates one.
    The Sensor ID is Randomly Generated and used to track Software Usage and Online History of Sensors.
    """
    try:
        if not os.path.isfile(file_locations.sensor_checkin_id):
            random_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            write_file_to_disk(file_locations.sensor_checkin_id, random_id)
    except Exception as error:
        logger.primary_logger.error("Problem Creating Sensor ID: " + str(error))


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
    try:
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
    except Exception as error:
        logger.primary_logger.error("Problem Creating HTTPS SSL Files: " + str(error))
