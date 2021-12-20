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
import zipfile
from random import randint
from datetime import datetime
from threading import Thread
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules.app_generic_functions import get_list_of_filenames_in_dir, zip_files, get_file_size, \
    adjust_datetime
from operations_modules.app_generic_disk import get_file_content
from operations_modules.sqlite_database import get_sqlite_tables_in_list, write_to_sql_database, \
    get_main_db_first_last_date, universal_database_structure_check
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page, get_clean_db_name, \
    get_html_atpro_index, sanitize_text

html_atpro_system_sql_db_routes = Blueprint("html_atpro_system_sql_db_routes", __name__)
uploaded_databases_folder = file_locations.uploaded_databases_folder
sqlite_valid_extensions_list = ["sqlite", "sqlite3", "db", "dbf", "sql"]


@html_atpro_system_sql_db_routes.route("/atpro/system-db-local")
def html_atpro_settings_db_information():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    db_backup_dropdown_selection = ""
    for zip_name in app_cached_variables.zipped_db_backup_list:
        db_backup_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", zip_name) + "\n"

    run_script = ""
    for check in [app_cached_variables.creating_zip_main_db,
                  app_cached_variables.creating_zip_mqtt_sub_db,
                  app_cached_variables.creating_zip_checkin_db]:
        if check:
            run_script = "CreatingDownload();"
    return render_template(
        "ATPro_admin/page_templates/system/system-db-local.html",
        HourOffset=app_config_access.primary_config.utc0_hour_offset,
        SQLDatabaseLocation=_remove_filename_from_location(file_locations.sensor_database),
        SQLDatabaseName=file_locations.sensor_database.split("/")[-1],
        SQLDatabaseDateRange=get_main_db_first_last_date(app_config_access.primary_config.utc0_hour_offset),
        SQLDatabaseSize=get_file_size(file_locations.sensor_database),
        ZipMainDBCreated=_get_file_creation_date(file_locations.database_zipped),
        ZipMainDBFileSize=get_file_size(file_locations.database_zipped),
        NumberNotes=app_cached_variables.notes_total_count,
        SQLMQTTDatabaseLocation=_remove_filename_from_location(file_locations.mqtt_subscriber_database),
        SQLMQTTDatabaseName=file_locations.mqtt_subscriber_database.split("/")[-1],
        SQLMQTTDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
        ZipMQTTDBCreated=_get_file_creation_date(file_locations.mqtt_database_zipped),
        ZipMQTTDBFileSize=get_file_size(file_locations.mqtt_database_zipped),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=_remove_filename_from_location(file_locations.sensor_checkin_database),
        SQLCheckinDatabaseName=file_locations.sensor_checkin_database.split("/")[-1],
        SQLCheckinDatabaseSize=get_file_size(file_locations.sensor_checkin_database),
        ZipCheckinDBCreated=_get_file_creation_date(file_locations.checkin_database_zipped),
        ZipCheckinDBFileSize=get_file_size(file_locations.checkin_database_zipped),
        SQLCheckinSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        BackupDBOptionNames=db_backup_dropdown_selection,
        RunScript=run_script
    )


def _get_file_creation_date(file_location):
    file_creation_date = "File Not Found"
    if os.path.isfile(file_location):
        utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
        file_creation_date = os.path.getmtime(file_location)
        file_creation_date = datetime.utcfromtimestamp(file_creation_date).strftime("%Y-%m-%d %H:%M:%S")
        file_creation_date = adjust_datetime(file_creation_date, hour_offset=utc0_hour_offset)
    return file_creation_date


def _remove_filename_from_location(file_location):
    location = ""
    for section in file_location.split("/")[:-1]:
        location += section + "/"
    return location


