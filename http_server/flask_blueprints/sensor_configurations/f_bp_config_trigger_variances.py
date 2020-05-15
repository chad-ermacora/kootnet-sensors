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
from operations_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return

html_config_trigger_variances_routes = Blueprint("html_config_trigger_variances_routes", __name__)


@html_config_trigger_variances_routes.route("/EditTriggerVariances", methods=["POST"])
@auth.login_required
def html_set_trigger_variances():
    logger.network_logger.debug("** HTML Apply - Trigger Variances - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.trigger_variances.update_with_html_request(request)
            app_config_access.trigger_variances.save_config_to_file()
            return message_and_return("Trigger Variances Set", url="/ConfigurationsHTML")
        except Exception as error:
            logger.primary_logger.warning("HTML Apply - Trigger Variances - Error: " + str(error))
    return message_and_return("Bad Trigger Variances POST Request", url="/ConfigurationsHTML")


@html_config_trigger_variances_routes.route("/ResetTriggerVariances")
@auth.login_required
def html_reset_trigger_variances():
    logger.network_logger.info("** Trigger Variances Reset - Source " + str(request.remote_addr))
    app_config_access.trigger_variances.reset_settings()
    return message_and_return("Trigger Variances Reset", url="/ConfigurationsHTML")


def get_config_trigger_variances_tab():
    try:
        variances = app_config_access.trigger_variances
        return render_template("edit_configurations/config_trigger_variances.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedSensorUptime=get_html_checkbox_state(variances.sensor_uptime_enabled),
                               DaysSensorUptime=(float(variances.sensor_uptime_wait_seconds) / 60.0 / 60.0 / 24.0),
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
                               SecondsGyroscope=variances.gyroscope_wait_seconds)
    except Exception as error:
        logger.network_logger.error("Error building Trigger Variances configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="trigger-variances-tab")
