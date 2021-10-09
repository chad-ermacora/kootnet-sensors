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
from queue import Queue
from flask import render_template
from operations_modules import app_cached_variables
from configuration_modules import app_config_access

network_commands = app_cached_variables.CreateNetworkGetCommands()
network_system_commands = app_cached_variables.CreateNetworkSystemCommands()
acv = app_cached_variables
data_queue = Queue()


def get_atpro_sensor_remote_management_page():
    run_script = _get_rm_running_msg()
    if run_script != "":
        run_script = "RunningRSM(blinking_text='" + run_script + "');"
    return render_template(
        "ATPro_admin/page_templates/remote-management.html",
        RunningRSMScript=run_script,
        DownloadReportsZipDisabled=_get_html_button_state(acv.creating_the_reports_zip, acv.sc_reports_zip_name),
        DownloadDatabasesDisabled=_get_html_button_state(acv.creating_databases_zip, acv.sc_databases_zip_name),
        DownloadLogsDisabled=_get_html_button_state(acv.creating_logs_zip, acv.sc_logs_zip_name),
        DownloadBigZipDisabled=_get_html_button_state(acv.creating_the_big_zip, acv.sc_big_zip_name),
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


def _get_html_button_state(setting1, setting2):
    return_text = "disabled"
    if not setting1 and setting2 != "":
        return_text = ""
    return return_text


def _get_rm_running_msg():
    extra_message = ""
    if app_cached_variables.creating_the_big_zip:
        extra_message += "Big Zip, "
    if app_cached_variables.creating_the_reports_zip:
        extra_message += "Reports Zip, "
    if app_cached_variables.creating_databases_zip:
        extra_message += "Databases Zip, "
    if app_cached_variables.creating_logs_zip:
        extra_message += "Logs Zip, "
    if app_cached_variables.creating_combo_report:
        extra_message += "Combo Report, "
    if app_cached_variables.creating_system_report:
        extra_message += "System Report, "
    if app_cached_variables.creating_config_report:
        extra_message += "Configuration Report, "
    if app_cached_variables.creating_readings_report:
        extra_message += "Readings Report, "
    if app_cached_variables.creating_latency_report:
        extra_message += "Latency Report, "

    if extra_message != "":
        extra_message = "Creating: " + extra_message[:-2]
    return extra_message
