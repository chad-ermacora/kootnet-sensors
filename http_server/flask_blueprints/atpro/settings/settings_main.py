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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import check_for_new_version
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications

html_atpro_settings_routes = Blueprint("html_atpro_settings_routes", __name__)


@html_atpro_settings_routes.route("/atpro/sensor-settings")
@auth.login_required
def html_atpro_sensor_settings(run_script="SelectSettingsNav('settings-main');"):
    return render_template("ATPro_admin/page_templates/settings.html", RunScript=run_script)


@html_atpro_settings_routes.route("/atpro/settings-main", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_main():
    if request.method == "POST":
        app_config_access.primary_config.update_with_html_request(request)
        app_config_access.primary_config.save_config_to_file()
        if app_config_access.primary_config.web_portal_port_changed:
            atpro_notifications.manage_service_restart()
        return get_message_page("Main Settings Updated", page_url="sensor-settings")

    debug_logging = get_html_checkbox_state(app_config_access.primary_config.enable_debug_logging)
    enable_major_upgrades = get_html_checkbox_state(app_config_access.upgrades_config.enable_automatic_upgrades_feature)
    enable_minor_upgrades = get_html_checkbox_state(app_config_access.upgrades_config.enable_automatic_upgrades_minor)
    enable_dev_up = get_html_checkbox_state(app_config_access.upgrades_config.enable_automatic_upgrades_developmental)
    upgrade_method_http = ""
    upgrade_method_smb = ""
    if app_config_access.upgrades_config.selected_upgrade_type == app_config_access.upgrades_config.upgrade_type_http:
        upgrade_method_http = "selected"
    else:
        upgrade_method_smb = "selected"
    return render_template(
        "ATPro_admin/page_templates/settings/settings-main.html",
        IPWebPort=app_config_access.primary_config.web_portal_port,
        CheckedDebug=debug_logging,
        HourOffset=app_config_access.primary_config.utc0_hour_offset,
        EnableAutoUpgrades=get_html_checkbox_state(app_config_access.upgrades_config.enable_automatic_upgrades),
        AutoUpDelayHours=str(app_config_access.upgrades_config.automatic_upgrade_delay_hours),
        HTTPSelected=upgrade_method_http,
        SMBSelected=upgrade_method_smb,
        SMBUsername=app_config_access.upgrades_config.smb_user,
        EnableStableFeatureAutoUpgrades=enable_major_upgrades,
        EnableStableMinorAutoUpgrades=enable_minor_upgrades,
        EnableDevAutoUpgrades=enable_dev_up,
        CheckinAddress=app_config_access.urls_config.url_checkin_server,
        UpdateServerAddress=app_config_access.urls_config.url_update_server,
        UpdateServerAddressSMB=app_config_access.urls_config.url_update_server_smb,
        USMD5=_get_file_present_color(app_cached_variables.update_server_file_present_md5),
        USVersion=_get_file_present_color(app_cached_variables.update_server_file_present_version),
        USFullInstaller=_get_file_present_color(app_cached_variables.update_server_file_present_full_installer),
        USUpgradeInstaller=_get_file_present_color(app_cached_variables.update_server_file_present_upgrade_installer)
    )


def _get_file_present_color(upgrade_file):
    if upgrade_file is None:
        return ""
    if upgrade_file:
        return "green"
    return "red"


@html_atpro_settings_routes.route("/atpro/settings-upgrades", methods=["POST"])
@auth.login_required
def html_atpro_sensor_settings_upgrades():
    validate_smb_username = app_config_access.upgrades_config.validate_smb_username
    validate_smb_password = app_config_access.upgrades_config.validate_smb_password
    bad_cred_msg = "The username must be alphanumeric and the password must not contain single quotes or ="
    if not validate_smb_username(request.form.get("smb_username")) \
            or not validate_smb_password(request.form.get("smb_password")) and request.form.get("smb_password") != "":
        logger.primary_logger.warning("The provided SMB username or password has invalid characters")
        return get_message_page("Invalid SMB username or password", message=bad_cred_msg, page_url="sensor-settings")
    app_config_access.upgrades_config.update_with_html_request(request)
    app_config_access.upgrades_config.save_config_to_file()
    app_cached_variables.restart_automatic_upgrades_thread = True
    return get_message_page("Upgrade Settings Updated", page_url="sensor-settings")


@html_atpro_settings_routes.route("/atpro/settings-urls", methods=["POST"])
@auth.login_required
def html_atpro_sensor_settings_urls():
    app_config_access.urls_config.update_with_html_request(request)
    app_config_access.urls_config.save_config_to_file()
    thread_function(check_for_new_version)
    app_cached_variables.restart_automatic_upgrades_thread = True
    return get_message_page("URL Settings Updated", page_url="sensor-settings")


@html_atpro_settings_routes.route("/atpro/reset-urls-config")
@auth.login_required
def html_atpro_sensor_settings_urls_reset():
    app_config_access.urls_config.reset_urls_to_default()
    thread_function(check_for_new_version)
    return get_message_page("URLs Configuration Reset", page_url="sensor-settings")


@html_atpro_settings_routes.route("/atpro/settings-is", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_installed_sensors():
    installed_sensors = app_config_access.installed_sensors
    if request.method == "POST":
        app_config_access.installed_sensors.update_with_html_request(request)
        app_config_access.installed_sensors.save_config_to_file()
        sensor_access.sensors_direct.__init__()
        msg = "Installed sensors updated and re-initialized"
        return get_message_page("Installed Sensors Updated", msg, page_url="sensor-settings")

    return render_template(
        "ATPro_admin/page_templates/settings/settings-installed-sensors.html",
        KootnetDummySensors=get_html_checkbox_state(installed_sensors.kootnet_dummy_sensor),
        SenseHAT=get_html_checkbox_state(installed_sensors.raspberry_pi_sense_hat),
        PimoroniBH1745=get_html_checkbox_state(installed_sensors.pimoroni_bh1745),
        PimoroniAS7262=get_html_checkbox_state(installed_sensors.pimoroni_as7262),
        PimoroniMCP9600=get_html_checkbox_state(installed_sensors.pimoroni_mcp9600),
        PimoroniBMP280=get_html_checkbox_state(installed_sensors.pimoroni_bmp280),
        PimoroniBME280=get_html_checkbox_state(installed_sensors.pimoroni_bme280),
        PimoroniBME680=get_html_checkbox_state(installed_sensors.pimoroni_bme680),
        PimoroniEnviroPHAT=get_html_checkbox_state(installed_sensors.pimoroni_enviro),
        PimoroniEnviro2=get_html_checkbox_state(installed_sensors.pimoroni_enviro2),
        PimoroniEnviroPlus=get_html_checkbox_state(installed_sensors.pimoroni_enviroplus),
        PimoroniPMS5003=get_html_checkbox_state(installed_sensors.pimoroni_pms5003),
        PimoroniMICS6814=get_html_checkbox_state(installed_sensors.pimoroni_mics6814),
        PimoroniRV3028=get_html_checkbox_state(installed_sensors.pimoroni_rv3028),
        PimoroniPA1010D=get_html_checkbox_state(installed_sensors.pimoroni_pa1010d),
        PimoroniSGP30=get_html_checkbox_state(installed_sensors.pimoroni_sgp30),
        PimoroniMSA301=get_html_checkbox_state(installed_sensors.pimoroni_msa301),
        PimoroniLSM303D=get_html_checkbox_state(installed_sensors.pimoroni_lsm303d),
        PimoroniICM20948=get_html_checkbox_state(installed_sensors.pimoroni_icm20948),
        PimoroniVL53L1X=get_html_checkbox_state(installed_sensors.pimoroni_vl53l1x),
        PimoroniLTR559=get_html_checkbox_state(installed_sensors.pimoroni_ltr_559),
        PimoroniVEML6075=get_html_checkbox_state(installed_sensors.pimoroni_veml6075),
        Pimoroni11x7LEDMatrix=get_html_checkbox_state(installed_sensors.pimoroni_matrix_11x7),
        PimoroniSPILCD10_96=get_html_checkbox_state(installed_sensors.pimoroni_st7735),
        PimoroniMonoOLED128x128BW=get_html_checkbox_state(installed_sensors.pimoroni_mono_oled_luma),
        SensirionSPS30=get_html_checkbox_state(installed_sensors.sensirion_sps30),
        W1ThermSensor=get_html_checkbox_state(installed_sensors.w1_therm_sensor)
    )


@html_atpro_settings_routes.route("/atpro/settings-sensor-offsets", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_offsets():
    if request.method == "POST":
        app_config_access.sensor_offsets.update_with_html_request(request)
        app_config_access.sensor_offsets.save_config_to_file()
        return get_message_page("Sensor Offset Settings Updated", page_url="sensor-settings")

    return render_template(
        "ATPro_admin/page_templates/settings/settings-sensor-offsets.html",
        CheckedCustomTempOffset=get_html_checkbox_state(app_config_access.sensor_offsets.enable_temp_offset),
        temperature_offset=app_config_access.sensor_offsets.temperature_offset,
        CheckedCustomTempComp=get_html_checkbox_state(app_config_access.sensor_offsets.enable_temperature_comp_factor),
        CustomTempComp=app_config_access.sensor_offsets.temperature_comp_factor,
    )


@html_atpro_settings_routes.route("/atpro/supported-sensors-info")
def html_atpro_sensor_settings_hw_sensor_info():
    return render_template("ATPro_admin/page_templates/settings/settings-hw-sensor-information.html")


@html_atpro_settings_routes.route("/atpro/settings-display", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_display():
    if request.method == "POST":
        app_config_access.display_config.update_with_html_request(request)
        app_config_access.display_config.save_config_to_file()
        app_cached_variables.restart_mini_display_thread = True
        return get_message_page("Display Settings Updated", page_url="sensor-settings")

    display_numerical_checked = ""
    display_graph_checked = ""
    display_type_numerical = app_config_access.display_config.display_type_numerical
    if app_config_access.display_config.display_type == display_type_numerical:
        display_numerical_checked = "checked"
    else:
        display_graph_checked = "checked"
    return render_template(
        "ATPro_admin/page_templates/settings/settings-display.html",
        CheckedEnableDisplay=get_html_checkbox_state(app_config_access.display_config.enable_display),
        DisplayIntervalDelay=app_config_access.display_config.minutes_between_display,
        DisplayNumericalChecked=display_numerical_checked,
        DisplayGraphChecked=display_graph_checked,
        CheckedSensorUptime=get_html_checkbox_state(app_config_access.display_config.sensor_uptime),
        CheckedCPUTemperature=get_html_checkbox_state(app_config_access.display_config.system_temperature),
        CheckedEnvTemperature=get_html_checkbox_state(app_config_access.display_config.env_temperature),
        CheckedPressure=get_html_checkbox_state(app_config_access.display_config.pressure),
        CheckedAltitude=get_html_checkbox_state(app_config_access.display_config.altitude),
        CheckedHumidity=get_html_checkbox_state(app_config_access.display_config.humidity),
        CheckedDewPoint=get_html_checkbox_state(app_config_access.display_config.dew_point),
        CheckedDistance=get_html_checkbox_state(app_config_access.display_config.distance),
        CheckedGas=get_html_checkbox_state(app_config_access.display_config.gas),
        CheckedPM=get_html_checkbox_state(app_config_access.display_config.particulate_matter),
        CheckedLumen=get_html_checkbox_state(app_config_access.display_config.lumen),
        CheckedColour=get_html_checkbox_state(app_config_access.display_config.color),
        CheckedUltraViolet=get_html_checkbox_state(app_config_access.display_config.ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(app_config_access.display_config.accelerometer),
        CheckedMagnetometer=get_html_checkbox_state(app_config_access.display_config.magnetometer),
        CheckedGyroscope=get_html_checkbox_state(app_config_access.display_config.gyroscope)
    )


@html_atpro_settings_routes.route("/atpro/settings-cs", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_checkin_server():
    if request.method == "POST":
        app_config_access.checkin_config.update_with_html_request(request)
        app_config_access.checkin_config.save_config_to_file()
        return get_message_page("Sensor Checkin Settings Updated", page_url="sensor-settings")
    return _get_checkin_settings_page_render()


@html_atpro_settings_routes.route("/atpro/settings-cs-adv", methods=["POST"])
@auth.login_required
def html_atpro_sensor_settings_checkin_adv():
    if request.method == "POST":
        app_config_access.checkin_config.update_with_html_request_advanced_checkin(request)
        app_config_access.checkin_config.save_config_to_file()
        app_cached_variables.restart_sensor_checkin_thread = True
        return get_message_page("Advanced Checkin Settings Updated", page_url="sensor-settings")
    return _get_checkin_settings_page_render()


def _get_checkin_settings_page_render():
    sensor_check_ins = get_html_checkbox_state(app_config_access.checkin_config.enable_checkin)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-checkin-server.html",
        CheckedSensorCheckIns=sensor_check_ins,
        CheckinHours=app_config_access.checkin_config.checkin_wait_in_hours,
        CheckedEnableCheckin=get_html_checkbox_state(app_config_access.checkin_config.enable_checkin_recording),
        ContactInPastDays=app_config_access.checkin_config.count_contact_days,
        MaxSensorCount=app_config_access.checkin_config.main_page_max_sensors,
        DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days,
        MaxLinesPerLog=app_config_access.checkin_config.max_log_lines_to_send,
        SensorName=get_html_checkbox_state(app_config_access.checkin_config.send_sensor_name),
        IPAddress=get_html_checkbox_state(app_config_access.checkin_config.send_ip),
        ProgramVersion=get_html_checkbox_state(app_config_access.checkin_config.send_program_version),
        SensorUptime=get_html_checkbox_state(app_config_access.checkin_config.send_system_uptime),
        SystemTemperature=get_html_checkbox_state(app_config_access.checkin_config.send_system_temperature),
        InstalledSensors=get_html_checkbox_state(app_config_access.checkin_config.send_installed_sensors),
        PrimaryLog=get_html_checkbox_state(app_config_access.checkin_config.send_primary_log),
        NetworkLog=get_html_checkbox_state(app_config_access.checkin_config.send_network_log),
        SensorsLog=get_html_checkbox_state(app_config_access.checkin_config.send_sensors_log)
    )
