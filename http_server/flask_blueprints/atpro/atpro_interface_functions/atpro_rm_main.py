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
from flask import render_template, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, get_http_sensor_reading, \
    clear_zip_names, save_to_memory_ok, get_response_bg_colour, get_ip_and_port_split, \
    check_for_port_in_address, start_and_wait_threads
from configuration_modules import app_config_access
from http_server.flask_blueprints.sensor_control_files.sensor_control_functions import \
    create_all_databases_zipped, create_multiple_sensor_logs_zipped, \
    create_the_big_zip, put_all_reports_zipped_to_cache, generate_html_reports_combo, get_sum_db_sizes
from http_server.flask_blueprints.sensor_control_files.reports import generate_sensor_control_report
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_html_atpro_index, \
    get_message_page

network_commands = app_cached_variables.CreateNetworkGetCommands()
network_system_commands = app_cached_variables.CreateNetworkSystemCommands()


def get_atpro_sensor_remote_management_page():
    download_big_zip = "disabled"
    if not app_cached_variables.creating_the_big_zip and app_cached_variables.sc_big_zip_name != "":
        download_big_zip = ""

    download_reports_zip = "disabled"
    if not app_cached_variables.creating_the_reports_zip and app_cached_variables.sc_reports_zip_name != "":
        download_reports_zip = ""

    download_databases_zip = "disabled"
    if not app_cached_variables.creating_databases_zip and app_cached_variables.sc_databases_zip_name != "":
        download_databases_zip = ""

    download_logs_zip = "disabled"
    if not app_cached_variables.creating_logs_zip and app_cached_variables.sc_logs_zip_name != "":
        download_logs_zip = ""

    run_script = _get_rm_running_msg()
    if run_script != "":
        run_script = "RunningRSM(blinking_text='" + run_script + "');"
    return render_template(
        "ATPro_admin/page_templates/remote-management.html",
        RunningRSMScript=run_script,
        DownloadReportsZipDisabled=download_reports_zip,
        DownloadDatabasesDisabled=download_databases_zip,
        DownloadLogsDisabled=download_logs_zip,
        DownloadBigZipDisabled=download_big_zip,
        IPListsOptionNames=get_rm_ip_lists_drop_down(),
        SensorIP1=app_config_access.sensor_control_config.sensor_ip_dns1,
        SensorIP2=app_config_access.sensor_control_config.sensor_ip_dns2,
        SensorIP3=app_config_access.sensor_control_config.sensor_ip_dns3,
        SensorIP4=app_config_access.sensor_control_config.sensor_ip_dns4,
        SensorIP5=app_config_access.sensor_control_config.sensor_ip_dns5,
        SensorIP6=app_config_access.sensor_control_config.sensor_ip_dns6,
        SensorIP7=app_config_access.sensor_control_config.sensor_ip_dns7,
        SensorIP8=app_config_access.sensor_control_config.sensor_ip_dns8,
        SensorIP9=app_config_access.sensor_control_config.sensor_ip_dns9,
        SensorIP10=app_config_access.sensor_control_config.sensor_ip_dns10,
        SensorIP11=app_config_access.sensor_control_config.sensor_ip_dns11,
        SensorIP12=app_config_access.sensor_control_config.sensor_ip_dns12,
        SensorIP13=app_config_access.sensor_control_config.sensor_ip_dns13,
        SensorIP14=app_config_access.sensor_control_config.sensor_ip_dns14,
        SensorIP15=app_config_access.sensor_control_config.sensor_ip_dns15,
        SensorIP16=app_config_access.sensor_control_config.sensor_ip_dns16,
        SensorIP17=app_config_access.sensor_control_config.sensor_ip_dns17,
        SensorIP18=app_config_access.sensor_control_config.sensor_ip_dns18,
        SensorIP19=app_config_access.sensor_control_config.sensor_ip_dns19,
        SensorIP20=app_config_access.sensor_control_config.sensor_ip_dns20
    )


