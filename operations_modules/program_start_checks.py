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
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import logger
from operations_modules import upgrade_functions
from operations_modules import variables


class CreateRefinedVersion:
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


def check_database_structure():
    logger.primary_logger.debug("Running DB Checks")
    database_variables = variables.CreateDatabaseVariables()

    try:
        db_connection = sqlite3.connect(file_locations.sensor_database_location)
        db_cursor = db_connection.cursor()

        _create_table_and_datetime(database_variables.table_interval, db_cursor)
        for column in database_variables.get_sensor_columns_list():
            _check_sql_table_and_column(database_variables.table_interval, column, db_cursor)

        _create_table_and_datetime(database_variables.table_trigger, db_cursor)
        for column in database_variables.get_sensor_columns_list():
            _check_sql_table_and_column(database_variables.table_trigger, column, db_cursor)

        _create_table_and_datetime(database_variables.table_other, db_cursor)
        for column in database_variables.get_other_columns_list():
            _check_sql_table_and_column(database_variables.table_other, column, db_cursor)

        db_connection.commit()
        db_connection.close()
    except Exception as error:
        logger.primary_logger.error("DB Connection Failed: " + str(error))


def _create_table_and_datetime(table, db_cursor):
    try:
        # Create or update table
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table, nf="DateTime", ft="TEXT"))
        logger.primary_logger.debug("Table '" + table + "' - Created")

    except Exception as error:
        logger.primary_logger.debug(table + " - " + str(error))


def _check_sql_table_and_column(table_name, column_name, db_cursor):
    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn=column_name, ct="TEXT"))
        logger.primary_logger.debug("COLUMN '" + column_name + "' - Created")
    except Exception as error:
        logger.primary_logger.debug("COLUMN '" + column_name + "' - " + str(error))


def run_upgrade_checks():
    logger.primary_logger.debug("Old Version: " + software_version.old_version +
                                " || New Version: " + software_version.version)
    previous_version = CreateRefinedVersion(software_version.old_version)
    no_changes = True

    if previous_version.major_version == 0:
        no_changes = False
        logger.primary_logger.info("New Install or broken/missing Old Version File")
        upgrade_functions.reset_installed_sensors()
        upgrade_functions.reset_config()

    if previous_version.major_version == "Alpha":
        if previous_version.feature_version == 22:
            no_changes = False
            logger.primary_logger.info("Upgraded: " + software_version.old_version +
                                       " || New: " + software_version.version)
            upgrade_functions.reset_installed_sensors()
            upgrade_functions.reset_config()
        elif previous_version.feature_version == 23:
            if previous_version.minor_version < 24:
                no_changes = False
                upgrade_functions.reset_config()
                logger.primary_logger.info("Upgraded: " + software_version.old_version +
                                           " || New: " + software_version.version)

    if no_changes:
        logger.primary_logger.info("Upgrade detected || No configuration changes || Old: " +
                                   software_version.old_version + " New: " + software_version.version)
    software_version.write_program_version_to_file()
    restart_services()


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(variables.restart_sensor_services_command)


def set_file_permissions():
    os.system(variables.bash_commands["SetPermissions"])
