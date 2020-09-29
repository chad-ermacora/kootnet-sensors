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
from threading import Thread
from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return
from http_server.flask_blueprints.sensor_control_files.reports import generate_sensor_control_report
from http_server.flask_blueprints.sensor_control_files.sensor_control_functions import \
    check_sensor_status_sensor_control, create_all_databases_zipped, create_multiple_sensor_logs_zipped, \
    create_the_big_zip, put_all_reports_zipped_to_cache, downloads_sensor_control, generate_html_reports_combo, \
    sensor_control_management, get_sum_db_sizes, CreateSensorHTTPCommand

html_sensor_control_routes = Blueprint("html_sensor_control_routes", __name__)

network_system_commands = app_cached_variables.CreateNetworkSystemCommands()
check_portal_login = app_cached_variables.CreateNetworkGetCommands().check_portal_login


@html_sensor_control_routes.route("/SensorControlManage", methods=["GET", "POST"])
def html_sensor_control_management():
    logger.network_logger.debug("* HTML Sensor Control accessed by " + str(request.remote_addr))
    if request.method == "POST":
        sc_action = request.form.get("selected_action")
        sc_download_type = request.form.get("selected_send_type")
        app_config_access.sensor_control_config.update_with_html_request(request)
        ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()

        if len(ip_list) > 0:
            if sc_action == app_config_access.sensor_control_config.radio_check_status:
                ip_list = app_config_access.sensor_control_config.get_raw_ip_addresses_as_list()
                return check_sensor_status_sensor_control(ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_combo:
                app_generic_functions.thread_function(_thread_combo_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_system:
                app_generic_functions.thread_function(_thread_system_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_config:
                app_generic_functions.thread_function(_thread_config_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_test_sensors:
                app_generic_functions.thread_function(_thread_readings_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_sensors_latency:
                app_generic_functions.thread_function(_thread_latency_report, ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_reports:
                app_cached_variables.creating_the_reports_zip = True
                logger.network_logger.info("Sensor Control - Reports Zip Generation Started")
                app_generic_functions.clear_zip_names()
                app_generic_functions.thread_function(put_all_reports_zipped_to_cache, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_databases:
                download_sql_databases = app_config_access.sensor_control_config.radio_download_databases
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    return downloads_sensor_control(ip_list, download_type=download_sql_databases)
                else:
                    app_cached_variables.creating_databases_zip = True
                    logger.network_logger.info("Sensor Control - Databases Zip Generation Started")
                    app_generic_functions.thread_function(create_all_databases_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_logs:
                app_generic_functions.clear_zip_names()
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    download_logs = app_config_access.sensor_control_config.radio_download_logs
                    return downloads_sensor_control(ip_list, download_type=download_logs)
                elif sc_download_type == app_config_access.sensor_control_config.radio_send_type_relayed:
                    app_cached_variables.creating_logs_zip = True
                    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Started")
                    app_generic_functions.thread_function(create_multiple_sensor_logs_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_create_the_big_zip:
                logger.network_logger.info("Sensor Control - The Big Zip Generation Started")
                databases_size = get_sum_db_sizes(ip_list)
                if app_generic_functions.save_to_memory_ok(databases_size):
                    app_generic_functions.clear_zip_names()
                    app_cached_variables.sc_big_zip_in_memory = True
                else:
                    app_cached_variables.sc_big_zip_in_memory = False
                app_cached_variables.creating_the_big_zip = True
                app_generic_functions.thread_function(create_the_big_zip, args=ip_list)
    return sensor_control_management()


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


@html_sensor_control_routes.route("/GetComboReport")
@auth.login_required
def html_get_combo_report():
    return app_cached_variables.html_combo_report


@html_sensor_control_routes.route("/GetSystemReport")
def html_get_system_report():
    return app_cached_variables.html_system_report


@html_sensor_control_routes.route("/GetConfigReport")
@auth.login_required
def html_get_config_report():
    return app_cached_variables.html_config_report


@html_sensor_control_routes.route("/GetReadingsReport")
def html_get_readings_report():
    return app_cached_variables.html_readings_report


@html_sensor_control_routes.route("/GetLatencyReport")
def html_get_latency_report():
    return app_cached_variables.html_latency_report


@html_sensor_control_routes.route("/MultiSCSaveSettings", methods=["POST"])
@auth.login_required
def html_sensor_control_save_settings():
    logger.network_logger.debug("* HTML Sensor Control Settings saved by " + str(request.remote_addr))
    try:
        app_config_access.sensor_control_config.update_with_html_request(request)
        app_config_access.sensor_control_config.save_config_to_file()
    except Exception as error:
        logger.network_logger.error("Unable to process HTML Sensor Control Settings: " + str(error))
    return sensor_control_management()


@html_sensor_control_routes.route("/DownloadSCDatabasesZip")
def download_sc_databases_zip():
    logger.network_logger.debug("* Download Zip of Multiple Sensor DBs Accessed by " + str(request.remote_addr))
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
                return message_and_return("Problem loading Zip", url="/SensorControlManage")
    else:
        return message_and_return("Zipped Databases Creation in Progress", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCReportsZip")
def download_sc_reports_zip():
    logger.network_logger.debug("* Download SC Reports Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_cached_variables.creating_the_reports_zip:
            if app_cached_variables.sc_reports_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_reports_zip_name
                app_cached_variables.sc_reports_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return message_and_return("Zipped Reports Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Reports Zip Error: " + str(error))

    app_cached_variables.sc_reports_zip_name = ""
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCLogsZip")
def download_sc_logs_zip():
    logger.network_logger.debug("* Download SC Logs Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_cached_variables.creating_logs_zip:
            if app_cached_variables.sc_logs_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_logs_zip_name
                app_cached_variables.sc_logs_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return message_and_return("Zipped Multiple Sensors Logs Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send SC Logs Zip Error: " + str(error))

    app_cached_variables.sc_logs_zip_name = ""
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCBigZip")
def download_sc_big_zip():
    logger.network_logger.debug("* Download 'The Big Zip' Accessed by " + str(request.remote_addr))
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
        else:
            return message_and_return("Big Zip Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Big Zip Error: " + str(error))
    app_cached_variables.sc_big_zip_in_memory = False
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/SCUpgradeOnline")
@auth.login_required
def sc_upgrade_online():
    logger.network_logger.debug("* Sensor Control 'HTTP Upgrade' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_http)


@html_sensor_control_routes.route("/SCUpgradeSMB")
@auth.login_required
def sc_upgrade_smb():
    logger.network_logger.debug("* Sensor Control 'SMB Upgrade' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_smb)


@html_sensor_control_routes.route("/SCUpgradeOnlineDev")
@auth.login_required
def sc_dev_upgrade_online():
    logger.network_logger.debug("* Sensor Control 'Dev HTTP Upgrade' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_http_dev)


@html_sensor_control_routes.route("/SCUpgradeSMBDev")
@auth.login_required
def sc_dev_upgrade_smb():
    logger.network_logger.debug("* Sensor Control 'Dev HTTP Upgrade' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_smb_dev)


@html_sensor_control_routes.route("/SCRestartServices")
@auth.login_required
def sc_restart_service():
    logger.network_logger.debug("* Sensor Control 'Restart Service' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.restart_services)


@html_sensor_control_routes.route("/SCRebootSystem")
@auth.login_required
def sc_reboot_system():
    logger.network_logger.debug("* Sensor Control 'Restart System' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.restart_system)


@html_sensor_control_routes.route("/SCUpgradeSystemOS")
@auth.login_required
def sc_upgrade_system_os():
    logger.network_logger.debug("* Sensor Control 'Upgrade System OS' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_system_os)


@html_sensor_control_routes.route("/SCUpdatePipModules")
@auth.login_required
def sc_upgrade_pip_modules():
    logger.network_logger.debug("* Sensor Control 'Upgrade Python Modules' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_pip_modules)


@html_sensor_control_routes.route("/SCUpgradeOnlineClean")
@auth.login_required
def sc_upgrade_http_clean():
    logger.network_logger.debug("* Sensor Control 'HTTP Clean Upgrade' Accessed by " + str(request.remote_addr))
    return run_system_command(network_system_commands.upgrade_http_clean)


@html_sensor_control_routes.route("/PushConfiguration", methods=["POST"])
@auth.login_required
def sc_push_config():
    logger.network_logger.debug("* Sensor Control Push Configuration Accessed by " + str(request.remote_addr))

    c_data = {"config_selection": request.form.get("config_selection"),
              "new_config_str": request.form.get("new_config_str")}

    return _push_data_to_sensors("ReceivePushConfiguration", c_data)


@html_sensor_control_routes.route("/SetActiveOnlineServices", methods=["POST"])
@auth.login_required
def sc_push_online_config():
    logger.network_logger.debug("* 'Active Online Services' sent to sensors")

    active_state = 0
    if request.form.get("enable_online_service") is not None:
        active_state = 1

    c_data = {"online_service_selected_action": request.form.get("online_service_selected_action"),
              "enable_online_service": active_state,
              "online_service_interval": request.form.get("online_service_interval")}
    return _push_data_to_sensors("ReceiveActiveOnlineServices", c_data)


def _push_data_to_sensors(url_command, html_dictionary_data):
    if _missing_login_credentials():
        return _get_missing_login_credentials_page()

    ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
    if len(ip_list) > 0:
        for ip in ip_list:
            http_command_instance = CreateSensorHTTPCommand(ip, url_command, command_data=html_dictionary_data)
            http_command_instance.send_http_command()
    msg2 = "HTML configuration data sent to " + str(len(ip_list)) + " Sensors"
    return message_and_return("Sensor Control - Configuration(s) Sent", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/PushConfigurationZip", methods=["POST"])
@auth.login_required
def sc_push_configurations_zip():
    logger.network_logger.debug("* 'Configurations by Zip' sent to sensors")
    pass


def run_system_command(command, include_data=None):
    logger.network_logger.debug("* Sensor Control '" + command + "' initiated by " + str(request.remote_addr))
    ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
    if len(ip_list) > 0:
        if _missing_login_credentials():
            return _get_missing_login_credentials_page()
        for ip in ip_list:
            thread = Thread(target=_system_command_thread, args=(ip, command, include_data))
            thread.daemon = True
            thread.start()
        msg1 = command + " is now being sent to " + str(len(ip_list)) + " Sensors"
        return message_and_return(msg1, url="/SensorControlManage")
    msg2 = "Error sending System Command '" + command + "' to " + str(len(ip_list)) + " Sensors"
    return message_and_return("Sensor Control - System Commands", url="/SensorControlManage", text_message2=msg2)


def _system_command_thread(ip, command, include_data=None):
    if _login_successful(ip):
        if include_data is not None:
            app_generic_functions.send_http_command(ip, command, included_data=include_data)
        else:
            app_generic_functions.get_http_sensor_reading(ip, command=command)


def _missing_login_credentials():
    if app_cached_variables.http_login == "" or app_cached_variables.http_password == "":
        return True
    return False


def _get_missing_login_credentials_page():
    msg1 = "Warning - Sensor Control - Configurations"
    msg2 = "Login Credentials cannot be blank"
    return message_and_return(msg1, url="/SensorControlManage", text_message2=msg2)


def _login_successful(ip):
    if app_generic_functions.get_http_sensor_reading(ip, command=check_portal_login) == "OK":
        return True
    logger.network_logger.warning("The Sensor " + str(ip) + " did not accept provided Login Credentials")
    return False
