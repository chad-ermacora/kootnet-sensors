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
from threading import Thread
from queue import Queue
from flask import render_template
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import zip_files, start_and_wait_threads
from operations_modules.http_generic_network import get_http_sensor_reading, get_http_kootnet_sensor_file, \
    check_for_port_in_address, get_html_response_bg_colour, get_ip_and_port_split
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.remote_management.rm_reports import generate_html_reports_combo
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index
from http_server.server_http_auth import auth_error_msg_contains
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables

network_commands = app_cached_variables.CreateNetworkGetCommands()
data_queue = Queue()


def check_sensor_status_sensor_control(address_list):
    """
    Uses provided remote sensor IP or DNS addresses (as a list) and checks if it's online.
    Returns a flask rendered template with results as an HTML page.
    """
    text_insert = ""
    threads = []
    for address in address_list:
        threads.append(Thread(target=get_remote_sensor_check_and_delay, args=[address, True]))
    start_and_wait_threads(threads)

    address_responses = []
    while not data_queue.empty():
        address_responses.append(data_queue.get())
        data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        new_address = response["address"]
        port = "10065"
        if check_for_port_in_address(new_address):
            new_address, port = get_ip_and_port_split(new_address)
        elif len(new_address.split(":")) > 1:
            new_address = "[" + new_address + "]"
        response_time = response["response_time"]
        background_colour = get_html_response_bg_colour(response_time)
        sensor_url_link = "'https://" + new_address + ":" + port + "/'"

        text_insert += "<tr><th width='160px'><span style='color: white; background-color: " + background_colour + \
                       ";'>" + response_time + " Seconds</span></th>\n<th width='250px'>" + \
                       response["sensor_hostname"] + "</th>\n<th><a target='_blank' href=" + sensor_url_link + ">" + \
                       response["address"] + "</a></th></tr>\n"
    status_page = render_template("ATPro_admin/page_templates/remote_management/online-status-check.html",
                                  SensorResponse=text_insert.strip())
    return get_html_atpro_index(run_script="SelectActiveMainMenu('sensor-rm');", main_page_view_content=status_page)


def clear_zip_names():
    """ Set's all sensor control download names to nothing ("") """

    rm_cached_variables.sc_reports_zip_name = ""
    rm_cached_variables.sc_logs_zip_name = ""
    if rm_cached_variables.sc_databases_zip_in_memory:
        rm_cached_variables.sc_databases_zip_name = ""
    if rm_cached_variables.sc_big_zip_in_memory:
        rm_cached_variables.sc_big_zip_name = ""


def get_remote_sensor_check_and_delay(address, add_hostname=False, add_db_size=False, add_logs_size=False):
    """
    Checks a remote sensor's response time and adds it to the data_queue
    Optional: Include hostname, database size and zipped log size.
    """
    get_sensor_reading = get_http_sensor_reading
    task_start_time = time.time()
    sensor_status = get_sensor_reading(address, timeout=5)
    task_end_time = round(time.time() - task_start_time, 3)
    if sensor_status == "OK":
        sensor_hostname = ""
        download_size = "NA"
        if add_hostname:
            sensor_hostname = get_sensor_reading(address, http_command="GetHostName").strip()
        if add_db_size:
            download_size = get_sensor_reading(address, http_command="GetSQLDBSize").strip()
        if add_logs_size:
            download_size = get_sensor_reading(address, http_command="GetZippedLogsSize").strip()
    else:
        task_end_time = "NA "
        sensor_hostname = "Offline"
        download_size = "NA"
    data_queue.put({"address": address,
                    "status": str(sensor_status),
                    "response_time": str(task_end_time),
                    "sensor_hostname": str(sensor_hostname),
                    "download_size": str(download_size)})


