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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, thread_function
from operations_modules.app_validation_checks import email_is_valid
from operations_modules.email_server import send_test_email, send_report_email, send_quick_graph_email
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from mqtt.server_mqtt_broker import start_mqtt_broker_server, restart_mqtt_broker_server, stop_mqtt_broker_server, \
    check_mqtt_broker_server_running
from online_services_modules.open_sense_map import start_open_sense_map_server, add_sensor_to_account
from online_services_modules.weather_underground import start_weather_underground_server
from online_services_modules.luftdaten import start_luftdaten_server
from http_server.server_http_generic_functions import get_html_checkbox_state, get_html_selected_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_message_page

html_atpro_settings_routes = Blueprint("html_atpro_settings_routes", __name__)
email_config = app_config_access.email_config
db_v = app_cached_variables.database_variables


@html_atpro_settings_routes.route("/atpro/sensor-settings")
def html_atpro_sensor_settings(run_script="SelectSettingsNav('settings-main');"):
    return render_template("ATPro_admin/page_templates/settings.html", RunScript=run_script)


@html_atpro_settings_routes.route("/atpro/settings-main", methods=["GET", "POST"])
def html_atpro_sensor_settings_main():
    if request.method == "POST":
        app_config_access.primary_config.update_with_html_request(request)
        app_config_access.primary_config.save_config_to_file()
        app_cached_variables.restart_sensor_checkin_thread = True
        return get_message_page("Main Settings Updated", page_url="sensor-settings")

    debug_logging = get_html_checkbox_state(app_config_access.primary_config.enable_debug_logging)
    sensor_check_ins = get_html_checkbox_state(app_config_access.primary_config.enable_checkin)
    custom_temp_offset = get_html_checkbox_state(app_config_access.primary_config.enable_custom_temp)
    custom_temp_comp = get_html_checkbox_state(app_config_access.primary_config.enable_temperature_comp_factor)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-main.html",
        IPWebPort=app_config_access.primary_config.web_portal_port,
        CheckedDebug=debug_logging,
        HourOffset=app_config_access.primary_config.utc0_hour_offset,
        CheckedSensorCheckIns=sensor_check_ins,
        CheckinHours=app_config_access.primary_config.checkin_wait_in_hours,
        CheckinAddress=app_config_access.primary_config.checkin_url,
        CheckedCustomTempOffset=custom_temp_offset,
        temperature_offset=float(app_config_access.primary_config.temperature_offset),
        CheckedCustomTempComp=custom_temp_comp,
        CustomTempComp=float(app_config_access.primary_config.temperature_comp_factor)
    )


@html_atpro_settings_routes.route("/atpro/settings-is", methods=["GET", "POST"])
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
        PageURL="/MainConfigurationsHTML",
        GnuLinux=get_html_checkbox_state(installed_sensors.linux_system),
        KootnetDummySensors=get_html_checkbox_state(installed_sensors.kootnet_dummy_sensor),
        RaspberryPi=get_html_checkbox_state(installed_sensors.raspberry_pi),
        SenseHAT=get_html_checkbox_state(installed_sensors.raspberry_pi_sense_hat),
        PimoroniBH1745=get_html_checkbox_state(installed_sensors.pimoroni_bh1745),
        PimoroniAS7262=get_html_checkbox_state(installed_sensors.pimoroni_as7262),
        PimoroniMCP9600=get_html_checkbox_state(installed_sensors.pimoroni_mcp9600),
        PimoroniBMP280=get_html_checkbox_state(installed_sensors.pimoroni_bmp280),
        PimoroniBME680=get_html_checkbox_state(installed_sensors.pimoroni_bme680),
        PimoroniEnviroPHAT=get_html_checkbox_state(installed_sensors.pimoroni_enviro),
        PimoroniEnviro2=get_html_checkbox_state(installed_sensors.pimoroni_enviro2),
        PimoroniEnviroPlus=get_html_checkbox_state(installed_sensors.pimoroni_enviroplus),
        PimoroniPMS5003=get_html_checkbox_state(installed_sensors.pimoroni_pms5003),
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


@html_atpro_settings_routes.route("/atpro/settings-display", methods=["GET", "POST"])
def html_atpro_sensor_settings_display():
    if request.method == "POST":
        app_config_access.display_config.update_with_html_request(request)
        app_config_access.display_config.save_config_to_file()
        app_cached_variables.restart_mini_display_thread = True
        return get_message_page("Display Settings Updated", "Restarting Display Service", page_url="sensor-settings")

    display_numerical_checked = ""
    display_graph_checked = ""
    display_type_numerical = app_config_access.display_config.display_type_numerical
    if app_config_access.display_config.display_type == display_type_numerical:
        display_numerical_checked = "checked"
    else:
        display_graph_checked = "checked"

    return render_template(
        "ATPro_admin/page_templates/settings/settings-display.html",
        PageURL="/DisplayConfigurationsHTML",
        CheckedEnableDisplay=get_html_checkbox_state(app_config_access.display_config.enable_display),
        DisplayIntervalDelay=app_config_access.display_config.minutes_between_display,
        DisplayNumericalChecked=display_numerical_checked,
        DisplayGraphChecked=display_graph_checked,
        DisplayUptimeChecked=get_html_checkbox_state(app_config_access.display_config.sensor_uptime),
        DisplayCPUTempChecked=get_html_checkbox_state(app_config_access.display_config.system_temperature),
        DisplayEnvTempChecked=get_html_checkbox_state(app_config_access.display_config.env_temperature),
        DisplayPressureChecked=get_html_checkbox_state(app_config_access.display_config.pressure),
        DisplayAltitudeChecked=get_html_checkbox_state(app_config_access.display_config.altitude),
        DisplayHumidityChecked=get_html_checkbox_state(app_config_access.display_config.humidity),
        DisplayDistanceChecked=get_html_checkbox_state(app_config_access.display_config.distance),
        DisplayGASChecked=get_html_checkbox_state(app_config_access.display_config.gas),
        DisplayPMChecked=get_html_checkbox_state(app_config_access.display_config.particulate_matter),
        DisplayLumenChecked=get_html_checkbox_state(app_config_access.display_config.lumen),
        DisplayColoursChecked=get_html_checkbox_state(app_config_access.display_config.color),
        DisplayUltraVioletChecked=get_html_checkbox_state(app_config_access.display_config.ultra_violet),
        DisplayAccChecked=get_html_checkbox_state(app_config_access.display_config.accelerometer),
        DisplayMagChecked=get_html_checkbox_state(app_config_access.display_config.magnetometer),
        DisplayGyroChecked=get_html_checkbox_state(app_config_access.display_config.gyroscope)
    )


