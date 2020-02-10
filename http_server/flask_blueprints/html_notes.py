from _datetime import datetime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import sqlite_database
from http_server.server_http_auth import auth
from sensor_modules.sensor_access import add_note_to_database, update_note_in_database, delete_db_note, \
    get_db_note_dates, get_db_note_user_dates

html_notes_routes = Blueprint("html_notes_routes", __name__)


def translate_note_text(note_text, translate_type="decode"):
    if translate_type == "decode":
        new_note = note_text.replace("[clean_slash]", "\\")
        new_note = new_note.replace("[replaced_comma]", ",")
        new_note = new_note.replace("[new_line]", "\n")
    else:
        new_note = note_text.replace("\\", "[clean_slash]")
        new_note = new_note.replace(",", "[replaced_comma]")
        new_note = new_note.replace("\n", "[new_line]")
        new_note = new_note.replace("\r", "[new_line]")
    return new_note


@html_notes_routes.route("/SensorNotes", methods=["GET", "POST"])
@auth.login_required
def sensor_notes():
    logger.network_logger.debug("** Notes accessed from " + str(request.remote_addr))
    note_count_sql_query = "SELECT count(" + \
                           str(app_cached_variables.database_variables.other_table_column_notes) + \
                           ") FROM " + \
                           str(app_cached_variables.database_variables.table_other)
    app_cached_variables.notes_total_count = sqlite_database.sql_execute_get_data(note_count_sql_query)[0][0]
    selected_note_sql_query = "SELECT " + \
                              str(app_cached_variables.database_variables.other_table_column_notes) + \
                              " FROM " + \
                              str(app_cached_variables.database_variables.table_other)
    if request.method == "POST":
        if request.form["button_function"]:
            button_operation = request.form["button_function"]
            if button_operation == "new":
                app_cached_variables.notes_total_count += 1
                app_cached_variables.note_current = app_cached_variables.notes_total_count
                current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                new_note_and_datetime = current_datetime + app_cached_variables.command_data_separator + "New Note"
                add_note_to_database(new_note_and_datetime)
                if app_cached_variables.note_current > app_cached_variables.notes_total_count:
                    app_cached_variables.note_current = 1
            elif button_operation == "save_note":
                if app_cached_variables.notes_total_count > 0:
                    note_text = translate_note_text(request.form["note_text"], translate_type="encode")
                    print(str(note_text))
                    note_auto_date_times = get_db_note_dates().split(",")
                    note_custom_date_times = get_db_note_user_dates().split(",")
                    primary_note_date_time = note_auto_date_times[app_cached_variables.note_current - 1]
                    custom_note_date_time = note_custom_date_times[app_cached_variables.note_current - 1]
                    updated_note_and_datetime = primary_note_date_time + app_cached_variables.command_data_separator + \
                                                custom_note_date_time + app_cached_variables.command_data_separator + \
                                                note_text
                    print(str(updated_note_and_datetime))
                    update_note_in_database(updated_note_and_datetime)

            elif button_operation == "next":
                app_cached_variables.note_current += 1
                if app_cached_variables.note_current > app_cached_variables.notes_total_count:
                    app_cached_variables.note_current = 1
            elif button_operation == "back":
                app_cached_variables.note_current -= 1
                if app_cached_variables.note_current < 1:
                    app_cached_variables.note_current = app_cached_variables.notes_total_count
            elif button_operation == "custom_note_number":
                custom_current_note = request.form["current_note_num"]
                if app_cached_variables.notes_total_count > 0:
                    app_cached_variables.note_current = int(custom_current_note)
                    print(str(type(custom_current_note)))
            elif button_operation == "delete":
                if app_cached_variables.notes_total_count > 0:
                    db_note_date_times = get_db_note_dates().split(",")
                    delete_db_note(db_note_date_times[(app_cached_variables.note_current - 1)])
                    app_cached_variables.notes_total_count -= 1
                    app_cached_variables.note_current = 1
    note_num = app_cached_variables.note_current - 1
    if app_cached_variables.notes_total_count > 0:
        selected_note = str(sqlite_database.sql_execute_get_data(selected_note_sql_query)[note_num][0])
        selected_note = translate_note_text(selected_note)
    else:
        selected_note = "No Notes Found"
    return render_template("sensor_notes.html",
                           CurrentNoteNumber=app_cached_variables.note_current,
                           LastNoteNumber=str(app_cached_variables.notes_total_count),
                           DisplayedNote=selected_note)
