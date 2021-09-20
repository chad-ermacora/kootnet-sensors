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
import time
import requests
from threading import Thread
from queue import Queue
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from http_server.flask_blueprints.html_functional import auth_error_msg
from http_server.flask_blueprints.atpro.remote_management.rm_reports import generate_html_reports_combo

network_commands = app_cached_variables.CreateNetworkGetCommands()
data_queue = Queue()


class CreateSensorHTTPCommand:
    """ Creates Object to use for Sending a command and optional data to a remote sensor. """

    def __init__(self, sensor_address, command, command_data=None):
        if command_data is None:
            self.sensor_command_data = {"NotSet": True}
        else:
            self.sensor_command_data = command_data

        self.sensor_address = sensor_address
        self.http_port = "10065"
        self.sensor_command = command
        self._check_ip_port()

    def send_http_command(self):
        """ Sends command and data to sensor. """
        try:
            url = "https://" + self.sensor_address + ":" + self.http_port + "/" + self.sensor_command
            requests.post(url=url, timeout=5, verify=False, data=self.sensor_command_data,
                          auth=(app_cached_variables.http_login, app_cached_variables.http_password))
        except Exception as error:
            logger.network_logger.error("Unable to send command to " + str(self.sensor_address) + ": " + str(error))

    def _check_ip_port(self):
        if app_generic_functions.check_for_port_in_address(self.sensor_address):
            ip_and_port = app_generic_functions.get_ip_and_port_split(self.sensor_address)
            self.sensor_address = ip_and_port[0]
            self.http_port = ip_and_port[1]


def create_all_databases_zipped(ip_list):
    """
    Downloads remote sensor databases from provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    try:
        _queue_name_and_file_list(ip_list, command=network_commands.sensor_sql_all_databases_zip)

        data_list = get_data_queue_items()
        database_names = []
        sensors_database = []
        for sensor_data in data_list:
            db_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".zip"
            try:
                if sensor_data[2].decode("utf-8") == auth_error_msg:
                    db_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".txt"
            except Exception as error:
                print(str(error))
            database_names.append(db_name)
            sensors_database.append(sensor_data[2])

        write_to_memory = app_generic_functions.save_to_memory_ok(get_sum_db_sizes(ip_list))
        if write_to_memory:
            app_generic_functions.clear_zip_names()
            app_cached_variables.sc_databases_zip_in_memory = True
            app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(database_names, sensors_database)
        else:
            app_cached_variables.sc_databases_zip_in_memory = False
            app_generic_functions.zip_files(database_names,
                                            sensors_database,
                                            save_type="save_to_disk",
                                            file_location=file_locations.html_sensor_control_databases_zip)
        app_cached_variables.sc_databases_zip_name = "Multiple_Databases_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Databases Zip Generation Error: " + str(error))
        app_cached_variables.sc_databases_zip_name = ""
    app_cached_variables.creating_databases_zip = False
    logger.network_logger.info("Sensor Control - Databases Zip Generation Complete")


def create_multiple_sensor_logs_zipped(ip_list):
    """
    Downloads remote sensor logs from provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    try:
        _queue_name_and_file_list(ip_list, command=network_commands.download_zipped_logs)

        data_list = get_data_queue_items()
        zip_names = []
        logs_zipped = []
        for sensor_data in data_list:
            zip_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".zip"
            try:
                if sensor_data[2].decode("utf-8") == auth_error_msg:
                    zip_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".txt"
            except Exception as error:
                print(str(error))
            zip_names.append(zip_name)
            logs_zipped.append(sensor_data[2])

        app_generic_functions.clear_zip_names()
        app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(zip_names, logs_zipped)
        app_cached_variables.sc_logs_zip_name = "Multiple_Logs_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Logs Zip Generation Error: " + str(error))
        app_cached_variables.sc_logs_zip_name = ""
    app_cached_variables.creating_logs_zip = False
    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Complete")


