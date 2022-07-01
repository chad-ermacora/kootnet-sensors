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
from multiprocessing import Process
from operations_modules import app_cached_variables
from operations_modules import logger
from operations_modules.app_generic_functions import adjust_datetime
from operations_modules.sqlite_database import sql_execute_get_data, get_one_db_entry
from http_server import server_plotly_graph_variables

try:
    from plotly import subplots, offline, io as plotly_io, graph_objs as go
except ImportError as import_error:
    subplots, offline, plotly_io, go = None, None, None, None
    log_message = "**** Missing Plotly Graph Dependencies - There may be unintended side effects as a result: "
    logger.primary_logger.error(log_message + str(import_error))

plotly_io.templates.default = app_cached_variables.plotly_theme
db_v = app_cached_variables.database_variables


class CreateGraphScatterData:
    def __init__(self, webgl, sql_table):
        self.enable_plotly_webgl = webgl
        self.text_graph_table = sql_table
        self.text_sensor_name = ""

        self.sql_time_list = []
        self.sql_data_list = []

        self.set_marker = server_plotly_graph_variables.mark_generic_dot
        if sql_table != db_v.table_trigger:
            self.set_marker["size"] = 5


def create_plotly_graph(new_graph_data):
    """ Create Plotly offline HTML Graph, based on user selections in the Web Portal Graphing section. """
    logger.primary_logger.info("Plotly Graph Generation Started")
    server_plotly_graph_variables.graph_creation_in_progress = True
    graph_multiprocess = Process(target=_start_plotly_graph, args=(new_graph_data,))
    graph_multiprocess.start()
    graph_multiprocess.join()
    logger.primary_logger.info("Plotly Graph Generation Complete")
    server_plotly_graph_variables.graph_creation_in_progress = False


def _start_plotly_graph(graph_data):
    """ Creates a Offline Plotly graph from a SQL database. """
    logger.primary_logger.debug("SQL Columns: " + str(graph_data.selected_sensors_list))
    logger.primary_logger.debug("SQL Table(s): " + graph_data.graph_db_table)
    logger.primary_logger.debug("SQL Start DateTime: " + graph_data.graph_datetime_start)
    logger.primary_logger.debug("SQL End DateTime: " + graph_data.graph_datetime_end)

    try:
        # Adjust dates to Database timezone in UTC 0
        new_time_offset = graph_data.datetime_offset * -1
        get_sql_graph_start = adjust_datetime(graph_data.graph_datetime_start, new_time_offset)
        get_sql_graph_end = adjust_datetime(graph_data.graph_datetime_end, new_time_offset)
        graph_data.sql_ip = get_one_db_entry(graph_data.graph_db_table, db_v.ip, database=graph_data.db_location)

        for var_column in graph_data.selected_sensors_list:
            var_sql_query = "SELECT " + var_column + \
                            " FROM " + graph_data.graph_db_table + \
                            " WHERE " + var_column + \
                            " IS NOT NULL AND DateTime BETWEEN date('" + get_sql_graph_start + \
                            "') AND date('" + get_sql_graph_end + \
                            "') AND ROWID % " + str(graph_data.sql_queries_skip + 1) + " = 0" + \
                            " ORDER BY " + db_v.all_tables_datetime + " DESC" + \
                            " LIMIT " + str(graph_data.max_sql_queries)

            var_time_sql_query = "SELECT " + db_v.all_tables_datetime + \
                                 " FROM " + graph_data.graph_db_table + \
                                 " WHERE " + var_column + \
                                 " IS NOT NULL AND DateTime BETWEEN date('" + get_sql_graph_start + \
                                 "') AND date('" + get_sql_graph_end + \
                                 "') AND ROWID % " + str(graph_data.sql_queries_skip + 1) + " = 0" + \
                                 " ORDER BY " + db_v.all_tables_datetime + " DESC" + \
                                 " LIMIT " + str(graph_data.max_sql_queries)

            original_sql_column_date_time = sql_execute_get_data(var_time_sql_query, graph_data.db_location)
            sql_column_date_time = []
            for var_d_time in original_sql_column_date_time:
                sql_column_date_time.append(adjust_datetime(var_d_time[0], graph_data.datetime_offset))

            if var_column == db_v.all_tables_datetime:
                graph_data.datetime_entries_in_db = len(sql_column_date_time)
            elif var_column == db_v.sensor_name or var_column == db_v.ip:
                graph_data.graph_data_dic[var_column][0] = _get_clean_sql_data(
                    var_sql_query, graph_data.db_location, data_to_float=False
                )
                graph_data.graph_data_dic[var_column][1] = sql_column_date_time
            else:
                graph_data.graph_data_dic[var_column][0] = _get_clean_sql_data(var_sql_query, graph_data.db_location)
                graph_data.graph_data_dic[var_column][1] = sql_column_date_time
        _plotly_graph(graph_data)
    except Exception as error:
        logger.primary_logger.warning("Plotly Graph Generation Failed: " + str(error))


