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
from flask import render_template
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, adjust_datetime
from configuration_modules import app_config_access
from operations_modules.sqlite_database import sql_execute_get_data

db_v = app_cached_variables.database_variables


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
                    html_code += "<div><canvas id='" + str(sensor_db_name[1]) + "'></canvas></div>\n<br><hr><br>\n"
                    sensor_dates = get_graph_datetime_from_column(sensor_db_name[1])
                    c_first_date = datetime.strptime(sensor_dates[-1][0][:-4], "%Y-%m-%d %H:%M:%S")
                    c_first_date = c_first_date + timedelta(hours=utc0_hour_offset)
                    c_last_date = datetime.strptime(sensor_dates[0][0][:-4], "%Y-%m-%d %H:%M:%S")
                    c_last_date = c_last_date + timedelta(hours=utc0_hour_offset)
                    datetime_labels = _get_graph_db_date_times(sensor_db_name[1])

                    tmp_s_text = start_sensor_code.replace("{{ ChartName }}", str(sensor_db_name[1]))
                    tmp_s_text = tmp_s_text.replace("{{ LabelDataSet }}", str(datetime_labels))
                    tmp_s_text = tmp_s_text.replace("{{ MainDataSet }}", str(sensor_data))
                    tmp_s_text = tmp_s_text.replace("{{ BGColour }}", str(colour))
                    tmp_s_text = tmp_s_text.replace("{{ StartDate }}", c_first_date.strftime("%Y-%m-%d %H:%M:%S"))
                    tmp_s_text = tmp_s_text.replace("{{ EndDate }}", c_last_date.strftime("%Y-%m-%d %H:%M:%S"))
                    tmp_s_text = tmp_s_text.replace("{{ Measurement }}", str(sensor_measurement))

                    graph_javascript_code += tmp_s_text
        except Exception as error:
            logger.network_logger.warning("Live Graph - Error Adding Graph: " + str(error))
    if email_graph:
        program_dir = file_locations.program_root_dir
        qg_location = program_dir + "/http_server/templates/ATPro_admin/page_templates/graphing-live-view.html"
        quick_graph = get_file_content(qg_location)

        replacement_text = ["{{ SensorName }}", "{{ TotalSQLEntries }}", "{{ UTCOffset }}", "{{ GraphPastHours }}",
                            "{{ HoursDisplayedDisabled }}", "{{ GraphJSCode | safe }}", "{{ GraphHTMLCode | safe }}"]

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


def get_graph_data_from_column(sql_column, graph_table="IntervalData"):
    start_date = _get_graph_start_date()
    end_date = "9999-01-01 00:00:01"
    var_sql_query = "SELECT " + sql_column + \
                    " FROM " + graph_table + \
                    " WHERE " + sql_column + \
                    " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + \
                    "') AND datetime('" + end_date + \
                    "') AND ROWID % " + str(app_cached_variables.quick_graph_skip_sql_entries + 1) + " = 0" + \
                    " ORDER BY DateTime DESC LIMIT " + str(app_cached_variables.quick_graph_max_sql_entries)
    return sql_execute_get_data(var_sql_query)


def get_graph_datetime_from_column(sql_column, graph_table="IntervalData"):
    start_date = _get_graph_start_date()
    end_date = "9999-01-01 00:00:01"

    var_time_sql_query = "SELECT DateTime" + \
                         " FROM " + graph_table + \
                         " WHERE " + sql_column + \
                         " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + \
                         "') AND datetime('" + end_date + \
                         "') AND ROWID % " + str(app_cached_variables.quick_graph_skip_sql_entries + 1) + " = 0" + \
                         " ORDER BY DateTime DESC LIMIT " + str(app_cached_variables.quick_graph_max_sql_entries)
    return sql_execute_get_data(var_time_sql_query)


def _get_graph_start_date():
    hours_to_view = app_cached_variables.quick_graph_hours
    start_date = (datetime.utcnow() - timedelta(hours=hours_to_view)).strftime("%Y-%m-%d %H:%M:%S")
    return start_date


def _get_graph_db_data(database_column, get_len_only=False):
    if get_len_only:
        return len(get_graph_datetime_from_column(database_column))
    temp_data = get_graph_data_from_column(database_column)
    if len(temp_data) < 2:
        return False
    db_temp_data = ""
    for var_data in temp_data:
        db_temp_data += "'" + var_data[0] + "',"
    return db_temp_data[:-1]


def _get_graph_db_date_times(database_column):
    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    temp_dates = get_graph_datetime_from_column(database_column)
    db_temp_data = " "
    for var_datetime in temp_dates:
        db_temp_data += "'" + adjust_datetime(var_datetime[0], utc0_hour_offset) + "',"
    return db_temp_data[:-1]


start_sensor_code = """
var {{ ChartName }}ctx = document.getElementById('{{ ChartName }}');
var {{ ChartName }}Chart = new Chart({{ ChartName }}ctx, {
    type: 'line',
    data: {
        labels: [{{ LabelDataSet }}],
        datasets: [{
            label: '{{ ChartName }}',
            data: [ {{ MainDataSet }} ],
            backgroundColor: '{{ BGColour }}',
            borderColor: '{{ BGColour }}'
        }]
    },
    options: {
        spanGaps: true,
        animation: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: 'white',
                    font: {
                        size: 20, 
                        weight: 'bolder'
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                reverse: true,
                ticks: {
                    display: false
                },
                title: {
                    display: true,
                    color: 'white',
                    font: {
                        size: 20,
                        weight: 'bolder'
                    },
                    text: '{{ StartDate }} <--> {{ EndDate }}'
                }
            },
            y: {
                beginAtZero: false,
                ticks: {
                    color: 'white', 
                    font: {
                        size: 20
                    }
                },
                title: {
                    display: true,
                    color: 'white',
                    font: {
                        size: 20
                    },
                    text: '{{ Measurement }}'
                }
            }
        }
    }
});
"""
