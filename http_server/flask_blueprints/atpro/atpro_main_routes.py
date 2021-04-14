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
from operations_modules.app_generic_functions import thread_function
from operations_modules.software_version import version
from operations_modules.sqlite_database import get_sql_element, get_sqlite_tables_in_list, get_clean_sql_table_name, \
    sql_execute_get_data
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from http_server.server_http_auth import auth
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.flask_blueprints.html_notes import add_note_to_database, update_note_in_database, get_db_note_dates, \
    get_db_note_user_dates, delete_db_note
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import html_sensor_readings_row, \
    get_ram_free, get_disk_free
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_html_atpro_index, \
    get_message_page, get_text_check_enabled, get_uptime_str, get_file_creation_date

html_atpro_main_routes = Blueprint("html_atpro_main_routes", __name__)
db_v = app_cached_variables.database_variables


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
        DateTime=strftime("%Y-%m-%d<br>%H:%M:%S<br>%Z"),
        DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d<br>%H:%M:%S"),
        HostName=app_cached_variables.hostname,
        LocalIP=app_cached_variables.ip,
        OperatingSystem=app_cached_variables.operating_system_name,
        DebugLogging=g_t_c_e(app_config_access.primary_config.enable_debug_logging),
        CPUTemperature=str(cpu_temp),
        SensorUptime=get_uptime_str(),
        SensorReboots=app_cached_variables.reboot_count,
        RAMUsage=get_ram_free(),
        DiskUsage=get_disk_free(),
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
        html_final_code += "<tr>\n<td>" + dic_readings[0] + "</td>\n<td>" + str(dic_readings[1]) + "</td>\n</tr>\n"
    html_return_code = html_sensor_readings_row.replace("{{ Readings }}", html_final_code)
    return render_template("ATPro_admin/page_templates/sensor-readings.html", HTMLReplacementCode=html_return_code)


@html_atpro_main_routes.route("/atpro/sensor-latency")
def html_atpro_sensors_latency():
    sensors_latency = sensor_access.get_sensors_latency()
    html_final_code = ""
    for index, dic_readings in enumerate(sensors_latency.items()):
        html_final_code += "<tr>\n<td>" + dic_readings[0] + "</td>\n<td>" + str(dic_readings[1]) + "</td>\n</tr>\n"
    html_return_code = html_sensor_readings_row.replace("<th>Sensor Reading</th>", "<th>Sensor Latency in Seconds</th>")
    html_return_code = html_return_code.replace("{{ Readings }}", html_final_code)

    return render_template("ATPro_admin/page_templates/sensors-latency.html", HTMLReplacementCode=html_return_code)


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


