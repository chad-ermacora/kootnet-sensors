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
from operations_modules import logger
from operations_modules.app_cached_variables import database_variables
from http_server import server_plotly_graph_variables
try:
    from plotly import graph_objs as go
except ImportError as import_error:
    logger.primary_logger.warning("Plotly Graph Import Failed: " + str(import_error))
    go = None


class CreateGraphScatterData:
    def __init__(self, webgl, sql_table, set_marker):
        self.enable_plotly_webgl = webgl
        self.text_graph_table = sql_table
        self.text_sensor_name = ""

        self.sql_time_list = []
        self.sql_data_list = []

        self.set_marker = set_marker


def add_plots(graph_data):
    if graph_data.graph_table == database_variables.table_interval:
        set_marker = server_plotly_graph_variables.mark_generic_line
    else:
        set_marker = server_plotly_graph_variables.mark_generic_dot
    scatter_data = CreateGraphScatterData(graph_data.enable_plotly_webgl, graph_data.graph_table, set_marker)

    if len(graph_data.sql_host_name) > 1:
        subplot_sensor_name = "Sensor Names over Time - First Name: " + str(graph_data.sql_host_name[0]) + \
                              " <---> Last Name: " + str(graph_data.sql_host_name[-1])

        put_sensor_trace(graph_data, scatter_data, "Sensor Name", graph_data.sql_host_name_date_time,
                         graph_data.sql_host_name, subplot_sensor_name)
    if len(graph_data.sql_up_time) > 1:
        name_and_subplot = "Sensor Uptime in Minutes"
        put_sensor_trace(graph_data, scatter_data, name_and_subplot, graph_data.sql_up_time_date_time,
                         graph_data.sql_up_time, name_and_subplot)

    if len(graph_data.sql_cpu_temp) > 1 or len(graph_data.sql_hat_temp) > 1:
        name_and_subplot = "Temperature in °C (Celsius)"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_dot
        put_sensor_trace(graph_data, scatter_data, "CPU", graph_data.sql_cpu_temp_date_time,
                         graph_data.sql_cpu_temp, name_and_subplot)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_dot
        put_sensor_trace(graph_data, scatter_data, "Environmental", graph_data.sql_hat_temp_date_time,
                         graph_data.sql_hat_temp, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_pressure) > 2:
        name_and_subplot = "Pressure in hPa (Hectopascals)"
        put_sensor_trace(graph_data, scatter_data, "Pressure", graph_data.sql_pressure_date_time,
                         graph_data.sql_pressure, name_and_subplot)

    if len(graph_data.sql_altitude) > 2:
        name_and_subplot = "Altitude in m (Meters)"
        put_sensor_trace(graph_data, scatter_data, "Altitude", graph_data.sql_altitude_date_time,
                         graph_data.sql_altitude, name_and_subplot)

    if len(graph_data.sql_humidity) > 2:
        put_sensor_trace(graph_data, scatter_data, "Humidity", graph_data.sql_humidity_date_time,
                         graph_data.sql_humidity, "% Relative Humidity")

    if len(graph_data.sql_distance) > 2:
        name_and_subplot = "Distance in Meters?"
        put_sensor_trace(graph_data, scatter_data, "Distance", graph_data.sql_distance_date_time,
                         graph_data.sql_distance, name_and_subplot)

    if len(graph_data.sql_gas_resistance) > 2 or len(graph_data.sql_gas_oxidising) > 2 \
            or len(graph_data.sql_gas_reducing) > 2 or len(graph_data.sql_gas_nh3) > 2:
        name_and_subplot = "Gas Resistance in Ω (ohms)"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_dot
        put_sensor_trace(graph_data, scatter_data, "VOC", graph_data.sql_gas_resistance_date_time,
                         graph_data.sql_gas_resistance, name_and_subplot)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_dot
        put_sensor_trace(graph_data, scatter_data, "Oxidising", graph_data.sql_gas_oxidising_date_time,
                         graph_data.sql_gas_oxidising, name_and_subplot, skip_row_count=True)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_dot
        put_sensor_trace(graph_data, scatter_data, "Reducing", graph_data.sql_gas_reducing_date_time,
                         graph_data.sql_gas_reducing, name_and_subplot, skip_row_count=True)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_dot
        put_sensor_trace(graph_data, scatter_data, "NH3", graph_data.sql_gas_nh3_date_time,
                         graph_data.sql_gas_nh3, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_pm_1) > 2 or len(graph_data.sql_pm_2_5) > 2 or len(graph_data.sql_pm_10) > 2:
        name_and_subplot = "Particulate Matter"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_dot
        put_sensor_trace(graph_data, scatter_data, "PM1", graph_data.sql_pm_1_date_time,
                         graph_data.sql_pm_1, name_and_subplot)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_dot
        put_sensor_trace(graph_data, scatter_data, "PM2.5", graph_data.sql_pm_2_5_date_time,
                         graph_data.sql_pm_2_5, name_and_subplot, skip_row_count=True)

        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_dot
        put_sensor_trace(graph_data, scatter_data, "PM10", graph_data.sql_pm_10_date_time,
                         graph_data.sql_pm_10, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_lumen) > 2:
        name_and_subplot = "Lumen in lm"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_dot
        put_sensor_trace(graph_data, scatter_data, name_and_subplot, graph_data.sql_lumen_date_time,
                         graph_data.sql_lumen, name_and_subplot)

    if len(graph_data.sql_red) > 2:
        name_and_subplot = "Visible Electromagnetic Spectrum in lm? (Lumen)"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_dot
        put_sensor_trace(graph_data, scatter_data, "Red", graph_data.sql_red_date_time,
                         graph_data.sql_red, name_and_subplot)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_dot
        put_sensor_trace(graph_data, scatter_data, "Orange", graph_data.sql_orange_date_time,
                         graph_data.sql_orange, name_and_subplot, skip_row_count=True)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_dot
        put_sensor_trace(graph_data, scatter_data, "Yellow", graph_data.sql_yellow_date_time,
                         graph_data.sql_yellow, name_and_subplot, skip_row_count=True)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_green_dot
        put_sensor_trace(graph_data, scatter_data, "Green", graph_data.sql_green_date_time,
                         graph_data.sql_green, name_and_subplot, skip_row_count=True)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_blue_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_blue_dot
        put_sensor_trace(graph_data, scatter_data, "Blue", graph_data.sql_blue_date_time,
                         graph_data.sql_blue, name_and_subplot, skip_row_count=True)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_violet_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_violet_dot
        put_sensor_trace(graph_data, scatter_data, "Violet", graph_data.sql_violet_date_time,
                         graph_data.sql_violet, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_uv_index) > 2 or len(graph_data.sql_uv_a) > 2 or len(graph_data.sql_uv_b) > 2:
        name_and_subplot = "Ultra Violet"
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_red_dot
        put_sensor_trace(graph_data, scatter_data, "Index", graph_data.sql_uv_index_date_time,
                         graph_data.sql_uv_index, name_and_subplot)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_orange_dot
        put_sensor_trace(graph_data, scatter_data, "UVA", graph_data.sql_uv_a_date_time,
                         graph_data.sql_uv_a, name_and_subplot, skip_row_count=True)
        if graph_data.graph_table == database_variables.table_interval:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_line
        else:
            scatter_data.set_marker = server_plotly_graph_variables.mark_yellow_dot
        put_sensor_trace(graph_data, scatter_data, "UVB", graph_data.sql_uv_b_date_time,
                         graph_data.sql_uv_b, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_acc_x) > 2:
        name_and_subplot = "Accelerometer in g (G-forces)"
        scatter_data.set_marker = server_plotly_graph_variables.mark_x_dot
        put_sensor_trace(graph_data, scatter_data, "Accelerometer X", graph_data.sql_acc_x_date_time,
                         graph_data.sql_acc_x, name_and_subplot)
        scatter_data.set_marker = server_plotly_graph_variables.mark_y_dot
        put_sensor_trace(graph_data, scatter_data, "Accelerometer Y", graph_data.sql_acc_y_date_time,
                         graph_data.sql_acc_y, name_and_subplot, skip_row_count=True)
        scatter_data.set_marker = server_plotly_graph_variables.mark_z_dot
        put_sensor_trace(graph_data, scatter_data, "Accelerometer Z", graph_data.sql_acc_z_date_time,
                         graph_data.sql_acc_z, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_mg_x) > 2:
        name_and_subplot = "Magnetometer in μT (microtesla)"
        scatter_data.set_marker = server_plotly_graph_variables.mark_x_dot
        put_sensor_trace(graph_data, scatter_data, "Magnetometer X", graph_data.sql_mg_x_date_time,
                         graph_data.sql_mg_x, name_and_subplot)

        scatter_data.set_marker = server_plotly_graph_variables.mark_y_dot
        put_sensor_trace(graph_data, scatter_data, "Magnetometer Y", graph_data.sql_mg_y_date_time,
                         graph_data.sql_mg_y, name_and_subplot, skip_row_count=True)

        scatter_data.set_marker = server_plotly_graph_variables.mark_z_dot
        put_sensor_trace(graph_data, scatter_data, "Magnetometer Z", graph_data.sql_mg_z_date_time,
                         graph_data.sql_mg_z, name_and_subplot, skip_row_count=True)

    if len(graph_data.sql_gyro_x) > 2:
        name_and_subplot = "Gyroscopic in °/s (degrees per second)"
        scatter_data.set_marker = server_plotly_graph_variables.mark_x_dot
        put_sensor_trace(graph_data, scatter_data, "Gyroscopic X", graph_data.sql_gyro_x_date_time,
                         graph_data.sql_gyro_x, name_and_subplot)

        scatter_data.set_marker = server_plotly_graph_variables.mark_y_dot
        put_sensor_trace(graph_data, scatter_data, "Gyroscopic Y", graph_data.sql_gyro_y_date_time,
                         graph_data.sql_gyro_y, name_and_subplot, skip_row_count=True)

        scatter_data.set_marker = server_plotly_graph_variables.mark_z_dot
        put_sensor_trace(graph_data, scatter_data, "Gyroscopic Z", graph_data.sql_gyro_z_date_time,
                         graph_data.sql_gyro_z, name_and_subplot, skip_row_count=True)


