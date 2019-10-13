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


class CreateMonitoredThread:
    def __init__(self, function, args=None, thread_name="Generic Thread", max_restart_tries=5):
        self.is_running = True
        self.function = function
        self.args = args
        self.thread_name = thread_name

        self.current_restart_count = 0
        self.max_restart_count = max_restart_tries

        self._thread_and_monitor()

    def _thread_and_monitor(self):
        try:
            monitored_thread = Thread(target=self._worker_thread_and_monitor)
            monitored_thread.daemon = True
            monitored_thread.start()
        except Exception as error:
            logger.primary_logger.error("--- " + self.thread_name + " Thread Failed: " + str(error))

    def _worker_thread_and_monitor(self):
        logger.primary_logger.debug(" -- Starting " + self.thread_name + " Thread")
        if self.args is not None:
            monitored_thread = Thread(target=self.function, args=self.args)
        else:
            monitored_thread = Thread(target=self.function)
        monitored_thread.daemon = True
        monitored_thread.start()

        while True:
            time.sleep(30)
            if not monitored_thread.is_alive():
                logger.primary_logger.error(self.thread_name + " Stopped Unexpectedly - Restarting...")
                self.is_running = False
                self.current_restart_count += 1
                if self.current_restart_count < self.max_restart_count:
                    if self.args is not None:
                        monitored_thread = Thread(target=self.function, args=self.args)
                    else:
                        monitored_thread = Thread(target=self.function)
                    monitored_thread.daemon = True
                    monitored_thread.start()
                    self.is_running = True
                else:
                    log_msg = self.thread_name + " has attempted to restart " + str(self.current_restart_count)
                    logger.primary_logger.critical(log_msg + " Times.  No further restart attempts will be made.")
                    while True:
                        time.sleep(600)


def get_text_running_thread_state(service_enabled, thread_variable):
    if service_enabled:
        return_text = "Stopped"
        if thread_variable is None:
            return_text = "Error"
        elif thread_variable.is_running:
            return_text = "Running"
        elif not thread_variable.is_running:
            return_text = "Stopped"
    else:
        return_text = "Disabled"
    return return_text


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns it's content. """
    logger.primary_logger.debug("Loading File: " + str(load_file))

    if os.path.isfile(load_file):
        try:
            loaded_file = open(load_file, open_type)
            file_content = loaded_file.read()
            loaded_file.close()
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
        write_file = open(file_location, open_type)
        write_file.write(file_content)
        write_file.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))


def thread_function(function, args=None):
    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)

    system_thread.daemon = True
    system_thread.start()


def get_http_sensor_reading(http_ip, http_port="10065", command="CheckOnlineStatus"):
    """ Returns requested sensor data (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/" + command
        tmp_return_data = requests.get(url=url,
                                       timeout=10,
                                       auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                                       verify=False)
        return tmp_return_data.text
    except Exception as error:
        logger.network_logger.debug("Remote Sensor Data Request - HTTPS GET Error for " + http_ip + ": " + str(error))
        return "Error"


def get_http_sensor_file(http_ip, command, http_port="10065"):
    """ Returns requested sensor file (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/" + command
        tmp_return_data = requests.get(url=url,
                                       timeout=(4, 120),
                                       auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                                       verify=False)
        return tmp_return_data.content
    except Exception as error:
        logger.network_logger.debug("Remote Sensor File Request - HTTPS GET Error for " + http_ip + ": " + str(error))
        return "Error"


def http_display_text_on_sensor(text_message, http_ip, http_port="10065"):
    """ Returns requested sensor data (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/DisplayText"
        requests.put(url=url,
                     timeout=4,
                     auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                     data={'command_data': text_message},
                     verify=False)
    except Exception as error:
        logger.network_logger.error("Unable to display text on Sensor: " + str(error))


def zip_files(file_names_list, files_content_list, save_type="get_bytes_io", file_location=""):
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
    files_size = 0.0
    try:
        with ZipFile(zip_file, 'r') as zip_file_access:
            for info in zip_file_access.infolist():
                files_size += info.compress_size
    except Exception as error:
        logger.primary_logger.error("Error during get zip size: " + str(error))
    return files_size


def get_data_queue_items():
    que_data = []
    while not app_cached_variables.data_queue.empty():
        que_data.append(app_cached_variables.data_queue.get())
        app_cached_variables.data_queue.task_done()
    return que_data


def replace_text_lists(text_file, old_list, new_list):
    for old_text, new_text in zip(old_list, new_list):
        text_file = text_file.replace(old_text, new_text)
    return text_file


def clear_zip_names():
    app_cached_variables.sc_reports_zip_name = ""
    app_cached_variables.sc_logs_zip_name = ""
    if app_cached_variables.sc_databases_zip_in_memory:
        app_cached_variables.sc_databases_zip_name = ""
    if app_cached_variables.sc_big_zip_in_memory:
        app_cached_variables.sc_big_zip_name = ""


def save_to_memory_ok(write_size):
    if psutil.virtual_memory().available > (write_size + 25000):
        return True
    return False


def get_response_bg_colour(response_time):
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
