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
import logging
from hashlib import scrypt, md5
from datetime import datetime, timedelta
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from threading import Thread
from operations_modules import logger
from operations_modules import app_cached_variables
try:
    # In try statement so import does not prevent loading when missing
    import requests
except Exception as import_error:
    logger.primary_logger.debug("requests python module import error: " + str(import_error))

logging.captureWarnings(True)
get_sensor_reading_error_msg = "Unable to get Sensor Reading/File"
network_get_commands = app_cached_variables.CreateNetworkGetCommands()


class CreateGeneralConfiguration:
    """ Base Configuration Template Class """

    def __init__(self, config_file_location, load_from_file=True):
        self.load_from_file = load_from_file
        self.config_file_location = config_file_location
        self.config_file_header = "General Configuration File"
        self.valid_setting_count = 0
        self.config_settings = []
        self.config_settings_names = []

    def _init_config_variables(self):
        """ Sets configuration settings from file, saves default if missing. """

        try:
            if self.check_config_file_exists():
                self.set_config_with_str(get_file_content(self.config_file_location))
        except Exception as error:
            log_msg = "Error setting variables from "
            log_msg2 = "Saving Default Configuration for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location) + " - " + str(error))
            logger.primary_logger.warning(log_msg2 + str(self.config_file_location))
            self.save_config_to_file()

    def check_config_file_exists(self):
        if not os.path.isfile(self.config_file_location):
            logger.primary_logger.info(self.config_file_location + " Not found, saving default")
            self.save_config_to_file()
            return False
        return True

    def save_config_to_file(self):
        """ Saves configuration to file. """
        logger.primary_logger.debug("Saving Configuration to " + str(self.config_file_location))

        write_file_to_disk(self.config_file_location, self.get_config_as_str())

    def get_config_as_str(self):
        """ Returns configuration as a String. """
        logger.primary_logger.debug("Returning Configuration as string for " + str(self.config_file_location))

        new_file_content = self.config_file_header + "\n"
        for setting, setting_name in zip(self.config_settings, self.config_settings_names):
            new_file_content += str(setting) + " = " + str(setting_name) + "\n"
        return new_file_content

    def set_config_with_str(self, config_file_text):
        """ Sets configuration with the provided Text. """

        if config_file_text is not None:
            config_file_text = config_file_text.strip().split("\n")
            config_file_text = config_file_text[1:]  # Remove the header that's not a setting
            if not self.valid_setting_count == len(config_file_text):
                if self.load_from_file:
                    log_msg = "Invalid number of settings found in "
                    logger.primary_logger.warning(log_msg + str(self.config_file_location) + " - Please Check Config")

            self.config_settings = []
            for line in config_file_text:
                try:
                    line_split = line.split("=")
                    setting = line_split[0].strip()
                except Exception as error:
                    if self.load_from_file:
                        logger.primary_logger.warning(str(self.config_file_location) + " - " + str(error))
                    setting = "error"
                self.config_settings.append(setting)
        else:
            if self.load_from_file:
                logger.primary_logger.error("Null configuration text provided " + str(self.config_file_location))


