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
from operations_modules import logger
from operations_modules.app_cached_variables import network_get_commands as sg_commands
from operations_modules.app_generic_functions import thread_function
from operations_modules.http_generic_network import get_http_sensor_reading, get_html_response_bg_colour
from sensor_modules.system_access import get_system_datetime
from http_server.server_http_auth import auth_error_msg_contains
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables


def generate_html_reports_combo(ip_list):
    """
    Returns a combination of all reports in HTML format.
    Reports are downloaded from the provided list of remote sensors (IP or DNS addresses)
    """
    try:
        threads = []
        for function in [generate_system_report, generate_config_report,
                         generate_readings_report, generate_latency_report]:
            threads.append(Thread(target=function, args=[ip_list, False]))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        tmp_html_system_report = _remove_css_js(rm_cached_variables.html_system_report)
        tmp_html_config_report = _remove_css_js(rm_cached_variables.html_config_report)
        tmp_html_readings_report = _remove_css_js(rm_cached_variables.html_readings_report)
        tmp_html_latency_report = _remove_css_js(rm_cached_variables.html_latency_report)

        html_final_combo_return = rm_cached_variables.html_report_combo

        html_final_combo_return = html_final_combo_return.replace("{{ FullSystemReport }}", tmp_html_system_report)
        html_final_combo_return = html_final_combo_return.replace("{{ FullConfigurationReport }}", tmp_html_config_report)
        html_final_combo_return = html_final_combo_return.replace("{{ FullReadingsReport }}", tmp_html_readings_report)
        html_final_combo_return = html_final_combo_return.replace("{{ FullLatencyReport }}", tmp_html_latency_report)
        html_final_combo_return += "\n" + rm_cached_variables.html_report_end
    except Exception as error:
        logger.primary_logger.error("Sensor Control - Unable to Generate Combo Report: " + str(error))
        html_final_combo_return = "Generation Error: " + str(error)
    rm_cached_variables.html_combo_report = html_final_combo_return


def _remove_css_js(html_report):
    html_report = html_report.replace(rm_cached_variables.html_report_css, "")
    html_report = html_report.replace(rm_cached_variables.html_report_js, "")
    return html_report


def generate_system_report(ip_list, threaded=True):
    if threaded:
        thread_function(_thread_system_report, args=ip_list)
    else:
        _thread_system_report(ip_list)


def _thread_system_report(ip_list):
    rm_cached_variables.creating_system_report = True
    new_report = create_sensor_report(ip_list, sg_commands.rm_system_report, "System")
    rm_cached_variables.html_system_report = new_report
    rm_cached_variables.creating_system_report = False


def generate_config_report(ip_list, threaded=True):
    if threaded:
        thread_function(_thread_config_report, args=ip_list)
    else:
        _thread_config_report(ip_list)


def _thread_config_report(ip_list):
    rm_cached_variables.creating_config_report = True
    new_report = create_sensor_report(ip_list, sg_commands.rm_config_report, "Configurations")
    rm_cached_variables.html_config_report = new_report
    rm_cached_variables.creating_config_report = False


def generate_readings_report(ip_list, threaded=True):
    if threaded:
        thread_function(_thread_readings_report, args=ip_list)
    else:
        _thread_readings_report(ip_list)


def _thread_readings_report(ip_list):
    rm_cached_variables.creating_readings_report = True
    new_report = create_sensor_report(ip_list, sg_commands.rm_readings_report, "Readings")
    rm_cached_variables.html_readings_report = new_report
    rm_cached_variables.creating_readings_report = False


def generate_latency_report(ip_list, threaded=True):
    if threaded:
        thread_function(_thread_latency_report, args=ip_list)
    else:
        _thread_latency_report(ip_list)


def _thread_latency_report(ip_list):
    rm_cached_variables.creating_latency_report = True
    new_report = create_sensor_report(ip_list, sg_commands.rm_latency_report, "Latency")
    rm_cached_variables.html_latency_report = new_report
    rm_cached_variables.creating_latency_report = False


def create_sensor_report(address_list, sensor_report_url, html_report_heading):
    data_queue = Queue()
    sensor_reports = []
    threads = []

    for address in address_list:
        threads.append(Thread(target=_get_remote_management_report, args=[address, sensor_report_url, data_queue]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    while not data_queue.empty():
        sensor_reports.append(data_queue.get())
        data_queue.task_done()

    sensor_reports.sort()

    final_report_replacement = ""
    for report in sensor_reports:
        html_report = str(report[1])
        rsm_address_port = str(report[2])
        if auth_error_msg_contains in html_report:
            sensor_report = rm_cached_variables.report_sensor_error_template.replace("{{ Heading }}", "Login Failed")
            sensor_report = sensor_report.replace("{{ RSMAddressAndPort }}", rsm_address_port)
            final_report_replacement += sensor_report + "\n"
        elif '<div class="col-12 col-m-12 col-sm-12">' in html_report:
            final_report_replacement += html_report + "\n"
        else:
            sensor_report = rm_cached_variables.report_sensor_error_template.replace("{{ Heading }}", "Unknown Error")
            sensor_report = sensor_report.replace("{{ RSMAddressAndPort }}", rsm_address_port)
            final_report_replacement += sensor_report + "\n"
    new_report = rm_cached_variables.html_report_start + rm_cached_variables.html_report_template
    new_report += rm_cached_variables.html_report_end
    new_report = new_report.replace("{{ ReportHeading }}", html_report_heading)
    new_report = new_report.replace("{{ DateTime }}", get_system_datetime())
    new_report = new_report.replace("{{ SensorInfoBoxes }}", final_report_replacement)
    return new_report


def _get_remote_management_report(ip_address, sensor_report_url, data_queue, login_required=False):
    sensor_check = _get_sensor_response_time(ip_address)
    rsm_address_port = ip_address.strip()
    if len(ip_address.split(":")) == 1:
        rsm_address_port = ip_address.strip() + ":10065"

    if sensor_check:
        login_check = get_http_sensor_reading(ip_address, http_command=sg_commands.check_portal_login)
        if login_check == "OK" or not login_required:
            if login_check == "OK":
                login_check = "Login OK"
            elif auth_error_msg_contains in login_check:
                login_check = "Login Failed"
            else:
                login_check = "Unknown Error"
            sensor_report = get_http_sensor_reading(ip_address, http_command=sensor_report_url)
            sensor_report = sensor_report.replace("{{ ResponseBackground }}", get_html_response_bg_colour(sensor_check))
            sensor_report = sensor_report.replace("{{ LoginCheck }}", login_check)
            sensor_report = sensor_report.replace("{{ SensorResponseTime }}", sensor_check)
        else:
            sensor_report = rm_cached_variables.report_sensor_error_template.replace("{{ Heading }}", "Login Failed")
    else:
        logger.network_logger.debug("Remote Sensor " + ip_address + " Offline")
        sensor_check = "99.99"
        sensor_report = rm_cached_variables.report_sensor_error_template.replace("{{ Heading }}", "Sensor Offline")
    sensor_report = sensor_report.replace("{{ RSMAddressAndPort }}", rsm_address_port)
    data_queue.put([sensor_check, sensor_report, rsm_address_port])


def _get_sensor_response_time(ip_address):
    start_time = time.time()
    sensor_check = get_http_sensor_reading(ip_address)
    if sensor_check == "OK":
        return str(round(time.time() - start_time, 3))
    return False
