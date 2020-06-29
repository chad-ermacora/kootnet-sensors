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
from http_server.server_http_generic_functions import message_and_return, get_restart_service_text
from operations_modules.online_services_modules.open_sense_map import start_open_sense_map_server
from operations_modules.online_services_modules.open_sense_map import add_sensor_to_account

html_config_osm_routes = Blueprint("html_config_osm_routes", __name__)


@html_config_osm_routes.route("/EditOnlineServicesOSM", methods=["POST"])
@auth.login_required
def html_edit_online_services_open_sense_map():
    logger.network_logger.debug("** Edit Online Services Open Sense Map accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.open_sense_map_config.update_with_html_request(request)
        app_config_access.open_sense_map_config.save_config_to_file()
        return_text = "Open Sense Map Configuration Saved"
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            return_text = get_restart_service_text("Open Sense Map")
            if app_cached_variables.open_sense_map_thread != "Disabled":
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


@html_config_osm_routes.route("/OnlineServicesRegisterSensorOSM", methods=["POST"])
@auth.login_required
def html_online_services_register_sensor_osm():
    logger.network_logger.debug("** Register Sensor with Open Sense Map accessed from " + str(request.remote_addr))
    if request.method == "POST":
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
        return message_and_return(message1, text_message2=message2, url="/ConfigurationsHTML")
    else:
        logger.primary_logger.error("HTML Register Sensor with Open Sense Map Error")
        return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def get_config_osm_tab():
    try:
        osm_disabled = "disabled"
        osm_enable_checked = ""
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            osm_enable_checked = "checked"
            osm_disabled = ""
        return render_template("edit_configurations/config_open_sense_map.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedOSMEnabled=osm_enable_checked,
                               OSMDisabled=osm_disabled,
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
                               OSMUVBID=app_config_access.open_sense_map_config.ultra_violet_b_id)
    except Exception as error:
        logger.network_logger.error("Error building Open Sense Map configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="open-sense-map-tab")
