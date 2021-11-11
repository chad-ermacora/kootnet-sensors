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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import write_file_to_disk, thread_function, get_file_content
from operations_modules.sqlite_database import check_main_database_structure, check_checkin_database_structure, \
    run_database_integrity_check, check_mqtt_subscriber_database_structure
from upgrade_modules.program_upgrade_checks import run_configuration_upgrade_checks
from http_server.server_http_generic_functions import set_http_auth_from_file


def run_program_start_checks():
    """
    This function is used before most of the program has started.
    Sets file permissions, checks the database and generates the HTTPS certificates if not present.
    """
    logger.primary_logger.info(" -- Pre-Start Initializations Started")
    _check_sensor_id()
    _check_ssl_files()
    set_http_auth_from_file()
    _set_file_permissions()
    _add_tct_terminal_alias()
    thread_function(_create_secondary_python_venv)

    if software_version.old_version != software_version.version:
        run_database_integrity_check(file_locations.sensor_database, quick=False)
        run_database_integrity_check(file_locations.sensor_checkin_database, quick=False)
        run_database_integrity_check(file_locations.mqtt_subscriber_database, quick=False)
        run_configuration_upgrade_checks()
        thread_function(check_checkin_database_structure)
        thread_function(check_mqtt_subscriber_database_structure)
    else:
        run_database_integrity_check(file_locations.sensor_database)
        run_database_integrity_check(file_locations.sensor_checkin_database)
        run_database_integrity_check(file_locations.mqtt_subscriber_database)
    thread_function(check_main_database_structure)
    logger.primary_logger.info(" -- Pre-Start Initializations Complete")


def _check_sensor_id():
    """
    Checks for Sensor Checkin ID file, if missing, creates one.
    The Sensor ID is Randomly Generated and used to track Software Usage and Online History of Sensors.
    """
    try:
        if not os.path.isfile(file_locations.sensor_id):
            random_id = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
            write_file_to_disk(file_locations.sensor_id, random_id)
        else:
            random_id = get_file_content(file_locations.sensor_id).strip()
    except Exception as error:
        logger.primary_logger.error("Problem Creating Sensor ID: " + str(error))
        random_id = "Error"
    app_cached_variables.tmp_sensor_id = "KS" + random_id


def _set_file_permissions():
    """ Re-sets program file permissions. """
    file_rights_data = 0o666
    file_rights_sensitive = 0o666
    if app_cached_variables.running_as_service:
        file_rights_data = 0o644
        file_rights_sensitive = 0o600

    # Disable logging due to error thrown in Dev Environment
    _change_permissions_recursive(file_locations.program_root_dir, 0o755, 0o755)
    _change_permissions_recursive(file_locations.sensor_config_dir, 0o755, file_rights_sensitive)
    _change_permissions_recursive(file_locations.sensor_data_dir, 0o755, file_rights_data)
    _change_permissions_recursive(file_locations.upgrade_scripts_folder, 0o755, 0o755)
    _change_permissions_recursive(file_locations.log_directory, 0o755, file_rights_data)
    _change_permissions_recursive(file_locations.http_ssl_folder, 0o755, file_rights_sensitive)


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
        logger.primary_logger.debug("Error setting permissions: " + str(error))


def _check_ssl_files():
    """ Checks for, and if missing, creates the HTTPS SSL certificate files. """
    logger.primary_logger.debug("Running SSL Certificate & Key Checks")
    try:
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


def _add_tct_terminal_alias():
    if app_cached_variables.running_as_service and app_cached_variables.running_with_root:
        kootnet_alias_file_location = "/etc/profile.d/00-kootnet-aliases.sh"
        if not os.path.isfile(kootnet_alias_file_location):
            kootnet_tct_id_line = "### Kootnet Sensors Terminal Configuration Tool Alias ###"
            python_exe_loc = file_locations.sensor_data_dir + "/upgrade_env/bin/python"
            tct_alias = "alias ks-tct='sudo " + python_exe_loc + " /opt/kootnet-sensors/start_cli_edit_config.py'"

            try:
                with open(kootnet_alias_file_location, "w") as alias_file:
                    alias_file.write(kootnet_tct_id_line + "\n" + tct_alias)
                logger.primary_logger.debug("-- TCT alias added")
            except Exception as error:
                logger.primary_logger.warning("-- Unable to create bash alias for TCT: " + str(error))


def _create_secondary_python_venv():
    """
    Checks to see if the secondary Python virtual environment is present, if not, creates it
    Used for software upgrades and Kootnet Sensor's TCT
    :return: Nothing
    """
    if app_cached_variables.running_as_service and app_cached_variables.running_with_root:
        upgrade_env_dir = file_locations.sensor_data_dir + "/upgrade_env/"
        try:
            if not os.path.isdir(upgrade_env_dir):
                os.mkdir(upgrade_env_dir)
            if not os.path.isfile(upgrade_env_dir + "bin/python"):
                logger.primary_logger.info(" - Creating Kootnet Sensor's Upgrade & TCT Python Virtual Environment")
                os.system("python3 -m venv " + upgrade_env_dir)
                os.system(upgrade_env_dir + "bin/python3 -m pip install requests")
                logger.primary_logger.info(" - Python Virtual Environment Created Successfully")
        except Exception as error:
            logger.primary_logger.critical("-- Unable to create Python virtual environment for upgrades: " + str(error))
