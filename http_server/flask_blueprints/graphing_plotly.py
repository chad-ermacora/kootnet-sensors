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
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return, get_html_hidden_state, get_html_checkbox_state
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables

html_plotly_graphing_routes = Blueprint("html_plotly_graphing_routes", __name__)


@html_plotly_graphing_routes.route("/Graphing")
def html_graphing():
    logger.network_logger.debug("* Graphing viewed by " + str(request.remote_addr))

    extra_message = ""
    button_disabled = ""
    if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
        extra_message = "Creating Graph - Please Wait"
        button_disabled = "disabled"

    try:
        unix_creation_date = os.path.getmtime(file_locations.plotly_graph_interval)
        interval_creation_date = str(datetime.fromtimestamp(unix_creation_date))[:-7]
    except FileNotFoundError:
        interval_creation_date = "No Plotly Graph Found"

    try:
        triggers_plotly_file_creation_date_unix = os.path.getmtime(file_locations.plotly_graph_triggers)
        triggers_creation_date = str(datetime.fromtimestamp(triggers_plotly_file_creation_date_unix))[:-7]
    except FileNotFoundError:
        triggers_creation_date = "No Plotly Graph Found"
    return render_template("graphing.html",
                           PageURL="/Graphing",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           ExtraTextMessage=extra_message,
                           CreateButtonDisabled=button_disabled,
                           IntervalPlotlyDate=interval_creation_date,
                           TriggerPlotlyDate=triggers_creation_date,
                           UTCOffset=app_config_access.primary_config.utc0_hour_offset,
                           SkipSQLEntries=app_cached_variables.quick_graph_skip_sql_entries,
                           MaxSQLEntries=app_cached_variables.quick_graph_max_sql_entries,
                           SensorUptimeChecked=get_html_checkbox_state(app_cached_variables.quick_graph_uptime),
                           CPUTemperatureChecked=get_html_checkbox_state(app_cached_variables.quick_graph_cpu_temp),
                           EnvTemperatureChecked=get_html_checkbox_state(app_cached_variables.quick_graph_env_temp),
                           PressureChecked=get_html_checkbox_state(app_cached_variables.quick_graph_pressure),
                           AltitudeChecked=get_html_checkbox_state(app_cached_variables.quick_graph_altitude),
                           HumidityChecked=get_html_checkbox_state(app_cached_variables.quick_graph_humidity),
                           DistanceChecked=get_html_checkbox_state(app_cached_variables.quick_graph_distance),
                           GasChecked=get_html_checkbox_state(app_cached_variables.quick_graph_gas),
                           PMChecked=get_html_checkbox_state(app_cached_variables.quick_graph_particulate_matter),
                           LumenChecked=get_html_checkbox_state(app_cached_variables.quick_graph_lumen),
                           ColoursChecked=get_html_checkbox_state(app_cached_variables.quick_graph_colours),
                           UltraVioletChecked=get_html_checkbox_state(app_cached_variables.quick_graph_ultra_violet),
                           AccChecked=get_html_checkbox_state(app_cached_variables.quick_graph_acc),
                           MagChecked=get_html_checkbox_state(app_cached_variables.quick_graph_mag),
                           GyroChecked=get_html_checkbox_state(app_cached_variables.quick_graph_gyro))


@html_plotly_graphing_routes.route("/CreatePlotlyGraph", methods=["POST"])
@auth.login_required
def html_create_plotly_graph():
    if not server_plotly_graph_variables.graph_creation_in_progress and \
            request.method == "POST" and "SQLRecordingType" in request.form:
        logger.network_logger.info("* Plotly Graph Initiated by " + str(request.remote_addr))
        try:
            new_graph_data = server_plotly_graph_variables.CreateGraphData()
            new_graph_data.graph_table = request.form.get("SQLRecordingType")

            if request.form.get("PlotlyRenderType") == "OpenGL":
                new_graph_data.enable_plotly_webgl = True
            else:
                new_graph_data.enable_plotly_webgl = False

            # The format the received datetime should look like "2019-01-01 00:00:00"
            new_graph_data.graph_start = request.form.get("graph_datetime_start").replace("T", " ") + ":00"
            new_graph_data.graph_end = request.form.get("graph_datetime_end").replace("T", " ") + ":00"
            new_graph_data.datetime_offset = request.form.get("HourOffset")
            new_graph_data.sql_queries_skip = int(request.form.get("SkipSQL").strip())
            new_graph_data.graph_columns = server_plotly_graph.check_form_columns(request.form)

            if len(new_graph_data.graph_columns) < 4:
                return message_and_return("Please Select at least One Sensor", url="/Graphing")
            else:
                app_generic_functions.thread_function(server_plotly_graph.create_plotly_graph, args=new_graph_data)
        except Exception as error:
            logger.primary_logger.warning("Plotly Graph: " + str(error))
    return html_graphing()


@html_plotly_graphing_routes.route("/ViewIntervalPlotlyGraph")
def html_view_interval_graph_plotly():
    logger.network_logger.info("* Interval Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_interval):
        return send_file(file_locations.plotly_graph_interval)
    else:
        message_title = "No Interval Plotly Graph Generated - Click to Close Tab"
        return message_and_return(message_title, special_command="JavaScript:window.close()", url="")


@html_plotly_graphing_routes.route("/ViewTriggerPlotlyGraph")
def html_view_triggers_graph_plotly():
    logger.network_logger.info("* Triggers Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_triggers):
        return send_file(file_locations.plotly_graph_triggers)
    else:
        message1 = "No Triggers Plotly Graph Generated - Click to Close Tab"
        special_command = "JavaScript:window.close()"
        return message_and_return(message1, special_command=special_command, url="")