class CreateMonitoredThread:
    """
    Creates a thread and checks every 30 seconds to make sure its still running.
    If the thread stops, it will be restarted up to 5 times by default.
    If it gets restarted more then 5 times, it logs an error message and stops.
    """

    def __init__(self, function, args=None, thread_name="Generic Thread", max_restart_tries=10):
        self.is_running = True
        self.current_state = "Starting"
        self.function = function
        self.args = args
        self.thread_name = thread_name
        self.current_restart_count = 0
        self.max_restart_count = max_restart_tries

        self.shutdown_thread = False

        if self.args is not None:
            self.monitored_thread = Thread(target=self.function, args=self.args)
        else:
            self.monitored_thread = Thread(target=self.function)
        self.monitored_thread.daemon = True

        self.watch_thread = Thread(target=self._thread_and_monitor)
        self.watch_thread.daemon = True
        self.watch_thread.start()

        self.restart_watch_thread = Thread(target=self._restart_count_reset_watch)
        self.restart_watch_thread.daemon = True
        self.restart_watch_thread.start()
        self.current_state = "Running"

    def _restart_count_reset_watch(self):
        """ Resets self.current_restart_count to 0 if it's been longer then 60 seconds since a restart. """

        last_restart_time = time.time()
        last_count = 0
        while True:
            if self.current_restart_count:
                if last_count != self.current_restart_count:
                    last_count = self.current_restart_count
                    last_restart_time = time.time()
                elif time.time() - last_restart_time > 60:
                    self.current_restart_count = 0
            time.sleep(30)

    def _thread_and_monitor(self):
        logger.primary_logger.debug(" -- Starting " + self.thread_name + " Thread")

        self.monitored_thread.start()
        while not self.shutdown_thread:
            if not self.monitored_thread.is_alive():
                logger.primary_logger.info(self.thread_name + " Restarting...")
                self.is_running = False
                self.current_state = "Restarting"
                self.current_restart_count += 1
                if self.current_restart_count < self.max_restart_count:
                    if self.args is None:
                        self.monitored_thread = Thread(target=self.function)
                    else:
                        self.monitored_thread = Thread(target=self.function, args=self.args)
                    self.monitored_thread.daemon = True
                    self.monitored_thread.start()
                    self.is_running = True
                    self.current_state = "Running"
                else:
                    log_msg = self.thread_name + " has restarted " + str(self.current_restart_count)
                    log_msg += " times in less then 1 minutes."
                    logger.primary_logger.critical(log_msg + " No further restart attempts will be made.")
                    self.current_state = "Error"
                    while True:
                        time.sleep(600)
            time.sleep(5)
        self.current_state = "Stopped"
        self.shutdown_thread = False


def thread_function(function, args=None):
    """ Starts provided function as a thread with optional arguments. """

    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)
    system_thread.daemon = True
    system_thread.start()


def start_and_wait_threads(threads_list):
    """ Starts provided list of threads and waits for them all to complete. """

    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()


def get_list_of_filenames_in_dir(folder_location, sort_list=True):
    """
    Takes a folder argument and returns a list of filenames from it
    Optional: Set sort_list to True or False to return a sorted list, Default = True
    """
    return_filenames_list = []
    try:
        _, _, filenames = next(os.walk(folder_location))
        for f_name in filenames:
            return_filenames_list.append(f_name)
        if sort_list:
            return_filenames_list.sort()
    except Exception as custom_db_error:
        log_msg = " -- Error getting list of filenames in folder " + folder_location + ": "
        logger.primary_logger.warning(log_msg + str(custom_db_error))
    return return_filenames_list


def get_file_size(file_location, round_to=2, return_as_level=1):
    """
     Returns provided file size. By default returns main Database Size.
     Set return_as_level to 0 for bytes, 1 for MB and 2 for GB.
     Set round_to for remainder length (Default 2).
    """
    if os.path.isfile(file_location):
        db_size = os.path.getsize(file_location)
        if db_size != 0:
            if return_as_level == 1:
                db_size = db_size / 1024 / 1024
            elif return_as_level == 2:
                db_size = db_size / 1024 / 1024 / 1024
            db_size = round(db_size, round_to)
        return db_size
    return "0.0"


def get_zip_size(zip_file):
    """ Returns the size of provided Zip file. """

    files_size = 0.0
    try:
        with ZipFile(zip_file, 'r') as zip_file_access:
            for info in zip_file_access.infolist():
                files_size += info.compress_size
    except Exception as error:
        logger.primary_logger.error("Error during get zip size: " + str(error))
    return files_size


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns it's content. """
    logger.primary_logger.debug("Loading File: " + str(load_file))

    if os.path.isfile(load_file):
        try:
            with open(load_file, open_type) as loaded_file:
                file_content = loaded_file.read()
        except Exception as error:
            file_content = ""
            logger.primary_logger.error("Unable to load " + load_file + " - " + str(error))
        return file_content
    else:
        logger.primary_logger.debug(load_file + " not found")
    return ""


