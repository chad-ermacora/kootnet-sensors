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


class CreateCheckinConfiguration(CreateGeneralConfiguration):
    """ Creates the Checkin Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.checkin_configuration, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 16
        self.config_settings_names = [
            "Enable Check-Ins Server", "Count Sensors Checked-In the past X Days",
            "Delete sensors with checkin older then X Days", "Send Sensor Name with Checkins",  "Send IP with Checkins",
            "Send Program Version with Checkins",  "Send Installed Sensors with Checkins",
            "Send System Uptime with Checkins",  "Send System Temperature with Checkins",  "Max Logs Lines to send",
            "Send Primary Logs with Checkins", "Send Network Logs with Checkins",  "Send Sensors Logs with Checkins",
            "Enable Sensor Checkins", "Hours between Sensor Checkins", "Sensor Checkin URL & Port"
        ]

        self.enable_checkin_recording = 0
        self.main_page_max_sensors = 10

        self.count_contact_days = 7.0
        self.delete_sensors_older_days = 365.0

        # These settings are used when sending a sensor checkin to a server.
        self.enable_checkin = 1
        self.checkin_wait_in_hours = 24
        self.checkin_url = "server.dragonwarz.net:10065"

        self.send_sensor_name = 0
        self.send_ip = 0
        self.send_program_version = 1
        self.send_installed_sensors = 1
        self.send_system_uptime = 1
        self.send_system_temperature = 1
        self.max_log_lines_to_send = 40
        self.send_primary_log = 1
        self.send_network_log = 0
        self.send_sensors_log = 1

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request, skip_all_but_delete_setting=False):
        """ Updates the Checkin Server configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Checkin Configuration Update Check")

        if not skip_all_but_delete_setting:
            self.enable_checkin_recording = 0
            if html_request.form.get("enable_checkin") is not None:
                self.enable_checkin_recording = 1
            if html_request.form.get("contact_in_past_days") is not None:
                self.count_contact_days = float(html_request.form.get("contact_in_past_days"))
        if html_request.form.get("delete_sensors_older_days") is not None:
            self.delete_sensors_older_days = float(html_request.form.get("delete_sensors_older_days"))
        self.update_configuration_settings_list()

    def update_with_html_request_advanced_checkin(self, html_request):
        """ Updates the Advanced Checkin configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Checkin Configuration Update Check")
        self.enable_checkin = 0
        self.send_sensor_name = 0
        self.send_ip = 0
        self.send_program_version = 0
        self.send_system_uptime = 0
        self.send_installed_sensors = 0
        self.send_system_temperature = 0
        self.send_primary_log = 0
        self.send_network_log = 0
        self.send_sensors_log = 0

        if html_request.form.get("enable_checkin") is not None:
            self.enable_checkin = 1
        if html_request.form.get("checkin_hours") is not None:
            self.checkin_wait_in_hours = float(html_request.form.get("checkin_hours"))
        if html_request.form.get("checkin_address") is not None:
            self.checkin_url = str(html_request.form.get("checkin_address")).strip()
            if ":" not in self.checkin_url:
                self.checkin_url = self.checkin_url + ":10065"

        if html_request.form.get("max_lines_per_log") is not None:
            try:
                new_number = int(html_request.form.get("max_lines_per_log"))
                self.max_log_lines_to_send = new_number
            except Exception as error:
                logger.network_logger.error("Invalid Max Lines Setting for Checkins: " + str(error))

        if html_request.form.get("sensor_name") is not None:
            self.send_sensor_name = 1
        if html_request.form.get("ip_address") is not None:
            self.send_ip = 1
        if html_request.form.get("program_version") is not None:
            self.send_program_version = 1
        if html_request.form.get("sensor_uptime") is not None:
            self.send_system_uptime = 1
        if html_request.form.get("system_temperature") is not None:
            self.send_system_temperature = 1
        if html_request.form.get("installed_sensors") is not None:
            self.send_installed_sensors = 1
        if html_request.form.get("primary_log") is not None:
            self.send_primary_log = 1
        if html_request.form.get("network_log") is not None:
            self.send_network_log = 1
        if html_request.form.get("sensors_log") is not None:
            self.send_sensors_log = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_checkin_recording), str(self.count_contact_days), str(self.delete_sensors_older_days),
            str(self.send_sensor_name), str(self.send_ip), str(self.send_program_version),
            str(self.send_installed_sensors), str(self.send_system_uptime), str(self.send_system_temperature),
            str(self.max_log_lines_to_send), str(self.send_primary_log), str(self.send_network_log),
            str(self.send_sensors_log), str(self.enable_checkin), str(self.checkin_wait_in_hours), str(self.checkin_url)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_checkin_recording = int(self.config_settings[0])
            self.count_contact_days = float(self.config_settings[1])
            self.delete_sensors_older_days = float(self.config_settings[2])
            self.send_sensor_name = int(self.config_settings[3])
            self.send_ip = int(self.config_settings[4])
            self.send_program_version = int(self.config_settings[5])
            self.send_installed_sensors = int(self.config_settings[6])
            self.send_system_uptime = int(self.config_settings[7])
            self.send_system_temperature = int(self.config_settings[8])
            self.max_log_lines_to_send = int(self.config_settings[9])
            self.send_primary_log = int(self.config_settings[10])
            self.send_network_log = int(self.config_settings[11])
            self.send_sensors_log = int(self.config_settings[12])
            self.enable_checkin = int(self.config_settings[13])
            self.checkin_wait_in_hours = float(self.config_settings[14])
            self.checkin_url = self.config_settings[15].strip()
        except Exception as error:
            logger.primary_logger.debug("Checkin Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Checkin Configuration.")
                self.save_config_to_file()
