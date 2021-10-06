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
import psutil
import socket
from time import sleep
import requests
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, get_file_content, \
    get_list_of_filenames_in_dir as get_names_list_from_dir, write_file_to_disk
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules.sqlite_database import sql_execute_get_data
from operations_modules import software_version
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications

db_v = app_cached_variables.database_variables


def update_cached_variables():
    """ Updates app_cached_variables.py variables. """
    if app_cached_variables.current_platform == "Linux":
        try:
            os_release_content_lines = get_file_content("/etc/os-release").split("\n")
            os_release_name = ""
            for line in os_release_content_lines:
                name_and_value = line.split("=")
                if name_and_value[0].strip() == "PRETTY_NAME":
                    os_release_name = name_and_value[1].strip()[1:-1]
            app_cached_variables.operating_system_name = str(os_release_name)
        except Exception as error:
            logger.sensors_logger.error("Error caching OS Name: " + str(error))
            app_cached_variables.operating_system_name = "NA"

        if app_cached_variables.operating_system_name[:8] == "Raspbian":
            try:
                wifi_config_lines = get_file_content(file_locations.wifi_config_file).split("\n")
                app_cached_variables.wifi_country_code = network_wifi.get_wifi_country_code(wifi_config_lines)
                app_cached_variables.wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)
                app_cached_variables.wifi_security_type = network_wifi.get_wifi_security_type(wifi_config_lines)
                app_cached_variables.wifi_psk = network_wifi.get_wifi_psk(wifi_config_lines)
            except Exception as error:
                logger.primary_logger.warning("Error checking WiFi configuration: " + str(error))

            try:
                dhcpcd_config_lines = get_file_content(file_locations.dhcpcd_config_file).split("\n")
                if not network_ip.check_for_dhcp(dhcpcd_config_lines):
                    app_cached_variables.ip = network_ip.get_dhcpcd_ip(dhcpcd_config_lines)
                    app_cached_variables.ip_subnet = network_ip.get_subnet(dhcpcd_config_lines)
                    app_cached_variables.gateway = network_ip.get_gateway(dhcpcd_config_lines)
                    app_cached_variables.dns1 = network_ip.get_dns(dhcpcd_config_lines)
                    app_cached_variables.dns2 = network_ip.get_dns(dhcpcd_config_lines, dns_server=1)
            except Exception as error:
                logger.primary_logger.warning("Error checking dhcpcd.conf: " + str(error))

    try:
        app_cached_variables.total_ram_memory = round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 3)
    except Exception as error:
        logger.primary_logger.warning("Error caching total RAM: " + str(error))

    try:
        app_cached_variables.total_disk_space = round(psutil.disk_usage("/").total / 1024 / 1024 / 1024, 2)
    except Exception as error:
        logger.primary_logger.warning("Error caching total Disk Space: " + str(error))

    last_updated = ""
    if not os.path.isfile(file_locations.program_last_updated):
        logger.sensors_logger.debug("Previous version file not found - Creating version file")
        write_file_to_disk(file_locations.program_last_updated, "No Update Detected")
    last_updated_file = get_file_content(file_locations.program_last_updated)
    last_updated_lines = last_updated_file.split("\n")
    for line in last_updated_lines:
        last_updated += str(line)

    app_cached_variables.program_last_updated = last_updated.strip()
    app_cached_variables.zipped_db_backup_list = get_names_list_from_dir(file_locations.database_backup_folder)
    app_cached_variables.uploaded_databases_list = get_names_list_from_dir(file_locations.uploaded_databases_folder)
    _update_cached_sensor_reboot_count()
    _update_cached_note_variables()
    _update_cached_ip()
    _update_cached_hostname()
    check_for_new_version()


def start_cached_variables_refresh():
    thread_function(_cached_variables_refresh)


def _cached_variables_refresh():
    """
    Updates app_cached_variables.py variables that may change while running.
    Gives 30 seconds before updating the variables within to allow network to be up.
    """
    sleep(30)
    while True:
        _update_cached_ip()
        _update_cached_hostname()
        check_for_new_version()
        sleep(3600)


