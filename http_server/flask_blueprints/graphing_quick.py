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
from datetime import datetime, timedelta
from flask import render_template, Blueprint, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, adjust_datetime
from configuration_modules import app_config_access
from operations_modules.sqlite_database import sql_execute_get_data
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_html_atpro_index

html_quick_graphing_routes = Blueprint("html_quick_graphing_routes", __name__)
db_v = app_cached_variables.database_variables


@html_quick_graphing_routes.route("/LiveGraphView", methods=["GET", "POST"])
def html_live_graphing():
    logger.network_logger.debug("* Live Graphs viewed by " + str(request.remote_addr))
    if request.method == "POST":
        if request.form.get("graph_hours") is not None:
            app_cached_variables.quick_graph_hours = float(request.form.get("graph_hours"))
            return get_html_live_graphing_page()
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
    return get_html_live_graphing_page()


def get_html_live_graphing_page(email_graph=False):
    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    graph_past_hours = app_cached_variables.quick_graph_hours

    if email_graph:
        graph_past_hours = app_config_access.email_config.graph_past_hours
        app_cached_variables.quick_graph_hours = graph_past_hours
        app_cached_variables.quick_graph_uptime = app_config_access.email_config.sensor_uptime
        app_cached_variables.quick_graph_cpu_temp = app_config_access.email_config.system_temperature
        app_cached_variables.quick_graph_env_temp = app_config_access.email_config.env_temperature
        app_cached_variables.quick_graph_pressure = app_config_access.email_config.pressure
        app_cached_variables.quick_graph_altitude = app_config_access.email_config.altitude
        app_cached_variables.quick_graph_humidity = app_config_access.email_config.humidity
        app_cached_variables.quick_graph_distance = app_config_access.email_config.distance
        app_cached_variables.quick_graph_gas = app_config_access.email_config.gas
        app_cached_variables.quick_graph_particulate_matter = app_config_access.email_config.particulate_matter
        app_cached_variables.quick_graph_lumen = app_config_access.email_config.lumen
        app_cached_variables.quick_graph_colours = app_config_access.email_config.color
        app_cached_variables.quick_graph_ultra_violet = app_config_access.email_config.ultra_violet
        app_cached_variables.quick_graph_acc = app_config_access.email_config.accelerometer
        app_cached_variables.quick_graph_mag = app_config_access.email_config.magnetometer
        app_cached_variables.quick_graph_gyro = app_config_access.email_config.gyroscope

    sensors_list = [
        [app_cached_variables.quick_graph_uptime, db_v.sensor_uptime],
        [app_cached_variables.quick_graph_cpu_temp, db_v.system_temperature],
        [app_cached_variables.quick_graph_env_temp, db_v.env_temperature],
        [app_cached_variables.quick_graph_pressure, db_v.pressure],
        [app_cached_variables.quick_graph_altitude, db_v.altitude],
        [app_cached_variables.quick_graph_humidity, db_v.humidity],
        [app_cached_variables.quick_graph_distance, db_v.distance],
        [app_cached_variables.quick_graph_gas, db_v.gas_resistance_index],
        [app_cached_variables.quick_graph_gas, db_v.gas_oxidising],
        [app_cached_variables.quick_graph_gas, db_v.gas_reducing],
        [app_cached_variables.quick_graph_gas, db_v.gas_nh3],
        [app_cached_variables.quick_graph_particulate_matter, db_v.particulate_matter_1],
        [app_cached_variables.quick_graph_particulate_matter, db_v.particulate_matter_2_5],
        [app_cached_variables.quick_graph_particulate_matter, db_v.particulate_matter_4],
        [app_cached_variables.quick_graph_particulate_matter, db_v.particulate_matter_10],
        [app_cached_variables.quick_graph_lumen, db_v.lumen],
        [app_cached_variables.quick_graph_colours, db_v.red],
        [app_cached_variables.quick_graph_colours, db_v.orange],
        [app_cached_variables.quick_graph_colours, db_v.yellow],
        [app_cached_variables.quick_graph_colours, db_v.green],
        [app_cached_variables.quick_graph_colours, db_v.blue],
        [app_cached_variables.quick_graph_colours, db_v.violet],
        [app_cached_variables.quick_graph_ultra_violet, db_v.ultra_violet_index],
        [app_cached_variables.quick_graph_ultra_violet, db_v.ultra_violet_a],
        [app_cached_variables.quick_graph_ultra_violet, db_v.ultra_violet_b],
        [app_cached_variables.quick_graph_acc, db_v.acc_x],
        [app_cached_variables.quick_graph_acc, db_v.acc_y],
        [app_cached_variables.quick_graph_acc, db_v.acc_z],
        [app_cached_variables.quick_graph_mag, db_v.mag_x],
        [app_cached_variables.quick_graph_mag, db_v.mag_y],
        [app_cached_variables.quick_graph_mag, db_v.mag_z],
        [app_cached_variables.quick_graph_gyro, db_v.gyro_x],
        [app_cached_variables.quick_graph_gyro, db_v.gyro_y],
        [app_cached_variables.quick_graph_gyro, db_v.gyro_z]
    ]
    measurements_list = [
        "Minutes", "°C", "°C", "hPa", "Meters", "%RH", "?", "kΩ", "kΩ", "kΩ", "kΩ", "PM 1.0", "PM 2.5", "PM 4", "PM 10",
        "lm", "", "", "", "", "", "", "", "", "", "g", "g", "g", "μT", "μT", "μT", "°/s", "°/s", "°/s"
    ]

    colour_list = [
        "grey", "red", "green", "blue", "blue", "blue", "grey", "grey", "grey", "grey", "grey",
        "grey", "grey", "grey", "grey", "yellow", "red", "orange", "yellow", "green", "blue", "violet",
        "violet", "violet", "violet", "grey", "grey", "grey", "grey", "grey", "grey", "grey", "grey", "grey"
    ]

    graph_javascript_code = ""
    html_code = ""
    total_data_points = _get_graph_db_data(db_v.all_tables_datetime, get_len_only=True)
    for sensor_db_name, sensor_measurement, colour in zip(sensors_list, measurements_list, colour_list):
        try:
            if sensor_db_name[0]:
                sensor_data = _get_graph_db_data(sensor_db_name[1])
                if sensor_data is not False:
                    html_code += "<div style='height: 300px'><canvas id='" + sensor_db_name[
                        1] + """'></canvas></div>\n"""
                    tmp_starter = start_sensor_code.replace("{{ ChartName }}", sensor_db_name[1])

                    sensor_dates = get_graph_datetime_from_column(sensor_db_name[1])

                    clean_first_checkin_date = datetime.strptime(sensor_dates[-1][0][:-4], "%Y-%m-%d %H:%M:%S")
                    clean_first_checkin_date = clean_first_checkin_date + timedelta(hours=utc0_hour_offset)
                    clean_last_checkin_date = datetime.strptime(sensor_dates[0][0][:-4], "%Y-%m-%d %H:%M:%S")
                    clean_last_checkin_date = clean_last_checkin_date + timedelta(hours=utc0_hour_offset)

                    tmp_starter = tmp_starter.replace("{{ StartDate }}",
                                                      clean_first_checkin_date.strftime("%Y-%m-%d %H:%M:%S"))
                    tmp_starter = tmp_starter.replace("{{ EndDate }}",
                                                      clean_last_checkin_date.strftime("%Y-%m-%d %H:%M:%S"))
                    tmp_starter = tmp_starter.replace("{{ UTCOffset }}", str(utc0_hour_offset))

                    replacement_code = _add_single_sensor(sensor_db_name[1], sensor_data, colour)
                    graph_javascript_code += tmp_starter.replace("{{ MainDataSet }}", replacement_code) + "\n"
                    graph_javascript_code = graph_javascript_code.replace("{{ Measurement }}", sensor_measurement)
        except Exception as error:
            logger.network_logger.warning("Live Graph - Error Adding Graph: " + str(error))
    if email_graph:
        quick_graph = get_file_content(file_locations.program_root_dir + "/http_server/templates/graphing_quick.html")

        replacement_text = ["{{ SensorName }}", "{{ TotalSQLEntries }}", "{{ UTCOffset }}", "{{ GraphPastHours }}",
                            "{{ HoursDisplayedDisabled }}", "{{ GraphJSCode |safe }}", "{{ GraphHTMLCode |safe }}"]

        new_values = [app_cached_variables.hostname, total_data_points, utc0_hour_offset,
                      graph_past_hours, "disabled", graph_javascript_code, html_code]

        for replace_name, content in zip(replacement_text, new_values):
            quick_graph = quick_graph.replace(replace_name, str(content))
        return quick_graph
    return render_template("ATPro_admin/page_templates/graphing-live-view.html",
                           SensorName=app_cached_variables.hostname,
                           TotalSQLEntries=total_data_points,
                           UTCOffset=utc0_hour_offset,
                           GraphPastHours=graph_past_hours,
                           HoursDisplayedDisabled="",
                           GraphJSCode=graph_javascript_code,
                           GraphHTMLCode=html_code)


