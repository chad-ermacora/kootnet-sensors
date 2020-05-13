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
from threading import Thread
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_validation_checks
from operations_modules.app_generic_functions import CreateGeneralConfiguration, get_http_sensor_reading


class CreateSensorControlConfiguration(CreateGeneralConfiguration):
    """ Creates the HTML Sensor Control Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        html_sensor_control_config = file_locations.html_sensor_control_config
        CreateGeneralConfiguration.__init__(self, html_sensor_control_config, load_from_file=load_from_file)
        self.config_file_header = "This contains saved values for HTML Sensor Control"
        self.valid_setting_count = 22
        self.config_settings_names = ["selected_action", "selected_send_type", "senor_ip_1", "senor_ip_2",
                                      "senor_ip_3", "senor_ip_4", "senor_ip_5", "senor_ip_6", "senor_ip_7",
                                      "senor_ip_8", "senor_ip_9", "senor_ip_10", "senor_ip_11", "senor_ip_12",
                                      "senor_ip_13", "senor_ip_14", "senor_ip_15", "senor_ip_16", "senor_ip_17",
                                      "senor_ip_18", "senor_ip_19", "senor_ip_20"]

        self.radio_check_status = "online_status"
        self.radio_report_combo = "combo_report"
        self.radio_report_system = "systems_report"
        self.radio_report_config = "config_report"
        self.radio_report_test_sensors = "sensors_test_report"
        self.radio_report_sensors_latency = "sensors_latency_report"
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

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def get_raw_ip_addresses_as_list(self):
        """ Returns a list of all IP addresses. """
        current_ip_list = [self.sensor_ip_dns1, self.sensor_ip_dns2, self.sensor_ip_dns3, self.sensor_ip_dns4,
                           self.sensor_ip_dns5, self.sensor_ip_dns6, self.sensor_ip_dns7, self.sensor_ip_dns8,
                           self.sensor_ip_dns9, self.sensor_ip_dns10, self.sensor_ip_dns11, self.sensor_ip_dns12,
                           self.sensor_ip_dns13, self.sensor_ip_dns14, self.sensor_ip_dns15, self.sensor_ip_dns16,
                           self.sensor_ip_dns17, self.sensor_ip_dns18, self.sensor_ip_dns19, self.sensor_ip_dns20]
        return_ip_list = []
        for ip in current_ip_list:
            if ip != "":
                return_ip_list.append(ip)
        return return_ip_list

    def get_clean_ip_addresses_as_list(self):
        """ Returns a list of verified Online remote sensors based on 'Sensor Controls' current address list. """
        raw_ip_list = self.get_raw_ip_addresses_as_list()
        valid_ip_list = []
        online_ip_list = []
        threaded_checks = []
        try:
            for ip in raw_ip_list:
                if app_validation_checks.ip_address_is_valid(ip):
                    valid_ip_list.append(ip)
            for address in valid_ip_list:
                threaded_checks.append(Thread(target=self._check_address, args=[address]))
            for thread in threaded_checks:
                thread.daemon = True
                thread.start()
            for thread in threaded_checks:
                thread.join()

            while not app_cached_variables.flask_return_data_queue.empty():
                online_ip_list.append(app_cached_variables.flask_return_data_queue.get())
                app_cached_variables.flask_return_data_queue.task_done()
        except Exception as error:
            logger.network_logger.error("Sensor Control - Error Processing Address List: " + str(error))
        return online_ip_list

    @staticmethod
    def _check_address(sensor_address):
        """
        Checks if a remote sensor is online and if so, saves the results to a queue.
        Queue located at app_cached_variables.flask_return_data_queue.
        """
        try:
            sensor_online_check = get_http_sensor_reading(sensor_address, timeout=4)
            if sensor_online_check == "OK":
                app_cached_variables.flask_return_data_queue.put(sensor_address)
        except Exception as error:
            logger.network_logger.error("Sensor Control - Error Checking Online Status: " + str(error))

    def update_with_html_request(self, html_request):
        """ Updates the HTML Sensor Control configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Sensor Control Configuration Update Check")
        self.__init__(load_from_file=False)
        try:
            self.selected_action = html_request.form.get(self.config_settings_names[0])
            self.selected_send_type = html_request.form.get(self.config_settings_names[1])
            self.sensor_ip_dns1 = html_request.form.get(self.config_settings_names[2])
            self.sensor_ip_dns2 = html_request.form.get(self.config_settings_names[3])
            self.sensor_ip_dns3 = html_request.form.get(self.config_settings_names[4])
            self.sensor_ip_dns4 = html_request.form.get(self.config_settings_names[5])
            self.sensor_ip_dns5 = html_request.form.get(self.config_settings_names[6])
            self.sensor_ip_dns6 = html_request.form.get(self.config_settings_names[7])
            self.sensor_ip_dns7 = html_request.form.get(self.config_settings_names[8])
            self.sensor_ip_dns8 = html_request.form.get(self.config_settings_names[9])
            self.sensor_ip_dns9 = html_request.form.get(self.config_settings_names[10])
            self.sensor_ip_dns10 = html_request.form.get(self.config_settings_names[11])
            self.sensor_ip_dns11 = html_request.form.get(self.config_settings_names[12])
            self.sensor_ip_dns12 = html_request.form.get(self.config_settings_names[13])
            self.sensor_ip_dns13 = html_request.form.get(self.config_settings_names[14])
            self.sensor_ip_dns14 = html_request.form.get(self.config_settings_names[15])
            self.sensor_ip_dns15 = html_request.form.get(self.config_settings_names[16])
            self.sensor_ip_dns16 = html_request.form.get(self.config_settings_names[17])
            self.sensor_ip_dns17 = html_request.form.get(self.config_settings_names[18])
            self.sensor_ip_dns18 = html_request.form.get(self.config_settings_names[19])
            self.sensor_ip_dns19 = html_request.form.get(self.config_settings_names[20])
            self.sensor_ip_dns20 = html_request.form.get(self.config_settings_names[21])

            http_login = html_request.form.get("sensor_username")
            http_password = html_request.form.get("sensor_password")
            if http_login != "":
                app_cached_variables.http_login = http_login
            if http_password != "":
                app_cached_variables.http_password = http_password
        except Exception as error:
            logger.network_logger.warning("Installed Sensors Configuration Error: " + str(error))
        self._update_configuration_settings_list()
        self.load_from_file = True

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.selected_action), str(self.selected_send_type),
                                str(self.sensor_ip_dns1), str(self.sensor_ip_dns2), str(self.sensor_ip_dns3),
                                str(self.sensor_ip_dns4), str(self.sensor_ip_dns5), str(self.sensor_ip_dns6),
                                str(self.sensor_ip_dns7), str(self.sensor_ip_dns8), str(self.sensor_ip_dns9),
                                str(self.sensor_ip_dns10), str(self.sensor_ip_dns11), str(self.sensor_ip_dns12),
                                str(self.sensor_ip_dns13), str(self.sensor_ip_dns14), str(self.sensor_ip_dns15),
                                str(self.sensor_ip_dns16), str(self.sensor_ip_dns17), str(self.sensor_ip_dns18),
                                str(self.sensor_ip_dns19), str(self.sensor_ip_dns20)]

    def _update_variables_from_settings_list(self):
        bad_load = 0
        try:
            self.selected_action = str(self.config_settings[0])
            self.selected_send_type = str(self.config_settings[1])
            self.sensor_ip_dns1 = str(self.config_settings[2])
            self.sensor_ip_dns2 = str(self.config_settings[3])
            self.sensor_ip_dns3 = str(self.config_settings[4])
            self.sensor_ip_dns4 = str(self.config_settings[5])
            self.sensor_ip_dns5 = str(self.config_settings[6])
            self.sensor_ip_dns6 = str(self.config_settings[7])
            self.sensor_ip_dns7 = str(self.config_settings[8])
            self.sensor_ip_dns8 = str(self.config_settings[9])
            self.sensor_ip_dns9 = str(self.config_settings[10])
            self.sensor_ip_dns10 = str(self.config_settings[11])
            self.sensor_ip_dns11 = str(self.config_settings[12])
            self.sensor_ip_dns12 = str(self.config_settings[13])
            self.sensor_ip_dns13 = str(self.config_settings[14])
            self.sensor_ip_dns14 = str(self.config_settings[15])
            self.sensor_ip_dns15 = str(self.config_settings[16])
            self.sensor_ip_dns16 = str(self.config_settings[17])
            self.sensor_ip_dns17 = str(self.config_settings[18])
            self.sensor_ip_dns18 = str(self.config_settings[19])
            self.sensor_ip_dns19 = str(self.config_settings[20])
            self.sensor_ip_dns20 = str(self.config_settings[21])
        except Exception as error:
            log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
            logger.primary_logger.error(log_msg + str(error))
            bad_load += 100

        if bad_load < 99:
            # Add new Settings here.
            pass

        if bad_load:
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Sensor Control Configuration.")
                self.save_config_to_file()