@html_atpro_settings_routes.route("/atpro/settings-cs", methods=["GET", "POST"])
def html_atpro_sensor_settings_checkin_server():
    if request.method == "POST":
        app_config_access.checkin_config.update_with_html_request(request)
        app_config_access.checkin_config.save_config_to_file()
        return get_message_page("Checkin Server Settings Updated", page_url="sensor-settings")

    return render_template(
        "ATPro_admin/page_templates/settings/settings-checkin-server.html",
        PageURL="/CheckinServerConfigurationHTML",
        CheckedEnableCheckin=get_html_checkbox_state(app_config_access.checkin_config.enable_checkin_recording),
        ContactInPastDays=app_config_access.checkin_config.count_contact_days,
        DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days
    )


@html_atpro_settings_routes.route("/atpro/settings-interval", methods=["GET", "POST"])
def html_atpro_sensor_settings_interval():
    if request.method == "POST":
        app_config_access.interval_recording_config.update_with_html_request(request)
        app_config_access.interval_recording_config.save_config_to_file()
        app_cached_variables.restart_interval_recording_thread = True
        return get_message_page("Interval Settings Saved", page_url="sensor-settings")
    interval_config = app_config_access.interval_recording_config
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-interval.html",
        PageURL="/MainConfigurationsHTML",
        CheckedInterval=get_html_checkbox_state(interval_config.enable_interval_recording),
        IntervalDelay=float(interval_config.sleep_duration_interval),
        CheckedSensorUptime=get_html_checkbox_state(interval_config.sensor_uptime_enabled),
        CheckedCPUTemperature=get_html_checkbox_state(interval_config.cpu_temperature_enabled),
        CheckedEnvTemperature=get_html_checkbox_state(interval_config.env_temperature_enabled),
        CheckedPressure=get_html_checkbox_state(interval_config.pressure_enabled),
        CheckedAltitude=get_html_checkbox_state(interval_config.altitude_enabled),
        CheckedHumidity=get_html_checkbox_state(interval_config.humidity_enabled),
        CheckedDewPoint=get_html_checkbox_state(interval_config.dew_point_enabled),
        CheckedDistance=get_html_checkbox_state(interval_config.distance_enabled),
        CheckedLumen=get_html_checkbox_state(interval_config.lumen_enabled),
        CheckedColour=get_html_checkbox_state(interval_config.colour_enabled),
        CheckedUltraViolet=get_html_checkbox_state(interval_config.ultra_violet_enabled),
        CheckedGas=get_html_checkbox_state(interval_config.gas_enabled),
        CheckedPM=get_html_checkbox_state(interval_config.particulate_matter_enabled),
        CheckedAccelerometer=get_html_checkbox_state(interval_config.accelerometer_enabled),
        CheckedMagnetometer=get_html_checkbox_state(interval_config.magnetometer_enabled),
        CheckedGyroscope=get_html_checkbox_state(interval_config.gyroscope_enabled)
    )


