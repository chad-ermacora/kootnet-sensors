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
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, \
    get_restart_service_text
from operations_modules.online_services_modules.weather_underground import start_weather_underground_server

html_config_weather_underground_routes = Blueprint("html_config_weather_underground_routes", __name__)


@html_config_weather_underground_routes.route("/EditOnlineServicesWeatherUnderground", methods=["POST"])
@auth.login_required
def html_edit_online_services_wu():
    logger.network_logger.debug("** Edit Online Services Weather Underground accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.weather_underground_config.update_with_html_request(request)
        app_config_access.weather_underground_config.save_config_to_file()
        return_text = "Weather Underground Configuration Saved"
        if app_config_access.weather_underground_config.weather_underground_enabled:
            return_text = get_restart_service_text("Weather Underground")
            if app_cached_variables.weather_underground_thread != "Disabled":
                if app_cached_variables.weather_underground_thread.monitored_thread.is_alive():
                    app_cached_variables.restart_weather_underground_thread = True
                else:
                    start_weather_underground_server()
            else:
                start_weather_underground_server()
        else:
            if app_cached_variables.weather_underground_thread is not None:
                app_cached_variables.weather_underground_thread.shutdown_thread = True
                app_cached_variables.restart_weather_underground_thread = True
        return message_and_return(return_text, url="/ConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Edit Weather Underground set Error")
        return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def get_config_weather_underground_tab():
    try:
        weather_underground_enabled = app_config_access.weather_underground_config.weather_underground_enabled
        wu_rapid_fire_enabled = app_config_access.weather_underground_config.wu_rapid_fire_enabled
        wu_checked = get_html_checkbox_state(weather_underground_enabled)
        wu_rapid_fire_checked = get_html_checkbox_state(wu_rapid_fire_enabled)
        wu_rapid_fire_disabled = "disabled"
        wu_interval_seconds_disabled = "disabled"
        wu_outdoor_disabled = "disabled"
        wu_station_id_disabled = "disabled"
        wu_station_key_disabled = "disabled"
        if app_config_access.weather_underground_config.weather_underground_enabled:
            wu_rapid_fire_disabled = ""
            wu_interval_seconds_disabled = ""
            wu_outdoor_disabled = ""
            wu_station_id_disabled = ""
            wu_station_key_disabled = ""

        wu_interval_seconds = app_config_access.weather_underground_config.interval_seconds
        wu_outdoor = get_html_checkbox_state(app_config_access.weather_underground_config.outdoor_sensor)
        wu_station_id = app_config_access.weather_underground_config.station_id
        return render_template("edit_configurations/config_weather_underground.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedWUEnabled=wu_checked,
                               CheckedWURapidFire=wu_rapid_fire_checked,
                               DisabledWURapidFire=wu_rapid_fire_disabled,
                               WUIntervalSeconds=wu_interval_seconds,
                               DisabledWUInterval=wu_interval_seconds_disabled,
                               CheckedWUOutdoor=wu_outdoor,
                               DisabledWUOutdoor=wu_outdoor_disabled,
                               DisabledStationID=wu_station_id_disabled,
                               WUStationID=wu_station_id,
                               DisabledStationKey=wu_station_key_disabled)
    except Exception as error:
        logger.network_logger.error("Error building Weather Underground configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="weather-underground-tab")
