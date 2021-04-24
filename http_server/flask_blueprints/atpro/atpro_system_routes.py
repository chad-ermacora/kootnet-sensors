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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_cached_variables_update
from operations_modules.app_generic_functions import thread_function, get_file_content, remove_line_from_text, \
    get_list_of_filenames_in_dir, zip_files, write_file_to_disk, get_file_size
from operations_modules.sqlite_database import get_sqlite_tables_in_list, write_to_sql_database, \
    validate_sqlite_database, check_mqtt_subscriber_database_structure, check_main_database_structure, \
    check_checkin_database_structure
from operations_modules import app_validation_checks
from operations_modules import network_ip
from operations_modules import network_wifi
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import atpro_notifications

try:
    from plotly import __version__ as plotly_version
    from numpy import __version__ as numpy_version
    from greenlet import __version__ as greenlet_version
    from gevent import __version__ as gevent_version
    from requests import __version__ as requests_version
    from werkzeug import __version__ as werkzeug_version
    from cryptography import __version__ as cryptography_version
    from flask import __version__ as flask_version
    from operations_modules.software_version import version as kootnet_version
except ImportError as import_error:
    logger.primary_logger.warning("Import Versions Failed: " + str(import_error))
    plotly_version = "Unknown"
    numpy_version = "Unknown"
    greenlet_version = "Unknown"
    gevent_version = "Unknown"
    requests_version = "Unknown"
    werkzeug_version = "Unknown"
    cryptography_version = "Unknown"
    flask_version = "Unknown"
    kootnet_version = "Unknown"
import os
import zipfile
import shutil
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from werkzeug.security import generate_password_hash
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from http_server.server_http_auth import auth, save_http_auth_to_file
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_message_page, \
    get_clean_db_name, get_html_atpro_index
from sensor_modules import sensor_access

html_atpro_system_routes = Blueprint("html_atpro_system_routes", __name__)
uploaded_databases_folder = file_locations.uploaded_databases_folder
sqlite_valid_extensions_list = ["sqlite", "sqlite3", "db", "dbf", "sql"]


@html_atpro_system_routes.route("/atpro/sensor-system")
def html_atpro_sensor_settings_system():
    return render_template("ATPro_admin/page_templates/system.html")


@html_atpro_system_routes.route("/atpro/sensor-logs")
def html_atpro_sensor_logs():
    return render_template("ATPro_admin/page_templates/sensor-logs.html")


@html_atpro_system_routes.route('/atpro/logs/<path:url_path>')
@auth.login_required
def atpro_get_log(url_path):
    if url_path == "log-download-all-zipped":
        zip_name = "Logs_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
        return_zip_file = zip_files(
            ["log_primary.txt", "log_network.txt", "log_sensors.txt"],
            [logger.get_sensor_log(file_locations.primary_log, max_lines=0),
             logger.get_sensor_log(file_locations.network_log, max_lines=0),
             logger.get_sensor_log(file_locations.sensors_log, max_lines=0)]
        )
        if type(return_zip_file) is str:
            return return_zip_file
        else:
            return send_file(return_zip_file, as_attachment=True, attachment_filename=zip_name)
    elif url_path == "log-primary":
        return logger.get_sensor_log(file_locations.primary_log)
    elif url_path == "log-primary-header":
        primary_log_lines = logger.get_number_of_log_entries(file_locations.primary_log)
        return _get_log_view_message("Primary Log", primary_log_lines)
    elif url_path == "log-network":
        return logger.get_sensor_log(file_locations.network_log)
    elif url_path == "log-network-header":
        network_log_lines = logger.get_number_of_log_entries(file_locations.network_log)
        return _get_log_view_message("Network Log", network_log_lines)
    elif url_path == "log-sensors":
        return logger.get_sensor_log(file_locations.sensors_log)
    elif url_path == "log-sensors-header":
        sensors_log_lines = logger.get_number_of_log_entries(file_locations.sensors_log)
        return _get_log_view_message("Sensors Log", sensors_log_lines)


@html_atpro_system_routes.route('/atpro/delete-log/<path:url_path>')
@auth.login_required
def atpro_delete_log(url_path):
    return_message = "Invalid Path"
    if url_path == "primary":
        logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_primary_log()
        return_message = "Primary Log Deleted"
    elif url_path == "network":
        logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_network_log()
        return_message = "Network Log Deleted"
    elif url_path == "sensors":
        logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
        logger.clear_sensor_log()
        return_message = "Sensors Log Deleted"
    return return_message


def _get_log_view_message(log_name, log_lines_length):
    if log_lines_length:
        if logger.max_log_lines_return > log_lines_length:
            text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
    else:
        text_log_entries_return = "0/0"
    return log_name + " - " + text_log_entries_return


