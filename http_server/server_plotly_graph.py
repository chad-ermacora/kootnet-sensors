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
import sqlite3
from plotly import subplots, offline
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_variables
from http_server import server_plotly_graph_extras
from http_server import server_plotly_graph_variables


def create_plotly_graph(new_graph_data):
    """ Create Plotly offline HTML Graph, based on user selections in the Graph Window. """
    server_plotly_graph_variables.graph_creation_in_progress = True

    if new_graph_data.graph_table is "Triggers":
        new_graph_data.bypass_sql_skip = True

    logger.primary_logger.info("Plotly Graph Generation Started")
    _start_plotly_graph(new_graph_data)
    logger.primary_logger.info("Plotly Graph Generation Complete")

    server_plotly_graph_variables.graph_creation_in_progress = False


def _start_plotly_graph(graph_data):
    """ Creates a Offline Plotly graph from a SQL database. """
    logger.primary_logger.debug("SQL Columns: " + str(graph_data.graph_columns))
    logger.primary_logger.debug("SQL Table(s): " + graph_data.graph_table)
    logger.primary_logger.debug("SQL Start DateTime: " + graph_data.graph_start)
    logger.primary_logger.debug("SQL End DateTime: " + graph_data.graph_end)
    logger.primary_logger.debug("SQL DataBase Location: " + graph_data.db_location)

    # Adjust dates to Database timezone in UTC 0
    sql_column_names = app_variables.CreateDatabaseVariables()
    new_time_offset = int(graph_data.datetime_offset) * -1
    get_sql_graph_start = server_plotly_graph_extras.adjust_datetime(graph_data.graph_start, new_time_offset)
    get_sql_graph_end = server_plotly_graph_extras.adjust_datetime(graph_data.graph_end, new_time_offset)

    for var_column in graph_data.graph_columns:
        var_sql_query = "SELECT " + \
                        var_column + \
                        " FROM " + \
                        graph_data.graph_table + \
                        " WHERE DateTime BETWEEN datetime('" + \
                        get_sql_graph_start + \
                        "') AND datetime('" + \
                        get_sql_graph_end + \
                        "') LIMIT " + \
                        str(graph_data.max_sql_queries)

        sql_column_data = _get_sql_data(graph_data, var_sql_query)

        # Adjust SQL data from its UTC time, to user set timezone (Hour Offset)
        if var_column == sql_column_names.all_tables_datetime:
            count = 0
            for data in sql_column_data:
                sql_column_data[count] = server_plotly_graph_extras.adjust_datetime(data,
                                                                                    int(graph_data.datetime_offset))
                count = count + 1
            graph_data.sql_time = sql_column_data
        elif var_column == sql_column_names.ip:
            graph_data.sql_ip = sql_column_data
        elif var_column == sql_column_names.sensor_name:
            graph_data.sql_host_name = sql_column_data
        elif var_column == sql_column_names.sensor_uptime:
            graph_data.sql_up_time = sql_column_data
        elif var_column == sql_column_names.system_temperature:
            graph_data.sql_cpu_temp = sql_column_data
        elif var_column == sql_column_names.env_temperature:
            count = 0
            if graph_data.enable_custom_temp_offset:
                for data in sql_column_data:
                    try:
                        sql_column_data[count] = str(float(data) + graph_data.temperature_offset)
                        count = count + 1
                    except Exception as error:
                        count = count + 1
                        logger.primary_logger.error("Bad SQL entry from Column 'EnvironmentTemp' - " + str(error))
            else:
                var_sql_query = "SELECT " + \
                                sql_column_names.env_temperature_offset + \
                                " FROM " + \
                                graph_data.graph_table + \
                                " WHERE DateTime BETWEEN datetime('" + \
                                get_sql_graph_start + \
                                "') AND datetime('" + \
                                get_sql_graph_end + \
                                "') LIMIT " + \
                                str(graph_data.max_sql_queries)

                sql_temp_offset_data = _get_sql_data(graph_data, var_sql_query)

                warn_message = False
                count = 0
                for data in sql_column_data:
                    try:
                        sql_column_data[count] = str(float(data) + float(sql_temp_offset_data[count]))
                        count = count + 1
                    except Exception as error:
                        logger.primary_logger.debug(
                            "Bad SQL entry from Column 'EnvironmentTemp' or 'EnvironmentTempOffset' - " + str(error))
                        count = count + 1
                        warn_message = True

                if warn_message:
                    logger.primary_logger.warning("Plotly Graph: " +
                                                  "One or more missing entries in 'EnvironmentTemp' or 'EnvTempOffset'")

            graph_data.sql_hat_temp = sql_column_data
        elif var_column == sql_column_names.env_temperature_offset:
            pass
        elif var_column == sql_column_names.pressure:
            graph_data.sql_pressure = sql_column_data
        elif var_column == sql_column_names.altitude:
            graph_data.sql_altitude = sql_column_data
        elif var_column == sql_column_names.humidity:
            graph_data.sql_humidity = sql_column_data
        elif var_column == sql_column_names.distance:
            graph_data.sql_distance = sql_column_data
        elif var_column == sql_column_names.gas_resistance_index:
            graph_data.sql_gas_resistance = sql_column_data
        elif var_column == sql_column_names.gas_oxidising:
            graph_data.sql_gas_oxidising = sql_column_data
        elif var_column == sql_column_names.gas_reducing:
            graph_data.sql_gas_reducing = sql_column_data
        elif var_column == sql_column_names.gas_nh3:
            graph_data.sql_gas_nh3 = sql_column_data
        elif var_column == sql_column_names.particulate_matter_1:
            graph_data.sql_pm_1 = sql_column_data
        elif var_column == sql_column_names.particulate_matter_2_5:
            graph_data.sql_pm_2_5 = sql_column_data
        elif var_column == sql_column_names.particulate_matter_10:
            graph_data.sql_pm_10 = sql_column_data
        elif var_column == sql_column_names.lumen:
            graph_data.sql_lumen = sql_column_data
        elif var_column == sql_column_names.red:
            graph_data.sql_red = sql_column_data
        elif var_column == sql_column_names.orange:
            graph_data.sql_orange = sql_column_data
        elif var_column == sql_column_names.yellow:
            graph_data.sql_yellow = sql_column_data
        elif var_column == sql_column_names.green:
            graph_data.sql_green = sql_column_data
        elif var_column == sql_column_names.blue:
            graph_data.sql_blue = sql_column_data
        elif var_column == sql_column_names.violet:
            graph_data.sql_violet = sql_column_data
        elif var_column == sql_column_names.ultra_violet_index:
            graph_data.sql_uv_index = sql_column_data
        elif var_column == sql_column_names.ultra_violet_a:
            graph_data.sql_uv_a = sql_column_data
        elif var_column == sql_column_names.ultra_violet_b:
            graph_data.sql_uv_b = sql_column_data
        elif var_column == sql_column_names.acc_x:
            graph_data.sql_acc_x = sql_column_data
        elif var_column == sql_column_names.acc_y:
            graph_data.sql_acc_y = sql_column_data
        elif var_column == sql_column_names.acc_z:
            graph_data.sql_acc_z = sql_column_data
        elif var_column == sql_column_names.mag_x:
            graph_data.sql_mg_x = sql_column_data
        elif var_column == sql_column_names.mag_y:
            graph_data.sql_mg_y = sql_column_data
        elif var_column == sql_column_names.mag_z:
            graph_data.sql_mg_z = sql_column_data
        elif var_column == sql_column_names.gyro_x:
            graph_data.sql_gyro_x = sql_column_data
        elif var_column == sql_column_names.gyro_y:
            graph_data.sql_gyro_y = sql_column_data
        elif var_column == sql_column_names.gyro_z:
            graph_data.sql_gyro_z = sql_column_data
        else:
            logger.primary_logger.error(var_column + " - Does Not Exist")
    _plotly_graph(graph_data)
    logger.primary_logger.debug("Interval DB Graph Complete")