@html_atpro_settings_routes.route("/atpro/settings-hl", methods=["GET", "POST"])
def html_atpro_sensor_settings_high_low():
    if request.method == "POST":
        app_config_access.trigger_high_low.update_with_html_request(request)
        app_config_access.trigger_high_low.save_config_to_file()
        app_cached_variables.html_service_restart = True
        return get_message_page("Trigger High/Low Settings Saved",
                                "Please Restart Program", page_url="sensor-settings")
    high_low_settings = app_config_access.trigger_high_low
    recording_enabled = get_html_checkbox_state(high_low_settings.enable_high_low_trigger_recording)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-high-low.html",
        CheckedEnableHLTRecording=recording_enabled,
        CheckedCPUTemperature=get_html_checkbox_state(high_low_settings.cpu_temperature_enabled),
        TriggerLowCPUTemperature=high_low_settings.cpu_temperature_low,
        TriggerHighCPUTemperature=high_low_settings.cpu_temperature_high,
        SecondsCPUTemperature=high_low_settings.cpu_temperature_wait_seconds,
        CheckedEnvTemperature=get_html_checkbox_state(high_low_settings.env_temperature_enabled),
        TriggerLowEnvTemperature=high_low_settings.env_temperature_low,
        TriggerHighEnvTemperature=high_low_settings.env_temperature_high,
        SecondsEnvTemperature=high_low_settings.env_temperature_wait_seconds,
        CheckedPressure=get_html_checkbox_state(high_low_settings.pressure_enabled),
        TriggerLowPressure=high_low_settings.pressure_low,
        TriggerHighPressure=high_low_settings.pressure_high,
        SecondsPressure=high_low_settings.pressure_wait_seconds,
        CheckedAltitude=get_html_checkbox_state(high_low_settings.altitude_enabled),
        TriggerLowAltitude=high_low_settings.altitude_low,
        TriggerHighAltitude=high_low_settings.altitude_high,
        SecondsAltitude=high_low_settings.altitude_wait_seconds,
        CheckedHumidity=get_html_checkbox_state(high_low_settings.humidity_enabled),
        TriggerLowHumidity=high_low_settings.humidity_low,
        TriggerHighHumidity=high_low_settings.humidity_high,
        SecondsHumidity=high_low_settings.humidity_wait_seconds,
        CheckedDistance=get_html_checkbox_state(high_low_settings.distance_enabled),
        TriggerLowDistance=high_low_settings.distance_low,
        TriggerHighDistance=high_low_settings.distance_high,
        SecondsDistance=high_low_settings.distance_wait_seconds,
        CheckedLumen=get_html_checkbox_state(high_low_settings.lumen_enabled),
        TriggerLowLumen=high_low_settings.lumen_low,
        TriggerHighLumen=high_low_settings.lumen_high,
        SecondsLumen=high_low_settings.lumen_wait_seconds,
        CheckedColour=get_html_checkbox_state(high_low_settings.colour_enabled),
        TriggerLowRed=high_low_settings.red_low,
        TriggerHighRed=high_low_settings.red_high,
        TriggerLowOrange=high_low_settings.orange_low,
        TriggerHighOrange=high_low_settings.orange_high,
        TriggerLowYellow=high_low_settings.yellow_low,
        TriggerHighYellow=high_low_settings.yellow_high,
        TriggerLowGreen=high_low_settings.green_low,
        TriggerHighGreen=high_low_settings.green_high,
        TriggerLowBlue=high_low_settings.blue_low,
        TriggerHighBlue=high_low_settings.blue_high,
        TriggerLowViolet=high_low_settings.violet_low,
        TriggerHighViolet=high_low_settings.violet_high,
        SecondsColour=high_low_settings.colour_wait_seconds,
        CheckedUltraViolet=get_html_checkbox_state(high_low_settings.ultra_violet_enabled),
        TriggerLowUltraVioletA=high_low_settings.ultra_violet_a_low,
        TriggerHighUltraVioletA=high_low_settings.ultra_violet_a_high,
        TriggerLowUltraVioletB=high_low_settings.ultra_violet_b_low,
        TriggerHighUltraVioletB=high_low_settings.ultra_violet_b_high,
        SecondsUltraViolet=high_low_settings.ultra_violet_wait_seconds,
        CheckedGas=get_html_checkbox_state(high_low_settings.gas_enabled),
        TriggerLowGasIndex=high_low_settings.gas_resistance_index_low,
        TriggerHighGasIndex=high_low_settings.gas_resistance_index_high,
        TriggerLowGasOxidising=high_low_settings.gas_oxidising_low,
        TriggerHighGasOxidising=high_low_settings.gas_oxidising_high,
        TriggerLowGasReducing=high_low_settings.gas_reducing_low,
        TriggerHighGasReducing=high_low_settings.gas_reducing_high,
        TriggerLowGasNH3=high_low_settings.gas_nh3_low,
        TriggerHighGasNH3=high_low_settings.gas_nh3_high,
        SecondsGas=high_low_settings.gas_wait_seconds,
        CheckedPM=get_html_checkbox_state(high_low_settings.particulate_matter_enabled),
        TriggerLowPM1=high_low_settings.particulate_matter_1_low,
        TriggerHighPM1=high_low_settings.particulate_matter_1_high,
        TriggerLowPM25=high_low_settings.particulate_matter_2_5_low,
        TriggerHighPM25=high_low_settings.particulate_matter_2_5_high,
        TriggerLowPM4=high_low_settings.particulate_matter_4_low,
        TriggerHighPM4=high_low_settings.particulate_matter_4_high,
        TriggerLowPM10=high_low_settings.particulate_matter_10_low,
        TriggerHighPM10=high_low_settings.particulate_matter_10_high,
        SecondsPM=high_low_settings.particulate_matter_wait_seconds,
        CheckedAccelerometer=get_html_checkbox_state(high_low_settings.accelerometer_enabled),
        TriggerLowAccelerometerX=high_low_settings.accelerometer_x_low,
        TriggerHighAccelerometerX=high_low_settings.accelerometer_x_high,
        TriggerLowAccelerometerY=high_low_settings.accelerometer_y_low,
        TriggerHighAccelerometerY=high_low_settings.accelerometer_y_high,
        TriggerLowAccelerometerZ=high_low_settings.accelerometer_z_low,
        TriggerHighAccelerometerZ=high_low_settings.accelerometer_z_high,
        SecondsAccelerometer=high_low_settings.accelerometer_wait_seconds,
        CheckedMagnetometer=get_html_checkbox_state(high_low_settings.magnetometer_enabled),
        TriggerLowMagnetometerX=high_low_settings.magnetometer_x_low,
        TriggerHighMagnetometerX=high_low_settings.magnetometer_x_high,
        TriggerLowMagnetometerY=high_low_settings.magnetometer_y_low,
        TriggerHighMagnetometerY=high_low_settings.magnetometer_y_high,
        TriggerLowMagnetometerZ=high_low_settings.magnetometer_z_low,
        TriggerHighMagnetometerZ=high_low_settings.magnetometer_z_high,
        SecondsMagnetometer=high_low_settings.magnetometer_wait_seconds,
        CheckedGyroscope=get_html_checkbox_state(high_low_settings.gyroscope_enabled),
        TriggerLowGyroscopeX=high_low_settings.gyroscope_x_low,
        TriggerHighGyroscopeX=high_low_settings.gyroscope_x_high,
        TriggerLowGyroscopeY=high_low_settings.gyroscope_y_low,
        TriggerHighGyroscopeY=high_low_settings.gyroscope_y_high,
        TriggerLowGyroscopeZ=high_low_settings.gyroscope_z_low,
        TriggerHighGyroscopeZ=high_low_settings.gyroscope_z_high,
        SecondsGyroscope=high_low_settings.gyroscope_wait_seconds
    )


