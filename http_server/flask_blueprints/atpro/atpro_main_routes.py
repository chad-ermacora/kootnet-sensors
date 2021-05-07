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
from operations_modules.app_generic_functions import get_file_size
from operations_modules.software_version import version
from operations_modules.sqlite_database import get_sql_element, get_sqlite_tables_in_list, get_clean_sql_table_name, \
    sql_execute_get_data
from operations_modules.software_version import version as kootnet_version
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_variables import html_sensor_readings_row, \
    get_ram_free, get_disk_free, atpro_notifications
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_text_check_enabled, get_uptime_str
from sensor_modules.sensor_access import add_note_to_database, update_note_in_database, delete_db_note, \
    get_db_note_dates, get_db_note_user_dates

html_atpro_main_routes = Blueprint("html_atpro_main_routes", __name__)
db_v = app_cached_variables.database_variables


@html_atpro_main_routes.route("/atpro/get-notification-count")
def html_atpro_get_notification_count():
    return str(atpro_notifications.get_notification_count())


@html_atpro_main_routes.route("/atpro/get-notification-messages")
def html_atpro_get_notification_messages():
    return atpro_notifications.get_notifications_as_string()


@html_atpro_main_routes.route("/atpro/")
def html_atpro_index():
    return get_html_atpro_index()


