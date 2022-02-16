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
from operations_modules.app_generic_classes import CreateGeneralConfiguration
from operations_modules import app_cached_variables


class CreateDatabaseGraphsConfiguration(CreateGeneralConfiguration):
    """ Creates the Database Graphs Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True, config_file_location=None):
        if config_file_location is None:
            config_file_location = file_locations.db_graphs_config
        CreateGeneralConfiguration.__init__(self, config_file_location, load_from_file=load_from_file)
        self.config_file_header = "Database Graphs Configuration. Enable = 1 and Disable = 0"
        self.valid_setting_count = 32
        self.config_settings_names = [
            "SQL Recording Type", "Render Engine", "Maximum Data Points per Graph", "Skip Data Points between Plots",
            "DateTime Offset in Hours", "Start Date", "End Date", "SQL Database Selection", "MQTT Database Checked",
            "MQTT Database Topic (Sensor ID)", "Plotly Graph Save Location", "Enable Uptime", "Enable CPU Temperature",
            "Enable Environmental Temperature", "Enable Pressure", "Enable Altitude", "Enable Humidity",
            "Enable Dew Point", "Enable Distance", "Enable GAS", "Enable Particulate Matter", "Enable Lumen",
            "Enable Colours", "Enable Ultra Violet", "Enable Accelerometer", "Enable Magnetometer", "Enable Gyroscope",
            "Database Location", "Graph Database Table Name", "Graph using Date Range", "Graph Past Hours",
            "Graph Past Hours Multiplier"
        ]

        self.sql_recording_type = app_cached_variables.database_variables.table_interval
        self.render_engine = "OpenGL"  # or CPU
        self.max_graph_data_points = 100000
        self.skip_data_between_plots = 3
        self.date_time_hours_offset = 0.0

        self.graph_past_hours = 7.0
        self.hours_multiplier = 24.0
        self.graph_using_date_range = 0
        self.graph_start_date = "2019-07-01 00:00:00"
        self.graph_end_date = "2219-07-01 00:00:00"

        self.sql_database_selection = "MainDatabase"  # or MQTTSubscriberDatabase or CheckinDatabase
        self.mqtt_database_checked = 0
        self.mqtt_database_topic = ""

        self.database_location = file_locations.sensor_database
        self.graph_db_table = app_cached_variables.database_variables.table_interval
        self.plotly_graph_saved_location = file_locations.plotly_graph_interval

        self.db_graph_uptime = 1
        self.db_graph_cpu_temp = 1
        self.db_graph_env_temp = 1
        self.db_graph_pressure = 1
        self.db_graph_altitude = 1
        self.db_graph_humidity = 1
        self.db_graph_dew_point = 1
        self.db_graph_distance = 1
        self.db_graph_gas = 1
        self.db_graph_particulate_matter = 1
        self.db_graph_lumen = 1
        self.db_graph_colours = 1
        self.db_graph_ultra_violet = 1
        self.db_graph_acc = 1
        self.db_graph_mag = 1
        self.db_graph_gyro = 1

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self.update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self.update_variables_from_settings_list()

    def get_enabled_graph_sensors_list(self):
        sql_column_selection = [
            app_cached_variables.database_variables.all_tables_datetime,
            app_cached_variables.database_variables.sensor_name,
        ]

        if self.db_graph_uptime:
            sql_column_selection.append(app_cached_variables.database_variables.sensor_uptime)
        if self.db_graph_cpu_temp:
            sql_column_selection.append(app_cached_variables.database_variables.system_temperature)
        if self.db_graph_env_temp:
            sql_column_selection.append(app_cached_variables.database_variables.env_temperature)
        if self.db_graph_pressure:
            sql_column_selection.append(app_cached_variables.database_variables.pressure)
        if self.db_graph_altitude:
            sql_column_selection.append(app_cached_variables.database_variables.altitude)
        if self.db_graph_humidity:
            sql_column_selection.append(app_cached_variables.database_variables.humidity)
        if self.db_graph_dew_point:
            sql_column_selection.append(app_cached_variables.database_variables.dew_point)
        if self.db_graph_distance:
            sql_column_selection.append(app_cached_variables.database_variables.distance)
        if self.db_graph_gas:
            sql_column_selection.append(app_cached_variables.database_variables.gas_resistance_index)
            sql_column_selection.append(app_cached_variables.database_variables.gas_nh3)
            sql_column_selection.append(app_cached_variables.database_variables.gas_oxidising)
            sql_column_selection.append(app_cached_variables.database_variables.gas_reducing)
        if self.db_graph_particulate_matter:
            sql_column_selection.append(app_cached_variables.database_variables.particulate_matter_1)
            sql_column_selection.append(app_cached_variables.database_variables.particulate_matter_2_5)
            sql_column_selection.append(app_cached_variables.database_variables.particulate_matter_4)
            sql_column_selection.append(app_cached_variables.database_variables.particulate_matter_10)
        if self.db_graph_lumen:
            sql_column_selection.append(app_cached_variables.database_variables.lumen)
        if self.db_graph_colours:
            sql_column_selection.append(app_cached_variables.database_variables.red)
            sql_column_selection.append(app_cached_variables.database_variables.orange)
            sql_column_selection.append(app_cached_variables.database_variables.yellow)
            sql_column_selection.append(app_cached_variables.database_variables.green)
            sql_column_selection.append(app_cached_variables.database_variables.blue)
            sql_column_selection.append(app_cached_variables.database_variables.violet)
        if self.db_graph_ultra_violet:
            sql_column_selection.append(app_cached_variables.database_variables.ultra_violet_index)
            sql_column_selection.append(app_cached_variables.database_variables.ultra_violet_a)
            sql_column_selection.append(app_cached_variables.database_variables.ultra_violet_b)
        if self.db_graph_acc:
            sql_column_selection.append(app_cached_variables.database_variables.acc_x)
            sql_column_selection.append(app_cached_variables.database_variables.acc_y)
            sql_column_selection.append(app_cached_variables.database_variables.acc_z)
        if self.db_graph_mag:
            sql_column_selection.append(app_cached_variables.database_variables.mag_x)
            sql_column_selection.append(app_cached_variables.database_variables.mag_y)
            sql_column_selection.append(app_cached_variables.database_variables.mag_z)
        if self.db_graph_gyro:
            sql_column_selection.append(app_cached_variables.database_variables.gyro_x)
            sql_column_selection.append(app_cached_variables.database_variables.gyro_y)
            sql_column_selection.append(app_cached_variables.database_variables.gyro_z)
        return sql_column_selection

    def update_with_html_request(self, html_request):
        """ Updates the Database Graphs configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Database Graphs Configuration Update Check")
        self.mqtt_database_checked = 0
        self.graph_using_date_range = 0

        self.db_graph_uptime = 0
        self.db_graph_cpu_temp = 0
        self.db_graph_env_temp = 0
        self.db_graph_pressure = 0
        self.db_graph_altitude = 0
        self.db_graph_humidity = 0
        self.db_graph_dew_point = 0
        self.db_graph_distance = 0
        self.db_graph_gas = 0
        self.db_graph_particulate_matter = 0
        self.db_graph_lumen = 0
        self.db_graph_colours = 0
        self.db_graph_ultra_violet = 0
        self.db_graph_acc = 0
        self.db_graph_mag = 0
        self.db_graph_gyro = 0

        if html_request.form.get("manual_date_range") is not None:
            self.graph_using_date_range = 1
            # The datetime format should look like "2019-01-01 00:00:00"
            if html_request.form.get("graph_datetime_start") is not None:
                self.graph_start_date = str(html_request.form.get("graph_datetime_start")).replace("T", " ") + ":00"
            if html_request.form.get("graph_datetime_end") is not None:
                self.graph_end_date = str(html_request.form.get("graph_datetime_end")).replace("T", " ") + ":00"
        else:
            try:
                self.hours_multiplier = 1.0
                if html_request.form.get("time_interval_selection") == "Days":
                    self.hours_multiplier = 24.0
                elif html_request.form.get("time_interval_selection") == "Years":
                    self.hours_multiplier = 8760.0
                self.graph_past_hours = self.hours_multiplier * float(html_request.form.get("graph_past_hours"))
            except Exception as error:
                logger.primary_logger.error("Database Graphs Config - Graph past hours: " + str(error))
                self.graph_past_hours = 7.0
                self.hours_multiplier = 24.0

        if html_request.form.get("sql_recording_type") is not None:
            self.sql_recording_type = str(html_request.form.get("sql_recording_type"))
        if html_request.form.get("plotly_render_engine") is not None:
            self.render_engine = str(html_request.form.get("plotly_render_engine"))

        if html_request.form.get("graph_max_data_points") is not None:
            self.max_graph_data_points = int(html_request.form.get("graph_max_data_points"))
        if html_request.form.get("graph_skip_data_points") is not None:
            self.skip_data_between_plots = int(html_request.form.get("graph_skip_data_points"))

        if html_request.form.get("utc_hour_offset") is not None:
            self.date_time_hours_offset = float(html_request.form.get("utc_hour_offset"))

        if html_request.form.get("mqtt_database_checked") is not None:
            self.mqtt_database_checked = 1
        if html_request.form.get("mqtt_database_topic") is not None:
            remote_sensor_id = str(html_request.form.get("mqtt_database_topic")).strip()
            self.mqtt_database_topic = "Invalid_MQTT_Sensor_ID"
            if remote_sensor_id.isalnum() and len(remote_sensor_id) < 65:
                self.mqtt_database_topic = remote_sensor_id

        if html_request.form.get("sql_database_selection") is not None:
            self.sql_database_selection = str(html_request.form.get("sql_database_selection"))
            self.graph_db_table = self.sql_recording_type
            if self.sql_database_selection == "MainDatabase":
                self.database_location = file_locations.sensor_database
                self.plotly_graph_saved_location = file_locations.plotly_graph_interval
                if self.sql_recording_type == app_cached_variables.database_variables.table_trigger:
                    self.plotly_graph_saved_location = file_locations.plotly_graph_triggers
            elif self.sql_database_selection == "MQTTSubscriberDatabase":
                self.database_location = file_locations.mqtt_subscriber_database
                self.plotly_graph_saved_location = file_locations.plotly_graph_mqtt
                self.graph_db_table = str(self.mqtt_database_topic)
            else:
                self.database_location = file_locations.uploaded_databases_folder + "/" + self.sql_database_selection
                self.plotly_graph_saved_location = file_locations.plotly_graph_custom
                if self.mqtt_database_checked:
                    self.graph_db_table = str(self.mqtt_database_topic)

        if html_request.form.get("sensor_uptime") is not None:
            self.db_graph_uptime = 1
        if html_request.form.get("cpu_temperature") is not None:
            self.db_graph_cpu_temp = 1
        if html_request.form.get("env_temperature") is not None:
            self.db_graph_env_temp = 1
        if html_request.form.get("pressure") is not None:
            self.db_graph_pressure = 1
        if html_request.form.get("altitude") is not None:
            self.db_graph_altitude = 1
        if html_request.form.get("humidity") is not None:
            self.db_graph_humidity = 1
        if html_request.form.get("dew_point") is not None:
            self.db_graph_dew_point = 1
        if html_request.form.get("distance") is not None:
            self.db_graph_distance = 1
        if html_request.form.get("gas") is not None:
            self.db_graph_gas = 1
        if html_request.form.get("particulate_matter") is not None:
            self.db_graph_particulate_matter = 1
        if html_request.form.get("lumen") is not None:
            self.db_graph_lumen = 1
        if html_request.form.get("colour") is not None:
            self.db_graph_colours = 1
        if html_request.form.get("ultra_violet") is not None:
            self.db_graph_ultra_violet = 1
        if html_request.form.get("accelerometer") is not None:
            self.db_graph_acc = 1
        if html_request.form.get("magnetometer") is not None:
            self.db_graph_mag = 1
        if html_request.form.get("gyroscope") is not None:
            self.db_graph_gyro = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [
            str(self.sql_recording_type), str(self.render_engine), str(self.max_graph_data_points),
            str(self.skip_data_between_plots), str(self.date_time_hours_offset), str(self.graph_start_date),
            str(self.graph_end_date), str(self.sql_database_selection), str(self.mqtt_database_checked),
            str(self.mqtt_database_topic), str(self.plotly_graph_saved_location), str(self.db_graph_uptime),
            str(self.db_graph_cpu_temp), str(self.db_graph_env_temp), str(self.db_graph_pressure),
            str(self.db_graph_altitude), str(self.db_graph_humidity), str(self.db_graph_dew_point),
            str(self.db_graph_distance), str(self.db_graph_gas), str(self.db_graph_particulate_matter),
            str(self.db_graph_lumen), str(self.db_graph_colours), str(self.db_graph_ultra_violet),
            str(self.db_graph_acc), str(self.db_graph_mag), str(self.db_graph_gyro), str(self.database_location),
            str(self.graph_db_table), str(self.graph_using_date_range), str(self.graph_past_hours),
            str(self.hours_multiplier)
        ]

    def update_variables_from_settings_list(self):
        try:
            self.sql_recording_type = self.config_settings[0].strip()
            self.render_engine = self.config_settings[1].strip()
            self.max_graph_data_points = int(self.config_settings[2].strip())
            self.skip_data_between_plots = int(self.config_settings[3].strip())
            self.date_time_hours_offset = float(self.config_settings[4].strip())
            self.graph_start_date = self.config_settings[5].strip()
            self.graph_end_date = self.config_settings[6].strip()
            self.sql_database_selection = self.config_settings[7].strip()
            self.mqtt_database_checked = int(self.config_settings[8].strip())
            self.mqtt_database_topic = self.config_settings[9].strip()
            self.plotly_graph_saved_location = self.config_settings[10].strip()
            self.db_graph_uptime = int(self.config_settings[11].strip())
            self.db_graph_cpu_temp = int(self.config_settings[12].strip())
            self.db_graph_env_temp = int(self.config_settings[13].strip())
            self.db_graph_pressure = int(self.config_settings[14].strip())
            self.db_graph_altitude = int(self.config_settings[15].strip())
            self.db_graph_humidity = int(self.config_settings[16].strip())
            self.db_graph_dew_point = int(self.config_settings[17].strip())
            self.db_graph_distance = int(self.config_settings[18].strip())
            self.db_graph_gas = int(self.config_settings[19].strip())
            self.db_graph_particulate_matter = int(self.config_settings[20].strip())
            self.db_graph_lumen = int(self.config_settings[21].strip())
            self.db_graph_colours = int(self.config_settings[22].strip())
            self.db_graph_ultra_violet = int(self.config_settings[23].strip())
            self.db_graph_acc = int(self.config_settings[24].strip())
            self.db_graph_mag = int(self.config_settings[25].strip())
            self.db_graph_gyro = int(self.config_settings[26].strip())
            self.database_location = self.config_settings[27].strip()
            self.graph_db_table = self.config_settings[28].strip()
            self.graph_using_date_range = int(self.config_settings[29].strip())
            self.graph_past_hours = float(self.config_settings[30].strip())
            self.hours_multiplier = float(self.config_settings[31].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Database Graphs Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Database Graphs Configuration.")
                self.save_config_to_file()