@html_atpro_settings_routes.route("/atpro/settings-variances", methods=["GET", "POST"])
def html_atpro_sensor_settings_variances():
    if request.method == "POST":
        app_config_access.trigger_variances.update_with_html_request(request)
        app_config_access.trigger_variances.save_config_to_file()
        app_cached_variables.html_service_restart = True
        return get_message_page("Trigger Variances Settings Saved",
                                "Please Restart Program", page_url="sensor-settings")
    variances = app_config_access.trigger_variances
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-variances.html",
        PageURL="/MainConfigurationsHTML",
        CheckedTrigger=get_html_checkbox_state(variances.enable_trigger_variance),
        CheckedCPUTemperature=get_html_checkbox_state(variances.cpu_temperature_enabled),
        TriggerCPUTemperature=variances.cpu_temperature_variance,
        SecondsCPUTemperature=variances.cpu_temperature_wait_seconds,
        CheckedEnvTemperature=get_html_checkbox_state(variances.env_temperature_enabled),
        TriggerEnvTemperature=variances.env_temperature_variance,
        SecondsEnvTemperature=variances.env_temperature_wait_seconds,
        CheckedPressure=get_html_checkbox_state(variances.pressure_enabled),
        TriggerPressure=variances.pressure_variance,
        SecondsPressure=variances.pressure_wait_seconds,
        CheckedAltitude=get_html_checkbox_state(variances.altitude_enabled),
        TriggerAltitude=variances.altitude_variance,
        SecondsAltitude=variances.altitude_wait_seconds,
        CheckedHumidity=get_html_checkbox_state(variances.humidity_enabled),
        TriggerHumidity=variances.humidity_variance,
        SecondsHumidity=variances.humidity_wait_seconds,
        CheckedDistance=get_html_checkbox_state(variances.distance_enabled),
        TriggerDistance=variances.distance_variance,
        SecondsDistance=variances.distance_wait_seconds,
        CheckedLumen=get_html_checkbox_state(variances.lumen_enabled),
        TriggerLumen=variances.lumen_variance,
        SecondsLumen=variances.lumen_wait_seconds,
        CheckedColour=get_html_checkbox_state(variances.colour_enabled),
        TriggerRed=variances.red_variance,
        TriggerOrange=variances.orange_variance,
        TriggerYellow=variances.yellow_variance,
        TriggerGreen=variances.green_variance,
        TriggerBlue=variances.blue_variance,
        TriggerViolet=variances.violet_variance,
        SecondsColour=variances.colour_wait_seconds,
        CheckedUltraViolet=get_html_checkbox_state(variances.ultra_violet_enabled),
        TriggerUltraVioletA=variances.ultra_violet_a_variance,
        TriggerUltraVioletB=variances.ultra_violet_b_variance,
        SecondsUltraViolet=variances.ultra_violet_wait_seconds,
        CheckedGas=get_html_checkbox_state(variances.gas_enabled),
        TriggerGasIndex=variances.gas_resistance_index_variance,
        TriggerGasOxidising=variances.gas_oxidising_variance,
        TriggerGasReducing=variances.gas_reducing_variance,
        TriggerGasNH3=variances.gas_nh3_variance,
        SecondsGas=variances.gas_wait_seconds,
        CheckedPM=get_html_checkbox_state(variances.particulate_matter_enabled),
        TriggerPM1=variances.particulate_matter_1_variance,
        TriggerPM25=variances.particulate_matter_2_5_variance,
        TriggerPM4=variances.particulate_matter_4_variance,
        TriggerPM10=variances.particulate_matter_10_variance,
        SecondsPM=variances.particulate_matter_wait_seconds,
        CheckedAccelerometer=get_html_checkbox_state(variances.accelerometer_enabled),
        TriggerAccelerometerX=variances.accelerometer_x_variance,
        TriggerAccelerometerY=variances.accelerometer_y_variance,
        TriggerAccelerometerZ=variances.accelerometer_z_variance,
        SecondsAccelerometer=variances.accelerometer_wait_seconds,
        CheckedMagnetometer=get_html_checkbox_state(variances.magnetometer_enabled),
        TriggerMagnetometerX=variances.magnetometer_x_variance,
        TriggerMagnetometerY=variances.magnetometer_y_variance,
        TriggerMagnetometerZ=variances.magnetometer_z_variance,
        SecondsMagnetometer=variances.magnetometer_wait_seconds,
        CheckedGyroscope=get_html_checkbox_state(variances.gyroscope_enabled),
        TriggerGyroscopeX=variances.gyroscope_x_variance,
        TriggerGyroscopeY=variances.gyroscope_y_variance,
        TriggerGyroscopeZ=variances.gyroscope_z_variance,
        SecondsGyroscope=variances.gyroscope_wait_seconds
    )


