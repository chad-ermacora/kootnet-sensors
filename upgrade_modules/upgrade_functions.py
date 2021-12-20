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
import time
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, get_md5_hash_of_file, check_if_version_newer
from operations_modules.http_generic_network import get_http_regular_file, check_http_file_exist
from operations_modules.software_version import version
from configuration_modules.app_config_access import urls_config, upgrades_config
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications

download_type_http = upgrades_config.upgrade_type_http
download_type_smb = upgrades_config.upgrade_type_smb
smb_in_use = False


class CreateUpdateChecksInterface:
    def __init__(self, start_auto_checks=None):
        if start_auto_checks is None:
            start_auto_checks = True
        self.running_version = version
        self.new_standard_version = "0.0.0"
        self.new_developmental_version = "0.0.0"
        self.standard_update_available = False
        self.developmental_update_available = False

        self.update_server_file_present_md5 = False
        self.update_server_file_present_version = False
        self.update_server_file_present_full_installer = False
        self.update_server_file_present_upgrade_installer = False
        if start_auto_checks:
            thread_function(self.update_versions_info_variables)
            thread_function(self._thread_worker_update_variables)
        else:
            self._update_new_release_versions()

    def update_versions_info_variables(self):
        self._update_new_release_versions()
        self._check_upgrade_files_present()

    def _thread_worker_update_variables(self):
        while True:
            try:
                time.sleep(upgrades_config.automatic_upgrade_delay_hours * 60 * 60)
                self.update_versions_info_variables()
            except Exception as error:
                logger.network_logger.warning("Failed to check for new versions: " + str(error))

    def _update_new_release_versions(self):
        standard_url = urls_config.url_update_server + "kootnet_version.txt"
        developmental_url = urls_config.url_update_server + "dev/kootnet_version.txt"

        standard_version_available = "Error"
        developmental_version_available = "Error"
        if upgrades_config.selected_upgrade_type == upgrades_config.upgrade_type_http:
            standard_version_available = self._get_cleaned_version(get_http_regular_file(standard_url))
            developmental_version_available = self._get_cleaned_version(get_http_regular_file(developmental_url))
        elif upgrades_config.selected_upgrade_type == upgrades_config.upgrade_type_smb:
            standard_version_available = self._get_cleaned_version(get_smb_file("kootnet_version.txt"))
            developmental_version_available = self._get_cleaned_version(get_smb_file("dev/kootnet_version.txt"))

        self.new_standard_version = standard_version_available
        self.new_developmental_version = developmental_version_available
        if check_if_version_newer(version, standard_version_available):
            self.standard_update_available = True
        if check_if_version_newer(version, developmental_version_available):
            self.developmental_update_available = True
        atpro_notifications.update_ks_upgrade_available(self.new_standard_version)

    @staticmethod
    def _get_cleaned_version(version_text):
        if len(version_text) < 13 and len(version_text.split(".")) == 3:
            return version_text
        return "0.0.0"

    def _check_upgrade_files_present(self):
        self.update_server_file_present_md5 = False
        self.update_server_file_present_version = False
        self.update_server_file_present_full_installer = False
        self.update_server_file_present_upgrade_installer = False

        try:
            update_server_files = [
                "KootnetSensors-deb-MD5.txt", "kootnet_version.txt", "KootnetSensors.deb", "KootnetSensors_online.deb"
            ]
            files_exist_list = []
            if upgrades_config.selected_upgrade_type == upgrades_config.upgrade_type_smb:
                files_exist_list = check_smb_file_exists(update_server_files)
            else:
                for update_file in update_server_files:
                    files_exist_list.append(check_http_file_exist(urls_config.url_update_server + update_file))
            self.update_server_file_present_md5 = files_exist_list[0]
            self.update_server_file_present_version = files_exist_list[1]
            self.update_server_file_present_full_installer = files_exist_list[2]
            self.update_server_file_present_upgrade_installer = files_exist_list[3]
        except Exception as error:
            logger.primary_logger.debug("Update Server File Checks Failed: " + str(error))


