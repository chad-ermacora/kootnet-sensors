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
from datetime import datetime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_list_of_filenames_in_dir, get_file_size
from operations_modules.http_generic_network import get_http_sensor_reading, send_http_command
from operations_modules.app_validation_checks import url_is_valid
from operations_modules.software_version import version
from operations_modules.software_automatic_upgrades import get_automatic_upgrade_enabled_text
from configuration_modules import app_config_access
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_urls import CreateURLConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_sensor_offsets import CreateSensorOffsetsConfiguration
from configuration_modules.config_check_ins import CreateCheckinConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from configuration_modules.config_sensor_control import CreateIPList
from sensor_modules.system_access import get_ram_space, get_disk_space
from sensor_modules.sensor_access import get_cpu_temperature, get_reading_unit, get_sensors_latency, \
    get_all_available_sensor_readings
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_clean_ip_list_name, get_uptime_str
from http_server.flask_blueprints.atpro.remote_management.rm_receive_configs import \
    remote_management_receive_configuration
from http_server.flask_blueprints.atpro.remote_management.rm_post import remote_management_main_post
from http_server.flask_blueprints.atpro.remote_management.rm_main import \
    get_atpro_sensor_remote_management_page, get_rm_ip_lists_drop_down
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables

base_rm_template_loc = "ATPro_admin/page_templates/remote_management/report_templates/"
db_v = app_cached_variables.database_variables
network_commands = app_cached_variables.network_get_commands
network_system_commands = app_cached_variables.network_system_commands

default_primary_config = CreatePrimaryConfiguration(load_from_file=False).get_config_as_str()
default_primary_config = default_primary_config.replace("\n", "\\n")
default_urls_config = CreateURLConfiguration(load_from_file=False).get_config_as_str()
default_urls_config = default_urls_config.replace("\n", "\\n")
default_installed_sensors_config = CreateInstalledSensorsConfiguration(load_from_file=False).get_config_as_str()
default_installed_sensors_config = default_installed_sensors_config.replace("\n", "\\n")
default_sensor_offsets_config = CreateSensorOffsetsConfiguration(load_from_file=False).get_config_as_str()
default_sensor_offsets_config = default_sensor_offsets_config.replace("\n", "\\n")
default_checkins_config = CreateCheckinConfiguration(load_from_file=False).get_config_as_str()
default_checkins_config = default_checkins_config.replace("\n", "\\n")
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


@html_atpro_remote_management_routes.route("/atpro/rm-get-system-entry")
def get_system_report_entry():
    try:
        cpu_temp = get_cpu_temperature()
        if cpu_temp is not None:
            cpu_temp = str(get_cpu_temperature()[db_v.system_temperature])
        else:
            cpu_temp = "0.0"
        return render_template(base_rm_template_loc + "report-system-sensor-template.html",
                               SensorID=app_config_access.primary_config.sensor_id,
                               SensorName=app_cached_variables.hostname,
                               RSMAddressAndPort="{{ RSMAddressAndPort }}",
                               LoginCheck="{{ LoginCheck }}",
                               CPUTemp=cpu_temp,
                               CPUResponseBackground=_get_cpu_background_colour(cpu_temp),
                               SensorResponseTime="{{ SensorResponseTime }}",
                               ResponseBackground="{{ ResponseBackground }}",
                               OSVersion=app_cached_variables.operating_system_name,
                               SensorDateTime=datetime.utcnow().strftime("%Y-%m-%d %H:%M - UTC 0"),
                               SystemUpTime=get_uptime_str(),
                               ProgramVersion=version,
                               AutomaticUpgrades=get_automatic_upgrade_enabled_text(),
                               LastUpdated=app_cached_variables.program_last_updated,
                               FreeRAM=get_ram_space(),
                               FreeDiskSpace=get_disk_space(),
                               MainDBSize=get_file_size(file_locations.sensor_database),
                               MQTTSubDBSize=get_file_size(file_locations.mqtt_subscriber_database),
                               CheckinDBSize=get_file_size(file_locations.sensor_checkin_database))
    except Exception as error:
        logger.network_logger.error("System Report - " + str(error))
        return "System Report - " + str(error)


