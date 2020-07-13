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
from configuration_modules import app_config_access
from operations_modules import app_cached_variables
from sensor_recording_modules.variance_checks import auto_set_triggers_wait_time
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return

html_config_trigger_high_low_routes = Blueprint("html_config_trigger_high_low_routes", __name__)


def get_config_trigger_high_low_tab():
    try:
        high_low_settings = app_config_access.trigger_high_low
        recording_enabled = get_html_checkbox_state(high_low_settings.enable_high_low_trigger_recording)
        return render_template("edit_configurations/config_trigger_high_low.html",
                               PageURL="/ConfigurationsHTML",
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
                               SecondsGyroscope=high_low_settings.gyroscope_wait_seconds)
    except Exception as error:
        logger.network_logger.error("Error building Trigger High/Low configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="trigger-high-low-config-tab")


@html_config_trigger_high_low_routes.route("/EditTriggerHighLow", methods=["POST"])
@auth.login_required
def html_set_trigger_high_low():
    logger.network_logger.debug("** HTML Apply - Trigger High/Low - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.trigger_high_low.update_with_html_request(request)
            app_config_access.trigger_high_low.save_config_to_file()
            page_msg = "Trigger High/Low Set, Please Restart Program"
            app_cached_variables.html_service_restart = True
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.warning("HTML Apply - Trigger High/Low - Error: " + str(error))
    return message_and_return("Bad Trigger High/Low POST Request", url="/ConfigurationsHTML")


@html_config_trigger_high_low_routes.route("/ResetTriggerHighLow")
@auth.login_required
def html_reset_trigger_high_low():
    logger.network_logger.info("** Trigger High/Low Reset - Source " + str(request.remote_addr))
    auto_set_triggers_wait_time(set_high_low=True)
    return message_and_return("Trigger High/Low Reset", url="/ConfigurationsHTML")