def _plotly_graph(graph_data):
    """ Create a HTML offline Plotly graph with the data provided. """
    graph_data.sub_plots = []
    graph_data.row_count = 0
    graph_data.graph_collection = []

    if graph_data.datetime_entries_in_db > 1:
        add_plots(graph_data)

        fig = subplots.make_subplots(rows=graph_data.row_count, cols=1, subplot_titles=graph_data.sub_plots)

        for graph in graph_data.graph_collection:
            fig.add_trace(graph[0], graph[1], graph[2])

        graph_height = (384 * graph_data.row_count)
        if graph_height < 1024:
            graph_height = 1024

        fig['layout'].update(
            title="Plotly Graph for Sensor IP: " + str(graph_data.sql_ip),
            title_font_size=25,
            height=graph_height
        )

        offline.plot(fig, filename=graph_data.save_plotly_graph_to, auto_open=False)
    else:
        msg = "Plotly Graph Creation - Failed: No SQL data found in the database within the selected time frame"
        msg += " || DB: " + graph_data.db_location + " || Table: " + graph_data.graph_db_table
        logger.primary_logger.info(msg)


def _get_clean_sql_data(var_sql_query, db_location, data_to_float=True):
    sql_data_tuple = sql_execute_get_data(var_sql_query, db_location)
    cleaned_list = []
    for data in sql_data_tuple:
        if data_to_float:
            try:
                cleaned_list.append(float(data[0]))
            except Exception as error:
                logger.primary_logger.debug("Plotly Graph data to Float Failed: " + str(error))
        else:
            cleaned_list.append(data[0])
    return cleaned_list


def add_plots(graph_data):
    scatter_data = CreateGraphScatterData(graph_data.enable_plotly_webgl, graph_data.graph_db_table)

    previous_subplot_name = ""
    for sensor_db_name, sensor_graph_data in graph_data.graph_data_dic.items():
        if len(sensor_graph_data[0]) > 1:
            try:
                if sensor_graph_data[2] != previous_subplot_name:
                    graph_data.row_count += 1
                    graph_data.sub_plots.append(sensor_graph_data[2])
                previous_subplot_name = sensor_graph_data[2]

                scatter_data.sql_data_list = sensor_graph_data[0]
                scatter_data.sql_time_list = sensor_graph_data[1]
                scatter_data.text_sensor_name = sensor_graph_data[3]
                if graph_data.graph_db_table != db_v.table_trigger:
                    sensor_graph_data[4]["line"] = {"width": 2, "color": 'rgb(0, 0, 0)'}
                scatter_data.set_marker = sensor_graph_data[4]

                graph_data.graph_collection.append([_add_scatter(scatter_data), graph_data.row_count, 1])
                logger.primary_logger.debug("Graph " + sensor_graph_data[3] + " Name Added")
            except Exception as error:
                log_msg = "Plotly Graph - Put Trace Error on " + sensor_graph_data[3] + ": " + str(error)
                logger.primary_logger.error(log_msg)


def _add_scatter(scatter_data):
    """
    Returns a OpenGL or CPU rendered trace based on configuration settings.

    Uses line graph for Interval data and dot markers for Trigger data.
    """
    try:
        if scatter_data.enable_plotly_webgl:
            if scatter_data.text_graph_table == db_v.table_trigger:
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
            if scatter_data.graph_table == db_v.table_trigger:
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