class CreateUpgradeScriptInterface:
    def __init__(self):
        self.start_upgrade_script_command = "systemctl start KootnetSensorsUpgrade.service"

        self.download_type = download_type_http
        self.dev_upgrade = False
        self.clean_upgrade = False
        self.thread = True
        self.verify_ssl = True

        self.local_upgrade_file_location = "Updated On start_kootnet_sensors_upgrade()"
        self.currently_released_version = "Updated On start_kootnet_sensors_upgrade()"
        self.currently_released_version_md5 = "Updated On start_kootnet_sensors_upgrade()"
        self.update_available = False  # Updated automatically with self.currently_released_version

    def start_kootnet_sensors_upgrade(self):
        """
        Starts the Kootnet Sensors Upgrade process
        :return: Nothing
        """
        if not app_cached_variables.running_as_service or not app_cached_variables.running_with_root:
            logger.network_logger.info("Upgrade Not Started - Must be running with root & as a service")
        elif app_cached_variables.sensor_ready_for_upgrade and app_cached_variables.pip_ready_for_upgrades:
            if self.thread:
                thread_function(self._kootnet_sensors_upgrade)
            else:
                self._kootnet_sensors_upgrade()
        else:
            logger.network_logger.info("Upgrade Not Started - There is another upgrade already running")

    def _kootnet_sensors_upgrade(self):
        app_cached_variables.sensor_ready_for_upgrade = False
        self._update_local_upgrade_file_location()
        self.update_currently_released_version()
        self._update_validated_md5()

        if self.download_type == download_type_http:
            if self.update_available or self.clean_upgrade:
                self._save_http_upgrade_to_file()
                if self._verify_upgrade_file():
                    self._start_upgrade_script()
            else:
                logger.network_logger.info("Upgrade Cancelled - The latest version or higher is already running")
                app_cached_variables.sensor_ready_for_upgrade = True
        elif self.download_type == download_type_smb:
            self._save_smb_to_file()
            if self._verify_upgrade_file():
                self._start_upgrade_script()
        log_msg = "Upgrade Details || DownloadType: " + self.download_type
        log_msg += " || Dev: " + str(self.dev_upgrade) + " || Clean: " + str(self.clean_upgrade)
        logger.network_logger.debug(log_msg)

    def _update_local_upgrade_file_location(self):
        file_name = self.download_type + "_upgrade_" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S") + ".deb"
        if self.dev_upgrade:
            file_name = "dev_" + file_name
        if self.clean_upgrade:
            file_name = "clean_" + file_name
        file_location = file_locations.downloads_folder + "/" + file_name
        if os.path.isfile(file_location):
            os.remove(file_location)
        self.local_upgrade_file_location = file_location

    def _update_validated_md5(self):
        """
        Updates self.currently_released_version_md5 with MD5 checksum of update installer
        :return: Nothing
        """
        if upgrades_config.md5_validation_enabled:
            verified_md5 = "MD5 or Version File Not Found"
            try:
                upgrade_filename_md5 = upgrades_config.upgrade_filename_md5

                versions_md5 = ""
                if self.download_type == download_type_smb:
                    versions_md5 = get_smb_file(upgrade_filename_md5)
                elif self.download_type == download_type_http:
                    versions_md5 = get_http_regular_file(urls_config.url_update_server + upgrade_filename_md5)

                versions_md5_list = versions_md5.split("\n")

                if len(versions_md5_list) > 4:
                    for index, version_md5_text in enumerate(versions_md5_list):
                        if self.currently_released_version == version_md5_text[:15].split(" ")[0]:
                            verified_md5 = versions_md5_list[index + 4].split(":")[-1].strip()
                            if self.clean_upgrade:
                                verified_md5 = versions_md5_list[index + 1].split(":")[-1].strip()
                            break
            except Exception as error:
                logger.network_logger.warning("Get MD5 checksum failed: " + str(error))
            self.currently_released_version_md5 = verified_md5

    def update_currently_released_version(self):
        http_standard_version_url = urls_config.url_update_server + upgrades_config.upgrade_filename_version
        http_dev_version_url = urls_config.url_update_server + "dev/" + upgrades_config.upgrade_filename_version

        current_online_version = "0.0.0"
        if self.download_type == download_type_http:
            if self.dev_upgrade:
                current_online_version = get_http_regular_file(http_dev_version_url)
            else:
                current_online_version = get_http_regular_file(http_standard_version_url)
        elif self.download_type == download_type_smb:
            if self.dev_upgrade:
                current_online_version = get_smb_file("dev/" + upgrades_config.upgrade_filename_version)
            else:
                current_online_version = get_smb_file(upgrades_config.upgrade_filename_version)
        current_online_version = current_online_version.strip()
        self.update_available = check_if_version_newer(version, current_online_version)
        self.currently_released_version = current_online_version

    def _get_http_download_url(self):
        upgrade_filename_update_installer = upgrades_config.upgrade_filename_update_installer
        upgrade_filename_full_installer = upgrades_config.upgrade_filename_full_installer

        http_standard_deb_url = urls_config.url_update_server + upgrade_filename_update_installer
        http_developmental_deb_url = urls_config.url_update_server + "dev/" + upgrade_filename_update_installer
        http_standard_clean_deb_url = urls_config.url_update_server + upgrade_filename_full_installer
        http_developmental_clean_deb_url = urls_config.url_update_server + "dev/" + upgrade_filename_full_installer

        if self.dev_upgrade:
            download_url = http_developmental_deb_url
            if self.clean_upgrade:
                download_url = http_developmental_clean_deb_url
        else:
            download_url = http_standard_deb_url
            if self.clean_upgrade:
                download_url = http_standard_clean_deb_url
        return download_url

    def _save_http_upgrade_to_file(self):
        """
        Downloads HTTP(S) URL to file
        :return: Nothing
        """
        download_url = self._get_http_download_url()
        try:
            with open(self.local_upgrade_file_location, "wb") as upgrade_file:
                upgrade_file_content = get_http_regular_file(download_url, get_text=False, verify_ssl=self.verify_ssl)
                if type(upgrade_file_content) is str:
                    logger.network_logger.error("Update File is str: " + upgrade_file_content)
                upgrade_file.write(upgrade_file_content)
        except Exception as error:
            logger.network_logger.error("HTTP(S) Upgrade Download " + download_url + ": " + str(error))

    def _save_smb_to_file(self):
        """
        Copies SMB URL to self.local_upgrade_file_location
        :return: Nothing
        """
        smb_deb_installer = upgrades_config.upgrade_filename_update_installer
        if self.clean_upgrade:
            smb_deb_installer = upgrades_config.upgrade_filename_full_installer
        if self.dev_upgrade:
            smb_deb_installer = "dev/" + smb_deb_installer
        get_smb_file(smb_deb_installer, new_location=self.local_upgrade_file_location)

    def _verify_upgrade_file(self):
        """
        Creates and checks MD5 hash of local upgrade file and compares it to the validated MD5 hash.
        :return: If Checksums match, True, else False
        """
        if os.path.isfile(self.local_upgrade_file_location):
            if not upgrades_config.md5_validation_enabled:
                log_msg = "MD5 verification Disabled in Upgrades Configuration - Proceeding with Upgrade"
                logger.network_logger.info(log_msg)
                return True

            file_md5 = get_md5_hash_of_file(self.local_upgrade_file_location)
            if file_md5 is not None and file_md5 == self.currently_released_version_md5:
                log_msg = "Upgrade File MD5 Checksum Verified - Type: " + self.download_type
                log_msg += " | Dev: " + str(self.dev_upgrade) + " | Ver: " + self.currently_released_version
                logger.network_logger.info(log_msg)
                return True
            log_msg = "Upgrade File MD5 Checksum Verification Failed - Type: " + self.download_type
            log_msg += " | Dev: " + str(self.dev_upgrade) + " | Ver: " + self.currently_released_version
            logger.network_logger.warning(log_msg)
            log_msg = "Downloaded Upgrade File MD5: " + str(file_md5)
            log_msg += " || Valid MD5: " + self.currently_released_version_md5
            logger.network_logger.warning(log_msg)
            logger.network_logger.warning("Upgrade Cancelled - Bad MD5 Checksum")
        else:
            logger.network_logger.error("MD5 verification failed - File not found")
        app_cached_variables.sensor_ready_for_upgrade = True
        return False

    def _start_upgrade_script(self):
        """
        Saves a configuration file for Kootnet Sensor's upgrade program & starts it
        :return: Nothing
        """
        _set_upgrade_notification_text(self.download_type, self.dev_upgrade, self.clean_upgrade)
        _set_upgrade_running_variable()

        clean_upgrade_str = "0"
        if self.clean_upgrade:
            clean_upgrade_str = "1"

        try:
            with open(upgrades_config.update_script_config_location, "w") as upgrade_config_file:
                config_str = self.local_upgrade_file_location
                config_str += "," + clean_upgrade_str
                upgrade_config_file.write(config_str)
            os.system(self.start_upgrade_script_command)
        except Exception as error:
            logger.primary_logger.error("Start Upgrade Script: " + str(error))
            app_cached_variables.sensor_ready_for_upgrade = True


