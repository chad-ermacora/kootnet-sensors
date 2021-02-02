import os
import re
import time
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import update_uploaded_databases_names_list
from operations_modules.app_generic_functions import get_file_content, zip_files, get_zip_size
from operations_modules.sqlite_database import sql_execute_get_data, get_sqlite_tables_in_list, \
    validate_sqlite_database, check_main_database_structure, write_to_sql_database
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return, get_html_hidden_state
from sensor_modules import sensor_access

html_database_routes = Blueprint("html_database_routes", __name__)


@html_database_routes.route("/databases")
def html_databases_management():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    database_dropdown_selection_html = ""
    for db_name in app_cached_variables.uploaded_databases_list:
        database_dropdown_selection_html += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", db_name) + "\n"
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
        UploadedDBOptionNames=database_dropdown_selection_html,
    )


@html_database_routes.route("/UploadCustomSQLDatabase", methods=["POST"])
@auth.login_required
def html_upload_custom_database():
    logger.network_logger.debug("* Upload Custom Database by " + str(request.remote_addr))
    return_message_fail = "Invalid SQLite3 Database File."
    sqlite_valid_extensions_list = ["sqlite", "sqlite3", "db"]
    new_db_name = _get_clean_db_name(str(request.form.get("UploadDatabaseName")).strip())
    temp_zip_name = file_locations.uploaded_databases_folder + "/tempzip.zip"
    save_sqlite_to_file = file_locations.uploaded_databases_folder + "/" + new_db_name

    new_database = request.files["command_data"]

    upload_file_name = new_database.filename
    if new_database is not None:
        try:
            if upload_file_name.split(".")[-1] == "zip":
                if os.path.isfile(temp_zip_name):
                    os.remove(temp_zip_name)

                new_database.save(temp_zip_name)
                db_check_msg = "Database(s) Checked Okay"
                with zipfile.ZipFile(temp_zip_name, "r") as temp_zip:
                    zip_file_infos = temp_zip.infolist()
                    db_found = False
                    for zip_info in zip_file_infos:
                        for sql_valid_extension in sqlite_valid_extensions_list:
                            if zip_info.filename.split(".")[-1] == sql_valid_extension:
                                db_found = True
                                zip_info.filename = new_db_name
                                temp_zip.extract(zip_info, path=file_locations.uploaded_databases_folder)
                                if not _test_sqlite_database_okay(save_sqlite_to_file):
                                    os.remove(save_sqlite_to_file)
                                    db_check_msg = "One or more Invalid Databases in Zip"
                                update_uploaded_databases_names_list()
                                new_db_name = _get_clean_db_name(new_db_name)
                os.remove(temp_zip_name)
                update_uploaded_databases_names_list()
                if not db_found:
                    db_check_msg = "No Database Found in Zip"
                return_msg = "Sensor Database Uploaded & Unzipped Okay"
                return message_and_return(return_msg, text_message2=db_check_msg, url="/databases")
            else:
                new_database.save(save_sqlite_to_file)
                if _test_sqlite_database_okay(save_sqlite_to_file):
                    update_uploaded_databases_names_list()
                    return message_and_return("Sensor Database Uploaded Okay", url="/databases")
                else:
                    os.remove(save_sqlite_to_file)
        except Exception as error:
            logger.network_logger.error("Database Upload Error: " + str(error))
    if os.path.isfile(temp_zip_name):
        os.remove(temp_zip_name)
    return message_and_return("Sensor Database Uploaded Failed", text_message2=return_message_fail, url="/databases")


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


def _test_sqlite_database_okay(database_location):
    try:
        get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
        sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=database_location)
        if len(sensor_ids) > 0:
            return True
    except Exception as error:
        logger.network_logger.error("Database Upload Check Error: " + str(error))
    return False


@html_database_routes.route("/CustomDatabaseManagement", methods=["POST"])
@auth.login_required
def html_custom_database_management():
    logger.network_logger.debug("* Custom Database Management accessed by " + str(request.remote_addr))
    upload_db_folder = file_locations.uploaded_databases_folder + "/"
    db_full_path = upload_db_folder + str(request.form.get("ManagementDatabaseSelection"))

    if str(request.form.get("db_management")) == "rename_db":
        new_db_full_path = upload_db_folder + _get_clean_db_name(str(request.form.get("RenameUploadDatabaseName")))
        os.rename(db_full_path, new_db_full_path)
    elif str(request.form.get("db_management")) == "delete_db":
        os.remove(db_full_path)

    update_uploaded_databases_names_list()
    return html_databases_management()


@html_database_routes.route("/GetSQLDBSize")
def get_sql_db_size():
    logger.network_logger.debug("* Sensor's Database Size sent to " + str(request.remote_addr))
    return str(sensor_access.get_file_size())


@html_database_routes.route("/UploadSQLDatabase", methods=["GET", "POST"])
@auth.login_required
def put_sql_db():
    logger.network_logger.info("* Sensor's Database Replacement accessed by " + str(request.remote_addr))
    return_message_ok = "The previous database was archived and replaced with the uploaded Database."
    return_message_fail = "Invalid SQLite3 Database File."
    return_backup_fail = "Upload cancelled due to failed database backup."

    temp_db_location = file_locations.sensor_data_dir + "/upload_test.sqlite"
    new_database = request.files["command_data"]
    if new_database is not None:
        new_database.save(temp_db_location)
        if validate_sqlite_database(database_location=temp_db_location):
            check_main_database_structure(database_location=temp_db_location)
            if _move_database():
                os.system("mv -f " + temp_db_location + " " + file_locations.sensor_database)
                logger.primary_logger.info(return_message_ok)
                return message_and_return("Sensor Database Uploaded OK", text_message2=return_message_ok, url="/")
            else:
                logger.primary_logger.error(return_backup_fail)
                return message_and_return("Sensor Database Backup Failed", text_message2=return_backup_fail, url="/")
    logger.primary_logger.error(return_message_fail)
    return message_and_return("Sensor Database Uploaded Failed", text_message2=return_message_fail, url="/")


def _move_database():
    sql_filename = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + "SensorDatabase.sqlite"
    zip_filename = str(datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")) + "SensorDatabase.zip"
    try:
        zip_content = get_file_content(file_locations.sensor_database, open_type="rb")
        zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.sensor_data_dir + "/" + zip_filename)
        logger.network_logger.info("* Sensor's Database backed up as " + file_locations.sensor_data_dir + zip_filename)
        os.system("rm " + file_locations.sensor_database)
        return True
    except Exception as error:
        logger.network_logger.error("Unable to backup database as zip - " + str(error))
    return False


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
        logger.primary_logger.error(log_message)
        return "Error"


@html_database_routes.route("/VacuumMainSQLDatabase")
@auth.login_required
def vacuum_main_database():
    logger.network_logger.info("** Main SQL Database VACUUM Initiated by " + str(request.remote_addr))
    write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_database)
    return message_and_return("Main SQL Database has been Shrunk", url="/SystemCommands")


@html_database_routes.route("/VacuumCheckInsSQLDatabase")
@auth.login_required
def vacuum_check_ins_database():
    logger.network_logger.info("** CheckIn SQL Database VACUUM Initiated by " + str(request.remote_addr))
    write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_checkin_database)
    return message_and_return("Check-Ins SQL Database has been Shrunk", url="/SystemCommands")