@html_atpro_system_routes.route("/atpro/system-db-local")
def html_atpro_sensor_settings_database_information():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    db_backup_dropdown_selection = ""
    for zip_name in app_cached_variables.zipped_db_backup_list:
        db_backup_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", zip_name) + "\n"
    return render_template(
        "ATPro_admin/page_templates/system/system-db-local.html",
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=get_file_size(file_locations.sensor_database),
        NumberNotes=sensor_access.get_db_notes_count(),
        SQLMQTTDatabaseLocation=file_locations.mqtt_subscriber_database,
        SQLMQTTDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=file_locations.sensor_checkin_database,
        SQLCheckinDatabaseSize=get_file_size(file_locations.sensor_checkin_database),
        SQLCheckinSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        BackupDBOptionNames=db_backup_dropdown_selection
    )


@html_atpro_system_routes.route("/atpro/system-db-management", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_database_management():
    if request.method == "POST":
        upload_db_folder = uploaded_databases_folder + "/"
        try:
            db_full_path = upload_db_folder + str(request.form.get("db_selected"))
            if str(request.form.get("db_backups")) == "download_backup_db":
                backup_db_folder = file_locations.database_backup_folder + "/"
                db_selected_name = str(request.form.get("DatabaseBackupSelection"))
                db_full_path = backup_db_folder + db_selected_name
                return send_file(db_full_path, as_attachment=True, attachment_filename=db_selected_name)
            elif str(request.form.get("db_management")) == "rename_db":
                old_name = db_full_path.split("/")[-1]
                new_name = get_clean_db_name(str(request.form.get("rename_db")))
                new_db_full_path = upload_db_folder + new_name
                os.rename(db_full_path, new_db_full_path)
                uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
                app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                msg = "Database renamed from " + old_name + " to " + new_name
                return get_message_page("Database Renamed", msg, page_url="sensor-system", skip_menu_select=True)
            elif str(request.form.get("db_management")) == "shrink_db":
                selected_database = str(request.form.get("SQLDatabaseSelection"))
                return _vacuum_database(selected_database)
            elif str(request.form.get("db_management")) == "delete_db":
                os.remove(db_full_path)
                uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
                app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                msg = str(request.form.get("db_selected")) + " Database has been deleted"
                return get_message_page("Database Deleted", msg, page_url="sensor-system", skip_menu_select=True)
            elif str(request.form.get("db_management")) == "delete_backup_db":
                db_full_path = file_locations.database_backup_folder + "/" + str(request.form.get("db_selected"))
                os.remove(db_full_path)
                backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.database_backup_folder)
                app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
                msg = str(request.form.get("db_selected")) + " Database backup has been deleted"
                return get_message_page("Database Backup Deleted", msg, page_url="sensor-system", skip_menu_select=True)
            return get_html_atpro_index(run_script="SelectNav('sensor-system');")
        except Exception as error:
            return_text2 = "HTML Database Management Error: " + str(error)
            logger.network_logger.error(return_text2)
            return get_message_page("Database Management Error", str(error), page_url="sensor-system", skip_menu_select=True)

    return render_template(
        "ATPro_admin/page_templates/system/system-db-management.html",
        HostName=app_cached_variables.hostname,
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=get_file_size(file_locations.sensor_database),
        NumberNotes=sensor_access.get_db_notes_count(),
        SQLMQTTDatabaseLocation=file_locations.mqtt_subscriber_database,
        SQLMQTTDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=file_locations.sensor_checkin_database,
        SQLCheckinDatabaseSize=get_file_size(file_locations.sensor_checkin_database),
        SQLCheckinSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        UploadedDBOptionNames=_get_drop_down_items(app_cached_variables.uploaded_databases_list),
        BackupDBOptionNames=_get_drop_down_items(app_cached_variables.zipped_db_backup_list)
    )