def _update_cached_ip():
    ip_address = "0.0.0.0"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = str(s.getsockname()[0])
        s.close()
    except Exception as error:
        logger.sensors_logger.warning("Error caching IP Address: " + str(error))
    app_cached_variables.ip = ip_address


def _update_cached_hostname():
    hostname = "NA"
    try:
        hostname = str(socket.gethostname())
    except Exception as error:
        logger.sensors_logger.warning("Error caching Host Name: " + str(error))
    app_cached_variables.hostname = hostname


def _update_cached_note_variables():
    try:
        note_count_sql_query = "SELECT count(" + db_v.other_table_column_notes + ") FROM " + db_v.table_other
        app_cached_variables.notes_total_count = sql_execute_get_data(note_count_sql_query)[0][0]

        selected_note_sql_query = "SELECT " + db_v.other_table_column_notes + " FROM " + db_v.table_other
        sql_notes = sql_execute_get_data(selected_note_sql_query)
        app_cached_variables.cached_notes_as_list = []
        for note in sql_notes:
            app_cached_variables.cached_notes_as_list.append(str(note[0]))
    except Exception as error:
        logger.sensors_logger.error("Unable to update cached note variables: " + str(error))


def _update_cached_sensor_reboot_count():
    """
    Returns the number of times the sensor has rebooted as a str.
    Reboot count is calculated by uptime values stored in the Database.
    """
    sql_query = "SELECT " + db_v.sensor_uptime + " FROM " + db_v.table_interval + \
                " WHERE length(" + db_v.sensor_uptime + ") < 2"
    sql_column_data = sql_execute_get_data(sql_query)

    reboot_count = 0
    previous_entry = 0
    bad_entries = 0
    for entry in sql_column_data:
        try:
            entry_int = int(entry[0])
        except Exception as error:
            print("Bad SQL Entry in System Uptime column: " + str(entry) + " : " + str(error))
            bad_entries += 1
            entry_int = previous_entry

        if entry_int < previous_entry:
            reboot_count += 1
        previous_entry = entry_int

    if bad_entries:
        logger.sensors_logger.warning(str(bad_entries) + " bad entries in DB reboot column")
    debug_message = "Linux System - " + str(len(sql_column_data)) + " entries in DB reboot column retrieved"
    logger.sensors_logger.debug(debug_message)
    app_cached_variables.reboot_count = reboot_count


def check_for_new_version():
    logger.primary_logger.debug(" -- Checking for new Kootnet Sensors Versions")
    standard_url = "https://kootenay-networks.com/installers/kootnet_version.txt"
    developmental_url = "https://kootenay-networks.com/installers/dev/kootnet_version.txt"

    try:
        request_data = requests.get(standard_url, allow_redirects=False)
        app_cached_variables.standard_version_available = request_data.content.decode("utf-8").strip()
        request_data = requests.get(developmental_url, allow_redirects=False)
        app_cached_variables.developmental_version_available = request_data.content.decode("utf-8").strip()

        if _check_if_version_newer(app_cached_variables.standard_version_available):
            app_cached_variables.software_update_available = True
        if _check_if_version_newer(app_cached_variables.developmental_version_available):
            app_cached_variables.software_update_dev_available = True
    except Exception as error:
        logger.primary_logger.debug("Available Update Check Failed: " + str(error))
        app_cached_variables.standard_version_available = "Retrieval Failed"
        app_cached_variables.developmental_version_available = "Retrieval Failed"
    atpro_notifications.check_updates()


def _check_if_version_newer(new_version_str):
    current_ver = software_version.CreateRefinedVersion(software_version.version)
    latest_ver = software_version.CreateRefinedVersion(new_version_str)

    if latest_ver.major_version > current_ver.major_version:
        return True
    elif latest_ver.major_version == current_ver.major_version:
        if latest_ver.feature_version > current_ver.feature_version:
            return True
        elif latest_ver.feature_version == current_ver.feature_version:
            if latest_ver.minor_version > current_ver.minor_version:
                return True
    return False
