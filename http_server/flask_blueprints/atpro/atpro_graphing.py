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
from operations_modules.app_generic_classes import CreateLiveGraphWrapperNetworkGetCommands
from operations_modules.app_generic_functions import thread_function
from configuration_modules import app_config_access
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_file_creation_date
from http_server.server_http_auth import auth

html_atpro_graphing_routes = Blueprint("html_atpro_graphing_routes", __name__)
lgc = app_config_access.live_graphs_config
db_gc = app_cached_variables.network_get_commands
db_wrapper_gc = CreateLiveGraphWrapperNetworkGetCommands()
live_chart_html_template = """
<div id="{{ ChartName }}container" class="col-{{ MinColSize }} col-m-6 col-sm-12">
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
        {{ ChartOptions }}
    });
"""
chart_options_standard = """
        options: {
            plugins: {}
        }
"""
chart_options_performance = """
        options: {
            animation: false,
            plugins: {}
        }
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
let {{ ChartName }}set_timeout_timer = 15000;
async function {{ ChartName }}AddDataToGraph() {
    let {{ ChartName }}update_okay = false;
    {{ AllFetchCommands }}
    if ({{ ChartName }}update_okay) {
        document.getElementById('{{ ChartName }}container').hidden = false;
        if ({{ ChartName }}.data.labels.length > {{ GraphMaxDataPoints }}) {
            {{ ChartName }}.data.labels.shift();
        }
        {{ ChartName }}.data.labels.push(new Date().toLocaleTimeString());
        {{ ChartName }}.update();
        setTimeout({{ ChartName }}AddDataToGraph, {{ ChartUpdateInterval }});
    } else {
        document.getElementById('{{ ChartName }}container').hidden = true;
        setTimeout({{ ChartName }}AddDataToGraph, {{ ChartName }}set_timeout_timer);
    }
}
{{ ChartName }}AddDataToGraph();
"""
live_chart_js_add_graph_data_fetch_entry = """
await fetch("{{ SensorDataURL }}")
    .then(response => {
        if (response.status === 404) {
            {{ ChartName }}set_timeout_timer = 600000;
            return "NoSensor";
        } else if (response.status === 503) {
            {{ ChartName }}set_timeout_timer = 10000;
            return "NoSensor";
        } else {
            if (!response.ok) {throw new Error('Network response was not OK');}
            return response.json();
        }
    })
    .then(data => {
        if (data !== "NoSensor") {
            {{ ChartName }}update_okay = true;
            if ({{ ChartName }}.data.datasets[{{ DataSetNumber }}].data.length > {{ GraphMaxDataPoints }}) {
                {{ ChartName }}.data.datasets[{{ DataSetNumber }}].data.shift();
            }
            {{ ChartName }}.data.datasets[{{ DataSetNumber }}].data.push(data);
        }
    })
    .catch(error => {});
"""


class CreateLiveGraphGenerator:
    def __init__(self, graph_options_list):
        self.chart_name = graph_options_list[0]
        self.chart_label_names_list = graph_options_list[1]
        self.chart_colors_list = graph_options_list[2]
        self.chart_http_commands_list = graph_options_list[3]
        self.chart_http_address = graph_options_list[4]
        self.chart_row_size = lgc.graphs_per_row

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
        if app_config_access.live_graphs_config.enable_performance_mode:
            return_chart_functions = return_chart_functions.replace("{{ ChartOptions }}", chart_options_performance)
        else:
            return_chart_functions = return_chart_functions.replace("{{ ChartOptions }}", chart_options_standard)
        return return_chart_functions

    def _get_chart_js_functions(self):
        chart_interval = str(lgc.live_graph_update_interval * 1000)
        max_dp = lgc.max_graph_data_points
        return_chart_functions = live_chart_js_add_graph_data.replace("{{ ChartName }}", self.chart_name)
        return_chart_functions = return_chart_functions.replace("{{ ChartUpdateInterval }}", chart_interval)

        chart_data_fetch_code = ""
        for index, command in enumerate(self.chart_http_commands_list):
            sensor_url_command = "/" + command
            if command[:3] != "LGW" and self.chart_http_address is not None:
                sensor_url_command = self.chart_http_address + command
            chart_data_fetch_code += live_chart_js_add_graph_data_fetch_entry.replace("{{ ChartName }}",
                                                                                      self.chart_name)
            chart_data_fetch_code = chart_data_fetch_code.replace("{{ SensorDataURL }}", sensor_url_command)
            chart_data_fetch_code = chart_data_fetch_code.replace("{{ DataSetNumber }}", str(index))
        return_chart_functions = return_chart_functions.replace("{{ AllFetchCommands }}", chart_data_fetch_code)
        return_chart_functions = return_chart_functions.replace("{{ GraphMaxDataPoints }}", str(max_dp))
        return return_chart_functions


