from flask import render_template
from threading import Thread
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from http_server import server_http_sensor_control
from sensor_modules.sensor_access import get_system_datetime


def message_and_return(return_message, text_message2="", url="/", special_command=""):
    return render_template("message_return.html",
                           TextMessage=return_message,
                           TextMessage2=text_message2,
                           CloseWindow=special_command,
                           URL=url)


def get_sensor_control_report(address_list, report_type="systems_report"):
    config_report = app_config_access.sensor_control_config.radio_report_config
    sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors
    html_sensor_report_end = server_http_sensor_control.html_report_system_end

    new_report = server_http_sensor_control.html_report_system_start
    if report_type == config_report:
        new_report = server_http_sensor_control.html_report_config_start
        html_sensor_report_end = server_http_sensor_control.html_report_config_end
    elif report_type == sensors_report:
        new_report = server_http_sensor_control.html_report_sensors_test_start
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
    if report_type == sensors_report:
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
    if config_setting:
        return "checked"
    return ""