def write_file_to_disk(file_location, file_content, open_type="w"):
    """ Writes provided file and content to local disk. """
    logger.primary_logger.debug("Writing content to " + str(file_location))

    try:
        with open(file_location, open_type) as write_file:
            write_file.write(file_content)
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))


def zip_files(file_names_list, files_content_list, save_type="get_bytes_io", file_location="", skip_datetime=False):
    """
    Creates a zip of 1 or more files provided as a list.
    Saves to memory or disk based on save_type & file_location
    """

    try:
        if save_type == "get_bytes_io":
            return_zip_file = BytesIO()
        else:
            return_zip_file = file_location
        date_time = time.localtime(time.time())[:6]

        file_meta_data_list = []
        for name in file_names_list:
            name_data = ZipInfo(name)
            if not skip_datetime:
                name_data.date_time = date_time
            name_data.compress_type = ZIP_DEFLATED
            file_meta_data_list.append(name_data)
        with ZipFile(return_zip_file, "w") as zip_file:
            for file_meta_data, file_content in zip(file_meta_data_list, files_content_list):
                zip_file.writestr(file_meta_data, file_content)
        if save_type == "get_bytes_io":
            return_zip_file.seek(0)
            return return_zip_file
        return "Saved to disk"
    except Exception as error:
        logger.primary_logger.error("Zip Files Failed: " + str(error))
        return "error"


def check_for_port_in_address(address):
    """ Checks provided remote sensor address text (IP or DNS) for a port and if found, returns True, else False. """

    ip_split = address.strip().split(":")
    if len(ip_split) == 2:
        return True
    elif len(ip_split) > 2:
        logger.network_logger.info("IPv6 Used in Sensor Control")
    return False


def get_ip_and_port_split(address):
    """ Takes a text address (IP or DNS) and returns a text list of address, and if found port number. """
    return address.split(":")


def get_http_sensor_reading(sensor_address, http_port="10065", command="CheckOnlineStatus", timeout=10, get_file=False):
    """ Returns requested remote sensor data (based on the provided command data). """

    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/"
        login_credentials = {"login_username": app_cached_variables.http_login,
                             "login_password": app_cached_variables.http_password}
        authenticated_requests = requests.Session()
        if command not in network_get_commands.no_http_auth_required_commands_list:
            authenticated_requests.post(url + "atpro/login", login_credentials, verify=False)
        url = url + command
        tmp_return_data = authenticated_requests.get(url=url, timeout=timeout, verify=False)
        if get_file:
            return tmp_return_data.content
        return tmp_return_data.text
    except Exception as error:
        log_msg = "Remote Sensor Data Request - HTTPS GET Error for " + sensor_address + ": " + str(error)
        logger.network_logger.debug(log_msg)
        return get_sensor_reading_error_msg


def send_http_command(sensor_address, command, included_data=None, test_run=None, http_port="10065", timeout=10):
    """ Sends command and data (if any) to a remote sensor. """

    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/"
        login_credentials = {"login_username": app_cached_variables.http_login,
                             "login_password": app_cached_variables.http_password}
        authenticated_requests = requests.Session()
        if command not in network_get_commands.no_http_auth_required_commands_list:
            authenticated_requests.post(url + "atpro/login", login_credentials, verify=False)

        url = url + command
        command_data = {"command_data": included_data, "test_run": test_run}
        authenticated_requests.put(url=url, timeout=timeout, verify=False, auth=login_credentials, data=command_data)
    except Exception as error:
        log_msg = "Remote Sensor Send Command: HTTPS PUT Error:" + sensor_address + ": " + str(error)
        logger.network_logger.error(log_msg)