@html_atpro_settings_routes.route("/atpro/settings-email-reports", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_reports():
    if request.method == "POST":
        email_config.update_with_html_request_reports(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        app_cached_variables.restart_report_email_thread = True
        return get_message_page("Email Reports Settings Saved", page_url="sensor-settings")

    report_send_selected_options = _get_send_option_selection(email_config.send_report_every)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-email-reports.html",
        CheckedEmailComboReport=get_html_checkbox_state(email_config.enable_combo_report_emails),
        EmailReportsSelectedDaily=report_send_selected_options[0],
        EmailReportsSelectedWeekly=report_send_selected_options[1],
        EmailReportsSelectedMonthly=report_send_selected_options[2],
        EmailReportsSelectedYearly=report_send_selected_options[3],
        EmailReportAtHourMin=email_config.email_reports_time_of_day,
        EmailReportsToCSVAddresses=email_config.send_report_to_csv_emails
    )


def _get_send_option_selection(selected_send_every):
    send_options = [
        app_config_access.email_config.send_option_daily, app_config_access.email_config.send_option_weekly,
        app_config_access.email_config.send_option_monthly, app_config_access.email_config.send_option_yearly
    ]

    selected_values = []
    for send_type in send_options:
        if selected_send_every == send_type:
            selected_values.append("selected")
        else:
            selected_values.append("")
    return selected_values


@html_atpro_settings_routes.route("/atpro/settings-email-graphs", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_graphs():
    if request.method == "POST":
        email_config.update_with_html_request_graph(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        app_cached_variables.restart_graph_email_thread = True
        return get_message_page("Email Graph Settings Saved", page_url="sensor-settings")

    quick_graph_checked = "checked"
    plotly_graph_checked = ""
    if email_config.graph_type:
        plotly_graph_checked = "checked"
        quick_graph_checked = ""

    graph_send_selected_options = _get_send_option_selection(email_config.send_graph_every)

    return render_template("ATPro_admin/page_templates/settings/settings-email-graphs.html",
                           CheckedEmailGraphs=get_html_checkbox_state(email_config.enable_graph_emails),
                           EmailGraphSelectedDaily=graph_send_selected_options[0],
                           EmailGraphSelectedWeekly=graph_send_selected_options[1],
                           EmailGraphSelectedMonthly=graph_send_selected_options[2],
                           EmailGraphSelectedYearly=graph_send_selected_options[3],
                           EmailGraphAtHourMin=email_config.email_graph_time_of_day,
                           EmailGraphsToCSVAddresses=email_config.send_graphs_to_csv_emails,
                           QuickGraphChecked=quick_graph_checked,
                           PlotlyGraphChecked=plotly_graph_checked,
                           GraphsPastHours=email_config.graph_past_hours,
                           SensorUptimeChecked=get_html_checkbox_state(email_config.sensor_uptime),
                           CPUTemperatureChecked=get_html_checkbox_state(email_config.system_temperature),
                           EnvTemperatureChecked=get_html_checkbox_state(email_config.env_temperature),
                           PressureChecked=get_html_checkbox_state(email_config.pressure),
                           AltitudeChecked=get_html_checkbox_state(email_config.altitude),
                           HumidityChecked=get_html_checkbox_state(email_config.humidity),
                           DistanceChecked=get_html_checkbox_state(email_config.distance),
                           GasChecked=get_html_checkbox_state(email_config.gas),
                           PMChecked=get_html_checkbox_state(email_config.particulate_matter),
                           LumenChecked=get_html_checkbox_state(email_config.lumen),
                           ColoursChecked=get_html_checkbox_state(email_config.color),
                           UltraVioletChecked=get_html_checkbox_state(email_config.ultra_violet),
                           AccChecked=get_html_checkbox_state(email_config.accelerometer),
                           MagChecked=get_html_checkbox_state(email_config.magnetometer),
                           GyroChecked=get_html_checkbox_state(email_config.gyroscope)
                           )


@html_atpro_settings_routes.route("/atpro/settings-email-settings", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_smtp():
    if request.method == "POST":
        email_config.update_with_html_request_server(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        return get_message_page("Email SMTP Settings Saved", page_url="sensor-settings")

    return render_template("ATPro_admin/page_templates/settings/settings-email-smtp.html",
                           ServerSendingEmail=email_config.server_sending_email,
                           ServerSMTPAddress=email_config.server_smtp_address,
                           CheckedEmailSSL=get_html_checkbox_state(email_config.server_smtp_ssl_enabled),
                           ServerSMTPPort=email_config.server_smtp_port,
                           ServerSMTPUser=email_config.server_smtp_user)


@html_atpro_settings_routes.route("/atpro/test-email", methods=["POST"])
@auth.login_required
def html_atpro_send_reports_email():
    logger.network_logger.debug("** HTML Reports Email Sent - Source: " + str(request.remote_addr))
    button_pressed = request.form.get("test_email_button")
    email_address = request.form.get("test_email_address")
    if email_is_valid(email_address):
        if button_pressed == "reports":
            thread_function(send_report_email, args=email_address)
            return get_message_page("Reports email is being sent", page_url="sensor-settings")
        elif button_pressed == "graphs":
            thread_function(send_quick_graph_email, args=email_address)
            return get_message_page("Graph email is being sent", page_url="sensor-settings")
        elif button_pressed == "settings":
            thread_function(send_test_email, args=email_address)
            return get_message_page("Test email is being sent", page_url="sensor-settings")
    return get_message_page("Please Specify a valid email address to send to", page_url="sensor-settings")


@html_atpro_settings_routes.route("/atpro/settings-mqtt-p", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_publisher():
    mqtt_publisher_config = app_config_access.mqtt_publisher_config

    if request.method == "POST":
        app_config_access.mqtt_publisher_config.update_with_html_request(request)
        app_config_access.mqtt_publisher_config.save_config_to_file()
        app_cached_variables.restart_mqtt_publisher_thread = True
        return get_message_page("MQTT Publisher Settings Saved", page_url="sensor-settings")

    enable_mqtt_publisher = mqtt_publisher_config.enable_mqtt_publisher
    enable_broker_auth = mqtt_publisher_config.enable_broker_auth
    mqtt_publisher_qos = mqtt_publisher_config.mqtt_publisher_qos
    qos_level_0 = ""
    qos_level_1 = ""
    qos_level_2 = ""
    if mqtt_publisher_qos == 0:
        qos_level_0 = get_html_selected_state(True)
    elif mqtt_publisher_qos == 1:
        qos_level_1 = get_html_selected_state(True)
    elif mqtt_publisher_qos == 2:
        qos_level_2 = get_html_selected_state(True)
    sensor_host_name = mqtt_publisher_config.sensor_host_name
    sensor_ip = mqtt_publisher_config.sensor_ip
    sensor_uptime = mqtt_publisher_config.sensor_uptime
    sensor_date_time = mqtt_publisher_config.sensor_date_time
    system_temperature = mqtt_publisher_config.system_temperature
    env_temperature = mqtt_publisher_config.env_temperature
    pressure = mqtt_publisher_config.pressure
    altitude = mqtt_publisher_config.altitude
    humidity = mqtt_publisher_config.humidity
    distance = mqtt_publisher_config.distance
    particulate_matter = mqtt_publisher_config.particulate_matter
    color = mqtt_publisher_config.color
    ultra_violet = mqtt_publisher_config.ultra_violet
    accelerometer = mqtt_publisher_config.accelerometer
    magnetometer = mqtt_publisher_config.magnetometer
    gyroscope = mqtt_publisher_config.gyroscope
    mqtt_send_format_kootnet = mqtt_publisher_config.mqtt_send_format_kootnet
    mqtt_send_format_individual_topics = mqtt_publisher_config.mqtt_send_format_individual_topics
    mqtt_send_format_custom_string = mqtt_publisher_config.mqtt_send_format_custom_string

    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-publisher.html",
        MQTTBaseTopic=mqtt_publisher_config.mqtt_base_topic[:-1],
        MQTTPublisherChecked=get_html_checkbox_state(enable_mqtt_publisher),
        MQTTBrokerAddress=mqtt_publisher_config.broker_address,
        MQTTBrokerPort=str(mqtt_publisher_config.broker_server_port),
        MQTTPublishSecondsWait=str(mqtt_publisher_config.seconds_to_wait),
        MQTTPublisherAuthChecked=get_html_checkbox_state(enable_broker_auth),
        MQTTPublisherUsername=mqtt_publisher_config.broker_user,
        PublisherQoSLevel0=qos_level_0,
        PublisherQoSLevel1=qos_level_1,
        PublisherQoSLevel2=qos_level_2,
        MQTTHostNameChecked=get_html_checkbox_state(sensor_host_name),
        MQTTSystemIPChecked=get_html_checkbox_state(sensor_ip),
        MQTTUptimeChecked=get_html_checkbox_state(sensor_uptime),
        MQTTSystemDateTimeChecked=get_html_checkbox_state(sensor_date_time),
        MQTTCPUTempChecked=get_html_checkbox_state(system_temperature),
        MQTTEnvTempChecked=get_html_checkbox_state(env_temperature),
        MQTTPressureChecked=get_html_checkbox_state(pressure),
        MQTTAltitudeChecked=get_html_checkbox_state(altitude),
        MQTTHumidityChecked=get_html_checkbox_state(humidity),
        MQTTDistanceChecked=get_html_checkbox_state(distance),
        MQTTGASChecked=get_html_checkbox_state(mqtt_publisher_config.gas),
        MQTTPMChecked=get_html_checkbox_state(particulate_matter),
        MQTTLumenChecked=get_html_checkbox_state(mqtt_publisher_config.lumen),
        MQTTColoursChecked=get_html_checkbox_state(color),
        MQTTUltraVioletChecked=get_html_checkbox_state(ultra_violet),
        MQTTAccChecked=get_html_checkbox_state(accelerometer),
        MQTTMagChecked=get_html_checkbox_state(magnetometer),
        MQTTGyroChecked=get_html_checkbox_state(gyroscope),
        SASKSChecked=_get_checked_send_as(mqtt_send_format_kootnet),
        SASIndChecked=_get_checked_send_as(mqtt_send_format_individual_topics),
        SASCustomChecked=_get_checked_send_as(mqtt_send_format_custom_string),
        MQTTCustomDataFormat=mqtt_publisher_config.mqtt_custom_data_string,
        MQTTSystemHostNameTopic=mqtt_publisher_config.sensor_host_name_topic,
        MQTTIPTopic=mqtt_publisher_config.sensor_ip_topic,
        MQTTUptimeTopic=mqtt_publisher_config.sensor_uptime_topic,
        MQTTDateTimeTopic=mqtt_publisher_config.sensor_date_time_topic,
        MQTTCPUTempTopic=mqtt_publisher_config.system_temperature_topic,
        MQTTEnvTempTopic=mqtt_publisher_config.env_temperature_topic,
        MQTTPressureTopic=mqtt_publisher_config.pressure_topic,
        MQTTAltitudeTopic=mqtt_publisher_config.altitude_topic,
        MQTTHumidityTopic=mqtt_publisher_config.humidity_topic,
        MQTTDistanceTopic=mqtt_publisher_config.distance_topic,
        MQTTGASTopic=mqtt_publisher_config.gas_topic,
        MQTTGASRestIndexTopic=mqtt_publisher_config.gas_resistance_index_topic,
        MQTTGASOxidisingTopic=mqtt_publisher_config.gas_oxidising_topic,
        MQTTGASReducingTopic=mqtt_publisher_config.gas_reducing_topic,
        MQTTGASNH3Topic=mqtt_publisher_config.gas_nh3_topic,
        MQTTPMTopic=mqtt_publisher_config.particulate_matter_topic,
        MQTTPM1Topic=mqtt_publisher_config.particulate_matter_1_topic,
        MQTTPM2_5Topic=mqtt_publisher_config.particulate_matter_2_5_topic,
        MQTTPM4Topic=mqtt_publisher_config.particulate_matter_4_topic,
        MQTTPM10Topic=mqtt_publisher_config.particulate_matter_10_topic,
        MQTTLumenTopic=mqtt_publisher_config.lumen_topic,
        MQTTColoursTopic=mqtt_publisher_config.color_topic,
        MQTTColourRedTopic=mqtt_publisher_config.color_red_topic,
        MQTTColourOrangeTopic=mqtt_publisher_config.color_orange_topic,
        MQTTColourYellowTopic=mqtt_publisher_config.color_yellow_topic,
        MQTTColourGreenTopic=mqtt_publisher_config.color_green_topic,
        MQTTColourBlueTopic=mqtt_publisher_config.color_blue_topic,
        MQTTColourVioletTopic=mqtt_publisher_config.color_violet_topic,
        MQTTUltraVioletTopic=mqtt_publisher_config.ultra_violet_topic,
        MQTTUVIndexTopic=mqtt_publisher_config.ultra_violet_index_topic,
        MQTTUVATopic=mqtt_publisher_config.ultra_violet_a_topic,
        MQTTUVBTopic=mqtt_publisher_config.ultra_violet_b_topic,
        MQTTAccTopic=mqtt_publisher_config.accelerometer_topic,
        MQTTAccXTopic=mqtt_publisher_config.accelerometer_x_topic,
        MQTTAccYTopic=mqtt_publisher_config.accelerometer_y_topic,
        MQTTAccZTopic=mqtt_publisher_config.accelerometer_z_topic,
        MQTTMagTopic=mqtt_publisher_config.magnetometer_topic,
        MQTTMagXTopic=mqtt_publisher_config.magnetometer_x_topic,
        MQTTMagYTopic=mqtt_publisher_config.magnetometer_y_topic,
        MQTTMagZTopic=mqtt_publisher_config.magnetometer_z_topic,
        MQTTGyroTopic=mqtt_publisher_config.gyroscope_topic,
        MQTTGyroXTopic=mqtt_publisher_config.gyroscope_x_topic,
        MQTTGyroYTopic=mqtt_publisher_config.gyroscope_y_topic,
        MQTTGyroZTopic=mqtt_publisher_config.gyroscope_z_topic
    )


def _get_checked_send_as(radio_text):
    if radio_text == app_config_access.mqtt_publisher_config.selected_mqtt_send_format:
        return "checked"
    return ""


@html_atpro_settings_routes.route("/atpro/settings-mqtt-s", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_subscriber():
    if request.method == "POST":
        app_config_access.mqtt_subscriber_config.update_with_html_request(request)
        app_config_access.mqtt_subscriber_config.save_config_to_file()
        app_cached_variables.html_service_restart = True
        return get_message_page("MQTT Subscriber Settings Saved", page_url="sensor-settings")

    mqtt_qos = app_config_access.mqtt_subscriber_config.mqtt_subscriber_qos
    qos_level_0 = ""
    qos_level_1 = ""
    qos_level_2 = ""
    if mqtt_qos == 0:
        qos_level_0 = get_html_selected_state(True)
    elif mqtt_qos == 1:
        qos_level_1 = get_html_selected_state(True)
    elif mqtt_qos == 2:
        qos_level_2 = get_html_selected_state(True)

    enable_mqtt_subscriber = app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber
    enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording
    enable_broker_auth = app_config_access.mqtt_subscriber_config.enable_broker_auth
    csv_mqtt_topics = ""
    for topic in app_config_access.mqtt_subscriber_config.subscribed_topics_list:
        csv_mqtt_topics += topic + ","
    csv_mqtt_topics = csv_mqtt_topics[:-1]
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-subscriber.html",
        PageURL="/MQTTConfigurationsHTML",
        MQTTSubscriberChecked=get_html_checkbox_state(enable_mqtt_subscriber),
        MQTTSQLRecordingChecked=get_html_checkbox_state(enable_mqtt_sql_recording),
        MQTTSubDatabaseSize=sensor_access.get_file_size(file_locations.mqtt_subscriber_database),
        MQTTBrokerAddress=app_config_access.mqtt_subscriber_config.broker_address,
        MQTTBrokerPort=str(app_config_access.mqtt_subscriber_config.broker_server_port),
        MQTTQoSLevel0=qos_level_0,
        MQTTQoSLevel1=qos_level_1,
        MQTTQoSLevel2=qos_level_2,
        MQTTSubscriberAuthChecked=get_html_checkbox_state(enable_broker_auth),
        MQTTSubscriberUsername=app_config_access.mqtt_subscriber_config.broker_user,
        SubscriberTopics=csv_mqtt_topics
    )


@html_atpro_settings_routes.route("/atpro/settings-mqtt-b", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_broker():
    if request.method == "POST":
        app_config_access.mqtt_broker_config.update_with_html_request(request)
        app_config_access.mqtt_broker_config.save_config_to_file()
        if app_config_access.mqtt_broker_config.enable_mqtt_broker:
            if check_mqtt_broker_server_running():
                return_text = "MQTT Broker Service Re-Started"
                restart_mqtt_broker_server()
            else:
                return_text = "MQTT Broker Service Started"
                start_mqtt_broker_server()
        else:
            return_text = "MQTT Broker Service Stopped"
            stop_mqtt_broker_server()
        return get_message_page("MQTT Broker Settings Saved", return_text, page_url="sensor-settings")
    mosquitto_configuration = ""
    if os.path.isfile(file_locations.mosquitto_configuration):
        mosquitto_configuration = get_file_content(file_locations.mosquitto_configuration)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-broker.html",
        PageURL="/MQTTConfigurationsHTML",
        BrokerServerChecked=get_html_checkbox_state(check_mqtt_broker_server_running()),
        BrokerMosquittoConfig=mosquitto_configuration
    )


@html_atpro_settings_routes.route("/atpro/settings-osm", methods=["GET", "POST"])
def html_atpro_sensor_settings_osm():
    if request.method == "POST":
        app_config_access.open_sense_map_config.update_with_html_request(request)
        app_config_access.open_sense_map_config.save_config_to_file()
        return_msg = "Stopping Open Sense Map"
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            return_msg = "Starting Open Sense Map"
            if app_cached_variables.open_sense_map_thread.current_state != "Disabled":
                if app_cached_variables.open_sense_map_thread.monitored_thread.is_alive():
                    return_msg = "Re-Starting Open Sense Map"
                    app_cached_variables.restart_open_sense_map_thread = True
                else:
                    start_open_sense_map_server()
            else:
                start_open_sense_map_server()
        else:
            if app_cached_variables.open_sense_map_thread is not None:
                app_cached_variables.open_sense_map_thread.shutdown_thread = True
                app_cached_variables.restart_open_sense_map_thread = True
        return get_message_page("Open Sense Map Settings Saved", return_msg, page_url="sensor-settings")
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-osm.html",
        CheckedOSMEnabled=get_html_checkbox_state(app_config_access.open_sense_map_config.open_sense_map_enabled),
        OSMStationID=app_config_access.open_sense_map_config.sense_box_id,
        OSMIntervalSeconds=app_config_access.open_sense_map_config.interval_seconds,
        OSMSEnvTempID=app_config_access.open_sense_map_config.temperature_id,
        OSMPressureID=app_config_access.open_sense_map_config.pressure_id,
        OSMAltitudeID=app_config_access.open_sense_map_config.altitude_id,
        OSMHumidityID=app_config_access.open_sense_map_config.humidity_id,
        OSMGasIndexID=app_config_access.open_sense_map_config.gas_voc_id,
        OSMGasNH3ID=app_config_access.open_sense_map_config.gas_nh3_id,
        OSMOxidisingID=app_config_access.open_sense_map_config.gas_oxidised_id,
        OSMGasReducingID=app_config_access.open_sense_map_config.gas_reduced_id,
        OSMPM1ID=app_config_access.open_sense_map_config.pm1_id,
        OSMPM25ID=app_config_access.open_sense_map_config.pm2_5_id,
        OSMPM4ID=app_config_access.open_sense_map_config.pm4_id,
        OSMPM10ID=app_config_access.open_sense_map_config.pm10_id,
        OSMLumenID=app_config_access.open_sense_map_config.lumen_id,
        OSMRedID=app_config_access.open_sense_map_config.red_id,
        OSMOrangeID=app_config_access.open_sense_map_config.orange_id,
        OSMYellowID=app_config_access.open_sense_map_config.yellow_id,
        OSMGreenID=app_config_access.open_sense_map_config.green_id,
        OSMBlueID=app_config_access.open_sense_map_config.blue_id,
        OSMVioletID=app_config_access.open_sense_map_config.violet_id,
        OSMUVIndexID=app_config_access.open_sense_map_config.ultra_violet_index_id,
        OSMUVAID=app_config_access.open_sense_map_config.ultra_violet_a_id,
        OSMUVBID=app_config_access.open_sense_map_config.ultra_violet_b_id
    )


@html_atpro_settings_routes.route("/atpro/settings-osm-registration", methods=["POST"])
@auth.login_required
def html_atpro_osm_registration():
    status = add_sensor_to_account(request)
    message1 = "OSM Sensor Registration Failed"
    if status == 201:
        message1 = "Sensor Registered OK"
        message2 = "Sensor Registered to Open Sense Map."
    elif status == 415:
        message2 = "Invalid or Missing content type"
    elif status == 422:
        message2 = "Invalid Location Setting"
    elif status == "FailedLogin":
        message2 = "Login Failed - Bad UserName or Password"
    else:
        message2 = "Unknown Error: " + status
    return get_message_page(message1, message2, page_url="sensor-settings")


@html_atpro_settings_routes.route("/atpro/settings-wu", methods=["GET", "POST"])
def html_atpro_sensor_settings_wu():
    weather_underground_config = app_config_access.weather_underground_config
    if request.method == "POST":
        app_config_access.weather_underground_config.update_with_html_request(request)
        app_config_access.weather_underground_config.save_config_to_file()
        return_msg = "Stopping Weather Underground"
        if app_config_access.weather_underground_config.weather_underground_enabled:
            return_msg = "Starting Weather Underground"
            if app_cached_variables.weather_underground_thread.current_state != "Disabled":
                if app_cached_variables.weather_underground_thread.monitored_thread.is_alive():
                    return_msg = "Re-Starting Weather Underground"
                    app_cached_variables.restart_weather_underground_thread = True
                else:
                    start_weather_underground_server()
            else:
                start_weather_underground_server()
        else:
            if app_cached_variables.weather_underground_thread is not None:
                app_cached_variables.weather_underground_thread.shutdown_thread = True
                app_cached_variables.restart_weather_underground_thread = True
        return get_message_page("Weather Underground Settings Saved", return_msg, page_url="sensor-settings")
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-wu.html",
        CheckedWUEnabled=get_html_checkbox_state(weather_underground_config.weather_underground_enabled),
        CheckedWURapidFire=get_html_checkbox_state(weather_underground_config.wu_rapid_fire_enabled),
        WUIntervalSeconds=weather_underground_config.interval_seconds,
        CheckedWUOutdoor=get_html_checkbox_state(weather_underground_config.outdoor_sensor),
        WUStationID=weather_underground_config.station_id,
    )


@html_atpro_settings_routes.route("/atpro/settings-luftdaten", methods=["GET", "POST"])
def html_atpro_sensor_settings_luftdaten():
    if request.method == "POST":
        app_config_access.luftdaten_config.update_with_html_request(request)
        app_config_access.luftdaten_config.save_config_to_file()
        return_msg = "Stopping Luftdaten"
        if app_config_access.luftdaten_config.luftdaten_enabled:
            return_msg = "Starting Luftdaten"
            if app_cached_variables.luftdaten_thread.current_state != "Disabled":
                if app_cached_variables.luftdaten_thread.monitored_thread.is_alive():
                    return_msg = "Re-Starting Luftdaten"
                    app_cached_variables.restart_luftdaten_thread = True
                else:
                    start_luftdaten_server()
            else:
                start_luftdaten_server()
        else:
            if app_cached_variables.luftdaten_thread is not None:
                app_cached_variables.luftdaten_thread.shutdown_thread = True
                app_cached_variables.restart_luftdaten_thread = True
        return get_message_page("Luftdaten Settings Saved", return_msg, page_url="sensor-settings")
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-luftdaten.html",
        CheckedLuftdatenEnabled=get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled),
        LuftdatenIntervalSeconds=app_config_access.luftdaten_config.interval_seconds,
        LuftdatenStationID=app_config_access.luftdaten_config.station_id
    )

# @html_atpro_settings_routes.route("/atpro/settings-Change", methods=["GET", "POST"])
# def html_atpro_sensor_settings_():
#     return "timmy"
