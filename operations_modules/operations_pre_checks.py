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

import operations_modules.operations_file_locations as file_locations
from operations_modules.operations_config_db import CreateDatabaseVariables
from operations_modules import operations_version
from operations_modules import operations_logger
from operations_modules import operations_upgrades
from operations_modules import operations_variables

create_important_files = [file_locations.last_updated_file_location,
                          file_locations.old_version_file_location]


class CreateRefinedVersion:
    def __init__(self, version):
        try:
            version_split = version.split(".")
            self.major_version = version_split[0]
            self.feature_version = int(version_split[1])
            self.minor_version = int(version_split[2])
        except Exception as error:
            operations_logger.primary_logger.warning("Bad Version - " + str(version))
            operations_logger.primary_logger.debug(str(error))
            self.major_version = 0
            self.feature_version = 0
            self.minor_version = 0

    def get_version_str(self):
        version_str = str(self.major_version) + "." + str(self.feature_version) + "." + str(self.minor_version)
        return version_str


def check_database_structure():
    operations_logger.primary_logger.debug("Running DB Checks")
    database_variables = CreateDatabaseVariables()

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
        operations_logger.primary_logger.error("DB Connection Failed: " + str(error))


def _create_table_and_datetime(table, db_cursor):
    try:
        # Create or update table
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table, nf="DateTime", ft="TEXT"))
        operations_logger.primary_logger.debug("Table '" + table + "' - Created")

    except Exception as error:
        operations_logger.primary_logger.debug(table + " - " + str(error))


def _check_sql_table_and_column(table_name, column_name, db_cursor):
    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn=column_name, ct="TEXT"))
        operations_logger.primary_logger.debug("COLUMN '" + column_name + "' - Created")
    except Exception as error:
        operations_logger.primary_logger.debug("COLUMN '" + column_name + "' - " + str(error))


def run_upgrade_checks():
    operations_logger.primary_logger.debug("Checking required packages")
    old_version = CreateRefinedVersion(operations_version.get_old_version())
    no_changes = True

    if old_version.major_version is False:
        no_changes = False
        operations_logger.primary_logger.info("New Install or broken/missing Old Version File")
        operations_upgrades.reset_installed_sensors()
        operations_upgrades.reset_config()
        operations_logger.primary_logger.debug("Old Version: " + old_version.get_version_str() +
                                               " || New Version: " + operations_version.version)

    if old_version.major_version is "Alpha":
        if old_version.feature_version is 22:
            operations_upgrades.reset_installed_sensors()
            operations_upgrades.reset_config()
            operations_logger.primary_logger.info("Upgraded: " + old_version.get_version_str() +
                                                  " || New: " + operations_version.version)
        elif old_version.feature_version is 23:
            if old_version.minor_version < 24:
                no_changes = False
                operations_upgrades.reset_config()
                operations_logger.primary_logger.info("Upgraded: " + old_version.get_version_str() +
                                                      " || New: " + operations_version.version)

    if no_changes:
        operations_logger.primary_logger.info("Upgrade detected || No configuration changes || Old: " +
                                              old_version.get_version_str() + " New: " + operations_version.version)
    operations_version.write_program_version_to_file()
    restart_services()


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(operations_variables.restart_sensor_services_command)


def check_missing_files():
    for file in create_important_files:
        if os.path.isfile(file):
            pass
        else:
            operations_logger.primary_logger.warning("Added missing file: " + file)
            os.system("touch " + file)

    os.system("bash /opt/kootnet-sensors/scripts/set_permissions.sh")