@html_atpro_system_routes.route("/atpro/system-db-uploads", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_database_uploads():
    if request.method == "POST":
        button_pressed = str(request.form.get("db_upload_button"))
        if button_pressed == "upload":
            return_msg = "Database(s) Uploaded"
            db_check_msg = "Database(s) Uploaded, Saved and Checked Okay"

            new_db_name = get_clean_db_name(str(request.form.get("UploadDatabaseName")).strip())
            zip_location = uploaded_databases_folder + "/temp_zip.zip"
            save_sqlite_to_file = uploaded_databases_folder + "/" + new_db_name

            uploaded_file = request.files["command_data"]

            upload_file_name = uploaded_file.filename
            if uploaded_file is not None:
                try:
                    if upload_file_name.split(".")[-1] == "zip":
                        if os.path.isfile(zip_location):
                            os.remove(zip_location)
                        uploaded_file.save(zip_location)
                        database_locations_list = _unzip_databases(zip_location, new_db_name)
                        if len(database_locations_list) == 0:
                            return_msg = "Database Upload Error"
                            db_check_msg = "No Valid Database Found in Zip"
                    else:
                        uploaded_file.save(save_sqlite_to_file)
                        if validate_sqlite_database(save_sqlite_to_file):
                            uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
                            app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                        else:
                            os.remove(save_sqlite_to_file)
                            return_msg = "Database Upload Error"
                            db_check_msg = "Invalid SQLite3 Database File"
                except Exception as error:
                    return_msg = "Database Upload Failed"
                    db_check_msg = str(error)
            logger.network_logger.info("Database Custom Upload: " + db_check_msg)
            return get_message_page(return_msg, db_check_msg, page_url="sensor-system", skip_menu_select=True)
        elif button_pressed == "replace":
            selected_database = str(request.form.get("DatabaseReplacementSelection"))

            return_msg = "Database Replaced"
            return_text2 = selected_database + " replaced Okay. The previous database was archived."

            zip_location = file_locations.uploaded_databases_folder + "/temp_zip.zip"
            temp_db_location = file_locations.sensor_data_dir + "/upload_test.sqlite"

            save_db_to = temp_db_location + ".invalid"
            backup_file_name = "_Invalid"
            database_structure_check = check_main_database_structure
            table_check = None
            if selected_database == "MainDatabase":
                backup_file_name = "_Main_Database"
                save_db_to = file_locations.sensor_database
                table_check = app_cached_variables.database_variables.table_interval
            elif selected_database == "MQTTSubscriberDatabase":
                backup_file_name = "_MQTT_Database"
                save_db_to = file_locations.mqtt_subscriber_database
                database_structure_check = check_mqtt_subscriber_database_structure
            elif selected_database == "CheckinDatabase":
                backup_file_name = "_SensorsCheckin_Database"
                save_db_to = file_locations.sensor_checkin_database
                database_structure_check = check_checkin_database_structure

            uploaded_file = request.files["command_data"]
            if uploaded_file is not None:
                if uploaded_file.filename.split(".")[-1] == "zip":
                    if os.path.isfile(zip_location):
                        os.remove(zip_location)
                    uploaded_file.save(zip_location)
                    s_db_name = save_db_to.split("/")[-1]
                    sensor_data_dir = file_locations.sensor_data_dir
                    database_locations_list = _unzip_databases(zip_location, s_db_name,
                                                               overwrite=True,
                                                               extract_folder=sensor_data_dir,
                                                               backup_file_name=backup_file_name)
                    if len(database_locations_list) == 0:
                        return_msg = "Database Error"
                        return_text2 = "No Valid SQLite3 Database Found in Zip"
                    else:
                        database_structure_check()
                else:
                    uploaded_filename_extension = uploaded_file.filename.split(".")[-1]
                    for sql_valid_extension in sqlite_valid_extensions_list:
                        if uploaded_filename_extension == sql_valid_extension:
                            uploaded_file.save(temp_db_location)
                            if validate_sqlite_database(temp_db_location, check_for_table=table_check):
                                if _zip_and_delete_database(save_db_to, backup_file_name):
                                    os.rename(temp_db_location, save_db_to)
                                    database_structure_check()
                                else:
                                    return_msg = "Database Backup Failed"
                                    return_text2 = "Database Replacement Cancelled"
                            else:
                                return_msg = "Database Error"
                                return_text2 = "Invalid SQLite3 Database"
            else:
                return_msg = "Database Error"
                return_text2 = "No File Uploaded"
            logger.network_logger.info("Database Upload: " + return_msg + " - " + return_text2)
            return get_message_page(return_msg, return_text2, page_url="sensor-system", skip_menu_select=True)

    return render_template("ATPro_admin/page_templates/system/system-db-uploads.html")


def _get_drop_down_items(file_list):
    custom_drop_downs_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    dropdown_selection = ""
    for file_name in file_list:
        dropdown_selection += custom_drop_downs_html_text.replace("{{ DBNameChangeMe }}", file_name) + "\n"
    return dropdown_selection


def _vacuum_database(selected_database):
    if selected_database == "MainDatabase":
        db_location = file_locations.sensor_database
    elif selected_database == "MQTTSubscriberDatabase":
        db_location = file_locations.mqtt_subscriber_database
    elif selected_database == "CheckinDatabase":
        db_location = file_locations.sensor_checkin_database
    else:
        db_location = file_locations.uploaded_databases_folder + "/" + selected_database
    if os.path.isfile(db_location):
        write_to_sql_database("VACUUM;", None, sql_database_location=db_location)
        msg = selected_database + " Database has been Shrunk"
        return get_message_page("Database Vacuum Successful", msg, page_url="sensor-system", skip_menu_select=True)
    msg = selected_database + " Database not found"
    return get_message_page("Database Vacuum Failed", msg, page_url="sensor-system", skip_menu_select=True)


def _unzip_databases(zip_location, new_db_name, overwrite=False, backup_file_name="_Main_Database",
                     extract_folder=uploaded_databases_folder):
    """
    Takes zip location and new database name as args
    Optional: overwrite set True will overwrite the provided database name: Default = False
    Optional: extract_folder is where the database will be extracted to: Default = uploaded_databases_folder
    Extracts all SQLite3 databases and returns their locations as a list
    Deletes zip file after completion
    """
    save_sqlite_to_file = extract_folder + "/" + new_db_name

    return_database_locations_list = []
    with zipfile.ZipFile(zip_location, "r") as temp_zip:
        zip_file_infos = temp_zip.infolist()
        for zip_info in zip_file_infos:
            for sql_valid_extension in sqlite_valid_extensions_list:
                if zip_info.filename.split(".")[-1] == sql_valid_extension:
                    db_name_in_zip = zip_info.filename
                    if overwrite and os.path.isfile(save_sqlite_to_file):
                        zip_info.filename = "upload_test.sqlite"
                        tmp_database_full_path = extract_folder + "/" + zip_info.filename
                        if os.path.isfile(tmp_database_full_path):
                            os.remove(tmp_database_full_path)
                        temp_zip.extract(zip_info, path=extract_folder)
                        if validate_sqlite_database(tmp_database_full_path):
                            _zip_and_delete_database(save_sqlite_to_file, backup_file_name)
                            os.rename(tmp_database_full_path, save_sqlite_to_file)
                        else:
                            return []
                    else:
                        zip_info.filename = new_db_name
                        temp_zip.extract(zip_info, path=extract_folder)

                    if validate_sqlite_database(save_sqlite_to_file):
                        return_database_locations_list.append(zip_info.filename)
                    else:
                        os.remove(save_sqlite_to_file)
                        log_msg = "Upload Database - Invalid Database found in Zip: "
                        logger.network_logger.warning(log_msg + db_name_in_zip)
                    new_db_name = get_clean_db_name(new_db_name)
    if os.path.isfile(zip_location):
        os.remove(zip_location)
    backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.uploaded_databases_folder)
    app_cached_variables.uploaded_databases_list = backup_db_zip_filenames
    return return_database_locations_list