def check_smb_file_exists(file_name_list):
    return_file_presence_list = []
    if app_cached_variables.running_with_root:
        _connect_smb()
    else:
        logger.network_logger.debug("Unable to check SMB files without root permissions")
    for file_name in file_name_list:
        smb_file_location = file_locations.smb_mount_dir + file_name
        if not app_cached_variables.running_with_root:
            return_file_presence_list.append(False)
        elif os.path.isfile(smb_file_location):
            return_file_presence_list.append(True)
        else:
            return_file_presence_list.append(False)
    if app_cached_variables.running_with_root:
        _disconnect_smb()
    return return_file_presence_list


def get_smb_file(file_name, new_location=None):
    """
    Gets file from SMB server and returns content or copies it to a new location
    :param file_name: SMB filename
    :param new_location: Location of where to copy file, if None, returns file content as text
    :return: SMB File Content or blank string
    """
    smb_file_location = file_locations.smb_mount_dir + file_name
    file_content = ""
    if not app_cached_variables.running_with_root:
        logger.network_logger.debug("Unable to get SMB files without root permissions")
        return ""

    _connect_smb()
    try:
        if os.path.isfile(smb_file_location):
            if new_location is not None:
                os.system("cp " + smb_file_location + " " + new_location)
            else:
                with open(smb_file_location, "r") as open_file:
                    file_content = open_file.read()
        else:
            logger.network_logger.warning("SMB file not found: " + str(smb_file_location))
    except Exception as error:
        logger.network_logger.error("SMB File Download: " + str(error))
    _disconnect_smb()
    return file_content