@html_atpro_main_routes.route("/atpro/sensor-dashboard")
def html_atpro_dashboard():
    g_t_c_e = get_text_check_enabled

    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = round(cpu_temp[app_cached_variables.database_variables.system_temperature], 3)
    return render_template(
        "ATPro_admin/page_templates/dashboard.html",
        KootnetVersion=version,
        StdVersion=app_cached_variables.standard_version_available,
        DevVersion=app_cached_variables.developmental_version_available,
        LastUpdated=app_cached_variables.program_last_updated,
        DateTime=strftime("%Y-%m-%d %H:%M:%S %Z"),
        DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        HostName=app_cached_variables.hostname,
        LocalIP=app_cached_variables.ip,
        OperatingSystem=app_cached_variables.operating_system_name,
        DebugLogging=g_t_c_e(app_config_access.primary_config.enable_debug_logging),
        CPUTemperature=str(cpu_temp),
        SensorUptime=get_uptime_str(),
        SensorReboots=app_cached_variables.reboot_count,
        RAMUsage=str(get_ram_free()) + " GB",
        DiskUsage=str(get_disk_free()) + " GB",
        InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
        IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
        TriggerHighLowRecording=g_t_c_e(app_config_access.trigger_high_low.enable_high_low_trigger_recording),
        TriggerVarianceRecording=g_t_c_e(app_config_access.trigger_variances.enable_trigger_variance),
        MQTTPublishing=app_cached_variables.mqtt_publisher_thread.current_state,
        MQTTSubscriber=app_cached_variables.mqtt_subscriber_thread.current_state,
        MQTTSubscriberRecording=g_t_c_e(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        SensorCheckins=g_t_c_e(app_config_access.primary_config.enable_checkin),
        CheckinServer=g_t_c_e(app_config_access.checkin_config.enable_checkin_recording),
        OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
        WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
        LuftdatenService=app_cached_variables.luftdaten_thread.current_state
    )


@html_atpro_main_routes.route("/atpro/sensor-readings")
def html_atpro_sensor_readings():
    all_readings = sensor_access.get_all_available_sensor_readings(skip_system_info=True)
    html_final_code = ""
    for index, dic_readings in enumerate(all_readings.items()):
        reading_unit = " " + sensor_access.get_reading_unit(dic_readings[0])
        new_reading = html_sensor_readings_row.replace("{{ SensorName }}", dic_readings[0].replace("_", " "))
        new_reading = new_reading.replace("{{ SensorReading }}", str(dic_readings[1]) + reading_unit)
        html_final_code += new_reading + "\n"
    return render_template("ATPro_admin/page_templates/sensor-readings.html", HTMLReplacementCode=html_final_code)


@html_atpro_main_routes.route("/atpro/sensor-latency")
def html_atpro_sensors_latency():
    sensors_latency = sensor_access.get_sensors_latency()
    html_final_code = ""
    for index, dic_readings in enumerate(sensors_latency.items()):
        new_reading = html_sensor_readings_row.replace("{{ SensorName }}", dic_readings[0].replace("_", " "))
        new_reading = new_reading.replace("{{ SensorReading }}", str(dic_readings[1]) + " Seconds")
        html_final_code += new_reading + "\n"
    return render_template("ATPro_admin/page_templates/sensors-latency.html", HTMLReplacementCode=html_final_code)


@html_atpro_main_routes.route("/atpro/sensor-notes", methods=["GET", "POST"])
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


@html_atpro_main_routes.route("/atpro/mqtt-subscriber-view-data-stream")
@auth.login_required
def html_atpro_mqtt_subscriber_data_stream_view():
    mqtt_subscriber_log = file_locations.mqtt_subscriber_log
    max_entries = app_config_access.mqtt_subscriber_config.mqtt_page_view_max_entries
    mqtt_subscriber_log_content = logger.get_sensor_log(mqtt_subscriber_log, max_lines=max_entries).strip()
    if mqtt_subscriber_log_content == "":
        mqtt_subscriber_log_content = _mqtt_sub_entry_to_html("")
    else:
        new_return = ""
        for line in mqtt_subscriber_log_content.split("\n"):
            new_return += _mqtt_sub_entry_to_html(line)
        mqtt_subscriber_log_content = new_return
    return render_template(
        "ATPro_admin/page_templates/mqtt-subscriber-data-view.html",
        MQTTSubDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
        MQTTSubscriberServerAddress=app_config_access.mqtt_subscriber_config.broker_address,
        MQTTShowing=max_entries,
        MQTTTotoalEntries=logger.get_number_of_log_entries(mqtt_subscriber_log),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        MQTTEnabledColor=_get_html_color(app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber),
        MQTTSubscriberEnabledText=_get_html_text(app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber),
        MQTTSQLEnabledColor=_get_html_color(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        MQTTSQLSubscriberEnabledText=_get_html_text(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        SubscriberTopicsContent=mqtt_subscriber_log_content
    )


def _get_html_color(setting):
    if setting:
        return "lightgreen"
    return "red"


def _get_html_text(setting):
    if setting:
        return "Enabled"
    return "Disabled"


def _mqtt_sub_entry_to_html(sub_entry):
    sensor_id = ""
    sensor_time = ""
    sensor_data = ""
    try:
        split_entry_space = sub_entry.split(" ")
        if len(split_entry_space) >= 5:
            sensor_time = split_entry_space[0] + " " + split_entry_space[1]
            sensor_id = split_entry_space[3]
            entry_dic = eval(str(sub_entry.split("=")[1].strip()))
            if type(entry_dic) is dict:
                sensor_data = ""
                for index, data in entry_dic.items():
                    unit_measurement_type = " " + sensor_access.get_reading_unit(index)
                    if index == "DateTime":
                        pass
                    else:
                        index = index.replace("_", " ")
                        sensor_data += "<div class='col-6 col-m-6 col-sm-6'><div class='counter bg-primary'>"
                        sensor_data += "<span class='sensor-info'>" + index + "</span><br>"
                        sensor_data += str(data) + unit_measurement_type + "<br></div></div>"
            else:
                sensor_id = "NA"
                sensor_time = "NA"
                sensor_data = "<div class='col-6 col-m-6 col-sm-6'><div class='counter bg-primary'>"
                sensor_data += str(sub_entry)
                sensor_data += "</div></div>"
    except Exception as error:
        logger.network_logger.debug("** HTML MQTT Subscriber convert for view: " + str(error))
        sensor_id = "NA"
        sensor_time = "NA"
        sensor_data = str(sub_entry)
    return render_template("ATPro_admin/page_templates/mqtt-subscriber-data-entry-template.html",
                           SensorID=sensor_id,
                           DateTimeContact=sensor_time,
                           MQTTData=sensor_data)


@html_atpro_main_routes.route("/atpro/mqtt-subscriber-clear-log")
@auth.login_required
def html_atpro_clear_mqtt_subscriber_log():
    logger.network_logger.debug("** HTML Clear - MQTT Subscriber Log - Source: " + str(request.remote_addr))
    logger.clear_mqtt_subscriber_log()
    return get_html_atpro_index(run_script="SelectNav('mqtt-subscriber-view-data-stream');")


@html_atpro_main_routes.route("/atpro/mqtt-subscriber-sensors-list")
@auth.login_required
def html_atpro_mqtt_subscriber_sensors_list():
    mqtt_subscriber_sensors = get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database)
    sensors_count = len(mqtt_subscriber_sensors)

    sensors_html_list = []
    for sensor_id in mqtt_subscriber_sensors:
        sensor_id = get_sql_element(sensor_id)
        sensors_html_list.append(_get_sensor_html_table_code(sensor_id))

    sensors_html_list.sort(key=lambda x: x[1], reverse=True)
    html_sensor_table_code = ""
    for sensor in sensors_html_list:
        html_sensor_table_code += sensor[0]
    return render_template(
        "ATPro_admin/page_templates/mqtt-subscriber-sensors-list.html",
        SQLMQTTSensorsInDB=str(sensors_count),
        HTMLSensorsTableCode=html_sensor_table_code)


def _get_sensor_html_table_code(sensor_id):
    dv_v = app_cached_variables.database_variables
    sensor_id = get_clean_sql_table_name(sensor_id)
    html_sensor_code = """<tr>
        <td>{{ SensorID }}</td>
        <td>{{ SensorHostName }}</td>
        <td>{{ IPAddress }}</td>
        <td>{{ LastContact }}</td>
    </tr>
    """.replace("{{ SensorID }}", sensor_id)

    columns_list = [dv_v.sensor_name, dv_v.ip, dv_v.all_tables_datetime]
    replacement_variables = ["{{ SensorHostName }}", "{{ IPAddress }}", "{{ LastContact }}"]
    sql_get_code = "SELECT {{ ColumnName }} FROM '" + sensor_id + "' WHERE {{ ColumnName }} != '' ORDER BY " \
                          + app_cached_variables.database_variables.all_tables_datetime + " DESC LIMIT 1;"

    results_list = []
    for column, replacement_var in zip(columns_list, replacement_variables):
        replacement_data = sql_execute_get_data(sql_get_code.replace("{{ ColumnName }}", column),
                                                sql_database_location=file_locations.mqtt_subscriber_database)
        replacement_data = get_sql_element(replacement_data)
        results_list.append(replacement_data)
        try:
            html_sensor_code = html_sensor_code.replace(replacement_var, replacement_data)
        except Exception as error:
            logger.network_logger.warning("MQTT Subscriber Sensors List Creation: " + str(error))
    return [html_sensor_code, results_list[-1]]


@html_atpro_main_routes.route("/atpro/sensor-help")
def html_atpro_sensor_help():
    documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"
    return send_file(documentation_root_dir + "/index.html")


@html_atpro_main_routes.route("/atpro/logout")
def html_atpro_logout():
    return get_message_page("Logged Out", "You have been logged out"), 401


@html_atpro_main_routes.route("/atpro/system-about")
def html_atpro_about():
    return render_template("ATPro_admin/page_templates/system/system-about.html", KootnetVersion=kootnet_version)
