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
from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules.app_cached_variables import database_variables
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables
from http_server.flask_blueprints.graphing import html_graphing

html_plotly_graphing_routes = Blueprint("html_plotly_graphing_routes", __name__)


@html_plotly_graphing_routes.route("/CreatePlotlyGraph", methods=["POST"])
@auth.login_required
def html_create_plotly_graph():
    if not server_plotly_graph_variables.graph_creation_in_progress:
        logger.network_logger.info("* Plotly Graph Initiated by " + str(request.remote_addr))
        try:
            new_graph_data = server_plotly_graph_variables.CreateGraphData()
            new_graph_data.graph_table = request.form.get("SQLRecordingType")
            new_graph_data.max_sql_queries = int(request.form.get("MaxSQLData"))

            db_location = request.form.get("SQLDatabaseSelection")
            if db_location == "MainDatabase":
                new_graph_data.db_location = file_locations.sensor_database
                new_graph_data.save_plotly_graph_to = file_locations.plotly_graph_interval
                if new_graph_data.graph_table == database_variables.table_trigger:
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
                    return message_and_return("Invalid Remote Sensor ID", url="/Graphing")

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


@html_plotly_graphing_routes.route("/ViewMQTTPlotlyGraph")
def html_view_mqtt_graph_plotly():
    logger.network_logger.info("* MQTT Subscriber Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_mqtt):
        return send_file(file_locations.plotly_graph_mqtt)
    else:
        message1 = "No MQTT Plotly Graph Generated - Click to Close Tab"
        special_command = "JavaScript:window.close()"
        return message_and_return(message1, special_command=special_command, url="")


@html_plotly_graphing_routes.route("/ViewCustomPlotlyGraph")
def html_view_custom_graph_plotly():
    logger.network_logger.info("* Custom DB Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_graph_custom):
        return send_file(file_locations.plotly_graph_custom)
    else:
        message1 = "No Custom Database Graph Generated - Click to Close Tab"
        special_command = "JavaScript:window.close()"
        return message_and_return(message1, special_command=special_command, url="")
