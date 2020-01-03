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
import sqlite3
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules import sqlite_database
from operations_modules import os_cli_commands


def run_program_start_checks():
    logger.primary_logger.info(" -- Starting Programs Checks ...")
    _set_file_permissions()
    if software_version.old_version != software_version.version:
        logger.primary_logger.info(" -- Starting Programs Upgrade Checks ...")
        os.system("systemctl start SensorUpgradeChecks")
        # Sleep before loading anything due to needed updates
        # The update service will automatically restart this app when it's done
        while True:
            time.sleep(30)
    _check_database_structure()
    _check_ssl_files()


def _set_file_permissions():
    """ Re-sets program file permissions. """
    if os.geteuid() == 0:
        os.system(os_cli_commands.bash_commands["SetPermissions"])


def _check_database_structure():
    """ Loads or creates the SQLite Database, verifying all Tables and Columns. """
    logger.primary_logger.debug("Running DB Checks")
    database_variables = sqlite_database.CreateDatabaseVariables()

    columns_created = 0
    columns_already_made = 0

    try:
        db_connection = sqlite3.connect(file_locations.sensor_database)
        db_cursor = db_connection.cursor()

        _create_table_and_datetime(database_variables.table_interval, db_cursor)
        _create_table_and_datetime(database_variables.table_trigger, db_cursor)
        for column_intervals, column_trigger in zip(database_variables.get_sensor_columns_list(),
                                                    database_variables.get_sensor_columns_list()):
            interval_response = _check_sql_table_and_column(database_variables.table_interval, column_intervals,
                                                            db_cursor)
            trigger_response = _check_sql_table_and_column(database_variables.table_trigger, column_trigger, db_cursor)
            if interval_response:
                columns_created += 1
            else:
                columns_already_made += 1
            if trigger_response:
                columns_created += 1
            else:
                columns_already_made += 1

        _create_table_and_datetime(database_variables.table_other, db_cursor)
        for column_other in database_variables.get_other_columns_list():
            other_response = _check_sql_table_and_column(database_variables.table_other, column_other, db_cursor)
            if other_response:
                columns_created += 1
            else:
                columns_already_made += 1

        db_connection.commit()
        db_connection.close()
        debug_log_message = str(columns_already_made) + " Columns found in 3 SQL Tables, " + \
                            str(columns_created) + " Created"
        logger.primary_logger.debug(debug_log_message)
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
        return True
    except Exception as error:
        print(str(error))
        return False


def _check_ssl_files():
    logger.primary_logger.debug("Running SSL Certificate & Key Checks")

    if os.path.isfile(file_locations.http_ssl_key):
        logger.primary_logger.debug("SSL Key Found")
    else:
        logger.primary_logger.info("SSL Key not Found - Generating Key")
        os.system("openssl genrsa -out " + file_locations.http_ssl_key + " 2048")

    if os.path.isfile(file_locations.http_ssl_csr):
        logger.primary_logger.debug("SSL CSR Found")
    else:
        logger.primary_logger.info("SSL CSR not Found - Generating CSR")
        os.system("openssl req -new -key " + file_locations.http_ssl_key + " -out " + file_locations.http_ssl_csr +
                  " -subj '/C=CA/ST=BC/L=Castlegar/O=Kootenay Networks I.T./OU=Kootnet Sensors/CN=kootnet.ca'")

    if os.path.isfile(file_locations.http_ssl_crt):
        logger.primary_logger.debug("SSL Certificate Found")
    else:
        logger.primary_logger.info("SSL Certificate not Found - Generating Certificate")
        os.system("openssl x509 -req -days 3650 -in " + file_locations.http_ssl_csr +
                  " -signkey " + file_locations.http_ssl_key + " -out " + file_locations.http_ssl_crt)