def put_all_reports_zipped_to_cache(ip_list):
    """
    Downloads ALL remote sensor reports from provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    try:
        hostname = app_cached_variables.hostname
        generate_html_reports_combo(ip_list)
        html_reports = [app_cached_variables.html_combo_report]
        html_report_names = ["ReportCombo.html"]
        app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(html_report_names, html_reports)
        app_cached_variables.sc_reports_zip_name = "Reports_from_" + hostname + "_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Reports Zip Generation Error: " + str(error))
    app_cached_variables.creating_the_reports_zip = False
    logger.network_logger.info("Sensor Control - Reports Zip Generation Complete")


def create_the_big_zip(ip_list):
    """
    Downloads everything from sensors based on provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    new_name = "TheBigZip_" + app_cached_variables.hostname + "_" + str(time.time())[:-8] + ".zip"
    app_cached_variables.sc_big_zip_name = new_name

    if len(ip_list) > 0:
        try:
            return_names = ["ReportCombo.html"]
            generate_html_reports_combo(ip_list)
            return_files = [app_cached_variables.html_combo_report]

            _queue_name_and_file_list(ip_list, network_commands.download_zipped_everything)
            ip_name_and_data = get_data_queue_items()

            for sensor in ip_name_and_data:
                current_file_name = sensor[0].split(".")[-1] + "_" + sensor[1] + ".zip"
                try:
                    if sensor[2].decode("utf-8") == auth_error_msg:
                        current_file_name = sensor[0].split(".")[-1] + "_" + sensor[1] + ".txt"
                except Exception as error:
                    print(str(error))

                return_names.append(current_file_name)
                return_files.append(sensor[2])

            if app_generic_functions.save_to_memory_ok(get_sum_db_sizes(ip_list)):
                app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(return_names, return_files)
            else:
                zip_location = file_locations.html_sensor_control_big_zip
                app_generic_functions.zip_files(return_names, return_files, save_type="to_disk",
                                                file_location=zip_location)

            logger.network_logger.info("Sensor Control - The Big Zip Generation Completed")
            app_cached_variables.creating_the_big_zip = False
        except Exception as error:
            logger.primary_logger.error("Sensor Control - Big Zip Error: " + str(error))
            app_cached_variables.creating_the_big_zip = False
            app_cached_variables.sc_big_zip_name = ""


def _queue_name_and_file_list(ip_list, command):
    threads_list = []
    for address in ip_list:
        threads_list.append(Thread(target=_worker_queue_list_ip_name_file, args=[address, command]))
    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()


def _worker_queue_list_ip_name_file(address, command):
    try:
        sensor_name = app_generic_functions.get_http_sensor_reading(address, command="GetHostName")
        sensor_data = app_generic_functions.get_http_sensor_file(address, command)
        data_queue.put([address, sensor_name, sensor_data])
    except Exception as error:
        logger.network_logger.error("Sensor Control - Get Remote File Failed: " + str(error))


def get_sum_db_sizes(ip_list):
    """ Gets the size of remote sensors zipped database based on provided IP or DNS addresses (as a list) """
    databases_size = 0.0
    try:
        threads = []
        for address in ip_list:
            threads.append(Thread(target=_worker_get_db_size, args=[address]))
        app_generic_functions.start_and_wait_threads(threads)

        while not data_queue.empty():
            db_size = data_queue.get()
            databases_size += db_size
            data_queue.task_done()
    except Exception as error:
        logger.network_logger.error("Sensor Control - Unable to retrieve Database Sizes Sum: " + str(error))
    logger.network_logger.debug("Total DB Sizes in MB: " + str(databases_size))
    return databases_size


def _worker_get_db_size(address):
    get_http_sensor_reading = app_generic_functions.get_http_sensor_reading
    get_database_size_command = network_commands.sensor_sql_database_size
    try:
        try_get = True
        get_error_count = 0
        while try_get and get_error_count < 3:
            try:
                db_size = float(get_http_sensor_reading(address, command=get_database_size_command))
                data_queue.put(db_size)
                try_get = False
            except Exception as error:
                log_msg = "Sensor Control - Error getting sensor DB Size for "
                logger.network_logger.error(log_msg + address + " attempt #" + str(get_error_count + 1))
                logger.network_logger.debug("Sensor Control DB Sizes Error: " + str(error))
                get_error_count += 1
        if get_error_count > 2:
            data_queue.put(0)
    except Exception as error:
        log_msg = "Sensor Control - Unable to retrieve Database Size for " + address + ": " + str(error)
        logger.network_logger.error(log_msg)


def get_data_queue_items():
    """ Returns a list of items from a data_queue. """
    que_data = []
    while not data_queue.empty():
        que_data.append(data_queue.get())
        data_queue.task_done()
    return que_data
