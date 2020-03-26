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
import psutil
import time
import requests
import logging
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from threading import Thread
from operations_modules import logger
from operations_modules import app_cached_variables

logging.captureWarnings(True)


class CreateGeneralConfiguration:
    """ Base Configuration Template Class """

    def __init__(self, config_file_location, load_from_file=True):
        self.load_from_file = load_from_file
        self.config_file_location = config_file_location
        self.config_file_header = "General Configuration File"
        self.valid_setting_count = 0
        self.config_settings = []
        self.config_settings_names = []

        self.bad_config_load = False

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
        if config_file_text is not None:
            config_file_text = config_file_text.strip().split("\n")
            config_file_text = config_file_text[1:]  # Remove the header that's not a setting
            if self.valid_setting_count == len(config_file_text):
                if self.load_from_file:
                    log_msg = "Invalid number of settings found in "
                    logger.primary_logger.warning(log_msg + str(self.config_file_location))
                self.bad_config_load = True

            self.config_settings = []
            for line in config_file_text:
                try:
                    line_split = line.split("=")
                    setting = line_split[0].strip()
                except Exception as error:
                    if self.load_from_file:
                        logger.primary_logger.warning(str(self.config_file_location) + " - " + str(error))
                    self.bad_config_load = True
                    setting = "error"
                self.config_settings.append(setting)
        else:
            if self.load_from_file:
                logger.primary_logger.error("Null configuration text provided " + str(self.config_file_location))
            self.bad_config_load = True


class CreateMonitoredThread:
    """
    Creates a thread and checks every 30 seconds to make sure its still running.
    If the thread stops, it will be restarted up to 5 times by default.
    If it gets restarted more then 5 times, it logs an error message and stops.
    """

    def __init__(self, function, args=None, thread_name="Generic Thread", max_restart_tries=5):
        self.is_running = True
        self.function = function
        self.args = args
        self.thread_name = thread_name
        self.current_restart_count = 0
        self.max_restart_count = max_restart_tries

        if self.args is not None:
            self.monitored_thread = Thread(target=self.function, args=self.args)
        else:
            self.monitored_thread = Thread(target=self.function)
        self.monitored_thread.daemon = True

        self.watch_thread = Thread(target=self._thread_and_monitor)
        self.watch_thread.daemon = True
        self.watch_thread.start()

    def _thread_and_monitor(self):
        logger.primary_logger.debug(" -- Starting " + self.thread_name + " Thread")
        self.monitored_thread.start()
        while True:
            time.sleep(30)
            if not self.monitored_thread.is_alive():
                logger.primary_logger.error(self.thread_name + " Stopped Unexpectedly - Restarting...")
                self.is_running = False
                self.current_restart_count += 1
                if self.current_restart_count < self.max_restart_count:
                    if self.args is not None:
                        self.monitored_thread = Thread(target=self.function, args=self.args)
                    else:
                        self.monitored_thread = Thread(target=self.function)
                    self.monitored_thread.daemon = True
                    self.monitored_thread.start()
                    self.is_running = True
                else:
                    log_msg = self.thread_name + " has attempted to restart " + str(self.current_restart_count)
                    logger.primary_logger.critical(log_msg + " Times.  No further restart attempts will be made.")
                    while True:
                        time.sleep(600)


def start_and_wait_threads(threads_list):
    """ Starts provided list of threads and waits for them all to complete. """
    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()


def get_text_running_thread_state(service_enabled, thread_variable):
    """ Checks to see if a 'service' thread is running and returns the result as text. """
    if service_enabled:
        return_text = "Stopped"
        if thread_variable is None:
            return_text = "Missing Sensor"
        elif thread_variable.is_running:
            return_text = "Running"
    else:
        return_text = "Disabled"
    return return_text


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
        logger.primary_logger.error(load_file + " not found")


def write_file_to_disk(file_location, file_content, open_type="w"):
    """ Writes provided file and content to local disk. """
    logger.primary_logger.debug("Writing content to " + str(file_location))
    try:
        with open(file_location, open_type) as write_file:
            write_file.write(file_content)
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))


def thread_function(function, args=None):
    """ Starts provided function as a thread with optional arguments. """
    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)
    system_thread.daemon = True
    system_thread.start()


def get_http_sensor_reading(sensor_address, http_port="10065", command="CheckOnlineStatus", timeout=10):
    """ Returns requested remote sensor data (based on the provided command data). """
    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/" + command
        login_credentials = (app_cached_variables.http_login, app_cached_variables.http_password)
        tmp_return_data = requests.get(url=url, timeout=timeout, verify=False, auth=login_credentials)
        return tmp_return_data.text
    except Exception as error:
        log_msg = "Remote Sensor Data Request - HTTPS GET Error for " + sensor_address + ": " + str(error)
        logger.network_logger.debug(log_msg)
        return "Error"


