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
from flask import Blueprint, request
from operations_modules import logger, app_config_access, app_cached_variables
from online_services_modules.weather_underground import start_weather_underground_server
from online_services_modules.luftdaten import start_luftdaten_server
from online_services_modules.open_sense_map import start_open_sense_map_server
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return

html_online_services_routes = Blueprint("html_online_services_routes", __name__)
running_with_root = app_cached_variables.running_with_root


@html_online_services_routes.route("/EditOnlineServicesWeatherUnderground", methods=["POST"])
@auth.login_required
def html_edit_online_services_wu():
    logger.network_logger.debug("** Edit Online Services Weather Underground accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.weather_underground_config.update_with_html_request(request)
        app_config_access.weather_underground_config.save_config_to_file()
        return_text = "Weather Underground Configuration Saved"
        if app_config_access.weather_underground_config.weather_underground_enabled:
            return_text = _get_restart_service_text("Weather Underground")
            if app_cached_variables.weather_underground_thread is not None:
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


@html_online_services_routes.route("/EditOnlineServicesLuftdaten", methods=["POST"])
@auth.login_required
def html_edit_online_services_luftdaten():
    logger.network_logger.debug("** Edit Online Services Luftdaten accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.luftdaten_config.update_with_html_request(request)
        app_config_access.luftdaten_config.save_config_to_file()
        return_text = "Luftdaten Configuration Saved"
        if app_config_access.luftdaten_config.luftdaten_enabled:
            return_text = _get_restart_service_text("Luftdaten")
            if app_cached_variables.luftdaten_thread is not None:
                if app_cached_variables.luftdaten_thread.monitored_thread.is_alive():
                    app_cached_variables.restart_luftdaten_thread = True
                else:
                    start_luftdaten_server()
            else:
                start_luftdaten_server()
        else:
            if app_cached_variables.luftdaten_thread is not None:
                app_cached_variables.luftdaten_thread.shutdown_thread = True
                app_cached_variables.restart_luftdaten_thread = True
        return message_and_return(return_text, url="/ConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Edit Luftdaten set Error")
        return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


@html_online_services_routes.route("/EditOnlineServicesOSM", methods=["POST"])
@auth.login_required
def html_edit_online_services_open_sense_map():
    logger.network_logger.debug("** Edit Online Services Open Sense Map accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.open_sense_map_config.update_with_html_request(request)
        app_config_access.open_sense_map_config.save_config_to_file()
        return_text = "Open Sense Map Configuration Saved"
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            return_text = _get_restart_service_text("Open Sense Map")
            if app_cached_variables.open_sense_map_thread is not None:
                if app_cached_variables.open_sense_map_thread.monitored_thread.is_alive():
                    app_cached_variables.restart_open_sense_map_thread = True
                else:
                    start_open_sense_map_server()
            else:
                start_open_sense_map_server()
        else:
            if app_cached_variables.open_sense_map_thread is not None:
                app_cached_variables.open_sense_map_thread.shutdown_thread = True
                app_cached_variables.restart_open_sense_map_thread = True
        return message_and_return(return_text, url="/ConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Edit Open Sense Map set Error")
        return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


@html_online_services_routes.route("/OnlineServicesRegisterSensorOSM", methods=["POST"])
@auth.login_required
def html_online_services_register_sensor_osm():
    logger.network_logger.debug("** Register Sensor with Open Sense Map accessed from " + str(request.remote_addr))
    if request.method == "POST":
        status = app_config_access.open_sense_map_config.add_sensor_to_account(request)
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
        return message_and_return(message1, text_message2=message2, url="/ConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Register Sensor with Open Sense Map Error")
        return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def _get_restart_service_text(service_name):
    return "Restarting " + str(service_name) + " Service, This may take up to 10 Seconds"