def _get_cpu_background_colour(cpu_temp):
    cpu_temp_background = "darkgreen"
    try:
        cpu_temp_int = float(cpu_temp)
        if cpu_temp_int == 0.0:
            cpu_temp_background = "purple"
        if cpu_temp_int > 80:
            cpu_temp_background = "red"
        elif cpu_temp_int > 70:
            cpu_temp_background = "#8b4c00"
    except Exception as error:
        logger.network_logger.debug("Error: CPU background for System Report - " + str(error))
        cpu_temp_background = "purple"
    return cpu_temp_background


@html_atpro_remote_management_routes.route("/atpro/rm-get-config-entry")
@auth.login_required
def get_config_report_entry():
    aca = app_config_access

    debug_logging = _get_enabled_disabled_text(aca.primary_config.enable_debug_logging)
    sensor_checkin = _get_enabled_disabled_text(aca.checkin_config.enable_checkin)
    sensor_checkin_server = _get_enabled_disabled_text(aca.checkin_config.enable_checkin_recording)
    display = _get_enabled_disabled_text(aca.display_config.enable_display)
    email_reports = _get_enabled_disabled_text(aca.email_config.enable_combo_report_emails)
    email_graphs = _get_enabled_disabled_text(aca.email_config.enable_graph_emails)
    interval_recording = _get_enabled_disabled_text(aca.interval_recording_config.enable_interval_recording)
    high_low_recording = _get_enabled_disabled_text(aca.trigger_high_low.enable_high_low_trigger_recording)
    variance_recording = _get_enabled_disabled_text(aca.trigger_variances.enable_trigger_variance)
    temp_offset = _get_enabled_disabled_text(aca.sensor_offsets.enable_temp_offset)
    temp_comp_factor = _get_enabled_disabled_text(aca.sensor_offsets.enable_temperature_comp_factor)
    mqtt_broker = _get_enabled_disabled_text(aca.mqtt_broker_config.enable_mqtt_broker)
    mqtt_subscriber = _get_enabled_disabled_text(aca.mqtt_subscriber_config.enable_mqtt_subscriber)
    mqtt_sub_rec = _get_enabled_disabled_text(aca.mqtt_subscriber_config.enable_mqtt_sql_recording)
    mqtt_publisher = _get_enabled_disabled_text(aca.mqtt_publisher_config.enable_mqtt_publisher)
    wu_enabled = _get_enabled_disabled_text(aca.weather_underground_config.weather_underground_enabled)
    luftdaten_enabled = _get_enabled_disabled_text(aca.luftdaten_config.luftdaten_enabled)
    open_sense_map_enabled = _get_enabled_disabled_text(aca.open_sense_map_config.open_sense_map_enabled)
    ip_and_port = app_cached_variables.ip + ":" + str(app_config_access.primary_config.web_portal_port)
    return render_template(base_rm_template_loc + "report-configurations-sensor-template.html",
                           SensorID=aca.primary_config.sensor_id,
                           InstalledSensors=aca.installed_sensors.get_installed_names_str(),
                           SensorName=app_cached_variables.hostname,
                           ProgramVersion=version,
                           IPAddressAndPort=ip_and_port,
                           RSMAddressAndPort="{{ RSMAddressAndPort }}",
                           LoginCheck="{{ LoginCheck }}",
                           SensorResponseTime="{{ SensorResponseTime }}",
                           ResponseBackground="{{ ResponseBackground }}",
                           DebugLogging=debug_logging,
                           SensorCheckin=sensor_checkin,
                           SensorCheckinServer=sensor_checkin_server,
                           Display=display,
                           WifiNetwork=app_cached_variables.wifi_ssid,
                           EmailReports=email_reports,
                           EmailGraphs=email_graphs,
                           IntervalRecording=interval_recording,
                           IntervalSeconds=aca.interval_recording_config.sleep_duration_interval,
                           HighLowRecording=high_low_recording,
                           VarianceRecording=variance_recording,
                           TemperatureOffset=temp_offset,
                           TOValue=str(app_config_access.sensor_offsets.temperature_offset),
                           TemperatureCorrectionFactor=temp_comp_factor,
                           TCFValue=str(app_config_access.sensor_offsets.temperature_comp_factor),
                           MQTTBroker=mqtt_broker,
                           MQTTSubscriber=mqtt_subscriber,
                           MQTTSubscriberRecording=mqtt_sub_rec,
                           MQTTPublisher=mqtt_publisher,
                           WeatherUnderground=wu_enabled,
                           Luftdaten=luftdaten_enabled,
                           OpenSenseMap=open_sense_map_enabled)


