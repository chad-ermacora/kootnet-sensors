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
from datetime import datetime
from operations_modules import logger
from operations_modules.app_cached_variables import command_data_separator, database_variables as db_v
from operations_modules import sqlite_database


def get_db_note_dates():
    """ Returns a comma separated string of Note Dates from the SQL Database. """
    sql_query_notes = "SELECT " + db_v.all_tables_datetime + \
                      " FROM " + db_v.table_other
    sql_note_dates = sqlite_database.sql_execute_get_data(sql_query_notes)
    return _create_str_from_list(sql_note_dates)


def get_db_note_user_dates():
    """ Returns a comma separated string of User Note Dates from the SQL Database. """
    sql_query_user_datetime = "SELECT " + db_v.other_table_column_user_date_time + \
                              " FROM " + db_v.table_other
    sql_data_user_datetime = sqlite_database.sql_execute_get_data(sql_query_user_datetime)
    return _create_str_from_list(sql_data_user_datetime)


def _create_str_from_list(sql_data_notes):
    """
    Takes in a list and returns a comma separated string.
    It also converts any commas located in the values to "[replaced_comma]".
    These converted values will later be converted back to regular commas.
    """
    if len(sql_data_notes) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data_notes:
            new_entry = str(entry[0])
            new_entry = new_entry.replace(",", "[replaced_comma]")
            return_data_string += new_entry + ","
            count += 1
        return_data_string = return_data_string[:-1]
    else:
        return_data_string = "No Data"
    return return_data_string


def add_note_to_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then writes it to the SQL Database. """
    user_date_and_note = datetime_note.split(command_data_separator)
    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]

        sql_execute = "INSERT OR IGNORE INTO OtherData (" + \
                      db_v.all_tables_datetime + "," + \
                      db_v.other_table_column_user_date_time + "," + \
                      db_v.other_table_column_notes + ")" + \
                      " VALUES (?,?,?);"

        data_entries = [current_datetime, custom_datetime, note]

        sqlite_database.write_to_sql_database(sql_execute, data_entries)
    else:
        logger.primary_logger.error("Unable to add Note to DB: Bad Note")


def update_note_in_database(datetime_note):
    """ Takes the provided DateTime and Note as a list then updates the note in the SQL Database. """
    try:
        data_list = datetime_note.split(command_data_separator)

        current_datetime = data_list[0]
        custom_datetime = data_list[1]
        note = data_list[2]

        sql_execute = "UPDATE OtherData SET Notes = ?,UserDateTime = ? WHERE DateTime = ?;"
        data_entries = [note, custom_datetime, current_datetime]
        sqlite_database.write_to_sql_database(sql_execute, data_entries)
    except Exception as error:
        logger.primary_logger.error("DB note update error: " + str(error))


def delete_db_note(note_datetime):
    """ Deletes a Note from the SQL Database based on it's DateTime entry. """
    sql_query = "DELETE FROM " + str(db_v.table_other) + \
                " WHERE " + str(db_v.all_tables_datetime) + \
                " = ?;"
    sql_data = [note_datetime]
    sqlite_database.write_to_sql_database(sql_query, sql_data)
