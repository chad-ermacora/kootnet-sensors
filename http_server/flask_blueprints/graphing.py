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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from http_server.server_http_generic_functions import get_html_hidden_state, get_html_checkbox_state
from http_server import server_plotly_graph

html_graphing_routes = Blueprint("html_graphing_routes", __name__)


@html_graphing_routes.route("/Graphing")
def html_graphing():
    logger.network_logger.debug("* Graphing viewed by " + str(request.remote_addr))
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"

    database_dropdown_selection_html = ""
    for db_name in app_cached_variables.uploaded_databases_list:
        database_dropdown_selection_html += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", db_name) + "\n"

    extra_message = ""
    button_disabled = ""
    if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
        extra_message = "Creating Graph - Please Wait"
        button_disabled = "disabled"
    return render_template("graphing.html",
                           PageURL="/Graphing",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           ExtraTextMessage=extra_message,
                           UploadedDBOptionNames=database_dropdown_selection_html,
                           CreateButtonDisabled=button_disabled,
                           IntervalPlotlyDate=_get_plotly_creation_date(file_locations.plotly_graph_interval),
                           TriggerPlotlyDate=_get_plotly_creation_date(file_locations.plotly_graph_triggers),
                           MQTTPlotlyDate=_get_plotly_creation_date(file_locations.plotly_graph_mqtt),
                           CustomPlotlyDate=_get_plotly_creation_date(file_locations.plotly_graph_custom),
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


def _get_plotly_creation_date(file_location):
    try:
        plotly_file_creation_date_unix = os.path.getmtime(file_location)
        creation_date = str(datetime.fromtimestamp(plotly_file_creation_date_unix))[:-7]
    except FileNotFoundError:
        creation_date = "No Plotly Graph Found"
    return creation_date
