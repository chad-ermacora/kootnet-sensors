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
from flask import render_template
from threading import Thread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from http_server import server_http_sensor_control
from sensor_modules.sensor_access import get_system_datetime


def message_and_return(return_message, text_message2="", url="/", special_command=""):
    """
    Returns an HTML page of the provided message then redirects to the index web page after 10 seconds.
    Optional: Add a secondary text message, customize the URL or add a special HTML command.
    """
    return render_template("message_return.html",
                           PageURL=url,
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           TextMessage=return_message,
                           TextMessage2=text_message2,
                           CloseWindow=special_command)


def get_sensor_control_report(address_list, report_type="systems_report"):
    """
    Returns a HTML report based on report_type and sensor addresses provided (IP or DNS addresses as a list).
    Default: systems_report
    """
    config_report = app_config_access.sensor_control_config.radio_report_config
    sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors
    latency_report = app_config_access.sensor_control_config.radio_report_sensors_latency
    html_sensor_report_end = server_http_sensor_control.html_report_system_end

    new_report = server_http_sensor_control.html_report_system_start
    if report_type == config_report:
        new_report = server_http_sensor_control.html_report_config_start
        html_sensor_report_end = server_http_sensor_control.html_report_config_end
    elif report_type == sensors_report:
        new_report = server_http_sensor_control.html_report_sensors_test_start
        html_sensor_report_end = server_http_sensor_control.html_report_sensors_test_end
    elif report_type == latency_report:
        new_report = server_http_sensor_control.html_report_sensors_latency_start
        html_sensor_report_end = server_http_sensor_control.html_report_sensors_test_end
    new_report = new_report.replace("{{ DateTime }}", get_system_datetime())

    sensor_reports = []
    threads = []
    for address in address_list:
        threads.append(Thread(target=server_http_sensor_control.get_online_report, args=[address, report_type]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    data_queue = app_cached_variables.data_queue
    if report_type == config_report:
        data_queue = app_cached_variables.data_queue2
    if report_type == sensors_report or report_type == latency_report:
        data_queue = app_cached_variables.data_queue3
    while not data_queue.empty():
        sensor_reports.append(data_queue.get())
        data_queue.task_done()

    sensor_reports.sort()
    for report in sensor_reports:
        new_report += str(report[1])
    new_report += html_sensor_report_end
    return new_report


def get_html_checkbox_state(config_setting):
    """ Generic function to return HTML code for checkboxes (Used in flask render templates). """
    if config_setting:
        return "checked"
    return ""


def get_html_disabled_state(config_setting):
    """ Generic function used to disable HTML content if config_setting is False (Used in flask render templates). """
    if config_setting:
        return ""
    return "disabled"


def get_html_hidden_state(config_setting):
    """ Generic function used to hide HTML content if config_setting is False (Used in flask render templates). """
    if config_setting:
        return ""
    return "hidden"


def get_html_selected_state(config_setting):
    """ Generic function to return HTML code for checkboxes (Used in flask render templates). """
    if config_setting:
        return "selected"
    return ""


def get_restart_service_text(service_name):
    return "Restarting " + str(service_name) + " Service, This may take up to 10 Seconds"