def _add_single_sensor(sensor_db_name, sensor_data, colour="red"):
    return_text = "{ label: '" + sensor_db_name + "', " + "borderColor: '" + colour + \
                  "', fill: false, data: [" + sensor_data + "] }"
    return return_text


def get_graph_data_from_column(sql_column, graph_table="IntervalData",
                               start_date="1111-08-21 00:00:01", end_date="9999-01-01 00:00:01"):
    var_sql_query = "SELECT " + sql_column + \
                    " FROM " + graph_table + \
                    " WHERE " + sql_column + \
                    " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + \
                    "') AND datetime('" + end_date + \
                    "') AND ROWID % " + str(app_cached_variables.quick_graph_skip_sql_entries + 1) + " = 0" + \
                    " ORDER BY DateTime DESC LIMIT " + str(app_cached_variables.quick_graph_max_sql_entries)
    return sql_execute_get_data(var_sql_query)


def get_graph_datetime_from_column(sql_column, graph_table="IntervalData",
                                   start_date="1111-08-21 00:00:01",
                                   end_date="9999-01-01 00:00:01"):
    var_time_sql_query = "SELECT DateTime" + \
                         " FROM " + graph_table + \
                         " WHERE " + sql_column + \
                         " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + \
                         "') AND datetime('" + end_date + \
                         "') AND ROWID % " + str(app_cached_variables.quick_graph_skip_sql_entries + 1) + " = 0" + \
                         " ORDER BY DateTime DESC LIMIT " + str(app_cached_variables.quick_graph_max_sql_entries)
    return sql_execute_get_data(var_time_sql_query)