def _connect_smb():
    global smb_in_use
    while smb_in_use:
        time.sleep(1)
    smb_in_use = True

    url_update_server_smb = urls_config.url_update_server_smb
    try:
        smb_connect = "mount -t cifs " + url_update_server_smb + " " + file_locations.smb_mount_dir
        smb_connect += " -o username=" + upgrades_config.smb_user + ",password='" + upgrades_config.smb_password + "'"
        os.system(smb_connect)
        time.sleep(0.5)
        return True
    except Exception as error:
        logger.network_logger.error("Connecting to SMB Server " + url_update_server_smb + ": " + str(error))
    smb_in_use = False
    return False


def _disconnect_smb():
    global smb_in_use
    try:
        os.system("umount " + file_locations.smb_mount_dir)
    except Exception as error:
        logger.network_logger.error("Disconnecting SMB Server: " + str(error))
    smb_in_use = False


def _set_upgrade_notification_text(download_type, dev_upgrade, clean_upgrade):
    short_type_msg = "Std " + download_type
    long_type_msg = "Standard " + download_type
    if dev_upgrade:
        short_type_msg = "Dev " + download_type
        long_type_msg = "Developmental " + download_type
    if clean_upgrade:
        short_type_msg += " Re-Install"
    atpro_notifications.manage_ks_upgrade_running(short_type_msg, long_type_msg)


def _set_upgrade_running_variable():
    try:
        with open(file_locations.upgrade_running_file_location, "w") as upgrade_file:
            upgrade_file.write("1")
        thread_function(_check_upgrade_still_running)
    except Exception as error:
        logger.network_logger.warning("Accessing upgrade running file: " + str(error))


def _check_upgrade_still_running():
    upgrade_running = 1
    while upgrade_running:
        try:
            with open(file_locations.upgrade_running_file_location, "r") as upgrade_file:
                upgrade_running = int(upgrade_file.read().strip())
        except Exception as error:
            logger.network_logger.warning("Accessing upgrade running file: " + str(error))
            upgrade_running = 0
        time.sleep(10)
    atpro_notifications.manage_ks_upgrade_running(enable=False)
    app_cached_variables.sensor_ready_for_upgrade = True