def put_sensor_trace(graph_data, scatter_data, sensor_name_text, sql_time_data,
                     sql_data, sub_plot_name_text, skip_row_count=False):
    try:
        if not skip_row_count:
            graph_data.row_count += 1
            graph_data.sub_plots.append(sub_plot_name_text)

        scatter_data.text_sensor_name = sensor_name_text
        scatter_data.sql_time_list = sql_time_data
        scatter_data.sql_data_list = sql_data
        trace_sensor_name = _add_scatter(scatter_data)

        graph_data.graph_collection.append([trace_sensor_name, graph_data.row_count, 1])
        logger.primary_logger.debug("Graph " + sensor_name_text + " Name Added")
    except Exception as error:
        logger.primary_logger.error("Plotly Graph - Put Trace Error on " + sensor_name_text + ": " + str(error))


def _add_scatter(scatter_data):
    """
    Returns a OpenGL or CPU rendered trace based on configuration settings.

    Uses line graph for Interval data and dot markers for Trigger data.
    """
    try:
        if scatter_data.enable_plotly_webgl:
            if scatter_data.text_graph_table == database_variables.table_trigger:
                trace = go.Scattergl(x=scatter_data.sql_time_list,
                                     y=scatter_data.sql_data_list,
                                     name=scatter_data.text_sensor_name,
                                     mode="markers",
                                     marker=scatter_data.set_marker)
            else:
                trace = go.Scattergl(x=scatter_data.sql_time_list,
                                     y=scatter_data.sql_data_list,
                                     name=scatter_data.text_sensor_name,
                                     marker=scatter_data.set_marker)

        else:
            if scatter_data.graph_table == database_variables.table_trigger:
                trace = go.Scatter(x=scatter_data.sql_time_list,
                                   y=scatter_data.sql_data_list,
                                   name=scatter_data.text_sensor_name,
                                   mode="markers",
                                   marker=scatter_data.set_marker)
            else:
                trace = go.Scatter(x=scatter_data.sql_time_list,
                                   y=scatter_data.sql_data_list,
                                   name=scatter_data.text_sensor_name,
                                   marker=scatter_data.set_marker)
        return trace
    except Exception as error:
        logger.primary_logger.error("Plotly Scatter Failed on " + scatter_data.text_sensor_name + ": " + str(error))
