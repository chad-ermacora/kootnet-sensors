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
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function
from configuration_modules import app_config_access
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables
from http_server.flask_blueprints.graphing_quick import html_live_graphing
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_file_creation_date
from http_server.server_http_auth import auth

html_atpro_graphing_routes = Blueprint("html_atpro_graphing_routes", __name__)


@html_atpro_graphing_routes.route("/atpro/sensor-graphing-live", methods=["GET", "POST"])
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


@html_atpro_graphing_routes.route("/LiveGraphView", methods=["GET", "POST"])
def html_atpro_live_graphing():
    logger.network_logger.debug("* Live Graphs viewed by " + str(request.remote_addr))
    return html_live_graphing(request)


@html_atpro_graphing_routes.route("/atpro/sensor-graphing-db")
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


@html_atpro_graphing_routes.route("/atpro/graphing-create-plotly", methods=["POST"])
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


@html_atpro_graphing_routes.route("/ViewIntervalPlotlyGraph")
def html_view_interval_graph_plotly():
    logger.network_logger.info("* Interval Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_interval):
        return send_file(file_locations.plotly_graph_interval)
    return "No Interval Plotly Graph Generated"


@html_atpro_graphing_routes.route("/ViewTriggerPlotlyGraph")
def html_view_triggers_graph_plotly():
    logger.network_logger.info("* Triggers Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_triggers):
        return send_file(file_locations.plotly_graph_triggers)
    return "No Triggers Plotly Graph Generated"


@html_atpro_graphing_routes.route("/ViewMQTTPlotlyGraph")
def html_view_mqtt_graph_plotly():
    logger.network_logger.info("* MQTT Subscriber Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_mqtt):
        return send_file(file_locations.plotly_graph_mqtt)
    return "No MQTT Plotly Graph Generated"


@html_atpro_graphing_routes.route("/ViewCustomPlotlyGraph")
def html_view_custom_graph_plotly():
    logger.network_logger.info("* Custom DB Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_custom):
        return send_file(file_locations.plotly_graph_custom)
    return "No Custom Database Graph Generated"
