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
import os
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions


class CreateSensorControlConfig:
    """ Creates object with default HTML Sensor Control configuration settings. """

    def __init__(self):
        self.html_post_settings = ["selected_action", "selected_send_type", "senor_ip_1", "senor_ip_2",
                                   "senor_ip_3", "senor_ip_4", "senor_ip_5", "senor_ip_6", "senor_ip_7",
                                   "senor_ip_8", "senor_ip_9", "senor_ip_10", "senor_ip_11", "senor_ip_12",
                                   "senor_ip_13", "senor_ip_14", "senor_ip_15", "senor_ip_16", "senor_ip_17",
                                   "senor_ip_18", "senor_ip_19", "senor_ip_20"]

        self.radio_check_status = "online_status"
        self.radio_report_system = "systems_report"
        self.radio_report_config = "config_report"
        self.radio_report_test_sensors = "sensors_test_report"
        self.radio_download_reports = "sensors_download_reports"
        self.radio_download_databases = "sensors_download_databases"
        self.radio_download_logs = "sensors_download_logs"
        self.radio_create_the_big_zip = "sensors_download_everything"

        self.radio_send_type_relayed = "relayed_download"
        self.radio_send_type_direct = "direct_download"

        self.selected_action = self.radio_check_status
        self.selected_send_type = self.radio_send_type_relayed
        self.sensor_ip_dns1 = ""
        self.sensor_ip_dns2 = ""
        self.sensor_ip_dns3 = ""
        self.sensor_ip_dns4 = ""
        self.sensor_ip_dns5 = ""
        self.sensor_ip_dns6 = ""
        self.sensor_ip_dns7 = ""
        self.sensor_ip_dns8 = ""
        self.sensor_ip_dns9 = ""
        self.sensor_ip_dns10 = ""
        self.sensor_ip_dns11 = ""
        self.sensor_ip_dns12 = ""
        self.sensor_ip_dns13 = ""
        self.sensor_ip_dns14 = ""
        self.sensor_ip_dns15 = ""
        self.sensor_ip_dns16 = ""
        self.sensor_ip_dns17 = ""
        self.sensor_ip_dns18 = ""
        self.sensor_ip_dns19 = ""
        self.sensor_ip_dns20 = ""

    def get_settings_as_str(self):
        """ Takes Sensor Control configuration Object and returns it as a string. """
        config_file_str = "This contains saved values for HTML Sensor Control.\n" + \
                          str(self.selected_action) + " = Default Choice for Action\n" + \
                          str(self.selected_send_type) + " = Default Choice for Download Type (Relayed orDirect)\n" + \
                          str(self.sensor_ip_dns1) + " = Sensor IP / DNS Entry 1\n" + \
                          str(self.sensor_ip_dns2) + " = Sensor IP / DNS Entry 2\n" + \
                          str(self.sensor_ip_dns3) + " = Sensor IP / DNS Entry 3\n" + \
                          str(self.sensor_ip_dns4) + " = Sensor IP / DNS Entry 4\n" + \
                          str(self.sensor_ip_dns5) + " = Sensor IP / DNS Entry 5\n" + \
                          str(self.sensor_ip_dns6) + " = Sensor IP / DNS Entry 6\n" + \
                          str(self.sensor_ip_dns7) + " = Sensor IP / DNS Entry 7\n" + \
                          str(self.sensor_ip_dns8) + " = Sensor IP / DNS Entry 8\n" + \
                          str(self.sensor_ip_dns9) + " = Sensor IP / DNS Entry 9\n" + \
                          str(self.sensor_ip_dns10) + " = Sensor IP / DNS Entry 10\n" + \
                          str(self.sensor_ip_dns11) + " = Sensor IP / DNS Entry 11\n" + \
                          str(self.sensor_ip_dns12) + " = Sensor IP / DNS Entry 12\n" + \
                          str(self.sensor_ip_dns13) + " = Sensor IP / DNS Entry 13\n" + \
                          str(self.sensor_ip_dns14) + " = Sensor IP / DNS Entry 14\n" + \
                          str(self.sensor_ip_dns15) + " = Sensor IP / DNS Entry 15\n" + \
                          str(self.sensor_ip_dns16) + " = Sensor IP / DNS Entry 16\n" + \
                          str(self.sensor_ip_dns17) + " = Sensor IP / DNS Entry 17\n" + \
                          str(self.sensor_ip_dns18) + " = Sensor IP / DNS Entry 18\n" + \
                          str(self.sensor_ip_dns19) + " = Sensor IP / DNS Entry 19\n" + \
                          str(self.sensor_ip_dns20) + " = Sensor IP / DNS Entry 20"
        return config_file_str

    def set_from_html_post(self, html_request):
        new_settings_list = []
        for html_request_setting in self.html_post_settings:
            new_settings_list.append(html_request.form.get(html_request_setting))
        self._update_settings_with_list(new_settings_list)
        http_login = html_request.form.get("sensor_username")
        http_password = html_request.form.get("sensor_password")
        if http_login != "":
            app_cached_variables.http_login = http_login
        if http_password != "":
            app_cached_variables.http_password = http_password

    def set_from_disk(self):
        """ Loads Sensor Control configuration from file and returns it as a configuration object. """
        if os.path.isfile(file_locations.html_sensor_control_config):
            config_content = app_generic_functions.get_file_content(file_locations.html_sensor_control_config).strip()
            self.set_from_raw_config_content(config_content)
        else:
            logger.primary_logger.info("Sensor Control Configuration file not found - Saving Default")
            self.write_current_config_to_file()

    def set_from_raw_config_content(self, sensor_control_config_text):
        """ Converts provided Sensor Control configuration text as a list of lines into a object and returns it. """
        sensor_control_config_text_lines_list = sensor_control_config_text.split("\n")
        new_config_settings_list = []
        for line in sensor_control_config_text_lines_list:
            new_config_settings_list.append(line.split("=")[0].strip())
        self._update_settings_with_list(new_config_settings_list[1:])
        self.write_current_config_to_file()

    def _update_settings_with_list(self, settings_list):
        count = 0
        for new_setting in settings_list:
            if count == 0:
                self.selected_action = new_setting
            if count == 1:
                self.selected_send_type = new_setting
            if count == 2:
                self.sensor_ip_dns1 = new_setting
            if count == 3:
                self.sensor_ip_dns2 = new_setting
            if count == 4:
                self.sensor_ip_dns3 = new_setting
            if count == 5:
                self.sensor_ip_dns4 = new_setting
            if count == 6:
                self.sensor_ip_dns5 = new_setting
            if count == 7:
                self.sensor_ip_dns6 = new_setting
            if count == 8:
                self.sensor_ip_dns7 = new_setting
            if count == 9:
                self.sensor_ip_dns8 = new_setting
            if count == 10:
                self.sensor_ip_dns9 = new_setting
            if count == 11:
                self.sensor_ip_dns10 = new_setting
            if count == 12:
                self.sensor_ip_dns11 = new_setting
            if count == 13:
                self.sensor_ip_dns12 = new_setting
            if count == 14:
                self.sensor_ip_dns13 = new_setting
            if count == 15:
                self.sensor_ip_dns14 = new_setting
            if count == 16:
                self.sensor_ip_dns15 = new_setting
            if count == 17:
                self.sensor_ip_dns16 = new_setting
            if count == 18:
                self.sensor_ip_dns17 = new_setting
            if count == 19:
                self.sensor_ip_dns18 = new_setting
            if count == 20:
                self.sensor_ip_dns19 = new_setting
            if count == 21:
                self.sensor_ip_dns20 = new_setting
            count += 1

    def write_current_config_to_file(self):
        """
        Writes provided Sensor Control configuration file to local disk.
        The provided configuration can be string or object.
        """
        new_config = self.get_settings_as_str()
        app_generic_functions.write_file_to_disk(file_locations.html_sensor_control_config, new_config)