def _zip_and_delete_database(database_location, db_save_name):
    """ Creates a zip of linked database in the database backup folder then deletes the original database. """
    filename_start = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + "_"
    sql_filename = filename_start + db_save_name + ".sqlite"
    zip_filename = filename_start + str(datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")) + db_save_name + ".zip"
    zip_full_path = file_locations.database_backup_folder + "/" + zip_filename
    try:
        zip_content = get_file_content(database_location, open_type="rb")
        zip_files([sql_filename], [zip_content], save_type="save_to_disk", file_location=zip_full_path)
        os.remove(database_location)
        backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.database_backup_folder)
        app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
        return True
    except Exception as error:
        print(str(error))
    backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.database_backup_folder)
    app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
    return False


@html_atpro_system_routes.route("/atpro/system/raw-configurations")
@auth.login_required
def atpro_raw_configurations_view():
    logger.network_logger.debug("** HTML Raw Configurations viewed by " + str(request.remote_addr))
    return render_template("ATPro_admin/page_templates/system/system-raw-configurations.html")


def _config_to_html_view(config_name, config_location, config_text_file, split_by_line=True):
    if split_by_line:
        config_lines = config_text_file.strip().split("\n")[1:]
        return_html = ""
        for text_line in config_lines:
            try:
                config_parts = text_line.split("=")
                return_html += "<span class='setting-title'>" + config_parts[-1].strip() + "</span>: " + \
                               "<span class='setting-value'>" + config_parts[0].strip() + "</span><br>"
            except Exception as error:
                log_msg = "HTML Raw Configurations creation error in " + config_location + ": "
                logger.network_logger.warning(log_msg + str(error))
    else:
        return_html = config_text_file.replace("\n", "<br>")
    return render_template("ATPro_admin/page_templates/system/system-raw-configurations-template.html",
                           ConfigName=config_name,
                           ConfigLocation=config_location,
                           Config=return_html)


