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
from threading import Thread
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_http_sensor_reading, send_http_command, \
    get_list_of_filenames_in_dir
from operations_modules.app_validation_checks import url_is_valid
from configuration_modules import app_config_access
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from configuration_modules.config_sensor_control import CreateIPList

from http_server.flask_blueprints.sensor_control_files.sensor_control_functions import CreateSensorHTTPCommand
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_clean_ip_list_name
from http_server.flask_blueprints.atpro.atpro_rm_receive_configs import \
    remote_management_receive_configuration
from http_server.flask_blueprints.atpro.atpro_rm_main import \
    remote_management_main_post, get_atpro_sensor_remote_management_page, get_rm_ip_lists_drop_down

network_commands = app_cached_variables.CreateNetworkGetCommands()
network_system_commands = app_cached_variables.CreateNetworkSystemCommands()

default_primary_config = CreatePrimaryConfiguration(load_from_file=False).get_config_as_str()
default_primary_config = default_primary_config.replace("\n", "\\n")
default_installed_sensors_config = CreateInstalledSensorsConfiguration(load_from_file=False).get_config_as_str()
default_installed_sensors_config = default_installed_sensors_config.replace("\n", "\\n")
default_interval_recording_config = CreateIntervalRecordingConfiguration(load_from_file=False).get_config_as_str()
default_interval_recording_config = default_interval_recording_config.replace("\n", "\\n")
default_variance_config = CreateTriggerVariancesConfiguration(load_from_file=False).get_config_as_str()
default_variance_config = default_variance_config.replace("\n", "\\n")
default_high_low_config = CreateTriggerHighLowConfiguration(load_from_file=False).get_config_as_str()
default_high_low_config = default_high_low_config.replace("\n", "\\n")
default_display_config = CreateDisplayConfiguration(load_from_file=False).get_config_as_str()
default_display_config = default_display_config.replace("\n", "\\n")
default_email_config = CreateEmailConfiguration(load_from_file=False).get_config_as_str()
default_email_config = default_email_config.replace("\n", "\\n")
default_wifi_config = "# https://manpages.debian.org/stretch/wpasupplicant/wpa_supplicant.conf.5.en.html"
default_network_config = "# https://manpages.debian.org/testing/dhcpcd5/dhcpcd.conf.5.en.html"

html_atpro_remote_management_routes = Blueprint("html_atpro_remote_management_routes", __name__)


