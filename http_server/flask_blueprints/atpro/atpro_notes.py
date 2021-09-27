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
from flask import Blueprint, render_template, request
from operations_modules import app_cached_variables
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index
from operations_modules.db_notes_access import add_note_to_database, update_note_in_database, delete_db_note, \
    get_db_note_dates, get_db_note_user_dates

html_atpro_notes_routes = Blueprint("html_atpro_notes_routes", __name__)
db_v = app_cached_variables.database_variables


@html_atpro_notes_routes.route("/atpro/sensor-notes", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_notes():
    if request.method == "POST":
        if request.form.get("button_function"):
            button_operation = request.form.get("button_function")
            if button_operation == "new":
                app_cached_variables.notes_total_count += 1
                app_cached_variables.note_current = app_cached_variables.notes_total_count
                app_cached_variables.cached_notes_as_list.append("New Note")
                current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                new_note_and_datetime = current_datetime + app_cached_variables.command_data_separator + "New Note"
                add_note_to_database(new_note_and_datetime)
                if app_cached_variables.note_current > app_cached_variables.notes_total_count:
                    app_cached_variables.note_current = 1
            elif button_operation == "save":
                note_text = request.form.get("note_text")
                if app_cached_variables.notes_total_count > 0:
                    note_auto_date_times = get_db_note_dates().split(",")
                    note_custom_date_times = get_db_note_user_dates().split(",")
                    primary_note_date_time = note_auto_date_times[app_cached_variables.note_current - 1]
                    custom_note_date_time = note_custom_date_times[app_cached_variables.note_current - 1]
                    updated_note_and_datetime = primary_note_date_time + app_cached_variables.command_data_separator + \
                                                custom_note_date_time + app_cached_variables.command_data_separator + \
                                                note_text
                    update_note_in_database(updated_note_and_datetime)
                else:
                    app_cached_variables.notes_total_count += 1
                    app_cached_variables.note_current = app_cached_variables.notes_total_count
                    app_cached_variables.cached_notes_as_list.append(note_text)
                    current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    new_note_and_datetime = current_datetime + app_cached_variables.command_data_separator + note_text
                    add_note_to_database(new_note_and_datetime)
                app_cached_variables.cached_notes_as_list[app_cached_variables.note_current - 1] = note_text
            elif button_operation == "next":
                app_cached_variables.note_current += 1
                if app_cached_variables.note_current > app_cached_variables.notes_total_count:
                    app_cached_variables.note_current = 1
            elif button_operation == "back":
                app_cached_variables.note_current -= 1
                if app_cached_variables.note_current < 1:
                    app_cached_variables.note_current = app_cached_variables.notes_total_count
            elif button_operation == "go":
                custom_current_note = request.form.get("current_note_num")
                if app_cached_variables.notes_total_count > 0:
                    app_cached_variables.note_current = int(custom_current_note)
            elif button_operation == "delete":
                if app_cached_variables.notes_total_count > 0:
                    db_note_date_times = get_db_note_dates().split(",")
                    app_cached_variables.cached_notes_as_list.pop(app_cached_variables.note_current - 1)
                    delete_db_note(db_note_date_times[(app_cached_variables.note_current - 1)])
                    app_cached_variables.notes_total_count -= 1
                    app_cached_variables.note_current = 1
            return get_html_atpro_index(run_script="SelectNav('sensor-notes');")
    if app_cached_variables.notes_total_count > 0:
        selected_note = app_cached_variables.cached_notes_as_list[app_cached_variables.note_current - 1]
    else:
        selected_note = "No Notes Found"
    return render_template("ATPro_admin/page_templates/notes.html",
                           CurrentNoteNumber=app_cached_variables.note_current,
                           LastNoteNumber=str(app_cached_variables.notes_total_count),
                           DisplayedNote=selected_note)
