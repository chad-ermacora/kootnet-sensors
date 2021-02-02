import os
import re
import zipfile
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import update_uploaded_databases_names_list
from operations_modules.sqlite_database import sql_execute_get_data, get_sqlite_tables_in_list
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
