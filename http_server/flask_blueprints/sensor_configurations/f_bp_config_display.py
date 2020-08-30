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
from operations_modules import logger
from operations_modules import app_cached_variables
from flask import Blueprint, render_template, request
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, get_restart_service_text

html_config_display_routes = Blueprint("html_config_display_routes", __name__)


@html_config_display_routes.route("/EditDisplayConfiguration", methods=["POST"])
@auth.login_required
def html_set_display_config():
    logger.network_logger.debug("** HTML Apply - Display Configuration - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.display_config.update_with_html_request(request)
            app_config_access.display_config.save_config_to_file()
            app_cached_variables.restart_mini_display_thread = True
            return message_and_return(get_restart_service_text("Display"), url="/DisplayConfigurationsHTML")
        except Exception as error:
            logger.primary_logger.error("HTML Apply - Display Configuration - Error: " + str(error))
            return message_and_return("Bad Display Configuration POST Request", url="/DisplayConfigurationsHTML")


def get_config_display_tab():
    try:
        display = get_html_checkbox_state(app_config_access.display_config.enable_display)
        display_numerical_checked = ""
        display_graph_checked = ""
        display_type_numerical = app_config_access.display_config.display_type_numerical
        if app_config_access.display_config.display_type == display_type_numerical:
            display_numerical_checked = "checked"
        else:
            display_graph_checked = "checked"

        sensor_uptime = app_config_access.display_config.sensor_uptime
        system_temperature = app_config_access.display_config.system_temperature
        env_temperature = app_config_access.display_config.env_temperature
        pressure = app_config_access.display_config.pressure
        altitude = app_config_access.display_config.altitude
        humidity = app_config_access.display_config.humidity
        distance = app_config_access.display_config.distance
        gas = app_config_access.display_config.gas
        particulate_matter = app_config_access.display_config.particulate_matter
        lumen = app_config_access.display_config.lumen
        color = app_config_access.display_config.color
        ultra_violet = app_config_access.display_config.ultra_violet
        accelerometer = app_config_access.display_config.accelerometer
        magnetometer = app_config_access.display_config.magnetometer
        gyroscope = app_config_access.display_config.gyroscope
        return render_template("edit_configurations/config_display.html",
                               PageURL="/DisplayConfigurationsHTML",
                               CheckedEnableDisplay=display,
                               DisplayIntervalDelay=app_config_access.display_config.minutes_between_display,
                               DisplayNumericalChecked=display_numerical_checked,
                               DisplayGraphChecked=display_graph_checked,
                               DisplayUptimeChecked=get_html_checkbox_state(sensor_uptime),
                               DisplayCPUTempChecked=get_html_checkbox_state(system_temperature),
                               DisplayEnvTempChecked=get_html_checkbox_state(env_temperature),
                               DisplayPressureChecked=get_html_checkbox_state(pressure),
                               DisplayAltitudeChecked=get_html_checkbox_state(altitude),
                               DisplayHumidityChecked=get_html_checkbox_state(humidity),
                               DisplayDistanceChecked=get_html_checkbox_state(distance),
                               DisplayGASChecked=get_html_checkbox_state(gas),
                               DisplayPMChecked=get_html_checkbox_state(particulate_matter),
                               DisplayLumenChecked=get_html_checkbox_state(lumen),
                               DisplayColoursChecked=get_html_checkbox_state(color),
                               DisplayUltraVioletChecked=get_html_checkbox_state(ultra_violet),
                               DisplayAccChecked=get_html_checkbox_state(accelerometer),
                               DisplayMagChecked=get_html_checkbox_state(magnetometer),
                               DisplayGyroChecked=get_html_checkbox_state(gyroscope))
    except Exception as error:
        logger.network_logger.error("Error building Display configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="displays-tab")
