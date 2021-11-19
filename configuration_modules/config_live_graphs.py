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
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateLiveGraphsConfiguration(CreateGeneralConfiguration):
    """ Creates the Live Graphs Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.live_graphs_config, load_from_file=load_from_file)
        self.config_file_header = "Live Graphs Configuration. Enable = 1 and Disable = 0"
        self.valid_setting_count = 22
        self.config_settings_names = [
            "Sensor Address", "Graph Update Interval in seconds", "Enable Uptime", "Enable CPU Temperature",
            "Enable Environmental Temperature", "Enable Pressure", "Enable Altitude", "Enable Humidity",
            "Enable Dew Point", "Enable Distance", "Enable GAS", "Enable Particulate Matter", "Enable Lumen",
            "Enable Colours", "Enable Ultra Violet", "Enable Accelerometer", "Enable Magnetometer", "Enable Gyroscope",
            "Graphs Per Row - Enter 12 for 1 sensor per row, 6 for 2, 4 for 3 and 3 for 4", "Enable SSL Verification",
            "Max Data Points per Graph", "Enable Performance Mode (Renders graphs faster)"
        ]

        self.graph_sensor_address = None
        self.live_graph_update_interval = 5
        self.graphs_per_row = "6"
        self.max_graph_data_points = 240
        self.enable_ssl_verification = 1
        self.enable_performance_mode = 0

        self.live_graph_uptime = 0
        self.live_graph_cpu_temp = 1
        self.live_graph_env_temp = 1
        self.live_graph_pressure = 0
        self.live_graph_altitude = 0
        self.live_graph_humidity = 0
        self.live_graph_dew_point = 0
        self.live_graph_distance = 0
        self.live_graph_gas = 0
        self.live_graph_particulate_matter = 0
        self.live_graph_lumen = 0
        self.live_graph_colours = 0
        self.live_graph_ultra_violet = 0
        self.live_graph_acc = 0
        self.live_graph_mag = 0
        self.live_graph_gyro = 0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def get_checked_graph_per_line_state(self, per_line_number):
        if per_line_number == 1:
            if self.graphs_per_row == "12":
                return "selected"
        elif per_line_number == 2:
            if self.graphs_per_row == "6":
                return "selected"
        elif per_line_number == 3:
            if self.graphs_per_row == "4":
                return "selected"
        elif per_line_number == 4:
            if self.graphs_per_row == "3":
                return "selected"
        return ""

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Live Graphs configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Live Graphs Configuration Update Check")
        self.enable_ssl_verification = 0
        self.enable_performance_mode = 0

        self.live_graph_uptime = 0
        self.live_graph_cpu_temp = 0
        self.live_graph_env_temp = 0
        self.live_graph_pressure = 0
        self.live_graph_altitude = 0
        self.live_graph_humidity = 0
        self.live_graph_dew_point = 0
        self.live_graph_distance = 0
        self.live_graph_gas = 0
        self.live_graph_particulate_matter = 0
        self.live_graph_lumen = 0
        self.live_graph_colours = 0
        self.live_graph_ultra_violet = 0
        self.live_graph_acc = 0
        self.live_graph_mag = 0
        self.live_graph_gyro = 0

        if html_request.form.get("enable_ssl_verification") is not None:
            self.enable_ssl_verification = 1
        if html_request.form.get("enable_performance_mode") is not None:
            self.enable_performance_mode = 1

        if html_request.form.get("graph_sensor_address") is not None:
            sensor_address = str(html_request.form.get("graph_sensor_address")).strip()
            if len(sensor_address) > 3:
                self.graph_sensor_address = sensor_address
            else:
                self.graph_sensor_address = None
        if html_request.form.get("graph_update_interval") is not None:
            self.live_graph_update_interval = int(html_request.form.get("graph_update_interval"))

        if html_request.form.get("graphs_per_line") is not None:
            graph_per_row_selection = html_request.form.get("graphs_per_line")
            if graph_per_row_selection == "graphs_per_line_1":
                self.graphs_per_row = "12"
            elif graph_per_row_selection == "graphs_per_line_2":
                self.graphs_per_row = "6"
            elif graph_per_row_selection == "graphs_per_line_3":
                self.graphs_per_row = "4"
            elif graph_per_row_selection == "graphs_per_line_4":
                self.graphs_per_row = "3"

        if html_request.form.get("graph_max_data_points") is not None:
            self.max_graph_data_points = int(html_request.form.get("graph_max_data_points"))

        if html_request.form.get("sensor_uptime") is not None:
            self.live_graph_uptime = 1
        if html_request.form.get("cpu_temperature") is not None:
            self.live_graph_cpu_temp = 1
        if html_request.form.get("env_temperature") is not None:
            self.live_graph_env_temp = 1
        if html_request.form.get("pressure") is not None:
            self.live_graph_pressure = 1
        if html_request.form.get("altitude") is not None:
            self.live_graph_altitude = 1
        if html_request.form.get("humidity") is not None:
            self.live_graph_humidity = 1
        if html_request.form.get("dew_point") is not None:
            self.live_graph_dew_point = 1
        if html_request.form.get("distance") is not None:
            self.live_graph_distance = 1
        if html_request.form.get("gas") is not None:
            self.live_graph_gas = 1
        if html_request.form.get("particulate_matter") is not None:
            self.live_graph_particulate_matter = 1
        if html_request.form.get("lumen") is not None:
            self.live_graph_lumen = 1
        if html_request.form.get("colour") is not None:
            self.live_graph_colours = 1
        if html_request.form.get("ultra_violet") is not None:
            self.live_graph_ultra_violet = 1
        if html_request.form.get("accelerometer") is not None:
            self.live_graph_acc = 1
        if html_request.form.get("magnetometer") is not None:
            self.live_graph_mag = 1
        if html_request.form.get("gyroscope") is not None:
            self.live_graph_gyro = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        graph_sensor_address = ""
        if self.graph_sensor_address is not None:
            graph_sensor_address = self.graph_sensor_address
        self.config_settings = [
            str(graph_sensor_address), str(self.live_graph_update_interval), str(self.live_graph_uptime),
            str(self.live_graph_cpu_temp), str(self.live_graph_env_temp), str(self.live_graph_pressure),
            str(self.live_graph_altitude), str(self.live_graph_humidity), str(self.live_graph_dew_point),
            str(self.live_graph_distance), str(self.live_graph_gas), str(self.live_graph_particulate_matter),
            str(self.live_graph_lumen), str(self.live_graph_colours), str(self.live_graph_ultra_violet),
            str(self.live_graph_acc), str(self.live_graph_mag), str(self.live_graph_gyro), str(self.graphs_per_row),
            str(self.enable_ssl_verification), str(self.max_graph_data_points), str(self.enable_performance_mode)
        ]

    def _update_variables_from_settings_list(self):
        try:
            sensor_address = self.config_settings[0].strip()
            if sensor_address != "":
                self.graph_sensor_address = sensor_address
            self.live_graph_update_interval = int(self.config_settings[1].strip())
            self.live_graph_uptime = int(self.config_settings[2].strip())
            self.live_graph_cpu_temp = int(self.config_settings[3].strip())
            self.live_graph_env_temp = int(self.config_settings[4].strip())
            self.live_graph_pressure = int(self.config_settings[5].strip())
            self.live_graph_altitude = int(self.config_settings[6].strip())
            self.live_graph_humidity = int(self.config_settings[7].strip())
            self.live_graph_dew_point = int(self.config_settings[8].strip())
            self.live_graph_distance = int(self.config_settings[9].strip())
            self.live_graph_gas = int(self.config_settings[10].strip())
            self.live_graph_particulate_matter = int(self.config_settings[11].strip())
            self.live_graph_lumen = int(self.config_settings[12].strip())
            self.live_graph_colours = int(self.config_settings[13].strip())
            self.live_graph_ultra_violet = int(self.config_settings[14].strip())
            self.live_graph_acc = int(self.config_settings[15].strip())
            self.live_graph_mag = int(self.config_settings[16].strip())
            self.live_graph_gyro = int(self.config_settings[17].strip())
            self.graphs_per_row = self.config_settings[18].strip()
            self.enable_ssl_verification = int(self.config_settings[19].strip())
            self.max_graph_data_points = int(self.config_settings[20].strip())
            self.enable_performance_mode = int(self.config_settings[21].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Live Graphs Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Live Graphs Configuration.")
                self.save_config_to_file()
