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
from operations_modules.app_cached_variables import database_variables as db_v

graph_creation_in_progress = False

mark_generic_dot = dict(size=2)
mark_red_dot = dict(size=5, color='rgba(255, 0, 0, .9)')
mark_orange_dot = dict(size=5, color='rgba(255, 102, 0, .9)')
mark_yellow_dot = dict(size=5, color='rgba(255, 170, 29, .9)')
mark_green_dot = dict(size=5, color='rgba(0, 255, 0, .9)')
mark_blue_dot = dict(size=5, color='rgba(25, 230, 255, .9)')
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

        if graph_config.graph_using_date_range:
            self.graph_datetime_start = graph_config.graph_start_date
            self.graph_datetime_end = graph_config.graph_end_date
        else:
            self.graph_datetime_start = datetime.utcnow() - timedelta(hours=graph_config.graph_past_hours)
            if graph_config.date_time_hours_offset < 0.0:
                self.graph_datetime_start -= timedelta(hours=abs(graph_config.date_time_hours_offset))
            self.graph_datetime_start = self.graph_datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            self.graph_datetime_end = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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
        self.graph_data_dic = {
            db_v.sensor_name: [[], [], "Sensor Names over Time", "Sensor Name", mark_generic_dot],
            db_v.sensor_uptime: [[], [], "Sensor Uptime in Minutes", "Sensor Uptime", mark_generic_dot],
            db_v.system_temperature: [[], [], "Temperature in °C (Celsius)", "CPU", mark_red_dot],
            db_v.env_temperature: [[], [], "Temperature in °C (Celsius)", "Environmental", mark_green_dot],
            db_v.dew_point: [[], [], "Temperature in °C (Celsius)", "Dew Point", mark_blue_dot],
            db_v.humidity: [[], [], "% Relative Humidity", "Humidity", mark_generic_dot],
            db_v.pressure: [[], [], "Pressure in hPa (Hectopascals)", "Pressure", mark_generic_dot],
            db_v.altitude: [[], [], "Altitude in m (Meters)", "Altitude", mark_generic_dot],
            db_v.distance: [[], [], "Distance in Meters?", "Distance", mark_generic_dot],
            db_v.gas_resistance_index: [[], [], "Gas Resistance in Ω (ohms)", "VOC", mark_red_dot],
            db_v.gas_oxidising: [[], [], "Gas Resistance in Ω (ohms)", "Oxidising", mark_orange_dot],
            db_v.gas_reducing: [[], [], "Gas Resistance in Ω (ohms)", "Reducing", mark_yellow_dot],
            db_v.gas_nh3: [[], [], "Gas Resistance in Ω (ohms)", "NH3", mark_green_dot],
            db_v.particulate_matter_1: [[], [], "Particulate Matter", "PM1", mark_red_dot],
            db_v.particulate_matter_2_5: [[], [], "Particulate Matter", "PM2.5", mark_orange_dot],
            db_v.particulate_matter_4: [[], [], "Particulate Matter", "PM4", mark_yellow_dot],
            db_v.particulate_matter_10: [[], [], "Particulate Matter", "PM10", mark_blue_dot],
            db_v.lumen: [[], [], "Lumen in lm", "lm", mark_yellow_dot],
            db_v.red: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Red", mark_red_dot],
            db_v.orange: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Orange", mark_orange_dot],
            db_v.yellow: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Yellow", mark_yellow_dot],
            db_v.green: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Green", mark_green_dot],
            db_v.blue: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Blue", mark_blue_dot],
            db_v.violet: [[], [], "Visible Electromagnetic Spectrum in lm? (Lumen)", "Violet", mark_violet_dot],
            db_v.ultra_violet_index: [[], [], "Ultra Violet", "Index", mark_red_dot],
            db_v.ultra_violet_a: [[], [], "Ultra Violet", "UVA", mark_orange_dot],
            db_v.ultra_violet_b: [[], [], "Ultra Violet", "UVB", mark_yellow_dot],
            db_v.acc_x: [[], [], "Accelerometer in g (G-forces)", "Accelerometer X", mark_x_dot],
            db_v.acc_y: [[], [], "Accelerometer in g (G-forces)", "Accelerometer Y", mark_y_dot],
            db_v.acc_z: [[], [], "Accelerometer in g (G-forces)", "Accelerometer Z", mark_z_dot],
            db_v.mag_x: [[], [], "Magnetometer in μT (microtesla)", "Magnetometer X", mark_x_dot],
            db_v.mag_y: [[], [], "Magnetometer in μT (microtesla)", "Magnetometer Y", mark_y_dot],
            db_v.mag_z: [[], [], "Magnetometer in μT (microtesla)", "Magnetometer Z", mark_z_dot],
            db_v.gyro_x: [[], [], "Gyroscopic in °/s (degrees per second)", "Gyroscopic X", mark_x_dot],
            db_v.gyro_y: [[], [], "Gyroscopic in °/s (degrees per second)", "Gyroscopic Y", mark_y_dot],
            db_v.gyro_z: [[], [], "Gyroscopic in °/s (degrees per second)", "Gyroscopic Z", mark_z_dot]
        }