@html_atpro_system_routes.route('/atpro/system/raw_config/<path:url_path>')
@auth.login_required
def atpro_raw_config_urls(url_path):
    if url_path == "config-software-ver":
        config_name = "Software Versions"
        module_version_text = "This will be removed\n" + \
                              kootnet_version + "=Kootnet Sensors\n" + \
                              str(flask_version) + "=Flask\n" + \
                              str(gevent_version) + "=Gevent\n" + \
                              str(greenlet_version) + "=Greenlet\n" + \
                              str(cryptography_version) + "=Cryptography\n" + \
                              str(werkzeug_version) + "=Werkzeug\n" + \
                              str(requests_version) + "=Requests\n" + \
                              str(plotly_version) + "=Plotly Graphing\n" + \
                              str(numpy_version) + "=Numpy\n"
        return _config_to_html_view(config_name, "NA", module_version_text)
    elif url_path == "config-main":
        config_name = "Main Configuration"
        config_content = get_file_content(file_locations.primary_config)
        return _config_to_html_view(config_name, file_locations.primary_config, config_content)
    elif url_path == "config-is":
        config_name = "Installed Sensors"
        config_content = get_file_content(file_locations.installed_sensors_config)
        return _config_to_html_view(config_name, file_locations.installed_sensors_config, config_content)
    elif url_path == "config-cs":
        config_name = "Checkin Server"
        config_content = get_file_content(file_locations.checkin_configuration)
        return _config_to_html_view(config_name, file_locations.checkin_configuration, config_content)
    elif url_path == "config-display":
        config_name = "Display"
        config_content = get_file_content(file_locations.display_config)
        return _config_to_html_view(config_name, file_locations.display_config, config_content)
    elif url_path == "config-sc":
        config_name = "Remote Management Configuration"
        config_content = get_file_content(file_locations.html_sensor_control_config)
        return _config_to_html_view(config_name, file_locations.html_sensor_control_config, config_content)
    elif url_path == "config-ir":
        config_name = "Interval Recording"
        config_content = get_file_content(file_locations.interval_config)
        return _config_to_html_view(config_name, file_locations.interval_config, config_content)
    elif url_path == "config-high-low":
        config_name = "High/Low Trigger Recording"
        config_content = get_file_content(file_locations.trigger_high_low_config)
        return _config_to_html_view(config_name, file_locations.trigger_high_low_config, config_content)
    elif url_path == "config-variance":
        config_name = "Variance Trigger Recording"
        config_content = get_file_content(file_locations.trigger_variances_config)
        return _config_to_html_view(config_name, file_locations.trigger_variances_config, config_content)
    elif url_path == "config-mqtt-b":
        config_name = "MQTT Broker"
        config_content = get_file_content(file_locations.mqtt_broker_config)
        return _config_to_html_view(config_name, file_locations.mqtt_broker_config, config_content)
    elif url_path == "config-mqtt-p":
        config_name = "MQTT Publisher"
        config_content = remove_line_from_text(get_file_content(file_locations.mqtt_publisher_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.mqtt_publisher_config, config_content)
    elif url_path == "config-mqtt-s":
        config_name = "MQTT Subscriber"
        config_content = remove_line_from_text(get_file_content(file_locations.mqtt_subscriber_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.mqtt_subscriber_config, config_content)
    elif url_path == "config-wu":
        config_name = "Weather Underground"
        config_content = remove_line_from_text(get_file_content(file_locations.weather_underground_config), [4, 5])
        return _config_to_html_view(config_name, file_locations.weather_underground_config, config_content)
    elif url_path == "config-luftdaten":
        config_name = "Luftdaten"
        config_content = get_file_content(file_locations.luftdaten_config)
        return _config_to_html_view(config_name, file_locations.luftdaten_config, config_content)
    elif url_path == "config-osm":
        config_name = "Open Sense Map"
        config_content = remove_line_from_text(get_file_content(file_locations.osm_config), [2])
        return _config_to_html_view(config_name, file_locations.osm_config, config_content)
    elif url_path == "config-email":
        config_name = "Email"
        config_content = remove_line_from_text(get_file_content(file_locations.email_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.email_config, config_content)
    elif url_path == "config-networking":
        config_name = "Networking (dhcpcd.conf)"
        config_content = get_file_content(file_locations.dhcpcd_config_file)
        return _config_to_html_view(config_name, file_locations.dhcpcd_config_file, config_content, split_by_line=False)
    elif url_path == "config-wifi":
        config_name = "WiFi"
        config_content = get_file_content(file_locations.wifi_config_file)
        return _config_to_html_view(config_name, file_locations.wifi_config_file, config_content, split_by_line=False)


@html_atpro_system_routes.route('/atpro/system/<path:url_path>')
@auth.login_required
def atpro_upgrade_urls(url_path):
    title = "Error!"
    message = "An Error occurred"
    system_command = "exit"
    if str(url_path) == "system-restart-program":
        logger.network_logger.info("** Program Restart Initiated by " + str(request.remote_addr))
        title = "Restarting Program"
        message = "The web interface may be temporarily unavailable"
        system_command = app_cached_variables.bash_commands["RestartService"]
    elif str(url_path) == "system-restart":
        logger.network_logger.info("** System Restart Initiated by " + str(request.remote_addr))
        title = "Restarting System"
        message = "The web interface may be temporarily unavailable"
        system_command = app_cached_variables.bash_commands["RebootSystem"]
    elif str(url_path) == "system-shutdown":
        logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
        title = "Shutting Down"
        message = "You will be unable to access the web interface until some one turns the sensor back on"
        system_command = app_cached_variables.bash_commands["ShutdownSystem"]
    elif str(url_path) == "upgrade-http-std":
        logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Standard Upgrade by HTTP Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeOnline"]
    elif str(url_path) == "upgrade-http-dev":
        logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Development Upgrade by HTTP Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeOnlineDEV"]
    elif str(url_path) == "upgrade-http-std-clean":
        logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Clean Standard Upgrade by HTTP Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeOnlineClean"]
    elif str(url_path) == "upgrade-http-dev-clean":
        logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Clean Development Upgrade by HTTP Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeOnlineCleanDEV"]
    elif str(url_path) == "upgrade-smb-std":
        logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Standard Upgrade by SMB Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeSMB"]
    elif str(url_path) == "upgrade-smb-dev":
        logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Development Upgrade by SMB Started. This may take awhile ..."
        system_command = app_cached_variables.bash_commands["UpgradeSMBDEV"]
    elif str(url_path) == "upgrade-os":
        logger.network_logger.info("** System OS Upgrade - SMB Initiated by " + str(request.remote_addr))
        title = "Upgrade Started"
        message = "Sensor's operating system upgrade started. This may take awhile ..."
        thread_function(_upgrade_linux_os)
    elif str(url_path) == "upgrade-py3-modules":
        logger.network_logger.info("** Python3 Module Upgrades Initiated by " + str(request.remote_addr))
        title = "Upgrades Started"
        message = "Python3 Module Upgrades Started. This may take awhile ..."
        thread_function(_upgrade_py3_modules)

    msg_page = get_message_page(title, message, full_reload=False)
    thread_function(os.system, args=system_command)
    return msg_page


def _upgrade_linux_os():
    """ Runs a bash command to upgrade the Linux System with apt-get. """
    try:
        os.system(app_cached_variables.bash_commands["UpgradeSystemOS"])
        logger.primary_logger.warning("Linux OS Upgrade Done")
        logger.primary_logger.info("Rebooting System")
        os.system(app_cached_variables.bash_commands["RebootSystem"])
    except Exception as error:
        logger.primary_logger.error("Linux OS Upgrade Error: " + str(error))


def _upgrade_py3_modules():
    if app_cached_variables.sensor_ready_for_upgrade:
        app_cached_variables.sensor_ready_for_upgrade = False
        with open(file_locations.program_root_dir + "/requirements.txt") as file:
            requirements_text = file.readlines()
            for line in requirements_text:
                if line[0] != "#":
                    command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + line.strip()
                    os.system(command)
            logger.primary_logger.info("Python3 Module Upgrades Complete")
            os.system(app_cached_variables.bash_commands["RestartService"])
    else:
        logger.network_logger.warning("* Upgrades Already Running")


@html_atpro_system_routes.route("/atpro/update-login", methods=["POST"])
@auth.login_required
def html_atpro_set_login_credentials():
    logger.primary_logger.warning("*** Login Credentials Changed - Source " + str(request.remote_addr))
    temp_username = str(request.form.get("login_username"))
    temp_password = str(request.form.get("login_password"))
    if len(temp_username) > 3 and len(temp_password) > 3:
        app_cached_variables.http_flask_user = temp_username
        app_cached_variables.http_flask_password = generate_password_hash(temp_password)
        save_http_auth_to_file(temp_username, temp_password)
        msg1 = "Username and Password Updated"
        msg2 = "The Username and Password has been updated"
    else:
        msg1 = "Invalid Username or Password"
        msg2 = "Username and Password must be 4 to 62 characters long and cannot be blank"
    return get_message_page(msg1, msg2)


@html_atpro_system_routes.route("/atpro/system-networking")
@auth.login_required
def html_atpro_system_networking():
    dhcp_checkbox = ""
    wifi_security_type_none1 = ""
    wifi_security_type_wpa1 = ""
    if app_config_access.installed_sensors.raspberry_pi:
        dhcpcd_lines = get_file_content(file_locations.dhcpcd_config_file).split("\n")
        if network_ip.check_for_dhcp(dhcpcd_lines):
            dhcp_checkbox = "checked"
    if app_cached_variables.wifi_security_type == "" or app_cached_variables.wifi_security_type == "WPA-PSK":
        wifi_security_type_wpa1 = "checked"
    else:
        wifi_security_type_none1 = "checked"
    return render_template("ATPro_admin/page_templates/system/system-networking-ip.html",
                           CheckedDHCP=dhcp_checkbox,
                           IPHostname=app_cached_variables.hostname,
                           IPv4Address=app_cached_variables.ip,
                           IPv4Subnet=app_cached_variables.ip_subnet,
                           IPGateway=app_cached_variables.gateway,
                           IPDNS1=app_cached_variables.dns1,
                           IPDNS2=app_cached_variables.dns2,
                           WirelessCountryCode=app_cached_variables.wifi_country_code,
                           SSID1=app_cached_variables.wifi_ssid,
                           CheckedWiFiSecurityWPA1=wifi_security_type_wpa1,
                           CheckedWiFiSecurityNone1=wifi_security_type_none1)


@html_atpro_system_routes.route("/atpro/system-ssl")
@auth.login_required
def html_atpro_system_ssl():
    return render_template("ATPro_admin/page_templates/system/system-networking-ssl.html",
                           SSLFileLocation=file_locations.http_ssl_folder)


@html_atpro_system_routes.route("/atpro/system-ssl-new-self-sign")
@auth.login_required
def html_atpro_create_new_self_signed_ssl():
    message2 = "Once complete, the sensor programs will be restarted. This may take a few minutes ..."
    os.system("rm -f -r " + file_locations.http_ssl_folder)
    thread_function(sensor_access.restart_services)
    return get_message_page("Creating new Self-Signed SSL", message2, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_routes.route("/atpro/system-ssl-custom", methods=["POST"])
@auth.login_required
def html_atpro_set_custom_ssl():
    logger.network_logger.info("* Sensor's Web SSL Replacement accessed by " + str(request.remote_addr))
    return_message_ok = "SSL Certificate and Key files replaced.  Please reboot sensor for changes to take effect."
    return_message_fail = "Failed to set SSL Certificate and Key files.  Invalid Files?"

    try:
        temp_ssl_crt_location = file_locations.http_ssl_folder + "/custom_upload_certificate.crt"
        temp_ssl_key_location = file_locations.http_ssl_folder + "/custom_upload_key.key"
        new_ssl_certificate = request.files["custom_crt"]
        new_ssl_key = request.files["custom_key"]
        new_ssl_certificate.save(temp_ssl_crt_location)
        new_ssl_key.save(temp_ssl_key_location)
        if _is_valid_ssl_certificate(get_file_content(temp_ssl_crt_location)):
            os.system("mv -f " + file_locations.http_ssl_crt + " " + file_locations.http_ssl_folder + "/old_cert.crt")
            os.system("mv -f " + file_locations.http_ssl_key + " " + file_locations.http_ssl_folder + "/old_key.key")
            os.system("mv -f " + temp_ssl_crt_location + " " + file_locations.http_ssl_crt)
            os.system("mv -f " + temp_ssl_key_location + " " + file_locations.http_ssl_key)
            logger.primary_logger.info("Web Portal SSL Certificate and Key replaced successfully")
            app_cached_variables.html_service_restart = 1
            return get_message_page("Sensor SSL Certificate OK", return_message_ok,
                                    page_url="sensor-system", skip_menu_select=True)
        logger.network_logger.error("Invalid Uploaded SSL Certificate")
        return get_message_page("Sensor SSL Certificate Failed", return_message_fail,
                                page_url="sensor-system", skip_menu_select=True)
    except Exception as error:
        logger.network_logger.error("Failed to set Web Portal SSL Certificate and Key - " + str(error))
    return get_message_page("Sensor SSL Certificate Failed", return_message_fail,
                            page_url="sensor-system", skip_menu_select=True)


def _is_valid_ssl_certificate(cert):
    try:
        x509.load_pem_x509_certificate(str.encode(cert), default_backend())
        return True
    except Exception as error:
        logger.network_logger.debug("Invalid SSL Certificate - " + str(error))
    return False


# TODO: move checks to _set function below. Return check and message for html return
@html_atpro_system_routes.route("/atpro/system-ip", methods=["POST"])
@auth.login_required
def html_atpro_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
        hostname = request.form.get("ip_hostname")
        app_cached_variables.hostname = hostname
        os.system("hostnamectl set-hostname " + hostname)

        ip_address = request.form.get("ip_address")
        ip_subnet = request.form.get("ip_subnet")
        ip_gateway = request.form.get("ip_gateway")
        ip_dns1 = request.form.get("ip_dns1")
        ip_dns2 = request.form.get("ip_dns2")

        dhcpcd_template = str(get_file_content(file_locations.dhcpcd_config_file_template))
        if request.form.get("ip_dhcp") is not None:
            dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", "")
            write_file_to_disk(file_locations.dhcpcd_config_file, dhcpcd_template)
            app_cached_variables.ip = ""
            app_cached_variables.ip_subnet = ""
            app_cached_variables.gateway = ""
            app_cached_variables.dns1 = ""
            app_cached_variables.dns2 = ""
        else:
            title_message = ""
            if not app_validation_checks.ip_address_is_valid(ip_address):
                title_message += "Invalid IP Address "
            if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
                title_message += "Invalid IP Subnet Mask "
            if not app_validation_checks.ip_address_is_valid(ip_gateway) and ip_gateway != "":
                title_message += "Invalid Gateway IP Address "
            if not app_validation_checks.ip_address_is_valid(ip_dns1) and ip_dns1 != "":
                title_message += "Invalid DNS Address "
            if not app_validation_checks.ip_address_is_valid(ip_dns2) and ip_dns2 != "":
                title_message += "Invalid DNS Address "
            if title_message != "":
                title_message = "Invalid IP Settings"
                return get_message_page(title_message, page_url="sensor-system", skip_menu_select=True)

            ip_network_text = "# Custom Static IP set by Kootnet Sensors" + \
                              "\ninterface wlan0" + \
                              "\nstatic ip_address=" + ip_address + ip_subnet + \
                              "\nstatic routers=" + ip_gateway + \
                              "\nstatic domain_name_servers=" + ip_dns1 + " " + ip_dns2

            new_dhcpcd_config = dhcpcd_template.replace("{{ StaticIPSettings }}", ip_network_text)
            write_file_to_disk(file_locations.dhcpcd_config_file, new_dhcpcd_config)
            shutil.chown(file_locations.dhcpcd_config_file, "root", "netdev")
            os.chmod(file_locations.dhcpcd_config_file, 0o664)

        title_message = "IPv4 Configuration Updated"
        message = "You must reboot for all settings to take effect."
        app_cached_variables_update.update_cached_variables()
        atpro_notifications.reboot_system_enabled = 1
        return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
    else:
        title_message = "Unable to Process IPv4 Configuration"
        message = "Invalid or Missing Hostname.\n\nOnly Alphanumeric Characters, Dashes and Underscores may be used."
        return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_routes.route("/atpro/system-wifi", methods=["POST"])
@auth.login_required
def html_atpro_set_wifi_config():
    logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
    if request.method == "POST" and "ssid1" in request.form:
        if app_validation_checks.text_has_no_double_quotes(request.form.get("wifi_key1")):
            pass
        else:
            message = "Do not use double quotes in the Wireless Key Sections."
            return get_message_page("Invalid Wireless Key", message, page_url="sensor-system", skip_menu_select=True)
        if app_validation_checks.wireless_ssid_is_valid(request.form.get("ssid1")):
            new_wireless_config = network_wifi.html_request_to_config_wifi(request)
            if new_wireless_config is not "":
                write_file_to_disk(file_locations.wifi_config_file, new_wireless_config)
                title_message = "WiFi Configuration Updated"
                message = "You must reboot the sensor to take effect."
                app_cached_variables_update.update_cached_variables()
                atpro_notifications.reboot_system_enabled = 1
                return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
        else:
            logger.network_logger.debug("HTML WiFi Configuration Update Failed")
            title_message = "Unable to Process Wireless Configuration"
            message = "Network Names cannot be blank and can only use " + \
                      "Alphanumeric Characters, dashes, underscores and spaces."
            return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
    return get_message_page("Unable to Process WiFi Configuration", page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_routes.route("/atpro/system-change-login")
def html_atpro_system_change_login():
    return render_template("ATPro_admin/page_templates/system/system-change-login.html")


@html_atpro_system_routes.route("/atpro/system-upgrades-power")
def html_atpro_system_upgrades_power():
    return render_template("ATPro_admin/page_templates/system/system-upgrades-power.html")


@html_atpro_system_routes.route("/atpro/system-about")
def html_atpro_system_about():
    return render_template("ATPro_admin/page_templates/system/system-about.html",
                           KootnetVersion=kootnet_version)
