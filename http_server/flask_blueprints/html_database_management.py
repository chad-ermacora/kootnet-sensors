import os
import re
import time
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, zip_files, get_zip_size, get_list_of_filenames_in_dir
from operations_modules.sqlite_database import get_sqlite_tables_in_list, validate_sqlite_database, \
    write_to_sql_database, check_main_database_structure, check_mqtt_subscriber_database_structure, \
    check_checkin_database_structure
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return, get_html_hidden_state
from sensor_modules import sensor_access

html_database_routes = Blueprint("html_database_routes", __name__)
uploaded_databases_folder = file_locations.uploaded_databases_folder
sqlite_valid_extensions_list = ["sqlite", "sqlite3", "db", "dbf", "sql"]


@html_database_routes.route("/databases")
def html_databases_management():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    db_dropdown_selection = ""
    for db_name in app_cached_variables.uploaded_databases_list:
        db_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", db_name) + "\n"

    db_backup_dropdown_selection = ""
    for zip_name in app_cached_variables.zipped_db_backup_list:
        db_backup_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", zip_name) + "\n"
    return render_template(
        "databases_management.html",
        PageURL="/databases",
        RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
        RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
        HostName=app_cached_variables.hostname,
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=sensor_access.get_file_size(),
        NumberNotes=sensor_access.get_db_notes_count(),
        SQLMQTTDatabaseLocation=file_locations.mqtt_subscriber_database,
        SQLMQTTDatabaseSize=sensor_access.get_file_size(file_location=file_locations.mqtt_subscriber_database),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=file_locations.sensor_checkin_database,
        SQLCheckinDatabaseSize=sensor_access.get_file_size(file_location=file_locations.sensor_checkin_database),
        SQLCheckinSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        UploadedDBOptionNames=db_dropdown_selection,
        BackupDBOptionNames=db_backup_dropdown_selection
    )


@html_database_routes.route("/UploadCustomSQLDatabase", methods=["POST"])
@auth.login_required
def html_upload_custom_database():
    logger.network_logger.debug("* Upload Custom Database by " + str(request.remote_addr))
    return_msg = "Sensor Database Uploaded Okay"
    db_check_msg = "Database(s) Uploaded, Saved and Checked Okay"

    new_db_name = _get_clean_db_name(str(request.form.get("UploadDatabaseName")).strip())
    zip_location = file_locations.uploaded_databases_folder + "/temp_zip.zip"
    save_sqlite_to_file = file_locations.uploaded_databases_folder + "/" + new_db_name

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
                    uploaded_db_filenames = get_list_of_filenames_in_dir(file_locations.uploaded_databases_folder)
                    app_cached_variables.uploaded_databases_list = uploaded_db_filenames
                else:
                    os.remove(save_sqlite_to_file)
                    return_msg = "Database Upload Error"
                    db_check_msg = "Invalid SQLite3 Database File"
        except Exception as error:
            return_msg = "Sensor Database Uploaded Failed"
            db_check_msg = str(error)
    logger.network_logger.info("Database Custom Upload: " + db_check_msg)
    return message_and_return(return_msg, text_message2=db_check_msg, url="/databases")


def _get_clean_db_name(db_text_name):
    final_db_name = ""
    for letter in db_text_name:
        if re.match("^[A-Za-z0-9_.-]*$", letter):
            final_db_name += letter

    if final_db_name == "":
        final_db_name = "No_Name"

    if final_db_name.split(".")[-1] == "sqlite":
        final_db_name = final_db_name[:-7]

    retry = True
    while retry:
        retry = False
        for name in app_cached_variables.uploaded_databases_list:
            if name == final_db_name + ".sqlite":
                final_db_name = final_db_name + "1"
                retry = True
    return final_db_name + ".sqlite"


@html_database_routes.route("/CustomDatabaseManagement", methods=["POST"])
@auth.login_required
def html_custom_database_management():
    logger.network_logger.debug("* Custom Database Management accessed by " + str(request.remote_addr))
    upload_db_folder = file_locations.uploaded_databases_folder + "/"

    try:
        db_full_path = upload_db_folder + str(request.form.get("ManagementDatabaseSelection"))
        if str(request.form.get("db_management")) == "rename_db":
            new_db_full_path = upload_db_folder + _get_clean_db_name(str(request.form.get("RenameUploadDatabaseName")))
            os.rename(db_full_path, new_db_full_path)
        elif str(request.form.get("db_management")) == "delete_db":
            os.remove(db_full_path)
        uploaded_db_filenames = get_list_of_filenames_in_dir(file_locations.uploaded_databases_folder)
        app_cached_variables.uploaded_databases_list = uploaded_db_filenames
        return html_databases_management()
    except Exception as error:
        return_text2 = str(error)
        logger.network_logger.error("Unable to rename or delete database: " + return_text2)
    return message_and_return("Unable to rename or delete database", text_message2=return_text2, url="/databases")


