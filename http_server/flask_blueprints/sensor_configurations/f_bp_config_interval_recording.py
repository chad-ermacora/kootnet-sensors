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
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return

html_config_interval_recording_routes = Blueprint("html_config_interval_recording_routes", __name__)


@html_config_interval_recording_routes.route("/EditIntervalRecording", methods=["POST"])
@auth.login_required
def html_set_config_interval_recording():
    logger.network_logger.debug("** HTML Apply - Interval Rec Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.interval_recording_config.update_with_html_request(request)
            app_config_access.interval_recording_config.save_config_to_file()
            page_msg = "Config Set, Restarting Interval Server"
            app_cached_variables.restart_interval_recording_thread = True
            return_page = message_and_return(page_msg, url="/MainConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/MainConfigurationsHTML")


def get_config_interval_recording_tab():
    interval_config = app_config_access.interval_recording_config
    try:
        return render_template(
            "edit_configurations/config_interval_recording.html",
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
    except Exception as error:
        logger.network_logger.error("Error building Interval recording configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="interval-recording-tab")