@html_atpro_graphing_routes.route("/atpro/sensor-graphing-live", methods=["GET", "POST"])
def html_atpro_sensor_graphing_live():
    if request.method == "POST":
        lgc.update_with_html_request(request)
        lgc.save_config_to_file()
        return get_html_atpro_index(run_script="SelectNav('sensor-graphing-live');")
    sensor_address = lgc.graph_sensor_address
    if sensor_address is None:
        sensor_address = ""
    return render_template(
        "ATPro_admin/page_templates/graphing-live.html",
        GraphSensorAddress=sensor_address,
        CheckedEnableSSLVerification=get_html_checkbox_state(lgc.enable_ssl_verification),
        CheckedEnablePerformanceMode=get_html_checkbox_state(lgc.enable_performance_mode),
        CheckedGPL1=lgc.get_checked_graph_per_line_state(1),
        CheckedGPL2=lgc.get_checked_graph_per_line_state(2),
        CheckedGPL3=lgc.get_checked_graph_per_line_state(3),
        CheckedGPL4=lgc.get_checked_graph_per_line_state(4),
        GraphMaxDataPoints=lgc.max_graph_data_points,
        GraphIntervalValue=lgc.live_graph_update_interval,
        CheckedSensorUptime=get_html_checkbox_state(lgc.live_graph_uptime),
        CheckedCPUTemperature=get_html_checkbox_state(lgc.live_graph_cpu_temp),
        CheckedEnvTemperature=get_html_checkbox_state(lgc.live_graph_env_temp),
        CheckedPressure=get_html_checkbox_state(lgc.live_graph_pressure),
        CheckedAltitude=get_html_checkbox_state(lgc.live_graph_altitude),
        CheckedHumidity=get_html_checkbox_state(lgc.live_graph_humidity),
        CheckedDewPoint=get_html_checkbox_state(lgc.live_graph_dew_point),
        CheckedDistance=get_html_checkbox_state(lgc.live_graph_distance),
        CheckedGas=get_html_checkbox_state(lgc.live_graph_gas),
        CheckedPM=get_html_checkbox_state(lgc.live_graph_particulate_matter),
        CheckedLumen=get_html_checkbox_state(lgc.live_graph_lumen),
        CheckedColour=get_html_checkbox_state(lgc.live_graph_colours),
        CheckedUltraViolet=get_html_checkbox_state(lgc.live_graph_ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(lgc.live_graph_acc),
        CheckedMagnetometer=get_html_checkbox_state(lgc.live_graph_mag),
        CheckedGyroscope=get_html_checkbox_state(lgc.live_graph_gyro)
    )


@html_atpro_graphing_routes.route("/LiveGraphView")
def html_atpro_live_graphing():
    logger.network_logger.debug("* Live Graphs viewed by " + str(request.remote_addr))
    graph_sensor_address = lgc.graph_sensor_address
    formatted_graph_sensor_address = _get_formatted_sensor_address(graph_sensor_address)
    if formatted_graph_sensor_address is None:
        formatted_graph_sensor_address = "/"
    if graph_sensor_address is None:
        graph_sensor_address = app_cached_variables.ip
    sensor_hostname_command = formatted_graph_sensor_address + db_gc.sensor_name
    sensor_version_command = formatted_graph_sensor_address + db_gc.program_version
    if lgc.graph_sensor_address is not None and not app_config_access.live_graphs_config.enable_ssl_verification:
        sensor_hostname_command = "/" + db_wrapper_gc.sensor_name
        sensor_version_command = "/" + db_wrapper_gc.program_version
    return render_template("ATPro_admin/page_templates/graphs_live/graphing-live-view.html",
                           SensorAddress=graph_sensor_address,
                           SensorNameFetchURL=sensor_hostname_command,
                           SensorVersionFetchURL=sensor_version_command,
                           SensorChartCode=get_quick_graph_html_js_code())


def get_quick_graph_html_js_code():
    sensor_address = _get_formatted_sensor_address(lgc.graph_sensor_address)
    graphs_enabled_list = [
        lgc.live_graph_uptime, lgc.live_graph_cpu_temp, lgc.live_graph_env_temp, lgc.live_graph_pressure,
        lgc.live_graph_altitude, lgc.live_graph_humidity, lgc.live_graph_dew_point, lgc.live_graph_distance,
        lgc.live_graph_gas, lgc.live_graph_particulate_matter, lgc.live_graph_lumen, lgc.live_graph_colours,
        lgc.live_graph_ultra_violet, lgc.live_graph_acc, lgc.live_graph_mag, lgc.live_graph_gyro

    ]
    get_commands = db_gc
    if lgc.graph_sensor_address is not None and not lgc.enable_ssl_verification:
        get_commands = db_wrapper_gc
    graph_creation_options_list = [
        [get_commands.system_uptime_minutes, ["Uptime Minutes"], ["red"], [get_commands.system_uptime_minutes],
         sensor_address],
        [get_commands.cpu_temp, ["CPU Temperature"], ["orange"], [get_commands.cpu_temp],
         sensor_address],
        [get_commands.environmental_temp, ["Env Temperature"], ["Green"], [get_commands.environmental_temp],
         sensor_address],
        [get_commands.pressure, ["Pressure"], ["grey"], [get_commands.pressure],
         sensor_address],
        [get_commands.altitude, ["Altitude"], ["grey"], [get_commands.altitude],
         sensor_address],
        [get_commands.humidity, ["Humidity"], ["grey"], [get_commands.humidity],
         sensor_address],
        [get_commands.dew_point, ["Dew Point"], ["blue"], [get_commands.dew_point],
         sensor_address],
        [get_commands.distance, ["Distance"], ["grey"], [get_commands.distance],
         sensor_address],

        [
            get_commands.all_gas,
            ["Resistance Index", "Oxidising", "Reducing", "NH3"],
            ["grey", "grey", "grey", "grey"],
            [get_commands.gas_resistance_index, get_commands.gas_oxidising,
             get_commands.gas_reducing, get_commands.gas_nh3],
            sensor_address
        ],
        [
            get_commands.all_particulate_matter,
            ["PM1", "PM2.5", "PM4", "PM10"],
            ["grey", "grey", "grey", "grey"],
            [
                get_commands.particulate_matter_1, get_commands.particulate_matter_2_5,
                get_commands.particulate_matter_4, get_commands.particulate_matter_10
            ],
            sensor_address
        ],
        [get_commands.lumen, ["Lumen"], ["yellow"], [get_commands.lumen], sensor_address],
        [
            get_commands.electromagnetic_spectrum,
            ["Red", "Orange", "Yellow", "Green", "Blue", "Violet"],
            ["red", "orange", "yellow", "green", "blue", "violet"],
            [get_commands.red, get_commands.orange, get_commands.yellow,
             get_commands.green, get_commands.blue, get_commands.violet],
            sensor_address
        ],
        [
            get_commands.all_ultra_violet,
            ["UV Index", "UV A", "UV B"],
            ["grey", "lightblue", "green"],
            [get_commands.ultra_violet_index, get_commands.ultra_violet_a, get_commands.ultra_violet_b],
            sensor_address
        ],
        [
            get_commands.accelerometer_xyz,
            ["Accelerometer X", "Accelerometer Y", "Accelerometer Z"],
            ["red", "orange", "green"],
            [get_commands.acc_x, get_commands.acc_y, get_commands.acc_z],
            sensor_address
        ],
        [
            get_commands.magnetometer_xyz,
            ["Magnetometer X", "Magnetometer Y", "Magnetometer Z"],
            ["red", "orange", "green"],
            [get_commands.mag_x, get_commands.mag_y, get_commands.mag_z],
            sensor_address
        ],
        [
            get_commands.gyroscope_xyz,
            ["Gyroscope X", "Gyroscope Y", "Gyroscope Z"],
            ["red", "orange", "green"],
            [get_commands.gyro_x, get_commands.gyro_y, get_commands.gyro_z],
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
        CheckedMQTTDatabase=get_html_checkbox_state(app_config_access.db_graphs_config.mqtt_database_checked),
        MQTTSenorID=app_config_access.db_graphs_config.mqtt_database_topic,
        IntervalPlotlyDate=get_file_creation_date(file_locations.plotly_graph_interval),
        TriggerPlotlyDate=get_file_creation_date(file_locations.plotly_graph_triggers),
        MQTTPlotlyDate=get_file_creation_date(file_locations.plotly_graph_mqtt),
        CustomPlotlyDate=get_file_creation_date(file_locations.plotly_graph_custom),
        MaxDataPoints=app_config_access.db_graphs_config.max_graph_data_points,
        SkipDataPoints=app_config_access.db_graphs_config.skip_data_between_plots,
        DateTimeStart=app_config_access.db_graphs_config.graph_start_date.replace(" ", "T")[:-3],
        DateTimeEnd=app_config_access.db_graphs_config.graph_end_date.replace(" ", "T")[:-3],
        UTCOffset=app_config_access.db_graphs_config.date_time_hours_offset,
        CheckedSensorUptime=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_uptime),
        CheckedCPUTemperature=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_cpu_temp),
        CheckedEnvTemperature=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_env_temp),
        CheckedPressure=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_pressure),
        CheckedAltitude=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_altitude),
        CheckedHumidity=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_humidity),
        CheckedDewPoint=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_dew_point),
        CheckedDistance=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_distance),
        CheckedGas=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_gas),
        CheckedPM=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_particulate_matter),
        CheckedLumen=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_lumen),
        CheckedColour=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_colours),
        CheckedUltraViolet=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_acc),
        CheckedMagnetometer=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_mag),
        CheckedGyroscope=get_html_checkbox_state(app_config_access.db_graphs_config.db_graph_gyro)
    )


