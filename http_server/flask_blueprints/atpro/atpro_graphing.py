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
from operations_modules.app_generic_functions import thread_function, get_file_content
from configuration_modules import app_config_access
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_file_creation_date
from http_server.server_http_auth import auth

html_atpro_graphing_routes = Blueprint("html_atpro_graphing_routes", __name__)
lgc = app_config_access.live_graphs_config
acv = app_cached_variables
db_gc = app_cached_variables.CreateNetworkGetCommands()
db_v = app_cached_variables.database_variables
http_base_html_files = file_locations.program_root_dir + "/http_server/templates/"
charts_templates_dir = http_base_html_files + "ATPro_admin/page_templates/graphs_live/"
live_chart_sensor_template = get_file_content(charts_templates_dir + "graphing-live-sensor-template.html")
live_chart_html_template = """
<div class="col-{{ MinColSize }} col-m-6 col-sm-12">
    <div class="card">
        <div class="card-content">
            <canvas id="{{ ChartName }}"></canvas>
        </div>
    </div>
</div>
"""

live_chart_js_configuration = """
let {{ ChartName }}ctx = document.getElementById('{{ ChartName }}').getContext('2d');
let {{ ChartName }} = new Chart({{ ChartName }}ctx,
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{{ ChartDataSets }}]
        },
        options: {
            plugins: {}
        }
    });
"""
live_chart_data_entry = """
{data: [],
label: "{{ ChartNameLabel }}",
pointRadius: 1,
borderWidth: 1,
borderColor: "{{ ChartColor }}",
backgroundColor: "#7bb6dd",
fill: false}
"""

live_chart_js_add_graph_data = """
function {{ ChartName }}StartGraphDataUpdateTimed() {
    window.setInterval({{ ChartName }}AddDataToGraph, {{ ChartUpdateInterval }});
}

async function {{ ChartName }}AddDataToGraph() {
    {{ AllFetchCommands }}
    {{ ChartName }}.data.labels.push(new Date().toLocaleTimeString());
    {{ ChartName }}.update();
}
{{ ChartName }}StartGraphDataUpdateTimed();
"""
live_chart_js_add_graph_data_fetch_entry = """
fetch("{{ SensorDataURL }}")
    .then(response => response.json())
    .then(data => {
        {{ ChartName }}.data.datasets[{{ DataSetNumber }}].data.push(data);
    })
"""


class CreateLiveGraphGenerator:
    def __init__(self, graph_options_list):
        self.chart_name = graph_options_list[0]
        self.chart_label_names_list = graph_options_list[1]
        self.chart_colors_list = graph_options_list[2]
        self.chart_http_commands_list = graph_options_list[3]
        self.chart_http_address = graph_options_list[4]
        self.chart_row_size = app_config_access.live_graphs_config.graphs_per_row

    def get_html_js_graph_code(self):
        try:
            return_code = self._get_html_chart_code() + "\n<script>\n" + self._get_chart_js_config()
            return_code += self._get_chart_js_functions() + "</script>\n\n"
            return return_code
        except Exception as error:
            logger.network_logger.error("Live Graph Generation: " + str(error))
        return "<p>Error Generating Graph</p>"

    def _get_html_chart_code(self):
        return_html_code = live_chart_html_template.replace("{{ MinColSize }}", str(self.chart_row_size))
        return_html_code = return_html_code.replace("{{ ChartName }}", self.chart_name)
        return return_html_code

    def _get_chart_js_config(self):
        return_chart_functions = live_chart_js_configuration.replace("{{ ChartName }}", self.chart_name)
        all_data_sets = ""
        for label_name, color in zip(self.chart_label_names_list, self.chart_colors_list):
            all_data_sets += live_chart_data_entry.replace("{{ ChartNameLabel }}", label_name)
            all_data_sets = all_data_sets.replace("{{ ChartColor }}", color)
            all_data_sets += ","
        return_chart_functions = return_chart_functions.replace("{{ ChartDataSets }}", all_data_sets[:-1])
        return return_chart_functions

    def _get_chart_js_functions(self):
        chart_interval = str(app_config_access.live_graphs_config.live_graph_update_interval * 1000)
        return_chart_functions = live_chart_js_add_graph_data.replace("{{ ChartName }}", self.chart_name)
        return_chart_functions = return_chart_functions.replace("{{ ChartUpdateInterval }}", chart_interval)

        chart_data_fetch_code = ""
        for index, command in enumerate(self.chart_http_commands_list):
            sensor_url_command = "/" + command
            if self.chart_http_address is not None:
                sensor_url_command = self.chart_http_address + command
            chart_data_fetch_code += live_chart_js_add_graph_data_fetch_entry.replace("{{ ChartName }}",
                                                                                      self.chart_name)
            chart_data_fetch_code = chart_data_fetch_code.replace("{{ SensorDataURL }}", sensor_url_command)
            chart_data_fetch_code = chart_data_fetch_code.replace("{{ DataSetNumber }}", str(index))
        return_chart_functions = return_chart_functions.replace("{{ AllFetchCommands }}", chart_data_fetch_code)
        return return_chart_functions