def _get_sql_data(graph_interval_data, sql_command):
    """ Execute SQLite3 command and return the results. """
    return_data = []

    try:
        database_connection = sqlite3.connect(file_locations.sensor_database_location)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_command)
        sql_column_data = sqlite_database.fetchall()
        sqlite_database.close()
        database_connection.close()
    except Exception as error:
        logger.primary_logger.error("DB Error: " + str(error))
        sql_column_data = []

    count = 0
    skip_count = 0
    null_data_entries = 0
    for data in sql_column_data:
        if str(data) == "(None,)":
            null_data_entries += 1
        if skip_count >= int(graph_interval_data.sql_queries_skip) or graph_interval_data.bypass_sql_skip:
            return_data.append(str(data)[2:-3])
            skip_count = 0

        skip_count = skip_count + 1
        count = count + 1

    logger.primary_logger.debug("SQL execute Command: " + str(sql_command))
    logger.primary_logger.debug("SQL Column Data Length: " + str(len(return_data)))
    if null_data_entries == len(sql_column_data):
        # Skip if all None
        return []
    else:
        return return_data


def _plotly_graph(graph_data):
    """ Create and open a HTML offline Plotly graph with the data provided. """
    graph_data.sub_plots = []
    graph_data.row_count = 0
    graph_data.graph_collection = []

    if len(graph_data.sql_time) > 1:
        if len(graph_data.sql_host_name) > 1:
            server_plotly_graph_extras.graph_host_name(graph_data)

        if len(graph_data.sql_up_time) > 1:
            server_plotly_graph_extras.graph_sql_uptime(graph_data)

        if len(graph_data.sql_cpu_temp) > 1 or len(graph_data.sql_hat_temp) > 1:
            server_plotly_graph_extras.graph_sql_cpu_env_temperature(graph_data)

        if len(graph_data.sql_pressure) > 2:
            server_plotly_graph_extras.graph_sql_pressure(graph_data)

        if len(graph_data.sql_altitude) > 2:
            server_plotly_graph_extras.graph_sql_altitude(graph_data)

        if len(graph_data.sql_humidity) > 2:
            server_plotly_graph_extras.graph_sql_humidity(graph_data)

        if len(graph_data.sql_distance) > 2:
            server_plotly_graph_extras.graph_sql_distance(graph_data)

        if len(graph_data.sql_gas_resistance) > 2 or len(graph_data.sql_gas_oxidising) > 2 \
                or len(graph_data.sql_gas_reducing) > 2 or len(graph_data.sql_gas_nh3) > 2:
            server_plotly_graph_extras.graph_sql_gas(graph_data)

        if len(graph_data.sql_pm_1) > 2 or len(graph_data.sql_pm_2_5) > 2 or len(graph_data.sql_pm_10) > 2:
            server_plotly_graph_extras.graph_sql_particulate_matter(graph_data)

        if len(graph_data.sql_lumen) > 2:
            server_plotly_graph_extras.graph_sql_lumen(graph_data)

        if len(graph_data.sql_red) > 2:
            server_plotly_graph_extras.graph_sql_ems_colours(graph_data)

        if len(graph_data.sql_uv_index) > 2 or len(graph_data.sql_uv_a) > 2 or len(graph_data.sql_uv_b) > 2:
            server_plotly_graph_extras.graph_sql_ultra_violet(graph_data)

        if len(graph_data.sql_acc_x) > 2:
            server_plotly_graph_extras.graph_sql_accelerometer(graph_data)

        if len(graph_data.sql_mg_x) > 2:
            server_plotly_graph_extras.graph_sql_magnetometer(graph_data)

        if len(graph_data.sql_gyro_x) > 2:
            server_plotly_graph_extras.graph_sql_gyroscope(graph_data)

        fig = subplots.make_subplots(rows=graph_data.row_count, cols=1, subplot_titles=graph_data.sub_plots)

        for graph in graph_data.graph_collection:
            fig.add_trace(graph[0], graph[1], graph[2])
        if len(graph_data.sql_ip) > 1:
            fig['layout'].update(title="Sensor IP: " + str(graph_data.sql_ip[0]))

        if graph_data.row_count > 4:
            fig['layout'].update(height=2048)

        try:
            offline.plot(fig, filename=graph_data.save_to + file_locations.plotly_html_filename)
            logger.primary_logger.debug("Plotly Graph Creation - OK")
        except Exception as error:
            logger.primary_logger.error("Plotly Graph Creation - Failed - " + str(error))
    else:
        logger.primary_logger.error("Graph Plot Failed - No SQL data found in Database within the selected Time Frame")
