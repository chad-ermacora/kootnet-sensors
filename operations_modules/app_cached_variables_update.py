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
import sqlite3
from datetime import datetime, timedelta
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, get_file_content, \
    get_list_of_filenames_in_dir as get_names_list_from_dir, write_file_to_disk, zip_files, get_md5_hash_of_file, \
    verify_password_to_hash
from operations_modules.http_generic_network import get_http_regular_file, check_http_file_exist
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules.sqlite_database import sql_execute_get_data, create_table_and_datetime, \
    check_sql_table_and_column, get_one_db_entry
from operations_modules import software_version
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications
from http_server.server_http_generic_functions import default_http_flask_user, default_http_flask_password

db_v = app_cached_variables.database_variables
first_run = True


def update_cached_variables():
    """ Updates app_cached_variables.py variables. """
    global first_run
    if first_run:
        first_run = False
        thread_function(_update_ks_info_table_data)
        demo_mode = app_config_access.primary_config.demo_mode
        if not app_cached_variables.running_with_root:
            click_msg = "Without root access, the following functions will be unavailable - "
            click_msg += "HW Sensors, Network Configurations, Upgrade & Power commands"
            icon = "fas fa-exclamation-triangle"
            notification_short_msg = "Warning: Not running with root<br>Click Here for more information"
            atpro_notifications.add_custom_message(notification_short_msg, click_msg=click_msg, icon=icon)
        if demo_mode:
            click_msg = "In Demo mode, there are no login prompts and the following functions will be unavailable - "
            click_msg += "Network Configurations, SSL, Change Login, Upgrade & Power commands"
            notification_short_msg = "Info: Running in Demo mode<br>Click Here for more information"
            atpro_notifications.add_custom_message(notification_short_msg, click_msg=click_msg)
        if default_http_flask_user == app_cached_variables.http_flask_user and not demo_mode:
            if verify_password_to_hash(default_http_flask_password):
                atpro_notifications.manage_default_login_detected()

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
                if app_cached_variables.running_with_root:
                    wifi_config_lines = get_file_content(file_locations.wifi_config_file).split("\n")
                else:
                    wifi_config_lines = ""
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


def _update_ks_info_table_data():
    """ Creates/Updates Kootnet Sensors Main Database Information Table """
    sleep(30)
    logger.primary_logger.debug("Updating Kootnet Sensors Database Information Table")
    try:
        db_connection = sqlite3.connect(file_locations.sensor_database)
        db_cursor = db_connection.cursor()
        create_table_and_datetime(db_v.table_ks_info, db_cursor)

        for column in [db_v.sensor_name, db_v.ip, db_v.kootnet_sensors_version, db_v.ks_info_configuration_backups_md5]:
            check_sql_table_and_column(db_v.table_ks_info, column, db_cursor)
        check_sql_table_and_column(db_v.table_ks_info, db_v.ks_info_logs, db_cursor, column_type="BLOB")
        check_sql_table_and_column(db_v.table_ks_info, db_v.ks_info_configuration_backups, db_cursor, column_type="BLOB")

        sql_query = "INSERT OR IGNORE INTO '" + db_v.table_ks_info + "' (" + \
                    db_v.all_tables_datetime + "," + \
                    db_v.sensor_name + "," + \
                    db_v.ip + "," + \
                    db_v.kootnet_sensors_version + "," + \
                    db_v.ks_info_configuration_backups_md5 + "," + \
                    db_v.ks_info_logs + "," + \
                    db_v.ks_info_configuration_backups + ")" + \
                    " VALUES (?,?,?,?,?,?,?);"

        configs_zipped = _get_zipped_configurations()
        configs_zip_md5 = get_md5_hash_of_file(configs_zipped)
        if _md5_matches_previous_configs_zip_md5(configs_zip_md5):
            log_msg = "Not saving configurations backup to Database - "
            logger.primary_logger.debug(log_msg + "Configurations have not changed since the last backup")
            configs_zipped = None
            configs_zip_md5 = None
        data_entries = [
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"), app_cached_variables.hostname,
            app_cached_variables.ip, software_version.version, configs_zip_md5, _get_zipped_logs(), configs_zipped
        ]
        data_entries = _check_for_changes_in_sensor_info_data(data_entries)
        db_cursor.execute(sql_query, data_entries)
        db_connection.commit()
        db_connection.close()
        logger.primary_logger.debug("Kootnet Sensors Database Information Updated OK")
    except Exception as error:
        logger.primary_logger.error("Kootnet Sensors Database Information Update Failed: " + str(error))