@html_atpro_main_routes.route("/atpro/sensor-graphing-live", methods=["GET", "POST"])
def html_atpro_sensor_graphing_live():
    if request.method == "POST":
        app_cached_variables.quick_graph_uptime = 0
        app_cached_variables.quick_graph_cpu_temp = 0
        app_cached_variables.quick_graph_env_temp = 0
        app_cached_variables.quick_graph_pressure = 0
        app_cached_variables.quick_graph_altitude = 0
        app_cached_variables.quick_graph_humidity = 0
        app_cached_variables.quick_graph_dew_point = 0
        app_cached_variables.quick_graph_distance = 0
        app_cached_variables.quick_graph_gas = 0
        app_cached_variables.quick_graph_particulate_matter = 0
        app_cached_variables.quick_graph_lumen = 0
        app_cached_variables.quick_graph_colours = 0
        app_cached_variables.quick_graph_ultra_violet = 0
        app_cached_variables.quick_graph_acc = 0
        app_cached_variables.quick_graph_mag = 0
        app_cached_variables.quick_graph_gyro = 0

        if request.form.get("SkipSQL") is not None:
            app_cached_variables.quick_graph_skip_sql_entries = int(request.form.get("SkipSQL"))
        if request.form.get("MaxSQLData") is not None:
            app_cached_variables.quick_graph_max_sql_entries = int(request.form.get("MaxSQLData"))
        if request.form.get("sensor_uptime") is not None:
            app_cached_variables.quick_graph_uptime = 1
        if request.form.get("cpu_temperature") is not None:
            app_cached_variables.quick_graph_cpu_temp = 1
        if request.form.get("env_temperature") is not None:
            app_cached_variables.quick_graph_env_temp = 1
        if request.form.get("pressure") is not None:
            app_cached_variables.quick_graph_pressure = 1
        if request.form.get("altitude") is not None:
            app_cached_variables.quick_graph_altitude = 1
        if request.form.get("humidity") is not None:
            app_cached_variables.quick_graph_humidity = 1
        if request.form.get("dew_point") is not None:
            app_cached_variables.quick_graph_dew_point = 1
        if request.form.get("distance") is not None:
            app_cached_variables.quick_graph_distance = 1
        if request.form.get("gas") is not None:
            app_cached_variables.quick_graph_gas = 1
        if request.form.get("particulate_matter") is not None:
            app_cached_variables.quick_graph_particulate_matter = 1
        if request.form.get("lumen") is not None:
            app_cached_variables.quick_graph_lumen = 1
        if request.form.get("colour") is not None:
            app_cached_variables.quick_graph_colours = 1
        if request.form.get("ultra_violet") is not None:
            app_cached_variables.quick_graph_ultra_violet = 1
        if request.form.get("accelerometer") is not None:
            app_cached_variables.quick_graph_acc = 1
        if request.form.get("magnetometer") is not None:
            app_cached_variables.quick_graph_mag = 1
        if request.form.get("gyroscope") is not None:
            app_cached_variables.quick_graph_gyro = 1
        return get_html_atpro_index(run_script="SelectNav('sensor-graphing-live');")
    return render_template(
        "ATPro_admin/page_templates/graphing-live.html",
        SkipSQLEntries=app_cached_variables.quick_graph_skip_sql_entries,
        MaxSQLEntries=app_cached_variables.quick_graph_max_sql_entries,
        CheckedSensorUptime=get_html_checkbox_state(app_cached_variables.quick_graph_uptime),
        CheckedCPUTemperature=get_html_checkbox_state(app_cached_variables.quick_graph_cpu_temp),
        CheckedEnvTemperature=get_html_checkbox_state(app_cached_variables.quick_graph_env_temp),
        CheckedPressure=get_html_checkbox_state(app_cached_variables.quick_graph_pressure),
        CheckedAltitude=get_html_checkbox_state(app_cached_variables.quick_graph_altitude),
        CheckedHumidity=get_html_checkbox_state(app_cached_variables.quick_graph_humidity),
        CheckedDewPoint=get_html_checkbox_state(app_cached_variables.quick_graph_dew_point),
        CheckedDistance=get_html_checkbox_state(app_cached_variables.quick_graph_distance),
        CheckedGas=get_html_checkbox_state(app_cached_variables.quick_graph_gas),
        CheckedPM=get_html_checkbox_state(app_cached_variables.quick_graph_particulate_matter),
        CheckedLumen=get_html_checkbox_state(app_cached_variables.quick_graph_lumen),
        CheckedColour=get_html_checkbox_state(app_cached_variables.quick_graph_colours),
        CheckedUltraViolet=get_html_checkbox_state(app_cached_variables.quick_graph_ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(app_cached_variables.quick_graph_acc),
        CheckedMagnetometer=get_html_checkbox_state(app_cached_variables.quick_graph_mag),
        CheckedGyroscope=get_html_checkbox_state(app_cached_variables.quick_graph_gyro)
    )


@html_atpro_main_routes.route("/atpro/sensor-graphing-db")
def html_atpro_sensor_graphing_database():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"

    database_dropdown_selection_html = ""
    for db_name in app_cached_variables.uploaded_databases_list:
        database_dropdown_selection_html += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", db_name) + "\n"

    run_script = ""
    if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
        run_script = "CreatingGraph();"

    return render_template(
        "ATPro_admin/page_templates/graphing-database.html",
        RunScript=run_script,
        UploadedDBOptionNames=database_dropdown_selection_html,
        IntervalPlotlyDate=get_file_creation_date(file_locations.plotly_graph_interval),
        TriggerPlotlyDate=get_file_creation_date(file_locations.plotly_graph_triggers),
        MQTTPlotlyDate=get_file_creation_date(file_locations.plotly_graph_mqtt),
        CustomPlotlyDate=get_file_creation_date(file_locations.plotly_graph_custom),
        UTCOffset=app_config_access.primary_config.utc0_hour_offset
    )


@html_atpro_main_routes.route("/atpro/graphing-create-plotly", methods=["POST"])
@auth.login_required
def html_create_plotly_graph():
    if not server_plotly_graph_variables.graph_creation_in_progress:
        logger.network_logger.info("* Plotly Graph Initiated by " + str(request.remote_addr))
        invalid_msg1 = "Invalid Options Selection"
        try:
            new_graph_data = server_plotly_graph_variables.CreateGraphData()
            new_graph_data.graph_table = request.form.get("SQLRecordingType")
            new_graph_data.max_sql_queries = int(request.form.get("MaxSQLData"))

            db_location = request.form.get("SQLDatabaseSelection")
            if db_location == "MainDatabase":
                new_graph_data.db_location = file_locations.sensor_database
                new_graph_data.save_plotly_graph_to = file_locations.plotly_graph_interval
                if new_graph_data.graph_table == app_cached_variables.database_variables.table_trigger:
                    new_graph_data.save_plotly_graph_to = file_locations.plotly_graph_triggers
            elif db_location == "MQTTSubscriberDatabase":
                new_graph_data.db_location = file_locations.mqtt_subscriber_database
                new_graph_data.save_plotly_graph_to = file_locations.plotly_graph_mqtt
            else:
                new_graph_data.db_location = file_locations.uploaded_databases_folder + "/" + db_location
                new_graph_data.save_plotly_graph_to = file_locations.plotly_graph_custom

            if request.form.get("MQTTDatabaseCheck") is not None:
                remote_sensor_id = str(request.form.get("MQTTCustomBaseTopic")).strip()
                if remote_sensor_id.isalnum() and len(remote_sensor_id) < 65:
                    new_graph_data.graph_table = remote_sensor_id
                else:
                    msg2 = "Invalid Remote Sensor ID"
                    return get_message_page(invalid_msg1, msg2, page_url="sensor-graphing-db")

            if request.form.get("PlotlyRenderType") == "OpenGL":
                new_graph_data.enable_plotly_webgl = True
            else:
                new_graph_data.enable_plotly_webgl = False

            # The format the received datetime should look like "2019-01-01 00:00:00"
            new_graph_data.graph_start = request.form.get("graph_datetime_start").replace("T", " ") + ":00"
            new_graph_data.graph_end = request.form.get("graph_datetime_end").replace("T", " ") + ":00"
            new_graph_data.datetime_offset = float(request.form.get("HourOffset"))
            new_graph_data.sql_queries_skip = int(request.form.get("SkipSQL"))
            new_graph_data.graph_columns = server_plotly_graph.check_form_columns(request.form)

            if len(new_graph_data.graph_columns) < 4:
                msg2 = "Please Select at least One Sensor"
                return get_message_page(invalid_msg1, msg2, page_url="sensor-graphing-db")
            else:
                thread_function(server_plotly_graph.create_plotly_graph, args=new_graph_data)
        except Exception as error:
            logger.primary_logger.warning("Plotly Graph: " + str(error))
    return get_html_atpro_index(run_script="SelectNav('sensor-graphing-db');")


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
        MQTTSubDatabaseSize=sensor_access.get_file_size(file_locations.mqtt_subscriber_database),
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
                    if index == "DateTime":
                        pass
                    else:
                        sensor_data += "<span class='sensor-name'>" + index + ":</span> " + str(data) + "<br>"
            else:
                sensor_id = "NA"
                sensor_time = "NA"
                sensor_data = str(sub_entry)
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