@html_atpro_graphing_routes.route("/atpro/graphing-create-plotly", methods=["POST"])
@auth.login_required
def html_create_plotly_graph():
    generate_plotly_graph(request)
    return get_html_atpro_index(run_script="SelectNav('sensor-graphing-db');")


def generate_plotly_graph(graph_request, graph_config=None):
    create_graph = True
    if graph_config is None:
        create_graph = False
        if graph_request.form.get("button_function") == "update":
            logger.network_logger.info("* Plotly Graph Config Update Initiated by " + str(request.remote_addr))
            app_config_access.db_graphs_config.update_with_html_request(graph_request)
            app_config_access.db_graphs_config.save_config_to_file()
        elif graph_request.form.get("button_function") == "email":
            logger.network_logger.info("* Plotly Graph Email Config Update Initiated by " + str(request.remote_addr))
            app_config_access.email_db_graph_config.update_with_html_request(graph_request)
            app_config_access.email_db_graph_config.save_config_to_file()
        elif graph_request.form.get("button_function") == "create":
            logger.network_logger.debug("* Plotly Graph Create Initiated by " + str(request.remote_addr))
            app_config_access.db_graphs_config.update_with_html_request(graph_request)
            graph_config = app_config_access.db_graphs_config
            create_graph = True

    if create_graph and not server_plotly_graph_variables.graph_creation_in_progress:
        logger.network_logger.info("Plotly Graph Generation Started")
        invalid_msg1 = "Invalid Options Selection"
        try:
            new_graph_data = server_plotly_graph_variables.CreateGraphData()
            new_graph_data.graph_table = graph_config.sql_recording_type
            if graph_config.mqtt_database_checked:
                new_graph_data.graph_table = graph_config.mqtt_database_topic
            new_graph_data.max_sql_queries = graph_config.max_graph_data_points

            db_location = graph_config.sql_database_selection
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

            if graph_config.mqtt_database_checked:
                remote_sensor_id = graph_config.mqtt_database_topic
                if remote_sensor_id.isalnum() and len(remote_sensor_id) < 65:
                    new_graph_data.graph_table = remote_sensor_id
                else:
                    msg2 = "Invalid Remote Sensor ID"
                    return get_message_page(invalid_msg1, msg2, page_url="sensor-graphing-db")

            if graph_config.render_engine == "OpenGL":
                new_graph_data.enable_plotly_webgl = True
            else:
                new_graph_data.enable_plotly_webgl = False

            # The format the received datetime should look like "2019-01-01 00:00:00"
            new_graph_data.graph_start = graph_config.graph_start_date
            new_graph_data.graph_end = graph_config.graph_end_date
            new_graph_data.datetime_offset = graph_config.date_time_hours_offset
            new_graph_data.sql_queries_skip = graph_config.skip_data_between_plots
            new_graph_data.graph_columns = graph_config.get_enabled_graph_sensors_list()

            if len(new_graph_data.graph_columns) < 4:
                msg2 = "Please Select at least One Sensor"
                return get_message_page(invalid_msg1, msg2, page_url="sensor-graphing-db")
            else:
                thread_function(server_plotly_graph.create_plotly_graph, args=new_graph_data)
        except Exception as error:
            logger.primary_logger.warning("Plotly Graph: " + str(error))


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