@html_atpro_remote_management_routes.route("/atpro/sensor-rm", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_remote_management():
    if request.method == "POST":
        return remote_management_main_post(request)
    return get_atpro_sensor_remote_management_page()


@html_atpro_remote_management_routes.route("/atpro/rm-ip-list-management", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_control_save_settings():
    if request.method == "POST":
        ip_list_command = str(request.form.get("ip_list_command"))
        selected_ip_list = str(request.form.get("selected_ip_list"))
        new_name = get_clean_ip_list_name(str(request.form.get("ip_list_new_name")))
        current_location = file_locations.custom_ip_lists_folder + "/" + selected_ip_list
        if ip_list_command == "CreateNewIPList":
            CreateIPList(new_name=new_name)
            _update_ip_lists(new_name)
        elif ip_list_command == "RenameIPList":
            new_location = file_locations.custom_ip_lists_folder + "/" + new_name
            os.rename(current_location, new_location)
            _update_ip_lists(new_name)
        elif ip_list_command == "DeleteIPList":
            os.remove(current_location)
            _update_ip_lists()
        return get_html_atpro_index(run_script="SelectNav('rm-ip-list-management', skip_menu_select=true);")
    return render_template("ATPro_admin/page_templates/remote_management/ip-list-management.html",
                           IPListsOptionNames=get_rm_ip_lists_drop_down())


def _update_ip_lists(select_ip_list_name=None):
    ip_list_names = get_list_of_filenames_in_dir(file_locations.custom_ip_lists_folder)
    if len(ip_list_names) == 0:
        CreateIPList().save_list_to_file()
        ip_list_names = get_list_of_filenames_in_dir(file_locations.custom_ip_lists_folder)

    app_config_access.sensor_control_config.custom_ip_list_names = ip_list_names
    if select_ip_list_name is None:
        app_config_access.sensor_control_config.selected_ip_list = ip_list_names[0]
    else:
        app_config_access.sensor_control_config.selected_ip_list = select_ip_list_name
    app_config_access.sensor_control_config.change_ip_list()


@html_atpro_remote_management_routes.route("/atpro/rm/rm-configurations")
def html_atpro_rm_configurations():
    return render_template(
        "ATPro_admin/page_templates/remote_management/configurations.html",
        DefaultPrimaryText=default_primary_config,
        DefaultInstalledSensorsText=default_installed_sensors_config,
        DefaultIntervalRecText=default_interval_recording_config,
        DefaultVarianceRecText=default_variance_config,
        DefaultHighLowRecText=default_high_low_config,
        DefaultDisplayText=default_display_config,
        DefaultEmailText=default_email_config,
        DefaultWifiText=default_wifi_config,
        DefaultNetworkText=default_network_config
    )


@html_atpro_remote_management_routes.route("/atpro/sensor-rm-push-config", methods=["POST"])
@auth.login_required
def html_atpro_sensor_rm_push_configuration():
    c_data = {"config_selection": str(request.form.get("config_selection"))}
    if request.form.get("online_service_interval") is None:
        c_data["new_config_str"] = request.form.get("new_config_str")
    else:
        active_state = 0
        if request.form.get("enable_online_service") is not None:
            active_state = 1
        c_data["enable_online_service"] = active_state
        c_data["online_service_interval"] = request.form.get("online_service_interval")
    return _push_data_to_sensors("atpro/sensor-rm-receive-config", c_data)


def _push_data_to_sensors(url_command, html_dictionary_data):
    if len(app_config_access.sensor_control_config.get_raw_ip_addresses_as_list()) < 1:
        return _get_missing_sensor_addresses_page()
    if _missing_login_credentials():
        return _get_missing_login_credentials_page()

    ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
    if len(ip_list) < 1:
        return get_message_page("All sensors appear to be Offline", page_url="sensor-rm")
    for ip in ip_list:
        http_command_instance = CreateSensorHTTPCommand(ip, url_command, command_data=html_dictionary_data)
        http_command_instance.send_http_command()
    msg_2 = "HTML configuration data sent to " + str(len(ip_list)) + " Sensors"
    return get_message_page("Sensor Control - Configuration(s) Sent", msg_2, page_url="sensor-rm")


@html_atpro_remote_management_routes.route("/atpro/sensor-rm-receive-config", methods=["POST"])
@auth.login_required
def html_atpro_sensor_rm_receive_configuration():
    return remote_management_receive_configuration(request)


@html_atpro_remote_management_routes.route("/atpro/rm/rm-online-services")
def html_atpro_rm_online_services():
    return render_template("ATPro_admin/page_templates/remote_management/configurations-3rd-party.html")


@html_atpro_remote_management_routes.route("/atpro/rm/rm-system-commands")
def html_atpro_rm_system_commands():
    return render_template("ATPro_admin/page_templates/remote_management/system-commands.html")


@html_atpro_remote_management_routes.route('/atpro/rm-report/<path:filename>')
def html_atpro_get_remote_management_reports(filename):
    if url_is_valid(filename):
        if filename == "combination":
            return app_cached_variables.html_combo_report
        if filename == "system":
            return app_cached_variables.html_system_report
        if filename == "configuration":
            return app_cached_variables.html_config_report
        if filename == "readings":
            return app_cached_variables.html_readings_report
        if filename == "latency":
            return app_cached_variables.html_latency_report
    return ""


@html_atpro_remote_management_routes.route('/atpro/rm/functions/<path:filename>')
def html_atpro_remote_management_functions(filename):
    if url_is_valid(filename):
        if filename == "rm-upgrade-http":
            return run_system_command(network_system_commands.upgrade_http)
        elif filename == "rm-upgrade-smb":
            return run_system_command(network_system_commands.upgrade_smb)
        elif filename == "rm-upgrade-dev-http":
            return run_system_command(network_system_commands.upgrade_http_dev)
        elif filename == "rm-upgrade-dev-smb":
            return run_system_command(network_system_commands.upgrade_smb_dev)
        elif filename == "rm-upgrade-clean-http":
            return run_system_command(network_system_commands.upgrade_http_clean)
        elif filename == "rm-upgrade-system-os":
            return run_system_command(network_system_commands.upgrade_system_os)
        elif filename == "rm-upgrade-pip-modules":
            return run_system_command(network_system_commands.upgrade_pip_modules)
        elif filename == "rm-power-restart-program":
            return run_system_command(network_system_commands.restart_services)
        elif filename == "rm-power-reboot-system":
            return run_system_command(network_system_commands.restart_system)
    return get_message_page("Invalid Remote Sensor Management Command", page_url="sensor-rm", full_reload=False)


def run_system_command(command, include_data=None):
    logger.network_logger.debug("* Sensor Control '" + command + "' initiated by " + str(request.remote_addr))
    if len(app_config_access.sensor_control_config.get_raw_ip_addresses_as_list()) < 1:
        return _get_missing_sensor_addresses_page()

    if _missing_login_credentials():
        return _get_missing_login_credentials_page(full_reload=False)

    ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
    if len(ip_list) < 1:
        msg_1 = "Sensors Offline"
        msg_2 = "All sensors appear to be Offline"
        return get_message_page(msg_1, msg_2, page_url="sensor-rm", full_reload=False)

    for ip in ip_list:
        thread = Thread(target=_system_command_thread, args=(ip, command, include_data))
        thread.daemon = True
        thread.start()
    msg_1 = command + " is now being sent to " + str(len(ip_list)) + " Sensors"
    return get_message_page("Sending Sensor Commands", msg_1, page_url="sensor-rm", full_reload=False)


def _system_command_thread(ip, command, include_data=None):
    if _login_successful(ip):
        if include_data is not None:
            send_http_command(ip, command, included_data=include_data)
        else:
            get_http_sensor_reading(ip, command=command)


def _login_successful(ip):
    if get_http_sensor_reading(ip, command=network_commands.check_portal_login) == "OK":
        return True
    logger.network_logger.warning("The Sensor " + str(ip) + " did not accept provided Login Credentials")
    return False


def _missing_login_credentials():
    if app_cached_variables.http_login == "" or app_cached_variables.http_password == "":
        return True
    return False


def _get_missing_login_credentials_page(full_reload=True):
    msg_1 = "Missing Remote Sensor Management Credentials"
    msg_2 = "Login Credentials cannot be blank for this operation"
    return get_message_page(msg_1, msg_2, page_url="sensor-rm", full_reload=full_reload)


def _get_missing_sensor_addresses_page(full_reload=True):
    msg_1 = "No Sensors set Sensor Address List"
    msg_2 = "Press 'Show/Hide Sensor Address List' under Remote Sensor Management to view & set sensor addresses"
    return get_message_page(msg_1, msg_2, page_url="sensor-rm", full_reload=full_reload)