@html_database_routes.route("/DatabaseBackupManagement", methods=["POST"])
@auth.login_required
def html_database_backup_management():
    logger.network_logger.debug("* Backup Database Management accessed by " + str(request.remote_addr))
    return_msg = "Unable to delete database backup"
    backup_db_folder = file_locations.database_backup_folder + "/"

    try:
        db_selected_name = str(request.form.get("DatabaseBackupSelection"))
        db_full_path = backup_db_folder + db_selected_name
        if str(request.form.get("db_backups")) == "delete_backup_db":
            os.remove(db_full_path)
            backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.database_backup_folder)
            app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
        elif str(request.form.get("db_backups")) == "download_backup_db":
            return send_file(db_full_path, as_attachment=True, attachment_filename=db_selected_name)
    except Exception as error:
        return_text2 = str(error)
        logger.network_logger.error(return_msg + ": " + return_text2)
        return message_and_return(return_msg, text_message2=return_text2, url="/databases")
    return html_databases_management()


@html_database_routes.route("/GetSQLDBSize")
def get_sql_db_size():
    logger.network_logger.debug("* Sensor's Database Size sent to " + str(request.remote_addr))
    return str(sensor_access.get_file_size())


@html_database_routes.route("/UploadSQLDatabase", methods=["POST"])
@auth.login_required
def replace_local_sql_database():
    logger.network_logger.info("* Sensor's Database Replacement accessed by " + str(request.remote_addr))
    selected_database = str(request.form.get("DatabaseReplacementSelection"))

    return_msg = selected_database + " SQLite3 Database Upload Okay"
    return_text2 = "The previous database was archived and replaced with the uploaded Database"

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
                            return_msg = "Sensor Database Backup Failed"
                            return_text2 = "Database Replacement Cancelled"
                    else:
                        return_msg = "Database Error"
                        return_text2 = "Invalid SQLite3 Database"
    else:
        return_msg = "Database Error"
        return_text2 = "No File Uploaded"
    logger.network_logger.info("Database Upload: " + return_msg + " - " + return_text2)
    return message_and_return(return_msg, text_message2=return_text2, url="/databases")


def _zip_and_delete_database(database_location, db_save_name):
    """ Creates a zip of linked database in the database backup folder then deletes the original database. """
    filename_start = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + "_"
    sql_filename = filename_start + db_save_name + ".sqlite"
    zip_filename = filename_start + str(datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")) + db_save_name + ".zip"
    zip_full_path = file_locations.database_backup_folder + "/" + zip_filename
    try:
        zip_content = get_file_content(database_location, open_type="rb")
        zip_files([sql_filename], [zip_content], save_type="save_to_disk", file_location=zip_full_path)
        backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.database_backup_folder)
        app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
        os.remove(database_location)
        return True
    except Exception as error:
        print(str(error))
    return False


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
                    backup_db_zip_filenames = get_list_of_filenames_in_dir(file_locations.uploaded_databases_folder)
                    app_cached_variables.zipped_db_backup_list = backup_db_zip_filenames
                    new_db_name = _get_clean_db_name(new_db_name)
    if os.path.isfile(zip_location):
        os.remove(zip_location)
    return return_database_locations_list


@html_database_routes.route("/GetZippedSQLDatabaseSize")
def get_zipped_sql_database_size():
    logger.network_logger.debug("* Zipped SQL Database Size Sent to " + str(request.remote_addr))
    try:
        database_name = app_cached_variables.hostname + "SensorDatabase.sqlite"
        start_time = time.time()
        sql_database = get_file_content(file_locations.sensor_database, open_type="rb")
        zip_file = zip_files([database_name], [sql_database])
        sql_database_size = round(get_zip_size(zip_file) / 1000000, 2)
        end_time = time.time()
        run_time = str(round(end_time - start_time, 2)) + " Seconds"
        log_message = "Database Zip Creation and Size Retrieval Took: " + run_time
        logger.network_logger.debug(log_message)
        return str(sql_database_size)
    except Exception as error:
        log_message = "* Unable to Send Database Size to " + str(request.remote_addr) + ": " + str(error)
        logger.network_logger.error(log_message)
        return "Error"


@html_database_routes.route("/VacuumSQLDatabase", methods=["POST"])
@auth.login_required
def vacuum_database():
    logger.network_logger.info("** SQL Database VACUUM Initiated by " + str(request.remote_addr))
    selected_database = str(request.form.get("SQLDatabaseSelection"))
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
        return message_and_return(selected_database + " Database has been Shrunk", url="/databases")
    return message_and_return(selected_database + " Database not found", url="/databases")