def send_http_command(sensor_address, command, included_data=None, test_run=None, http_port="10065", timeout=10):
    """ Sends command and data (if any) to a remote sensor. """
    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/" + command
        login_credentials = (app_cached_variables.http_login, app_cached_variables.http_password)
        command_data = {"command_data": included_data, "test_run": test_run}
        requests.put(url=url, timeout=timeout, verify=False, auth=login_credentials, data=command_data)
    except Exception as error:
        log_msg = "Remote Sensor Send Command: HTTPS PUT Error:" + sensor_address + ": " + str(error)
        logger.network_logger.debug(log_msg)


def get_http_sensor_file(sensor_address, command, http_port="10065"):
    """ Returns requested remote sensor file (based on the provided command data). """
    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/" + command
        login_credentials = (app_cached_variables.http_login, app_cached_variables.http_password)
        tmp_return_data = requests.get(url=url, timeout=(4, 120), verify=False, auth=login_credentials)
        return tmp_return_data.content
    except Exception as error:
        log_msg = "Remote Sensor File Request - HTTPS GET Error for " + sensor_address + ": " + str(error)
        logger.network_logger.debug(log_msg)
        return "Error"


def http_display_text_on_sensor(text_message, sensor_address, http_port="10065"):
    """ Sends provided text message to a remote sensor's display. """
    if check_for_port_in_address(sensor_address):
        ip_and_port = get_ip_and_port_split(sensor_address)
        sensor_address = ip_and_port[0]
        http_port = ip_and_port[1]
    try:
        url = "https://" + sensor_address + ":" + http_port + "/DisplayText"
        login_credentials = (app_cached_variables.http_login, app_cached_variables.http_password)
        send_data = {'command_data': text_message}
        tmp_return_data = requests.put(url=url, timeout=4, data=send_data, verify=False, auth=login_credentials)
        if tmp_return_data.text == "OK":
            return True
    except Exception as error:
        logger.network_logger.error("Unable to display text on Sensor: " + str(error))
    return False


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


def zip_files(file_names_list, files_content_list, save_type="get_bytes_io", file_location=""):
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


def get_data_queue_items():
    """ Returns an item from the app_cached_variables.data_queue. """
    que_data = []
    while not app_cached_variables.data_queue.empty():
        que_data.append(app_cached_variables.data_queue.get())
        app_cached_variables.data_queue.task_done()
    return que_data


def replace_text_lists(original_text, old_list, new_list):
    """
    Replaces text in the provided 'original_text' argument.
    original_text = a string of text.
    old_list = a list of strings to replace in 'original_text'.
    new_list = a list of strings that will replace the 'old_list' list of strings.
    """
    for old_text, new_text in zip(old_list, new_list):
        original_text = original_text.replace(old_text, new_text)
    return original_text


def clear_zip_names():
    """
    Set's all sensor control download names to nothing ("")
    """
    app_cached_variables.sc_reports_zip_name = ""
    app_cached_variables.sc_logs_zip_name = ""
    if app_cached_variables.sc_databases_zip_in_memory:
        app_cached_variables.sc_databases_zip_name = ""
    if app_cached_variables.sc_big_zip_in_memory:
        app_cached_variables.sc_big_zip_name = ""


def save_to_memory_ok(write_size):
    """ Checks to see if there is enough RAM to save file to to memory or not. """
    try:
        # Numbers 1,000,000 / 25,000,000. Not using underscores to maintain compatibility with Python 3.5.x
        if psutil.virtual_memory().available > (write_size * 1000000) + 25000000:
            return True
    except Exception as error:
        logger.primary_logger.warning("Error checking virtual memory: " + str(error))
    return False


def get_response_bg_colour(response_time):
    """ Returns background colour to use in Sensor Control HTML pages based on provided sensor response time. """
    try:
        delay_float = float(response_time)
        background_colour = "green"
        if 0.0 <= delay_float < 0.3:
            pass
        elif 0.3 < delay_float < 0.5:
            background_colour = "yellow"
        elif 0.5 < delay_float < 1.0:
            background_colour = "orange"
        elif 1.0 < delay_float:
            background_colour = "red"
    except Exception as error:
        logger.network_logger.debug("Sensor Control - Check Online Status - Bad Delay")
        logger.network_logger.debug("Check Online Status Error: " + str(error))
        background_colour = "purple"
    return background_colour
