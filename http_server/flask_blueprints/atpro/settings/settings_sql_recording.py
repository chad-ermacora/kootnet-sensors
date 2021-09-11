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
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_recording_modules.triggers_auto_set import auto_set_triggers_wait_time
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from http_server.flask_blueprints.atpro.atpro_variables import atpro_notifications

html_atpro_settings_sql_recording_routes = Blueprint("html_atpro_settings_sql_recording_routes", __name__)


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-interval", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_interval():
    if request.method == "POST":
        app_config_access.interval_recording_config.update_with_html_request(request)
        app_config_access.interval_recording_config.save_config_to_file()
        app_cached_variables.restart_interval_recording_thread = True
        return get_message_page("Interval Settings Updated", page_url="sensor-settings")

    interval_config = app_config_access.interval_recording_config
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-interval.html",
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
        CheckedGyroscope=get_html_checkbox_state(interval_config.gyroscope_enabled),
        CheckedGPS=get_html_checkbox_state(interval_config.gps_enabled)
    )


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-hl", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_high_low():
    if request.method == "POST":
        app_config_access.trigger_high_low.update_with_html_request(request)
        app_config_access.trigger_high_low.save_config_to_file()
        atpro_notifications.manage_service_restart()
        return_msg = "Please Restart Program"
        return get_message_page("Trigger High/Low Settings Updated", return_msg, page_url="sensor-settings")

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


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-hl-triggers-lowest")
@auth.login_required
def html_atpro_auto_set_lowest_trigger_high_low():
    auto_set_triggers_wait_time(app_config_access.trigger_high_low, set_lowest=True)
    msg_1 = "Trigger High/Low Seconds Settings Set to Lowest"
    msg_2 = "The High/Low Trigger recording 'Seconds' settings have been set to the Lowest recommended values."
    return get_message_page(msg_1, msg_2, page_url="sensor-settings")


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-hl-triggers-recommended")
@auth.login_required
def html_atpro_auto_set_default_trigger_high_low():
    auto_set_triggers_wait_time(app_config_access.trigger_high_low)
    msg_1 = "Trigger High/Low Seconds Settings Set to Recommended"
    msg_2 = "The High/Low Trigger recording 'Seconds' settings have been set to the recommend defaults."
    return get_message_page(msg_1, msg_2, page_url="sensor-settings")


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-variances", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_variances():
    if request.method == "POST":
        app_config_access.trigger_variances.update_with_html_request(request)
        app_config_access.trigger_variances.save_config_to_file()
        atpro_notifications.manage_service_restart()
        msg = "Please Restart Program"
        return get_message_page("Trigger Variances Settings Updated", msg, page_url="sensor-settings")
    variances = app_config_access.trigger_variances
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-variances.html",
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


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-variances-reset")
@auth.login_required
def html_atpro_reset_trigger_variances():
    auto_set_triggers_wait_time(app_config_access.trigger_variances)
    msg_1 = "Trigger Variances Reset"
    msg_2 = "The Variance Trigger recording 'seconds' settings have been set to recommended defaults."
    return get_message_page(msg_1, msg_2, page_url="sensor-settings")


@html_atpro_settings_sql_recording_routes.route("/atpro/settings-variances-low")
@auth.login_required
def html_atpro_set_lowest_trigger_variances_seconds():
    auto_set_triggers_wait_time(app_config_access.trigger_variances, set_lowest=True)
    msg_1 = "Trigger Variance Seconds Settings Set to Lowest"
    msg_2 = "The Variance Trigger recording 'seconds' settings have been set to the Lowest recommended values."
    return get_message_page(msg_1, msg_2, page_url="sensor-settings")
