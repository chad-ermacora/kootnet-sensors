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


class CreateUpgradesConfiguration(CreateGeneralConfiguration):
    """ Creates the Upgrades Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.upgrades_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 9
        self.config_settings_names = [
            "Enable Automatic Upgrades", "Delay in Hours between Automatic Upgrade Checks",
            "SMB Username", "SMB Password", "Selected Upgrade Type", "Enable Automatic Feature version upgrades",
            "Enable Automatic Minor version upgrades", "Enable Automatic Developmental version upgrades",
            "Enable MD5 Validation"
        ]
        self.upgrade_type_http = "http"
        self.upgrade_type_smb = "smb"

        self.enable_automatic_upgrades = 1
        self.automatic_upgrade_delay_hours = 6
        self.smb_user = "Guest"
        self.smb_password = "NoPassword"

        self.selected_upgrade_type = self.upgrade_type_http
        self.enable_automatic_upgrades_feature = 0
        self.enable_automatic_upgrades_minor = 1
        self.enable_automatic_upgrades_developmental = 0
        self.md5_validation_enabled = 1

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    @staticmethod
    def validate_smb_username(username):
        if username is not None:
            if username.isalnum():
                return True
        return False

    @staticmethod
    def validate_smb_password(password):
        # ToDo: I'm expecting there to be other characters that should not be used, will add those later
        invalid_characters_list = ["'"]
        password_valid = True
        if password is None or password == "":
            password_valid = False
        else:
            for invalid_character in invalid_characters_list:
                if invalid_character in password:
                    password_valid = False
        return password_valid

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Upgrades configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Upgrades Configuration Update Check")
        self.enable_automatic_upgrades = 0
        self.enable_automatic_upgrades_feature = 0
        self.enable_automatic_upgrades_minor = 0
        self.enable_automatic_upgrades_developmental = 0
        self.md5_validation_enabled = 0

        if html_request.form.get("enable_auto_upgrades") is not None:
            self.enable_automatic_upgrades = 1

        if html_request.form.get("auto_upgrade_delay_hours") is not None:
            new_hours = float(html_request.form.get("auto_upgrade_delay_hours"))
            if new_hours < 0.25:
                new_hours = 0.25
            self.automatic_upgrade_delay_hours = new_hours

        smb_username = html_request.form.get("smb_username")
        if self.validate_smb_username(smb_username):
            self.smb_user = smb_username.strip()

        smb_password = html_request.form.get("smb_password")
        if self.validate_smb_password(smb_password):
            self.smb_password = smb_password.strip()

        if html_request.form.get("upgrade_method") is not None:
            self.selected_upgrade_type = html_request.form.get("upgrade_method")
        if html_request.form.get("enable_stable_feature_auto_upgrades") is not None:
            self.enable_automatic_upgrades_feature = 1
        if html_request.form.get("enable_stable_minor_auto_upgrades") is not None:
            self.enable_automatic_upgrades_minor = 1
        if html_request.form.get("enable_dev_auto_upgrades") is not None:
            self.enable_automatic_upgrades_developmental = 1
        if html_request.form.get("enable_md5_validation") is not None:
            self.md5_validation_enabled = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_automatic_upgrades), str(self.automatic_upgrade_delay_hours),
            str(self.smb_user), str(self.smb_password), str(self.selected_upgrade_type),
            str(self.enable_automatic_upgrades_feature), str(self.enable_automatic_upgrades_minor),
            str(self.enable_automatic_upgrades_developmental), str(self.md5_validation_enabled)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_automatic_upgrades = int(self.config_settings[0])
            self.automatic_upgrade_delay_hours = float(self.config_settings[1])
            self.smb_user = self.config_settings[2].strip()
            self.smb_password = self.config_settings[3].strip()
            self.selected_upgrade_type = self.config_settings[4].strip()
            self.enable_automatic_upgrades_feature = int(self.config_settings[5])
            self.enable_automatic_upgrades_minor = int(self.config_settings[6])
            self.enable_automatic_upgrades_developmental = int(self.config_settings[7])
            self.md5_validation_enabled = int(self.config_settings[8])
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Upgrades Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Upgrades Configuration.")
                self.save_config_to_file()