def get_html_response_bg_colour(response_time):
    """ Returns background colour to use in Sensor Control HTML pages based on provided sensor response time. """

    try:
        delay_float = float(response_time)
        background_colour = "darkgreen"
        if 0.0 <= delay_float < 0.5:
            pass
        elif 0.5 < delay_float < 0.75:
            background_colour = "#859B14"
        elif 0.75 < delay_float < 1.5:
            background_colour = "#8b4c00"
        elif 1.5 < delay_float:
            background_colour = "red"
    except Exception as error:
        logger.network_logger.debug("Sensor Control - Check Online Status - Bad Delay")
        logger.network_logger.debug("Check Online Status Error: " + str(error))
        background_colour = "purple"
    return background_colour


def adjust_datetime(var_datetime, hour_offset, return_datetime_obj=False):
    """ Adjusts the provided datetime as a string by the provided hour offset and returns the result as a string. """
    datetime_format = "%Y-%m-%d %H:%M:%S"
    min_expected_datetime_length = 19
    max_expected_datetime_length = 26
    cleaned_datetime = var_datetime.strip()

    if min_expected_datetime_length <= len(cleaned_datetime) <= max_expected_datetime_length:
        try:
            year = cleaned_datetime[:4]
            month_var = cleaned_datetime[5:7]
            day_var = cleaned_datetime[8:10]
            hour_var = cleaned_datetime[11:13]
            min_var = cleaned_datetime[14:16]
            second_var = cleaned_datetime[17:19]

            original_date_time = year + "-" + month_var + "-" + day_var + " " + \
                                 hour_var + ":" + min_var + ":" + second_var
            adjusted_date = datetime.strptime(original_date_time, datetime_format)
            adjusted_date = adjusted_date + timedelta(hours=hour_offset)
            replacement_date = adjusted_date.strftime(datetime_format)
            if return_datetime_obj:
                return adjusted_date
            return replacement_date
        except Exception as error:
            logger.primary_logger.warning("Date Adjustment Error: " + str(error))
            return var_datetime
    else:
        logger.primary_logger.debug("DateTime Adjustment input is invalid")
        return var_datetime


def create_password_hash(password, salt=None):
    """
    Creates and returns a [password_hash, password_salt] based on provided password.
    Optional: Provide the salt (must be bytes)
    """
    if salt is None:
        salt = os.urandom(16)
    scrypt_n = 16384
    scrypt_r = 8
    scrypt_p = 1
    try:
        start_time = time.time()
        pass_bytes = password.encode("UTF-8")
        password_hash = scrypt(password=pass_bytes, salt=salt, n=scrypt_n, r=scrypt_r, p=scrypt_p)
        end_time = time.time()
        total_processing_time = round(float(end_time - start_time), 6)
        logger.primary_logger.debug("Password Hash took " + str(total_processing_time) + " Seconds to Create")
        return [password_hash, salt]
    except Exception as error:
        logger.primary_logger.error("Creating Password Hash: " + str(error))
    return ["Hash_Error", "Hash_Error"]


def verify_password_to_hash(password_guess, salt=None, valid_password_hash=None):
    """
    Takes plain text password and creates hash to compare to the saved password hash.
    If hashes are equal, return True, else, return False
    Optional: salt and valid_password_hash, if missing, uses app_cached_variables flask variables
    """
    try:
        if valid_password_hash is None or salt is None:
            valid_password_hash = app_cached_variables.http_flask_password_hash
            salt = app_cached_variables.http_flask_password_salt
        password_guess_hash = create_password_hash(password_guess, salt=salt)[0]
        if password_guess_hash == valid_password_hash:
            return True
    except Exception as error:
        logger.primary_logger.error("Verifying Password Hash: " + str(error))
    return False


def get_md5_hash_of_file(file_location):
    try:
        if type(file_location) is str:
            with open(file_location, "rb") as file:
                file_md5 = md5(file.read()).hexdigest()
        else:
            file_md5 = md5(file_location).hexdigest()
        return file_md5
    except Exception as error:
        logger.primary_logger.warning("Error Creating MD5 of " + str(file_location) + ": " + str(error))
    return None
