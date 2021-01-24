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
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, get_restart_service_text
from online_services_modules.luftdaten import start_luftdaten_server

html_config_luftdaten_routes = Blueprint("html_config_luftdaten_routes", __name__)


@html_config_luftdaten_routes.route("/EditOnlineServicesLuftdaten", methods=["POST"])
@auth.login_required
def html_edit_online_services_luftdaten():
    logger.network_logger.debug("** Edit Online Services Luftdaten accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.luftdaten_config.update_with_html_request(request)
        app_config_access.luftdaten_config.save_config_to_file()
        return_text = "Luftdaten Configuration Saved"
        if app_config_access.luftdaten_config.luftdaten_enabled:
            return_text = get_restart_service_text("Luftdaten")
            if app_cached_variables.luftdaten_thread.current_state != "Disabled":
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
        return message_and_return(return_text, url="/3rdPartyConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Edit Luftdaten set Error")
        return message_and_return("Bad Configuration POST Request", url="/3rdPartyConfigurationsHTML")


def get_config_luftdaten_tab():
    try:
        luftdaten_checked = get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled)

        luftdaten_interval_seconds = app_config_access.luftdaten_config.interval_seconds
        luftdaten_station_id = app_config_access.luftdaten_config.station_id
        return render_template("edit_configurations/config_luftdaten.html",
                               PageURL="/3rdPartyConfigurationsHTML",
                               CheckedLuftdatenEnabled=luftdaten_checked,
                               LuftdatenIntervalSeconds=luftdaten_interval_seconds,
                               LuftdatenStationID=luftdaten_station_id)
    except Exception as error:
        logger.network_logger.error("Error building Luftdaten configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="luftdaten-tab")
