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
from time import strftime
from datetime import datetime
from flask import Blueprint, render_template, send_file, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.software_version import version
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from http_server.server_http_generic_functions import get_html_hidden_state
from http_server.flask_blueprints.html_notes import add_note_to_database, update_note_in_database, get_db_note_dates, \
    get_db_note_user_dates, delete_db_note
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import atpro_variables, \
    html_sensor_readings_row, get_ram_free, get_disk_free
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_html_atpro_index, \
    get_message_page

html_atpro_main_routes = Blueprint("html_atpro_main_routes", __name__)
db_v = app_cached_variables.database_variables


@html_atpro_main_routes.route("/atpro/")
def html_atpro_index():
    return get_html_atpro_index()


@html_atpro_main_routes.route("/atpro/sensor-dashboard")
def html_atpro_dashboard():
    atpro_variables.init_tests()

    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = round(cpu_temp[app_cached_variables.database_variables.system_temperature], 3)

    enable_debug_logging = app_config_access.primary_config.enable_debug_logging
    enable_high_low_trigger_recording = app_config_access.trigger_high_low.enable_high_low_trigger_recording
    enable_trigger_variance = app_config_access.trigger_variances.enable_trigger_variance
    enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording
    enable_checkin = app_config_access.primary_config.enable_checkin
    enable_checkin_recording = app_config_access.checkin_config.enable_checkin_recording
    return render_template("ATPro_admin/page_templates/dashboard.html",
                           KootnetVersion=version,
                           StdVersion=app_cached_variables.standard_version_available,
                           DevVersion=app_cached_variables.developmental_version_available,
                           LastUpdated=app_cached_variables.program_last_updated,
                           DateTime=strftime("%Y-%m-%d %H:%M:%S - %Z"),
                           DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                           HostName=app_cached_variables.hostname,
                           LocalIP=app_cached_variables.ip,
                           DebugLogging=_get_text_check_enabled(enable_debug_logging),
                           CPUTemperature=str(cpu_temp),
                           SensorReboots=app_cached_variables.reboot_count,
                           RAMUsage=get_ram_free(),
                           DiskUsage=get_disk_free(),
                           IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
                           TriggerHighLowRecording=_get_text_check_enabled(enable_high_low_trigger_recording),
                           TriggerVarianceRecording=_get_text_check_enabled(enable_trigger_variance),
                           MQTTPublishing=app_cached_variables.mqtt_publisher_thread.current_state,
                           MQTTSubscriber=app_cached_variables.mqtt_subscriber_thread.current_state,
                           MQTTSubscriberRecording=_get_text_check_enabled(enable_mqtt_sql_recording),
                           SensorCheckins=_get_text_check_enabled(enable_checkin),
                           CheckinServer=_get_text_check_enabled(enable_checkin_recording),
                           OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
                           WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
                           LuftdatenService=app_cached_variables.luftdaten_thread.current_state,
                           InstalledSensors=app_config_access.installed_sensors.get_installed_names_str())


@html_atpro_main_routes.route("/atpro/sensor-readings")
def html_atpro_sensor_readings():
    all_readings = sensor_access.get_all_available_sensor_readings(skip_system_info=True)
    html_final_code = ""
    for index, dic_readings in enumerate(all_readings.items()):
        html_final_code += "<tr>\n<td>" + dic_readings[0] + "</td>\n<td>" + str(dic_readings[1]) + "</td>\n</tr>\n"

    html_return_code = html_sensor_readings_row.replace("{{ Readings }}", html_final_code)
    return render_template("ATPro_admin/page_templates/sensor_readings.html",
                           HTMLReplacementCode=html_return_code)


@html_atpro_main_routes.route("/atpro/sensor-notes", methods=["GET", "POST"])
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
    return render_template("ATPro_admin/page_templates/sensor_notes.html",
                           PageURL="/atpro/sensor-notes",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           CurrentNoteNumber=app_cached_variables.note_current,
                           LastNoteNumber=str(app_cached_variables.notes_total_count),
                           DisplayedNote=selected_note)


@html_atpro_main_routes.route("/atpro/sensor-graphing")
def html_atpro_sensor_graphing():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_main_routes.route("/atpro/sensor-rm")
def html_atpro_sensor_remote_management():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_main_routes.route("/atpro/sensor-help")
def html_atpro_sensor_help():
    documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"
    return send_file(documentation_root_dir + "/index.html")


@html_atpro_main_routes.route("/atpro/logout")
def html_atpro_logout():
    return get_message_page("Logged Out", "You have been logged out"), 401


def _get_text_check_enabled(setting):
    if setting:
        return "Enabled"
    return "Disabled"
