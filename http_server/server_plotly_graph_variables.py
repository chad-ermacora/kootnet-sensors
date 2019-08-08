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
from operations_modules import file_locations

graph_creation_in_progress = False

mark_red_line = dict(size=10,
                     color='rgba(255, 0, 0, .9)',
                     line=dict(width=2, color='rgb(0, 0, 0)'))

mark_orange_line = dict(size=10,
                        color='rgba(255, 102, 0, .9)',
                        line=dict(width=2, color='rgb(0, 0, 0)'))

mark_yellow_line = dict(size=10,
                        color='rgba(230, 230, 0, .9)',
                        line=dict(width=2, color='rgb(0, 0, 0)'))

mark_green_line = dict(size=10,
                       color='rgba(0, 255, 0, .9)',
                       line=dict(width=2, color='rgb(0, 0, 0)'))

mark_blue_line = dict(size=10,
                      color='rgba(0, 0, 255, .9)',
                      line=dict(width=2, color='rgb(0, 0, 0)'))

mark_violet_line = dict(size=10,
                        color='rgba(153, 0, 204, .9)',
                        line=dict(width=2, color='rgb(0, 0, 0)'))

mark_red_dot = dict(size=5,
                    color='rgba(255, 0, 0, .9)')

mark_orange_dot = dict(size=5,
                       color='rgba(255, 102, 0, .9)')

mark_yellow_dot = dict(size=5,
                       color='rgba(230, 230, 0, .9)')

mark_green_dot = dict(size=5,
                      color='rgba(0, 255, 0, .9)')

mark_blue_dot = dict(size=5,
                     color='rgba(0, 0, 255, .9)')

mark_violet_dot = dict(size=5,
                       color='rgba(153, 0, 204, .9)')

mark_x_dot = dict(size=5,
                  color='rgba(255, 0, 0, 1)')

mark_y_dot = dict(size=5,
                  color='rgba(0, 255, 0, 1)')

mark_z_dot = dict(size=5,
                  color='rgba(0, 0, 255, 1)')

mark_generic_dot = dict(size=2)

mark_generic_line = dict(size=5, line=dict(width=2, color='rgb(0, 0, 0)'))


class CreateGraphData:
    """ Creates an object to hold all the data needed for a graph. """

    def __init__(self):
        self.enable_plotly_webgl = False
        self.db_location = file_locations.sensor_database_location
        self.graph_table = "IntervalData"
        self.save_to = file_locations.save_plotly_html_to
        self.graph_start = "1111-08-21 00:00:01"
        self.graph_end = "9999-01-01 00:00:01"
        self.datetime_offset = 7.0
        self.sql_queries_skip = 12
        self.bypass_sql_skip = False
        self.enable_custom_temp_offset = False
        self.temperature_offset = 0.0

        self.sub_plots = []
        self.row_count = 0
        self.graph_collection = []

        self.graph_columns = ["DateTime", "SensorName", "SensorUpTime", "IP", "SystemTemp",
                              "EnvironmentTemp", "EnvTempOffset", "Pressure", "Altitude", "Humidity", "Lumen",
                              "Distance", "Gas_Resistance_Index", "Gas_Oxidising", "Gas_Reducing", "Gas_NH3",
                              "Particulate_Matter_1", "Particulate_Matter_2_5", "Particulate_Matter_10",
                              "Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Ultra_Violet_Index",
                              "Ultra_Violet_A", "Ultra_Violet_B"]
        self.max_sql_queries = 200000

        # Graph data holders for SQL DataBase
        self.sql_time = []
        self.sql_ip = []
        self.sql_host_name = []
        self.sql_up_time = []
        self.sql_cpu_temp = []
        self.sql_hat_temp = []
        self.sql_temp_offset = []
        self.sql_pressure = []
        self.sql_altitude = []
        self.sql_humidity = []
        self.sql_distance = []
        self.sql_gas_resistance = []
        self.sql_gas_oxidising = []
        self.sql_gas_reducing = []
        self.sql_gas_nh3 = []
        self.sql_pm_1 = []
        self.sql_pm_2_5 = []
        self.sql_pm_10 = []
        self.sql_lumen = []
        self.sql_red = []
        self.sql_orange = []
        self.sql_yellow = []
        self.sql_green = []
        self.sql_blue = []
        self.sql_violet = []
        self.sql_uv_index = []
        self.sql_uv_a = []
        self.sql_uv_b = []
        self.sql_acc_x = []
        self.sql_acc_y = []
        self.sql_acc_z = []
        self.sql_mg_x = []
        self.sql_mg_y = []
        self.sql_mg_z = []
        self.sql_gyro_x = []
        self.sql_gyro_y = []
        self.sql_gyro_z = []