def create_the_big_zip(ip_list):
    """
    Downloads everything from sensors based on provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    new_name = "TheBigZip_" + app_cached_variables.hostname + "_" + str(time.time())[:-8] + ".zip"
    rm_cached_variables.sc_big_zip_name = new_name

    if len(ip_list) > 0:
        try:
            return_names = ["ReportCombo.html"]
            generate_html_reports_combo(ip_list)
            return_files = [rm_cached_variables.html_combo_report]

            _queue_name_and_file_list(ip_list, network_commands.download_zipped_everything)
            ip_name_and_data = get_data_queue_items()

            for sensor in ip_name_and_data:
                current_file_name = sensor[0].split(".")[-1] + "_" + sensor[1] + ".zip"
                try:
                    if auth_error_msg_contains in str(sensor[2]):
                        current_file_name = sensor[0].split(".")[-1] + "_" + sensor[1] + ".txt"
                        sensor[2] = "Incorrect Login Provided"
                except Exception as error:
                    print(str(error))

                return_names.append(current_file_name)
                return_files.append(sensor[2])

            zip_location = file_locations.html_sensor_control_big_zip
            zip_files(return_names, return_files, save_type="to_disk", file_location=zip_location)

            logger.network_logger.info("Sensor Control - The Big Zip Generation Completed")
        except Exception as error:
            logger.primary_logger.error("Sensor Control - Big Zip Error: " + str(error))
            rm_cached_variables.sc_big_zip_name = ""
    rm_cached_variables.creating_the_big_zip = False


def downloads_direct_rsm(address_list, download_type="sensors_download_databases"):
    """
    Used to initiate Downloads from provided IP or DNS addresses (list).
    Function option "download_type" dictates which type of download.
    Default = sensors_download_databases
    """
    download_command = network_commands.sensor_sql_all_databases_zip
    download_type_message = "the SQLite3 Databases Zipped"
    add_zipped_database_size = True
    add_zipped_logs_size = False
    size_type = "MB"
    column_download_message = "Uncompressed Main DB Size"
    extra_message = "Due to the CPU demands of zipping on the fly, raw Database size is shown here.<br>" + \
                    "Actual download size will be much smaller. MQTT / Checkin Database Size not shown."
    if download_type == app_config_access.sensor_control_config.radio_download_logs:
        extra_message = ""
        column_download_message = "Zipped Logs Size"
        size_type = "KB"
        add_zipped_database_size = False
        add_zipped_logs_size = True
        download_command = network_commands.download_zipped_logs
        download_type_message = "Full Logs Zipped"
    sensor_download_url = "window.open('https://{{ IPAddress }}/" + download_command + "');"
    sensor_download_sql_list = ""
    text_ip_and_response = ""

    threads = []
    for address in address_list:
        threads.append(Thread(target=get_remote_sensor_check_and_delay,
                              args=[address, False, add_zipped_database_size, add_zipped_logs_size]))
    start_and_wait_threads(threads)

    address_responses = []
    while not data_queue.empty():
        address_responses.append(data_queue.get())
        data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        if response["status"] == "OK":
            new_address = response["address"].strip()
            if check_for_port_in_address(new_address):
                address_split = get_ip_and_port_split(new_address)
                address_and_port = address_split[0] + ":" + address_split[1]
            elif len(new_address.split(":")) > 1:
                address_and_port = "[" + new_address + "]:10065"
            else:
                address_and_port = new_address + ":10065"
            response_time = response["response_time"]
            background_colour = get_html_response_bg_colour(response_time)
            new_download = sensor_download_url.replace("{{ IPAddress }}", address_and_port)
            sensor_download_sql_list += new_download + "\n"
            text_ip_and_response += "<tr><th width='160px'><span style='background-color: " + background_colour + \
                                    ";'>" + response_time + " Seconds</span></th>\n" + \
                                    "<th width='220'>" + response["download_size"] + " " + size_type + "</th>\n" + \
                                    "<th>" + response["address"] + "</th></tr>"

    download_page = render_template("ATPro_admin/page_templates/remote_management/direct-sensor-downloads.html",
                                    DownloadTypeMessage=download_type_message,
                                    DownloadURLs=sensor_download_sql_list.strip(),
                                    SensorResponse=text_ip_and_response.strip(),
                                    ColumnDownloadMessage=column_download_message,
                                    ExtraMessage=extra_message)
    return get_html_atpro_index(run_script="", main_page_view_content=download_page)


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
                if auth_error_msg_contains in str(sensor_data[2]):
                    db_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".txt"
                    sensor_data[2] = "Incorrect Login Provided"
            except Exception as error:
                print(str(error))
            database_names.append(db_name)
            sensors_database.append(sensor_data[2])

        rm_cached_variables.sc_databases_zip_in_memory = False
        zip_files(database_names, sensors_database, save_type="save_to_disk",
                  file_location=file_locations.html_sensor_control_databases_zip)
        rm_cached_variables.sc_databases_zip_name = "Multiple_Databases_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Databases Zip Generation Error: " + str(error))
        rm_cached_variables.sc_databases_zip_name = ""
    rm_cached_variables.creating_databases_zip = False
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
                if auth_error_msg_contains in str(sensor_data[2]):
                    zip_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".txt"
                    sensor_data[2] = "Incorrect Login Provided"
            except Exception as error:
                print(str(error))
            zip_names.append(zip_name)
            logs_zipped.append(sensor_data[2])

        clear_zip_names()
        rm_cached_variables.sc_in_memory_zip = zip_files(zip_names, logs_zipped)
        rm_cached_variables.sc_logs_zip_name = "Multiple_Logs_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Logs Zip Generation Error: " + str(error))
        rm_cached_variables.sc_logs_zip_name = ""
    rm_cached_variables.creating_logs_zip = False
    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Complete")


def get_data_queue_items():
    """ Returns a list of items from a data_queue. """
    que_data = []
    while not data_queue.empty():
        que_data.append(data_queue.get())
        data_queue.task_done()
    return que_data


def _queue_name_and_file_list(ip_list, command):
    threads_list = []
    for address in ip_list:
        threads_list.append(Thread(target=_worker_queue_list_ip_name_file, args=[address, command]))
    start_and_wait_threads(threads_list)


def _worker_queue_list_ip_name_file(address, command):
    try:
        sensor_name = get_http_sensor_reading(address, http_command="GetHostName")
        sensor_data = get_http_kootnet_sensor_file(address, http_command=command)
        data_queue.put([address, sensor_name, sensor_data])
    except Exception as error:
        logger.network_logger.error("Sensor Control - Get Remote File Failed: " + str(error))


def put_all_reports_zipped_to_cache(ip_list):
    """
    Downloads ALL remote sensor reports from provided IP or DNS addresses (as a list)
    then creates a single zip file for download off the local web portal.
    """
    try:
        hostname = app_cached_variables.hostname
        generate_html_reports_combo(ip_list)
        html_reports = [rm_cached_variables.html_combo_report]
        html_report_names = ["ReportCombo.html"]
        rm_cached_variables.sc_in_memory_zip = zip_files(html_report_names, html_reports)
        rm_cached_variables.sc_reports_zip_name = "Reports_from_" + hostname + "_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Reports Zip Generation Error: " + str(error))
    rm_cached_variables.creating_combo_reports_zip = False
    logger.network_logger.info("Sensor Control - Reports Zip Generation Complete")