def _get_enabled_disabled_text(setting):
    if setting:
        return "Enabled"
    return "Disabled"


@html_atpro_remote_management_routes.route("/atpro/rm-get-readings-entry")
def get_readings_report_entry():
    sensor_readings = get_all_available_sensor_readings()
    readings_name = []
    readings_data = []
    for index, reading in sensor_readings.items():
        readings_name.append(index)
        readings_data.append(reading)
    return render_template(base_rm_template_loc + "report-readings-latency-sensor-template.html",
                           SensorID=app_config_access.primary_config.sensor_id,
                           SensorName=app_cached_variables.hostname,
                           RSMAddressAndPort="{{ RSMAddressAndPort }}",
                           SensorDateTime=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S - UTC 0"),
                           SensorResponseTime="{{ SensorResponseTime }}",
                           ResponseBackground="{{ ResponseBackground }}",
                           SensorInfoBoxes=_convert_lists_to_html_thread(readings_name, readings_data))


@html_atpro_remote_management_routes.route("/atpro/rm-get-latency-entry")
def get_latency_report_entry():
    latency_dic = get_sensors_latency()
    sensor_names = []
    sensor_latency = []
    for name, entry in latency_dic.items():
        if entry is not None:
            sensor_names.append(name)
            sensor_latency.append(entry)
    return render_template(base_rm_template_loc + "report-readings-latency-sensor-template.html",
                           SensorID=app_config_access.primary_config.sensor_id,
                           SensorName=app_cached_variables.hostname,
                           RSMAddressAndPort="{{ RSMAddressAndPort }}",
                           SensorDateTime=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S - UTC 0"),
                           SensorResponseTime="{{ SensorResponseTime }}",
                           ResponseBackground="{{ ResponseBackground }}",
                           SensorInfoBoxes=_convert_lists_to_html_thread(sensor_names, sensor_latency, latency=True))


def _convert_lists_to_html_thread(list_names, list_data, latency=False):
    return_labels = "<thead><tr>"
    return_readings = "<tbody><tr>"
    for sensor_type, sensor_reading in zip(list_names, list_data):
        sensor_type = str(sensor_type)
        sensor_reading = str(sensor_reading)
        if sensor_type != "SensorName" and sensor_type != "IP":
            if latency:
                reading_unit = "Sec"
            else:
                reading_unit = get_reading_unit(sensor_type)
            return_labels += "<td><span class='sensor-info'>" + sensor_type.replace("_", " ") + "</span></td>"
            return_readings += "<td>" + sensor_reading + " " + reading_unit + "</td>"
    return return_labels + "</tr></thead>\n\n" + return_readings + "</tr></tbody>"


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
        DefaultURLsText=default_urls_config,
        DefaultInstalledSensorsText=default_installed_sensors_config,
        DefaultSensorOffsetsText=default_sensor_offsets_config,
        DefaultCheckinsText=default_checkins_config,
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
        send_http_command(ip, url_command, dic_data=html_dictionary_data)
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
            return rm_cached_variables.html_combo_report
        if filename == "system":
            return rm_cached_variables.html_system_report
        if filename == "configuration":
            return rm_cached_variables.html_config_report
        if filename == "readings":
            return rm_cached_variables.html_readings_report
        if filename == "latency":
            return rm_cached_variables.html_latency_report
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


def run_system_command(command):
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
        thread = Thread(target=_system_command_thread, args=(ip, command))
        thread.daemon = True
        thread.start()
    msg_1 = command + " is now being sent to " + str(len(ip_list)) + " Sensors"
    return get_message_page("Sending Sensor Commands", msg_1, page_url="sensor-rm", full_reload=False)


def _system_command_thread(ip, command):
    if _login_successful(ip):
        get_http_sensor_reading(ip, http_command=command)


def _login_successful(ip):
    if get_http_sensor_reading(ip, http_command=network_commands.check_portal_login) == "OK":
        return True
    logger.network_logger.warning("The Sensor " + str(ip) + " did not accept provided Login Credentials")
    return False


def _missing_login_credentials():
    if rm_cached_variables.http_login == "" or rm_cached_variables.http_password == "":
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