def _get_rm_running_msg():
    extra_message = ""
    if app_cached_variables.creating_the_big_zip:
        extra_message = "Creating Big Zip"
    elif app_cached_variables.creating_the_reports_zip:
        extra_message = "Creating Reports Zip"
    elif app_cached_variables.creating_databases_zip:
        extra_message = "Creating Databases Zip"
    elif app_cached_variables.creating_logs_zip:
        extra_message = "Creating Logs Zip"
    elif app_cached_variables.creating_combo_report:
        extra_message = "Creating Combo Report"
    elif app_cached_variables.creating_system_report:
        extra_message = "Creating System Report"
    elif app_cached_variables.creating_config_report:
        extra_message = "Creating Configuration Report"
    elif app_cached_variables.creating_readings_report:
        extra_message = "Creating Readings Report"
    elif app_cached_variables.creating_latency_report:
        extra_message = "Creating Latency Report"
    return extra_message


def remote_management_main_post(request):
    run_command = request.form.get("rsm-run-command")
    selected_ip_list = str(request.form.get("selected_ip_list"))
    if run_command == "ChangeIPList":
        app_config_access.sensor_control_config.selected_ip_list = selected_ip_list
        app_config_access.sensor_control_config.change_ip_list()
    elif run_command == "SaveSettings":
        app_config_access.sensor_control_config.update_with_html_request(request)
        app_config_access.sensor_control_config.save_config_to_file()
    elif run_command == "RunAction":
        sc_action = request.form.get("selected_action")
        sc_download_type = request.form.get("selected_send_type")
        app_config_access.sensor_control_config.update_with_html_request(request)
        ip_list = app_config_access.sensor_control_config.get_raw_ip_addresses_as_list()

        if len(ip_list) > 0:
            if sc_action == app_config_access.sensor_control_config.radio_check_status:
                return check_sensor_status_sensor_control(ip_list)
        else:
            return _sensor_addresses_required_msg()

        if len(ip_list) > 0:
            ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
            if len(ip_list) < 1:
                msg_1 = "All sensors appear to be Offline"
                return get_message_page(msg_1, page_url="sensor-rm")
            if sc_action == app_config_access.sensor_control_config.radio_report_combo:
                thread_function(_thread_combo_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_system:
                thread_function(_thread_system_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_config:
                thread_function(_thread_config_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_test_sensors:
                thread_function(_thread_readings_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_sensors_latency:
                thread_function(_thread_latency_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_reports:
                app_cached_variables.creating_the_reports_zip = True
                logger.network_logger.info("Sensor Control - Reports Zip Generation Started")
                clear_zip_names()
                thread_function(put_all_reports_zipped_to_cache, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_databases:
                download_sql_databases = app_config_access.sensor_control_config.radio_download_databases
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    return downloads_direct_rsm(ip_list, download_type=download_sql_databases)
                else:
                    app_cached_variables.creating_databases_zip = True
                    logger.network_logger.info("Sensor Control - Databases Zip Generation Started")
                    thread_function(create_all_databases_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_logs:
                clear_zip_names()
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    download_logs = app_config_access.sensor_control_config.radio_download_logs
                    return downloads_direct_rsm(ip_list, download_type=download_logs)
                elif sc_download_type == app_config_access.sensor_control_config.radio_send_type_relayed:
                    app_cached_variables.creating_logs_zip = True
                    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Started")
                    thread_function(create_multiple_sensor_logs_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_create_the_big_zip:
                logger.network_logger.info("Sensor Control - The Big Zip Generation Started")
                databases_size = get_sum_db_sizes(ip_list)
                if save_to_memory_ok(databases_size):
                    clear_zip_names()
                    app_cached_variables.sc_big_zip_in_memory = True
                else:
                    app_cached_variables.sc_big_zip_in_memory = False
                app_cached_variables.creating_the_big_zip = True
                thread_function(create_the_big_zip, args=ip_list)
        else:
            return _sensor_addresses_required_msg()
    elif run_command == "DownloadRSMReportsZip":
        try:
            if not app_cached_variables.creating_the_reports_zip:
                if app_cached_variables.sc_reports_zip_name != "":
                    zip_file = app_cached_variables.sc_in_memory_zip
                    zip_filename = app_cached_variables.sc_reports_zip_name
                    app_cached_variables.sc_reports_zip_name = ""
                    return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        except Exception as error:
            logger.network_logger.error("Send Reports Zip Error: " + str(error))
            msg_1 = "Problem loading Zip"
            msg_2 = str(error)
            return get_message_page(msg_1, msg_2, page_url="sensor-rm")
        app_cached_variables.sc_reports_zip_name = ""
    elif run_command == "DownloadRSMDatabasesZip":
        if not app_cached_variables.creating_databases_zip:
            if app_cached_variables.sc_databases_zip_name != "":
                try:
                    if app_cached_variables.sc_databases_zip_in_memory:
                        zip_file = app_cached_variables.sc_in_memory_zip
                    else:
                        zip_file = file_locations.html_sensor_control_databases_zip

                    zip_filename = app_cached_variables.sc_databases_zip_name
                    app_cached_variables.sc_databases_zip_name = ""
                    app_cached_variables.sc_databases_zip_in_memory = False
                    return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
                except Exception as error:
                    logger.network_logger.error("Send Databases Zip Error: " + str(error))
                    app_cached_variables.sc_databases_zip_name = ""
                    app_cached_variables.sc_databases_zip_in_memory = False
                    msg_1 = "Problem loading Zip"
                    msg_2 = str(error)
                    return get_message_page(msg_1, msg_2, page_url="sensor-rm")
    elif run_command == "DownloadRSMLogsZip":
        try:
            if not app_cached_variables.creating_logs_zip:
                if app_cached_variables.sc_logs_zip_name != "":
                    zip_file = app_cached_variables.sc_in_memory_zip
                    zip_filename = app_cached_variables.sc_logs_zip_name
                    app_cached_variables.sc_logs_zip_name = ""
                    return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        except Exception as error:
            logger.network_logger.error("Send SC Logs Zip Error: " + str(error))
            msg_1 = "Problem loading Zip"
            msg_2 = str(error)
            return get_message_page(msg_1, msg_2, page_url="sensor-rm")
        app_cached_variables.sc_logs_zip_name = ""
    elif run_command == "DownloadRSMBigZip":
        try:
            if not app_cached_variables.creating_the_big_zip:
                if app_cached_variables.sc_big_zip_name != "":
                    if app_cached_variables.sc_big_zip_in_memory:
                        zip_file = app_cached_variables.sc_in_memory_zip
                    else:
                        zip_file = file_locations.html_sensor_control_big_zip

                    zip_filename = app_cached_variables.sc_big_zip_name
                    app_cached_variables.sc_big_zip_name = ""
                    app_cached_variables.sc_big_zip_in_memory = False
                    return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        except Exception as error:
            logger.network_logger.error("Send Big Zip Error: " + str(error))
            msg_1 = "Problem loading Zip"
            msg_2 = str(error)
            return get_message_page(msg_1, msg_2, page_url="sensor-rm")
        app_cached_variables.sc_big_zip_in_memory = False
    return get_html_atpro_index(run_script="SelectNav('sensor-rm');")


def _sensor_addresses_required_msg():
    msg_1 = "Please set at least one remote sensor address"
    msg_2 = "Press the button 'Show Sensors Address List' under remote management to set sensor addresses."
    return get_message_page(msg_1, msg_2, page_url="sensor-rm")


def _thread_combo_report(ip_list):
    generate_html_reports_combo(ip_list, skip_rewrite_link=True)


def _thread_system_report(ip_list):
    system_report = app_config_access.sensor_control_config.radio_report_system
    generate_sensor_control_report(ip_list, report_type=system_report)


def _thread_config_report(ip_list):
    config_report = app_config_access.sensor_control_config.radio_report_config
    generate_sensor_control_report(ip_list, report_type=config_report)


def _thread_readings_report(ip_list):
    sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors
    generate_sensor_control_report(ip_list, report_type=sensors_report)


def _thread_latency_report(ip_list):
    latency_report = app_config_access.sensor_control_config.radio_report_sensors_latency
    generate_sensor_control_report(ip_list, report_type=latency_report)


def check_sensor_status_sensor_control(address_list):
    """
    Uses provided remote sensor IP or DNS addresses (as a list) and checks if it's online.
    Returns a flask rendered template with results as an HTML page.
    """
    data_queue = Queue()

    text_insert = ""
    threads = []
    for address in address_list:
        threads.append(Thread(target=get_remote_sensor_check_and_delay, args=[address, data_queue, True]))
    start_and_wait_threads(threads)

    address_responses = []
    while not data_queue.empty():
        address_responses.append(data_queue.get())
        data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        new_address = response["address"]
        port = "10065"
        if check_for_port_in_address(response["address"]):
            address_split = get_ip_and_port_split(response["address"])
            new_address = address_split[0]
            port = address_split[1]
        response_time = response["response_time"]
        background_colour = get_response_bg_colour(response_time)
        sensor_url_link = "'https://" + new_address + ":" + port + "/'"

        text_insert += "<tr><th width='160px'><span style='background-color: " + background_colour + ";'>" + \
                       response_time + " Seconds</span></th>\n<th width='250px'>" + response["sensor_hostname"] + \
                       "</th>\n<th><a target='_blank' href=" + sensor_url_link + ">" + \
                       response["address"] + "</a></th></tr>\n"
    status_page = render_template("ATPro_admin/page_templates/remote_management/online-status-check.html",
                                  SensorResponse=text_insert.strip())
    return get_html_atpro_index(run_script="SelectActiveMainMenu('sensor-rm');", main_page_view_content=status_page)


def get_remote_sensor_check_and_delay(address, data_queue, add_hostname=False, add_db_size=False, add_logs_size=False):
    """
    Checks a remote sensor's response time and add's it to the data_queue
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
            sensor_hostname = get_sensor_reading(address, command="GetHostName").strip()
        if add_db_size:
            download_size = get_sensor_reading(address, command="GetSQLDBSize").strip()
        if add_logs_size:
            download_size = get_sensor_reading(address, command="GetZippedLogsSize").strip()
    else:
        task_end_time = "NA "
        sensor_hostname = "Offline"
        download_size = "NA"
    data_queue.put({"address": address,
                    "status": str(sensor_status),
                    "response_time": str(task_end_time),
                    "sensor_hostname": str(sensor_hostname),
                    "download_size": str(download_size)})



def downloads_direct_rsm(address_list, download_type="sensors_download_databases"):
    """
    Used to initiate Downloads from provided IP or DNS addresses (list).
    Function option "download_type" dictates which type of download.
    Default = sensors_download_databases
    """
    data_queue = Queue()

    download_command = network_commands.sensor_sql_database
    download_type_message = "the SQLite3 Database Zipped"
    add_zipped_database_size = True
    add_zipped_logs_size = False
    size_type = "MB"
    column_download_message = "Uncompressed DB Size"
    extra_message = "Due to the CPU demands of zipping on the fly, raw Database size is shown here.<br>" + \
                    "Actual download size will be much smaller."
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
                              args=[address, data_queue, False,
                                    add_zipped_database_size,
                                    add_zipped_logs_size]))
    start_and_wait_threads(threads)

    address_responses = []
    while not data_queue.empty():
        address_responses.append(data_queue.get())
        data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        if response["status"] == "OK":
            if check_for_port_in_address(response["address"]):
                address_split = get_ip_and_port_split(response["address"])
                address_and_port = address_split[0].strip() + ":" + address_split[1].strip()
            else:
                address_and_port = response["address"].strip() + ":10065"
            response_time = response["response_time"]
            background_colour = get_response_bg_colour(response_time)
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


def get_rm_ip_lists_drop_down():
    custom_ips_option_html = "<option value='{{ IPListChangeMe }}'>{{ IPListChangeMe }}</option>"
    selected_ip_option = "<option selected='selected' value='{{ IPListChangeMe }}'>{{ IPListChangeMe }}</option>"
    ip_lists_dropdown_selection = ""
    for ip_list_name in app_config_access.sensor_control_config.custom_ip_list_names:
        if ip_list_name == app_config_access.sensor_control_config.selected_ip_list:
            ip_lists_dropdown_selection += selected_ip_option.replace("{{ IPListChangeMe }}", ip_list_name) + "\n"
        else:
            ip_lists_dropdown_selection += custom_ips_option_html.replace("{{ IPListChangeMe }}", ip_list_name) + "\n"
    return ip_lists_dropdown_selection
