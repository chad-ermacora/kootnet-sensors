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
from operations_modules.app_cached_variables import database_variables as db_v

graph_creation_in_progress = False

mark_generic_dot = dict(size=2)
mark_red_dot = dict(size=5, color='rgba(255, 0, 0, .9)')
mark_orange_dot = dict(size=5, color='rgba(255, 102, 0, .9)')
mark_yellow_dot = dict(size=5, color='rgba(255, 170, 29, .9)')
mark_green_dot = dict(size=5, color='rgba(0, 255, 0, .9)')
mark_blue_dot = dict(size=5, color='rgba(0, 0, 255, .9)')
mark_violet_dot = dict(size=5, color='rgba(153, 0, 204, .9)')
mark_x_dot = dict(size=5, color='rgba(255, 0, 0, 1)')
mark_y_dot = dict(size=5, color='rgba(0, 255, 0, 1)')
mark_z_dot = dict(size=5, color='rgba(0, 0, 255, 1)')


class CreateGraphData:
    """ Creates an object to hold all required Plotly graph data """

    def __init__(self, graph_config):
        self.db_location = graph_config.database_location
        self.graph_db_table = graph_config.graph_db_table
        self.save_plotly_graph_to = graph_config.plotly_graph_saved_location

        self.graph_datetime_start = graph_config.graph_start_date
        self.graph_datetime_end = graph_config.graph_end_date
        self.enable_plotly_webgl = False
        if graph_config.render_engine == "OpenGL":
            self.enable_plotly_webgl = True
        self.do_not_skip_data_points = False
        if self.graph_db_table == db_v.table_trigger:
            self.do_not_skip_data_points = True
        self.datetime_offset = graph_config.date_time_hours_offset
        self.sql_queries_skip = graph_config.skip_data_between_plots
        self.max_sql_queries = graph_config.max_graph_data_points

        self.sql_ip = ""

        # Used to make sure there is enough of something written to the Database to graph
        self.datetime_entries_in_db = 0

        self.graph_collection = []

        # A list of sensors to be graphed (based on what has been selected in the web interface)
        self.selected_sensors_list = graph_config.get_enabled_graph_sensors_list()

        # Filled with sensor data to be graphed later in the process. [[Sensor Data], [Sensor Datetime entries]]
        temperature_text = " Temperature in °C (Celsius)"
        self.graph_data_dic = {
            db_v.sensor_name: [[], [], "Sensor Names over Time", "Sensor Name", False],
            db_v.sensor_uptime: [[], [], "Sensor Uptime in Minutes", "Sensor Uptime", False],
            db_v.system_temperature: [[], [], "CPU" + temperature_text, "CPU", mark_red_dot],
            db_v.env_temperature: [[], [], "Environmental" + temperature_text, "Environmental", mark_green_dot],
            db_v.pressure: [[], [], "Pressure in hPa (Hectopascals)", "Pressure", False],
            db_v.altitude: [[], [], "Altitude in m (Meters)", "Altitude", False],
            db_v.humidity: [[], [], "% Relative Humidity", "Humidity", False],
            db_v.dew_point: [[], [], "Dew Point" + temperature_text, "Dew Point", False],
            db_v.distance: [[], [], "Distance in Meters?", "Distance", False],
            db_v.gas_resistance_index: [[], [], "Gas Resistance in Ω (ohms)", "VOC", mark_red_dot],
            db_v.gas_oxidising: [[], [], False, "Oxidising", mark_orange_dot],
            db_v.gas_reducing: [[], [], False, "Reducing", mark_yellow_dot],
            db_v.gas_nh3: [[], [], False, "NH3", mark_green_dot],
            db_v.particulate_matter_1: [[], [], "Particulate Matter", "PM1", mark_red_dot],
            db_v.particulate_matter_2_5: [[], [], False, "PM2.5", mark_orange_dot],
            db_v.particulate_matter_4: [[], [], False, "PM4", mark_yellow_dot],
            db_v.particulate_matter_10: [[], [], False, "PM10", mark_blue_dot],
            db_v.lumen: [[], [], "Lumen in lm", "lm", mark_yellow_dot],
            db_v.red: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Red", mark_red_dot],
            db_v.orange: [[], [], False, "Orange", mark_orange_dot],
            db_v.yellow: [[], [], False, "Yellow", mark_yellow_dot],
            db_v.green: [[], [], False, "Green", mark_green_dot],
            db_v.blue: [[], [], False, "Blue", mark_blue_dot],
            db_v.violet: [[], [], False, "Violet", mark_violet_dot],
            db_v.ultra_violet_index: [[], [], "Ultra Violet", "Index", mark_red_dot],
            db_v.ultra_violet_a: [[], [], False, "UVA", mark_orange_dot],
            db_v.ultra_violet_b: [[], [], False, "UVB", mark_yellow_dot],
            db_v.acc_x: [[], [], "Accelerometer in g (G-forces)", "Accelerometer X", mark_x_dot],
            db_v.acc_y: [[], [], False, "Accelerometer Y", mark_y_dot],
            db_v.acc_z: [[], [], False, "Accelerometer Z", mark_z_dot],
            db_v.mag_x: [[], [], "Magnetometer in μT (microtesla)", "Magnetometer X", mark_x_dot],
            db_v.mag_y: [[], [], False, "Magnetometer Y", mark_y_dot],
            db_v.mag_z: [[], [], False, "Magnetometer Z", mark_z_dot],
            db_v.gyro_x: [[], [], "Gyroscopic in °/s (degrees per second)", "Gyroscopic X", mark_x_dot],
            db_v.gyro_y: [[], [], False, "Gyroscopic Y", mark_y_dot],
            db_v.gyro_z: [[], [], False, "Gyroscopic Z", mark_z_dot]
        }
