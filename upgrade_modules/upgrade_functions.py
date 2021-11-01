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
from threading import Thread
from hashlib import md5
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function
from operations_modules.software_version import CreateRefinedVersion
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications

try:
    import requests
except Exception as import_error:
    print("Please Install Python requests module: " + str(import_error))

http_standard_deb_url = "https://kootenay-networks.com/installers/KootnetSensors_online.deb"
http_developmental_deb_url = "https://kootenay-networks.com/installers/dev/KootnetSensors_online.deb"

kootnet_installers_url = "https://kootenay-networks.com/installers/"
md5_file_url = kootnet_installers_url + "KootnetSensors-deb-MD5.txt"
download_type_http = "HTTP"
download_type_smb = "SMB"

smb_cifs_options = "username=myself,password='123'"
smb_mount_dir = "/tmp/super_nas/"
smb_server = "//USB-Development/"
smb_share = "KootNetSMB/"
smb_deb_installer = "KootnetSensors_online.deb"

upgrade_running_file_location = file_locations.upgrade_scripts_folder + "/upgrade_running.txt"


def start_kootnet_sensors_upgrade(dev_upgrade=False, clean_upgrade=False, download_type=download_type_http):
    """
    Starts the Kootnet Sensors Upgrade process
    :param dev_upgrade: Developmental Upgrade, True/False, Default False
    :param clean_upgrade: Clean Upgrade (Re-Install), True/False, Default False
    :param download_type: Use global variables download_type_http or download_type_smb, Default download_type_http
    :return: Nothing
    """
    if app_cached_variables.sensor_ready_for_upgrade:
        app_cached_variables.sensor_ready_for_upgrade = False
        system_thread = Thread(target=_kootnet_sensors_upgrade, args=[dev_upgrade, clean_upgrade, download_type])
        system_thread.daemon = True
        system_thread.start()
        _set_upgrade_notification_text(dev_upgrade, clean_upgrade, download_type)


def _kootnet_sensors_upgrade(dev_upgrade, clean_upgrade, download_type):
    """
    Initiates Kootnet Sensor's upgrade process.
    This Function is meant to be started in it's own Thread
    :param dev_upgrade: Developmental Upgrade, True/False
    :param clean_upgrade: Delete program folder & main Python virtual environment before install, True/False
    :param download_type: Get upgrade file from HTTP(S) server or SMB server
    :return: Nothing
    """
    upgrade_can_proceed = False

    clean_upgrade_str = "0"
    if clean_upgrade:
        clean_upgrade_str = "1"

    if download_type == download_type_http:
        if dev_upgrade:
            current_online_version = _get_http_url(kootnet_installers_url + "dev/kootnet_version.txt").decode("UTF-8")
            new_version_str = CreateRefinedVersion(current_online_version).get_version_string()
            download_url = http_developmental_deb_url
        else:
            current_online_version = _get_http_url(kootnet_installers_url + "kootnet_version.txt").decode("UTF-8")
            new_version_str = CreateRefinedVersion(current_online_version).get_version_string()
            download_url = http_standard_deb_url

        if new_version_str[:1] == "0":
            new_version_str = "Beta" + new_version_str[1:]

        download_file_location = _save_http_url_to_file(download_url)
        if _verify_http_upgrade_file(download_file_location, _get_md5_for_version(new_version_str)):
            _save_upgrade_config(download_file_location, clean_upgrade_str)
            upgrade_can_proceed = True
        else:
            logger.network_logger.error("Upgrade Cancelled, Bad MD5 Checksum")
    elif download_type == download_type_smb:
        smb_upgrade_file_location = _save_smb_to_file(dev_upgrade)
        if smb_upgrade_file_location is not None:
            _save_upgrade_config(smb_upgrade_file_location, clean_upgrade_str)
            upgrade_can_proceed = True
    if upgrade_can_proceed:
        _set_upgrade_running_variable()
        os.system("systemctl start KootnetSensorsUpgrade.service")
    else:
        atpro_notifications.manage_ks_upgrade(enable=False)
        app_cached_variables.sensor_ready_for_upgrade = True


def _set_upgrade_notification_text(dev_upgrade, clean_upgrade, download_type):
    short_type_msg = "Std " + download_type
    long_type_msg = "Standard " + download_type
    if dev_upgrade:
        short_type_msg = "Dev " + download_type
        long_type_msg = "Developmental " + download_type
    if clean_upgrade:
        short_type_msg += " Re-Install"
    atpro_notifications.manage_ks_upgrade(short_type_msg, long_type_msg)


def _set_upgrade_running_variable():
    try:
        with open(upgrade_running_file_location, "w") as upgrade_file:
            upgrade_file.write("1")
        thread_function(_check_upgrade_still_running)
    except Exception as error:
        logger.network_logger.warning("Accessing upgrade running file: " + str(error))


def _check_upgrade_still_running():
    upgrade_running = 1
    while upgrade_running:
        try:
            with open(upgrade_running_file_location, "r") as upgrade_file:
                upgrade_running = int(upgrade_file.read().strip())
        except Exception as error:
            logger.network_logger.warning("Accessing upgrade running file: " + str(error))
            upgrade_running = 0
        time.sleep(10)
    atpro_notifications.manage_ks_upgrade(enable=False)
    app_cached_variables.sensor_ready_for_upgrade = True