@html_atpro_system_sql_db_routes.route("/atpro/system-db-management", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_database_management():
    if request.method == "POST":
        upload_db_folder = uploaded_databases_folder + "/"
        try:
            db_full_path = upload_db_folder + sanitize_text(request.form.get("db_selected"))
            if sanitize_text(request.form.get("db_backups")) == "download_backup_db":
                backup_db_folder = file_locations.database_backup_folder + "/"
                db_selected_name = sanitize_text(request.form.get("DatabaseBackupSelection"))
                db_full_path = backup_db_folder + db_selected_name
                if db_selected_name in app_cached_variables.zipped_db_backup_list:
                    return send_file(db_full_path, as_attachment=True, attachment_filename=db_selected_name)
            elif sanitize_text(request.form.get("db_management")) == "rename_db":
                old_name = db_full_path.split("/")[-1]
                new_name = get_clean_db_name(str(request.form.get("rename_db")))
                new_db_full_path = upload_db_folder + new_name
                os.rename(db_full_path, new_db_full_path)
                uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
                app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                msg = "Database renamed from " + old_name + " to " + new_name
                return get_message_page("Database Renamed", msg, page_url="sensor-system", skip_menu_select=True)
            elif sanitize_text(request.form.get("db_management")) == "shrink_db":
                selected_database = sanitize_text(request.form.get("SQLDatabaseSelection"))
                return _vacuum_database(selected_database)
            elif sanitize_text(request.form.get("db_management")) == "delete_db":
                os.remove(db_full_path)
                uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
                app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                msg = sanitize_text(request.form.get("db_selected")) + " Database has been deleted"
                return get_message_page("Database Deleted", msg, page_url="sensor-system", skip_menu_select=True)
            elif sanitize_text(request.form.get("db_management")) == "delete_backup_db":
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
            msg_name = "Database Management Error"
            return get_message_page(msg_name, str(error), page_url="sensor-system", skip_menu_select=True)
    return render_template(
        "ATPro_admin/page_templates/system/system-db-management.html",
        UploadedDBOptionNames=_get_drop_down_items(app_cached_variables.uploaded_databases_list),
        BackupDBOptionNames=_get_drop_down_items(app_cached_variables.zipped_db_backup_list)
    )


@html_atpro_system_sql_db_routes.route("/atpro/system-db-uploads", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_database_uploads():
    if request.method == "POST":
        zip_location = uploaded_databases_folder + "/temp_zip" + str(randint(100, 999)) + ".zip"
        if os.path.isfile(zip_location):
            os.remove(zip_location)
        button_pressed = str(request.form.get("db_upload_button"))
        if button_pressed == "upload":
            uploaded_file = request.files["command_data"]

            overwrite = False
            if request.form.get("overwrite_database") is not None:
                overwrite = True

            if uploaded_file is not None:
                upload_file_name = uploaded_file.filename
                if upload_file_name.split(".")[-1] == "zip":
                    uploaded_file.save(zip_location)
                    system_thread = Thread(target=_unzip_to_upload_folder, args=(zip_location, overwrite))
                    system_thread.daemon = True
                    system_thread.start()
                elif upload_file_name.split(".")[-1] in sqlite_valid_extensions_list:
                    original_new_db_name = str(request.form.get("UploadDatabaseName")).strip()
                    if overwrite:
                        new_db_name = get_clean_db_name(original_new_db_name, find_unique_name=False)
                        if os.path.isfile(uploaded_databases_folder + "/" + new_db_name):
                            os.remove(uploaded_databases_folder + "/" + new_db_name)
                    else:
                        new_db_name = get_clean_db_name(original_new_db_name)

                    save_sqlite_to_file = uploaded_databases_folder + "/" + new_db_name
                    uploaded_file.save(save_sqlite_to_file)
                    system_thread = Thread(target=_check_uploaded_db_raw_worker, args=(save_sqlite_to_file,))
                    system_thread.daemon = True
                    system_thread.start()
                else:
                    logger.network_logger.error("Upload Database: Invalid extension on uploaded file")
        elif button_pressed == "replace":
            selected_database = str(request.form.get("DatabaseReplacementSelection"))
            uploaded_file = request.files["command_data"]
            temp_db_location = file_locations.sensor_data_dir + "/upload_test " + str(randint(111, 999)) + ".sqlite"
            save_db_to = temp_db_location + ".invalid"
            backup_file_name = "_Invalid"
            if selected_database == "MainDatabase":
                backup_file_name = "_Main_Database"
                save_db_to = file_locations.sensor_database
            elif selected_database == "MQTTSubscriberDatabase":
                backup_file_name = "_MQTT_Database"
                save_db_to = file_locations.mqtt_subscriber_database
            elif selected_database == "CheckinDatabase":
                backup_file_name = "_SensorsCheckin_Database"
                save_db_to = file_locations.sensor_checkin_database

            if uploaded_file is not None:
                if uploaded_file.filename.split(".")[-1] == "zip":
                    uploaded_file.save(zip_location)
                    system_thread = Thread(target=_unzip_and_replace_database,
                                           args=(zip_location, save_db_to, backup_file_name))
                    system_thread.daemon = True
                    system_thread.start()
                elif uploaded_file.filename.split(".")[-1] in sqlite_valid_extensions_list:
                    uploaded_file.save(temp_db_location)
                    system_thread = Thread(target=_db_replacement_raw_worker,
                                           args=(temp_db_location, save_db_to, backup_file_name))
                    system_thread.daemon = True
                    system_thread.start()
                else:
                    logger.network_logger.error("Upload Database: Invalid extension on uploaded file")
            else:
                logger.network_logger.error("Database Upload: No File Uploaded")
        return_msg = "Database(s) Uploaded"
        db_check_msg = "Database(s) are being processed, check logs for more details"
        return get_message_page(return_msg, db_check_msg, page_url="sensor-system", skip_menu_select=True)
    return render_template("ATPro_admin/page_templates/system/system-db-uploads.html")


def _unzip_to_upload_folder(zip_location, overwrite):
    logger.network_logger.info("Database Upload Processing ...")
    return_database_locations_list = []
    try:
        with zipfile.ZipFile(zip_location, "r") as temp_zip:
            zip_file_infos = temp_zip.infolist()
            for zip_info in zip_file_infos:
                if zip_info.filename.split(".")[-1] in sqlite_valid_extensions_list:
                    db_name_in_zip = zip_info.filename
                    db_path_and_name = uploaded_databases_folder + "/" + db_name_in_zip

                    if os.path.isfile(db_path_and_name):
                        if overwrite:
                            log_msg = "Database " + db_path_and_name + " was overwritten"
                            os.remove(db_path_and_name)
                            temp_zip.extract(zip_info, path=uploaded_databases_folder)
                        else:
                            log_msg = "Database " + db_path_and_name + " already exists, skipping database"
                        logger.network_logger.info(log_msg)
                    else:
                        temp_zip.extract(zip_info, path=uploaded_databases_folder)

                    if universal_database_structure_check(db_path_and_name):
                        return_database_locations_list.append(db_path_and_name)
                    else:
                        os.remove(db_path_and_name)
                        log_msg = "Upload Database - Invalid Database found in Zip: "
                        logger.network_logger.warning(log_msg + db_name_in_zip)
    except Exception as error:
        logger.network_logger.error("Database Upload: " + str(error))
    if os.path.isfile(zip_location):
        os.remove(zip_location)
    app_cached_variables.uploaded_databases_list = get_list_of_filenames_in_dir(uploaded_databases_folder)
    if len(return_database_locations_list):
        for db_location in return_database_locations_list:
            _set_file_permissions(db_location)
            logger.network_logger.info("Database Upload " + db_location + " Okay")
    else:
        logger.network_logger.error("No Databases Uploaded: Invalid Database(s) or Database name(s) already exists")
    logger.network_logger.info("Database Upload Complete")


def _unzip_and_replace_database(zip_location, db_location, backup_file_name):
    return_database_locations_list = []
    logger.network_logger.info("Database Replacement Processing ...")
    expected_database_type = None
    if db_location == file_locations.sensor_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_main
    elif db_location == file_locations.sensor_checkin_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_sensor_checkins
    elif db_location == file_locations.mqtt_subscriber_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_mqtt

    try:
        with zipfile.ZipFile(zip_location, "r") as temp_zip:
            zip_file_infos = temp_zip.infolist()
            zip_info = None
            for tmp_zip_info in zip_file_infos:
                if tmp_zip_info.filename.split(".")[-1] in sqlite_valid_extensions_list:
                    return_database_locations_list.append(db_location)
                    zip_info = tmp_zip_info
            if len(return_database_locations_list) == 1:
                tmp_db_name = "temp_up" + str(randint(1111, 99999)) + ".sqlite"
                tmp_db_full_path_name = uploaded_databases_folder + "/" + tmp_db_name
                if os.path.isfile(tmp_db_full_path_name):
                    os.remove(tmp_db_full_path_name)
                zip_info.filename = tmp_db_name
                temp_zip.extract(zip_info, path=uploaded_databases_folder)
                if universal_database_structure_check(tmp_db_full_path_name, expected_database_type):
                    _zip_and_delete_database(db_location, backup_file_name)
                    zip_info.filename = db_location.split("/")[-1]
                    temp_zip.extract(zip_info, path=file_locations.sensor_data_dir)
                    _set_file_permissions(db_location)
                else:
                    logger.network_logger.error("Database Replacement - Invalid Database in Zip")
                    return_database_locations_list = []
                os.remove(tmp_db_full_path_name)
            else:
                logger.network_logger.error("Database Replacement: Zip must only contain 1 database")
    except Exception as error:
        logger.network_logger.error("Database Replacement: " + str(error))
        return_database_locations_list = []
    if os.path.isfile(zip_location):
        os.remove(zip_location)
    app_cached_variables.uploaded_databases_list = get_list_of_filenames_in_dir(uploaded_databases_folder)
    logger.network_logger.info("Database Replacement Complete")
    return return_database_locations_list


def _check_uploaded_db_raw_worker(sqlite_file_location):
    logger.network_logger.info("Database Upload Processing ...")
    if universal_database_structure_check(sqlite_file_location):
        uploaded_db_filenames = get_list_of_filenames_in_dir(uploaded_databases_folder)
        app_cached_variables.uploaded_databases_list = uploaded_db_filenames
        _set_file_permissions(sqlite_file_location)
        logger.network_logger.info("Database Upload " + sqlite_file_location + " Okay")
    else:
        os.remove(sqlite_file_location)
        logger.network_logger.error("Database Upload: Invalid SQLite3 Database File")
    logger.network_logger.info("Database Upload Complete")


def _db_replacement_raw_worker(temp_db_location, save_db_to, backup_file_name):
    logger.network_logger.info("Database Replacement Processing ...")
    expected_database_type = None
    if save_db_to == file_locations.sensor_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_main
    elif save_db_to == file_locations.sensor_checkin_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_sensor_checkins
    elif save_db_to == file_locations.mqtt_subscriber_database:
        expected_database_type = app_cached_variables.database_variables.db_info_database_type_mqtt

    if universal_database_structure_check(temp_db_location, expected_database_type):
        if _zip_and_delete_database(save_db_to, backup_file_name):
            os.rename(temp_db_location, save_db_to)
            _set_file_permissions(save_db_to)
            logger.network_logger.info("Database Replaced " + save_db_to)
        else:
            logger.network_logger.error("Database Backup Failed: Database Replacement Cancelled")
            os.remove(temp_db_location)
    else:
        logger.network_logger.error("Database Upload: Invalid Database")
        os.remove(temp_db_location)
    logger.network_logger.info("Database Replacement Complete")


def _set_file_permissions(file_location, file_permissions=0o666):
    try:
        os.chmod(file_location, file_permissions)
    except Exception as error:
        logger.network_logger.error("Setting file permissions on " + file_location + ": " + str(error))


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