@html_atpro_graphing_routes.route("/atpro/sensor-graphing-live", methods=["GET", "POST"])
def html_atpro_sensor_graphing_live():
    if request.method == "POST":
        app_config_access.live_graphs_config.update_with_html_request(request)
        app_config_access.live_graphs_config.save_config_to_file()
        return get_html_atpro_index(run_script="SelectNav('sensor-graphing-live');")
    sensor_address = app_config_access.live_graphs_config.graph_sensor_address
    if sensor_address is None:
        sensor_address = ""
    return render_template(
        "ATPro_admin/page_templates/graphing-live.html",
        GraphSensorAddress=sensor_address,
        CheckedGPL1=app_config_access.live_graphs_config.get_checked_graph_per_line_state(1),
        CheckedGPL2=app_config_access.live_graphs_config.get_checked_graph_per_line_state(2),
        CheckedGPL3=app_config_access.live_graphs_config.get_checked_graph_per_line_state(3),
        CheckedGPL4=app_config_access.live_graphs_config.get_checked_graph_per_line_state(4),
        GraphIntervalValue=app_config_access.live_graphs_config.live_graph_update_interval,
        CheckedSensorUptime=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_uptime),
        CheckedCPUTemperature=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_cpu_temp),
        CheckedEnvTemperature=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_env_temp),
        CheckedPressure=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_pressure),
        CheckedAltitude=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_altitude),
        CheckedHumidity=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_humidity),
        CheckedDewPoint=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_dew_point),
        CheckedDistance=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_distance),
        CheckedGas=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_gas),
        CheckedPM=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_particulate_matter),
        CheckedLumen=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_lumen),
        CheckedColour=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_colours),
        CheckedUltraViolet=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_acc),
        CheckedMagnetometer=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_mag),
        CheckedGyroscope=get_html_checkbox_state(app_config_access.live_graphs_config.live_graph_gyro)
    )


@html_atpro_graphing_routes.route("/LiveGraphView")
def html_atpro_live_graphing():
    logger.network_logger.debug("* Live Graphs viewed by " + str(request.remote_addr))
    sensor_name = app_config_access.live_graphs_config.graph_sensor_address
    if sensor_name is None:
        sensor_name = "Local Sensor"
    return render_template("ATPro_admin/page_templates/graphs_live/graphing-live-view.html",
                           SensorName=sensor_name,
                           SensorChartCode=get_quick_graph_html_js_code())


