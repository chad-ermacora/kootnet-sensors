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
from shutil import disk_usage
from datetime import datetime

from operations_modules.operations_config import current_config, version, installed_sensors
from operations_modules.operations_variables import restart_sensor_services_command
from operations_modules.operations_file_locations import last_updated_file_location, wifi_config_file
from operations_modules.operations_db import write_to_sql_database, CreateOtherDataEntry
from operations_modules import operations_logger
from operations_modules import operations_sensors

command_data_separator = "[new_data_section]"


def get_sensor_readings():
    """ Returns sensor types and readings for interval and trigger sensors in html table format. """

    return_data = ""
    return_types = ""
    interval_data = operations_sensors.get_interval_sensor_readings()

    str_interval_types = interval_data.sensor_types.split(",")
    str_interval_data = interval_data.sensor_readings.split(",")

    count = 0
    for interval_type in str_interval_types:
        return_types += "<th><span style='background-color: #00ffff;'>" + interval_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + str_interval_data[count] + "</span></th>"
        count = count + 1

    return [return_types, return_data]


def get_system_information():
    """ Returns System Information needed for a Control Center 'System Report'. """
    free_disk = disk_usage("/")[2]

    try:
        str_sensor_data = operations_sensors.get_hostname() + \
                          "," + operations_sensors.get_ip() + \
                          "," + str(operations_sensors.get_system_datetime()) + \
                          "," + str(operations_sensors.get_system_uptime()) + \
                          "," + str(version) + \
                          "," + str(round(float(operations_sensors.get_cpu_temperature()), 2)) + \
                          "," + str(round(free_disk / (2 ** 30), 2)) + \
                          "," + str(operations_sensors.get_db_size()) + \
                          "," + str(get_last_updated())
    except Exception as error:
        operations_logger.network_logger.error("Sensor reading failed - " + str(error))
        str_sensor_data = "Sensor, Data Retrieval, Failed, 0, 0, 0, 0, 0, 0, 0, 0, 0"

    return str_sensor_data


def get_config_information():
    """ Opens configuration file and returns it as a comma separated string. """
    str_installed_sensors = installed_sensors.get_installed_names_str()

    try:
        tmp_str_config = str(current_config.enable_interval_recording) + \
                         "," + str(current_config.enable_trigger_recording) + \
                         "," + str(current_config.sleep_duration_interval) + \
                         "," + str(current_config.enable_custom_temp) + \
                         "," + str(current_config.temperature_offset) + \
                         "," + str(str_installed_sensors)

    except Exception as error:
        operations_logger.network_logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, 0, 0"

    return tmp_str_config


def get_sensor_log(log_file):
    """ Opens provided log file location and returns its content. """
    log_content = open(log_file, "r")
    log = log_content.read()
    log_content.close()
    return log


def get_last_updated():
    """ Returns when the sensor programs were last updated and how. """
    try:
        last_updated_file = open(last_updated_file_location, "r")
        tmp_last_updated = last_updated_file.readlines()
        last_updated_file.close()
        last_updated = str(tmp_last_updated[0]) + str(tmp_last_updated[1])
    except Exception as error:
        operations_logger.network_logger.error("Unable to Load Last Updated File: " + str(error))
        last_updated = "N/A"

    return last_updated


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system(restart_sensor_services_command)


def add_note_to_database(datetime_note):
    sql_data = CreateOtherDataEntry()
    user_date_and_note = datetime_note.split(command_data_separator)

    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-6] + "000"
    if len(user_date_and_note) > 1:
        custom_datetime = user_date_and_note[0]
        note = user_date_and_note[1]
    else:
        custom_datetime = "NA"
        note = user_date_and_note[0]

    sql_data.sensor_types = "DateTime, UserDateTime, Notes"
    sql_data.sensor_readings = "'" + current_datetime + "','" + custom_datetime + "','" + note + "'"

    sql_execute = (sql_data.sql_query_start + sql_data.sensor_types +
                   sql_data.sql_query_values_start + sql_data.sensor_readings +
                   sql_data.sql_query_values_end)

    write_to_sql_database(sql_execute)


def update_note_in_database(datetime_note):
    data_list = datetime_note.split(command_data_separator)

    try:
        current_datetime = "'" + data_list[0] + "'"
        user_datetime = "'" + data_list[1] + "'"
        note = "'" + data_list[2] + "'"

        sql_execute = "UPDATE OtherData SET Notes = " + note + \
                      ",UserDateTime = " + user_datetime + \
                      " WHERE DateTime = " + current_datetime

        write_to_sql_database(sql_execute)
    except Exception as error:
        operations_logger.primary_logger.error("DB note update error: " + str(error))
