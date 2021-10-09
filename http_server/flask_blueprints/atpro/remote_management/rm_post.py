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
from flask import send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, save_to_memory_ok
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, get_message_page
from http_server.flask_blueprints.atpro.remote_management.rm_reports import generate_system_report, \
    generate_config_report, generate_readings_report, generate_latency_report
from http_server.flask_blueprints.atpro.remote_management.rm_post_functions import check_sensor_status_sensor_control, \
    clear_zip_names, generate_html_reports_combo, put_all_reports_zipped_to_cache, downloads_direct_rsm, \
    create_all_databases_zipped, create_multiple_sensor_logs_zipped, get_sum_db_sizes, create_the_big_zip


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
        ip_list_raw = app_config_access.sensor_control_config.get_raw_ip_addresses_as_list()

        if len(ip_list_raw) > 0:
            if sc_action == app_config_access.sensor_control_config.radio_check_status:
                return check_sensor_status_sensor_control(ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_report_combo:
                thread_function(_thread_combo_report, args=ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_report_system:
                generate_system_report(ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_report_config:
                generate_config_report(ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_report_test_sensors:
                generate_readings_report(ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_report_sensors_latency:
                generate_latency_report(ip_list_raw)
            elif sc_action == app_config_access.sensor_control_config.radio_download_reports:
                app_cached_variables.creating_the_reports_zip = True
                logger.network_logger.info("Sensor Control - Reports Zip Generation Started")
                clear_zip_names()
                thread_function(put_all_reports_zipped_to_cache, args=ip_list_raw)
            else:
                ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
                if len(ip_list) < 1:
                    msg_1 = "All sensors appear to be Offline"
                    return get_message_page(msg_1, page_url="sensor-rm")
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


def _thread_combo_report(ip_list):
    generate_html_reports_combo(ip_list)


def _sensor_addresses_required_msg():
    msg_1 = "Please set at least one remote sensor address"
    msg_2 = "Press the button 'Show Sensors Address List' under remote management to set sensor addresses."
    return get_message_page(msg_1, msg_2, page_url="sensor-rm")