def _check_for_changes_in_sensor_info_data(data_entries):
    try:
        if data_entries[1] == str(get_one_db_entry(db_v.table_ks_info, db_v.sensor_name)):
            data_entries[1] = None
        if data_entries[2] == str(get_one_db_entry(db_v.table_ks_info, db_v.ip)):
            data_entries[2] = None
        if data_entries[3] == str(get_one_db_entry(db_v.table_ks_info, db_v.kootnet_sensors_version)):
            data_entries[3] = None
    except Exception as error:
        logger.primary_logger.error("Checking DB Info entries: " + str(error))
    return data_entries


def _get_zipped_logs():
    utc_now = datetime.utcnow().strftime("%Y-%m-%d_%H:%M_")
    try:
        return_names = [utc_now + os.path.basename(file_locations.primary_log),
                        utc_now + os.path.basename(file_locations.network_log),
                        utc_now + os.path.basename(file_locations.sensors_log)]
        return_files = [logger.get_sensor_log(file_locations.primary_log),
                        logger.get_sensor_log(file_locations.network_log),
                        logger.get_sensor_log(file_locations.sensors_log)]

        blob_data = zip_files(return_names, return_files).read()
        return blob_data
    except Exception as error:
        logger.primary_logger.error("* Unable to Zip Logs: " + str(error))
    return None


def _md5_matches_previous_configs_zip_md5(new_md5):
    try:
        last_md5_of_zip = str(get_one_db_entry(db_v.table_ks_info, db_v.ks_info_configuration_backups_md5))
        if last_md5_of_zip == new_md5:
            return True
    except Exception as error:
        logger.primary_logger.error("* Unable to verify backup configurations MD5: " + str(error))
    return False


def _get_zipped_configurations():
    main_config = app_config_access.primary_config.get_config_as_str()
    installed_sensors = app_config_access.installed_sensors.get_config_as_str()
    display_config = app_config_access.display_config.get_config_as_str()
    checkin_config = app_config_access.checkin_config.get_config_as_str()
    interval_recording_config = app_config_access.interval_recording_config.get_config_as_str()
    trigger_high_low = app_config_access.trigger_high_low.get_config_as_str()
    trigger_variances = app_config_access.trigger_variances.get_config_as_str()
    email_config = remove_line_from_text(app_config_access.email_config.get_config_as_str(), [5, 6])
    mqtt_broker_config = app_config_access.mqtt_broker_config.get_config_as_str()
    mqtt_pub_config = remove_line_from_text(app_config_access.mqtt_publisher_config.get_config_as_str(), [5, 6])
    mqtt_sub_config = remove_line_from_text(app_config_access.mqtt_subscriber_config.get_config_as_str(), [5, 6])
    open_sense_map_config = remove_line_from_text(app_config_access.open_sense_map_config.get_config_as_str(), [2])
    wu_config = remove_line_from_text(app_config_access.weather_underground_config.get_config_as_str(), [4, 5])
    luftdaten_config = app_config_access.luftdaten_config.get_config_as_str()
    sensor_control_config = app_config_access.sensor_control_config.get_config_as_str()

    try:
        return_names = [os.path.basename(file_locations.primary_config),
                        os.path.basename(file_locations.installed_sensors_config),
                        os.path.basename(file_locations.display_config),
                        os.path.basename(file_locations.checkin_configuration),
                        os.path.basename(file_locations.interval_config),
                        os.path.basename(file_locations.trigger_high_low_config),
                        os.path.basename(file_locations.trigger_variances_config),
                        os.path.basename(file_locations.email_config),
                        os.path.basename(file_locations.mqtt_broker_config),
                        os.path.basename(file_locations.mqtt_publisher_config),
                        os.path.basename(file_locations.mqtt_subscriber_config),
                        os.path.basename(file_locations.osm_config),
                        os.path.basename(file_locations.weather_underground_config),
                        os.path.basename(file_locations.luftdaten_config),
                        os.path.basename(file_locations.html_sensor_control_config)]

        return_files = [main_config, installed_sensors, display_config, checkin_config,
                        interval_recording_config, trigger_high_low, trigger_variances,
                        email_config, mqtt_broker_config, mqtt_pub_config, mqtt_sub_config,
                        open_sense_map_config, wu_config, luftdaten_config, sensor_control_config]

        blob_data = zip_files(return_names, return_files, skip_datetime=True).read()
        return blob_data
    except Exception as error:
        logger.primary_logger.error("* Unable to Zip Configurations: " + str(error))
    return None


