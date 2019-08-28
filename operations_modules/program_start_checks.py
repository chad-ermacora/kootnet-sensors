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
import sqlite3
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import sqlite_database
from operations_modules import program_upgrade_functions
from operations_modules import os_cli_commands


class CreateRefinedVersion:
    """ Takes the provided program version and creates a data class object. """

    def __init__(self, version):
        try:
            version_split = version.split(".")
            self.major_version = version_split[0]
            self.feature_version = int(version_split[1])
            self.minor_version = int(version_split[2])
        except Exception as error:
            logger.primary_logger.warning("Bad Version - " + str(version))
            logger.primary_logger.debug(str(error))
            self.major_version = 0
            self.feature_version = 0
            self.minor_version = 0


def check_ssl_files():
    logger.primary_logger.debug("Running SSL Certificate & Key Checks")

    if os.path.isfile(file_locations.http_ssl_key):
        logger.primary_logger.debug("SSL Key Found")
    else:
        logger.primary_logger.warning("SSL Key not Found - Generating Key")
        command = "openssl genrsa -out " + file_locations.http_ssl_key + " 2048"
        os.system(command)

    if os.path.isfile(file_locations.http_ssl_csr):
        logger.primary_logger.debug("SSL CSR Found")
    else:
        logger.primary_logger.warning("SSL CSR not Found - Generating CSR")
        command2 = "openssl req -new -key " + file_locations.http_ssl_key + " -out " + file_locations.http_ssl_csr + \
                   " -subj '/C=CA/ST=BC/L=Castlegar/O=Kootenay Networks I.T./OU=Kootnet Sensors/CN=kootnet.ca'"
        os.system(command2)

    if os.path.isfile(file_locations.http_ssl_crt):
        logger.primary_logger.debug("SSL Certificate Found")
    else:
        logger.primary_logger.warning("SSL Certificate not Found - Generating Certificate")
        command3 = "openssl x509 -req -days 3650 -in " + file_locations.http_ssl_csr + \
                   " -signkey " + file_locations.http_ssl_key + " -out " + file_locations.http_ssl_crt
        os.system(command3)


def check_database_structure():
    """ Loads or creates the SQLite Database, verifying all Tables and Columns. """
    logger.primary_logger.debug("Running DB Checks")
    database_variables = sqlite_database.CreateDatabaseVariables()

    try:
        db_connection = sqlite3.connect(file_locations.sensor_database_location)
        db_cursor = db_connection.cursor()

        _create_table_and_datetime(database_variables.table_interval, db_cursor)
        _create_table_and_datetime(database_variables.table_trigger, db_cursor)
        for column_intervals, column_trigger in zip(database_variables.get_sensor_columns_list(),
                                                    database_variables.get_sensor_columns_list()):
            _check_sql_table_and_column(database_variables.table_interval, column_intervals, db_cursor)
            _check_sql_table_and_column(database_variables.table_trigger, column_trigger, db_cursor)

        _create_table_and_datetime(database_variables.table_other, db_cursor)
        for column_other in database_variables.get_other_columns_list():
            _check_sql_table_and_column(database_variables.table_other, column_other, db_cursor)

        db_connection.commit()
        db_connection.close()
    except Exception as error:
        logger.primary_logger.error("DB Connection Failed: " + str(error))


def _create_table_and_datetime(table, db_cursor):
    """ Add's or verifies provided table and DateTime column in the SQLite Database. """
    try:
        # Create or update table
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table, nf="DateTime", ft="TEXT"))
        logger.primary_logger.debug("Table '" + table + "' - Created")
    except Exception as error:
        logger.primary_logger.debug(table + " - " + str(error))


def _check_sql_table_and_column(table_name, column_name, db_cursor):
    """ Add's or verifies provided table and column in the SQLite Database. """
    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn=column_name, ct="TEXT"))
        logger.primary_logger.debug("COLUMN '" + column_name + "' - Created")
    except Exception as error:
        logger.primary_logger.debug("COLUMN '" + column_name + "' - " + str(error))


def run_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    logger.primary_logger.debug("Old Version: " + software_version.old_version +
                                " || New Version: " + software_version.version)
    previous_version = CreateRefinedVersion(software_version.old_version)
    no_changes = True

    if previous_version.major_version == "New_Install":
        no_changes = False
        logger.primary_logger.info("New Install Detected")

    elif previous_version.major_version == "Alpha":
        if previous_version.feature_version < 26:
            no_changes = False
            logger.primary_logger.info("Upgraded: " + software_version.old_version +
                                       " || New: " + software_version.version)
            program_upgrade_functions.reset_installed_sensors()
            program_upgrade_functions.reset_config()
            program_upgrade_functions.reset_variance_config()
        elif previous_version.feature_version == 26:
            no_changes = False
            program_upgrade_functions.reset_installed_sensors()
        elif previous_version.feature_version == 27:
            if previous_version.minor_version < 8:
                program_upgrade_functions.reset_installed_sensors()
    else:
        no_changes = False
        logger.primary_logger.error("Bad or Missing Previous Version Detected - Resetting Config and Installed Sensors")
        program_upgrade_functions.reset_installed_sensors()
        program_upgrade_functions.reset_config()

    # Since run_upgrade_checks is only run if there is a different version, show upgrade but no configuration changes
    if no_changes:
        logger.primary_logger.info("Upgrade detected || No configuration changes || Old: " +
                                   software_version.old_version + " New: " + software_version.version)
    software_version.write_program_version_to_file()
    restart_services()


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(os_cli_commands.restart_sensor_services_command)


def set_file_permissions():
    """ Re-sets program file permissions. """
    os.system(os_cli_commands.bash_commands["SetPermissions"])