def _get_graph_db_data(database_column, get_len_only=False):
    hours_to_view = app_cached_variables.quick_graph_hours
    start_date = (datetime.utcnow() - timedelta(hours=hours_to_view)).strftime("%Y-%m-%d %H:%M:%S")
    if get_len_only:
        return len(get_graph_datetime_from_column(database_column, start_date=start_date))
    temp_data = get_graph_data_from_column(database_column, start_date=start_date)
    temp_dates = get_graph_datetime_from_column(database_column, start_date=start_date)
    if len(temp_data) < 2:
        return False
    db_temp_data = " "
    for var_datetime, var_data in zip(temp_dates, temp_data):
        replacement_dates = adjust_datetime(var_datetime[0], app_config_access.primary_config.utc0_hour_offset)
        db_temp_data += "{ x: '" + replacement_dates + "', y: " + var_data[0] + " },"
    return db_temp_data[:-1]


start_sensor_code = """
new Chart(document.getElementById('{{ ChartName }}').getContext('2d'),
    { 
        type: 'line',
        data: {
            datasets: [ {{ MainDataSet }} ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            title: {
                display: true,
                text: '{{ StartDate }} <--> {{ EndDate }}'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    type: 'time',
                    distribution: 'linear',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'MMM DD HH:mm:ss UTC{{ UTCOffset }}',
                        displayFormats: {
                            day: 'MMM D hh:mm'
                        }
                    }
                }],
                yAxes: [{
                    display: true,
                    ticks: {
                        beginAtZero: false
                    },
                    scaleLabel: {
                        display: true,
                        labelString: ' {{ Measurement }}'
                    }
                }]
            }

        }
    }
);
"""