def start_cached_variables_refresh():
    thread_function(_cached_variables_refresh)
    thread_function(_remove_stale_failed_login_entries)
    thread_function(_remove_stale_http_logins)


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


def _remove_stale_failed_login_entries():
    """
    Removes stale failed http logins from the failed_flask_logins_dic dictionary every 12 hours
    A failed login is considered stale if it has not been active for more than 2 hour
    :return:
    """
    while True:
        try:
            stale_ip_addresses = []
            for ip_address, data_list in app_cached_variables.failed_flask_logins_dic.items():
                if datetime.utcnow() - data_list[0] > timedelta(hours=2):
                    stale_ip_addresses.append(ip_address)
            for stale_ip in stale_ip_addresses:
                del app_cached_variables.failed_flask_logins_dic[stale_ip]
        except Exception as error:
            logger.network_logger.error("Removing Stale Failed HTTP Logins: " + str(error))
        sleep(86400)


def _remove_stale_http_logins():
    """
    Removes stale http logins from the http_flask_login_session_ids dictionary every 30 minutes
    A login is considered stale if it has not been active for more than 12 hours
    :return: Nothing
    """
    while True:
        try:
            stale_http_login_ids = []
            for login_id, login_id_datetime in app_cached_variables.http_flask_login_session_ids.items():
                if datetime.utcnow() - login_id_datetime > timedelta(hours=12):
                    stale_http_login_ids.append(login_id)
            for stale_id in stale_http_login_ids:
                del app_cached_variables.http_flask_login_session_ids[stale_id]
        except Exception as error:
            logger.network_logger.error("Removing Stale HTTP Logins: " + str(error))
        sleep(1800)


def _update_cached_ip():
    ip_address = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip_address = str(sock.getsockname()[0])
    except Exception as error:
        logger.sensors_logger.debug("Error caching IP Address: " + str(error))
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
    standard_url = app_config_access.urls_config.url_update_server + "kootnet_version.txt"
    developmental_url = app_config_access.urls_config.url_update_server + "dev/kootnet_version.txt"

    app_cached_variables.update_server_file_present_md5 = None
    app_cached_variables.update_server_file_present_version = None
    app_cached_variables.update_server_file_present_full_installer = None
    app_cached_variables.update_server_file_present_upgrade_installer = None

    try:
        standard_version_available = _get_cleaned_version(get_http_regular_file(standard_url, timeout=10))
        app_cached_variables.standard_version_available = standard_version_available
        developmental_version_available = _get_cleaned_version(get_http_regular_file(developmental_url, timeout=10))
        app_cached_variables.developmental_version_available = developmental_version_available

        if _check_if_version_newer(app_cached_variables.standard_version_available):
            app_cached_variables.software_update_available = True
        if _check_if_version_newer(app_cached_variables.developmental_version_available):
            app_cached_variables.software_update_dev_available = True
    except Exception as error:
        logger.primary_logger.debug("Available Update Check Failed: " + str(error))
        app_cached_variables.standard_version_available = "Retrieval Failed"
        app_cached_variables.developmental_version_available = "Retrieval Failed"

    try:
        update_server_files = [
            app_config_access.urls_config.url_update_server + "KootnetSensors-deb-MD5.txt",
            app_config_access.urls_config.url_update_server + "kootnet_version.txt",
            app_config_access.urls_config.url_update_server + "KootnetSensors.deb",
            app_config_access.urls_config.url_update_server + "KootnetSensors_online.deb"
        ]
        files_exist_list = []
        for update_file in update_server_files:
            if check_http_file_exist(update_file):
                files_exist_list.append(True)
            else:
                files_exist_list.append(False)
        app_cached_variables.update_server_file_present_md5 = files_exist_list[0]
        app_cached_variables.update_server_file_present_version = files_exist_list[1]
        app_cached_variables.update_server_file_present_full_installer = files_exist_list[2]
        app_cached_variables.update_server_file_present_upgrade_installer = files_exist_list[3]
    except Exception as error:
        logger.primary_logger.debug("Update Server Files Check Failed: " + str(error))
    atpro_notifications.check_updates()


def _get_cleaned_version(version_text):
    if len(version_text) < 13 and len(version_text.split(".")) == 3:
        return version_text
    return "NA"


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


def remove_line_from_text(text_var, line_numbers_list):
    """ Removes specified line from provided configuration text. """

    return_config = ""
    for index, line_content in enumerate(text_var.split("\n")):
        if index not in line_numbers_list:
            return_config += line_content + "\n"
        else:
            setting_description = line_content.split("=")[1]
            return_config += "Removed_for_viewing = " + setting_description + "\n"
    return return_config