def _save_http_url_to_file(file_url, verify_https=True):
    """
    Downloads & saves HTTP(S) URL to file then returns the file's location
    :param file_url: HTTP(S) URL to a file
    :param verify_https: Verify HTTPS SSL connection, Default: True
    :return: File's locally saved location, on failure None
    """
    try:
        file_name = "http_upgrade_" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S") + "." + file_url.split(".")[-1]
        file_location = file_locations.downloads_folder + "/" + file_name
        if os.path.isfile(file_location):
            os.remove(file_location)

        tmp_return_data = requests.get(url=file_url, timeout=(4, 30), allow_redirects=True, verify=verify_https)

        with open(file_location, "wb") as upgrade_file:
            upgrade_file.write(tmp_return_data.content)
        return file_location
    except Exception as error:
        logger.network_logger.error("HTTP(S) Upgrade URL Download " + file_url + ": " + str(error))
    return None


def _save_smb_to_file(dev_upgrade=False):
    """
    Downloads & saves Kootnet Sensors upgrade file from an SMB server
    :param dev_upgrade: Download the Developmental version, Default False
    :return: Upgrade file's locally saved location, on failure None
    """
    file_name = "smb_upgrade_" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S") + ".deb"
    file_location = file_locations.downloads_folder + "/" + file_name

    try:
        for directory_var in ["/tmp", smb_mount_dir]:
            if not os.path.isdir(directory_var):
                os.mkdir(directory_var)

        if os.path.isfile(file_location):
            os.remove(file_location)

        smb_share_new = smb_share
        if dev_upgrade:
            smb_share_new += "dev/"
        os.system("mount -t cifs " + smb_server + smb_share_new + " " + smb_mount_dir + " -o " + smb_cifs_options +
                  " && sleep 1 && cp " + smb_mount_dir + smb_deb_installer + " " + file_location +
                  " && sleep 1 && umount " + smb_mount_dir)
        return file_location
    except Exception as error:
        logger.network_logger.error("SMB Download: " + str(error))
    return None


def _get_http_url(file_url, verify_https=True):
    """
    Downloads and returns HTTP(S) URL content.
    :param file_url: HTTP(S) URL to a file
    :param verify_https: Verify HTTPS connection, Default: True
    :return: URL file content
    """
    try:
        tmp_return_data = requests.get(url=file_url, timeout=(4, 30), allow_redirects=True, verify=verify_https)
        return tmp_return_data.content
    except Exception as error:
        logger.network_logger.error("URL Download " + file_url + ": " + str(error))
    return None


def _verify_http_upgrade_file(file_location, good_md5_checksum):
    """
    Creates and checks MD5 hash of file and compares it to the provided MD5 hash.
    If they match, returns True, else False
    :param file_location: Upgrade Installer file location
    :param good_md5_checksum: MD5 Checksum the Upgrade file should match
    :return: If Checksums match, True, else False
    """
    file_md5 = "BAD"
    try:
        with open(file_location, "rb") as file:
            file_md5 = md5(file.read()).hexdigest()
    except Exception as error:
        logger.network_logger.warning("Error Creating MD5 of File: " + str(error))

    logger.network_logger.info("Downloaded File MD5: " + file_md5 + " || Online MD5: " + good_md5_checksum)
    if file_md5 == good_md5_checksum:
        logger.network_logger.debug("File MD5 Verified")
        return True
    return False


def _get_md5_for_version(kootnet_version, get_full_installer=False):
    """
    Gets the MD5 checksum for provided version installer
    :param kootnet_version: Kootnet Sensors version you want to get the MD5 checksum of
    :param get_full_installer: Get the full installer instead of the upgrade installer, Default: upgrade installer
    :return: MD5 checksum of provided version's Kootnet Senors installer, on error returns not found message
    """
    versions_md5 = _get_http_url(md5_file_url).decode("UTF-8")
    versions_md5_list = versions_md5.split("\n")
    try:
        for index, version in enumerate(versions_md5_list):
            if kootnet_version == version[:11].strip():
                if get_full_installer:
                    return versions_md5_list[index + 1].split(":")[-1].strip()
                return versions_md5_list[index + 4].split(":")[-1].strip()
    except Exception as error:
        logger.network_logger.warning("Get MD5 checksum failed for version " + kootnet_version + ": " + str(error))
    return kootnet_version + " Not Found"


def _save_upgrade_config(ks_upgrade_file_location, clean_upgrade_str):
    """
    Saves a configuration file to automate Kootnet Sensor's upgrade program
    :param ks_upgrade_file_location: Location of debian upgrade package to install
    :param clean_upgrade_str: Do a 'Clean' upgrade, removes program folder & main virtual environment
    :return: Nothing
    """
    try:
        # Location is hardcoded into kootnet_sensors_upgrade.py in upgrade scripts folder
        with open(file_locations.upgrade_scripts_folder + "/upgrade_options.conf", "w") as info_file:
            config_str = ks_upgrade_file_location
            config_str += "," + clean_upgrade_str
            info_file.write(config_str)
    except Exception as error:
        logger.primary_logger.error("Save Upgrade Configuration Error: " + str(error))