def get_quick_graph_html_js_code():
    sensor_address = _get_formatted_sensor_address(lgc.graph_sensor_address)
    graphs_enabled_list = [
        lgc.live_graph_uptime, lgc.live_graph_cpu_temp, lgc.live_graph_env_temp, lgc.live_graph_pressure,
        lgc.live_graph_altitude, lgc.live_graph_humidity, lgc.live_graph_dew_point, lgc.live_graph_distance,
        lgc.live_graph_gas, lgc.live_graph_particulate_matter, lgc.live_graph_lumen, lgc.live_graph_colours,
        lgc.live_graph_ultra_violet, lgc.live_graph_acc, lgc.live_graph_mag, lgc.live_graph_gyro

    ]
    graph_creation_options_list = [
        [db_gc.system_uptime_minutes, ["Uptime Minutes"], ["red"], [db_gc.system_uptime_minutes], sensor_address],
        [db_gc.cpu_temp, ["CPU Temperature"], ["orange"], [db_gc.cpu_temp], sensor_address],
        [db_gc.environmental_temp, ["Env Temperature"], ["Green"], [db_gc.environmental_temp], sensor_address],
        [db_gc.pressure, ["Pressure"], ["grey"], [db_gc.pressure], sensor_address],
        [db_gc.altitude, ["Altitude"], ["grey"], [db_gc.altitude], sensor_address],
        [db_gc.humidity, ["Humidity"], ["grey"], [db_gc.humidity], sensor_address],
        [db_gc.dew_point, ["Dew Point"], ["blue"], [db_gc.dew_point], sensor_address],
        [db_gc.distance, ["Distance"], ["grey"], [db_gc.distance], sensor_address],

        [
            db_gc.all_gas,
            ["Resistance Index", "Oxidising", "Reducing", "NH3"],
            ["grey", "grey", "grey", "grey"],
            [db_gc.gas_resistance_index, db_gc.gas_oxidising, db_gc.gas_reducing, db_gc.gas_nh3],
            sensor_address
        ],
        [
            db_gc.all_particulate_matter,
            ["PM1", "PM2.5", "PM4", "PM10"],
            ["grey", "grey", "grey", "grey"],
            [
                db_gc.particulate_matter_1, db_gc.particulate_matter_2_5,
                db_gc.particulate_matter_4, db_gc.particulate_matter_10
            ],
            sensor_address
        ],
        [db_gc.lumen, ["Lumen"], ["yellow"], [db_gc.lumen], sensor_address],
        [
            db_gc.electromagnetic_spectrum,
            ["Red", "Orange", "Yellow", "Green", "Blue", "Violet"],
            ["red", "orange", "yellow", "green", "blue", "violet"],
            [db_gc.red, db_gc.orange, db_gc.yellow, db_gc.green, db_gc.blue, db_gc.violet],
            sensor_address
        ],
        [
            db_gc.all_ultra_violet,
            ["UV Index", "UV A", "UV B"],
            ["grey", "lightblue", "green"],
            [db_gc.ultra_violet_index, db_gc.ultra_violet_a, db_gc.ultra_violet_b],
            sensor_address
        ],
        [
            db_gc.accelerometer_xyz,
            ["Accelerometer X", "Accelerometer Y", "Accelerometer Z"],
            ["red", "orange", "green"],
            [db_gc.acc_x, db_gc.acc_y, db_gc.acc_z],
            sensor_address
        ],
        [
            db_gc.magnetometer_xyz,
            ["Magnetometer X", "Magnetometer Y", "Magnetometer Z"],
            ["red", "orange", "green"],
            [db_gc.mag_x, db_gc.mag_y, db_gc.mag_z],
            sensor_address
        ],
        [
            db_gc.gyroscope_xyz,
            ["Gyroscope X", "Gyroscope Y", "Gyroscope Z"],
            ["red", "orange", "green"],
            [db_gc.gyro_x, db_gc.gyro_y, db_gc.gyro_z],
            sensor_address
        ]
    ]

    all_graphs_final_code = ""
    for enabled, g_c_o in zip(graphs_enabled_list, graph_creation_options_list):
        if enabled:
            graph_creator = CreateLiveGraphGenerator(g_c_o)
            all_graphs_final_code += graph_creator.get_html_js_graph_code()
    return all_graphs_final_code


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


def _get_formatted_sensor_address(sensor_address):
    if sensor_address is None:
        return None
    new_sensor_address = sensor_address.lower().strip()
    if new_sensor_address[-1] == "/":
        new_sensor_address = new_sensor_address[:-1]
    if "http" not in new_sensor_address:
        new_sensor_address = "https://" + new_sensor_address
    if ":" not in sensor_address:
        new_sensor_address = new_sensor_address + ":10065"
    return new_sensor_address + "/"
