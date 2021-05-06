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
from online_services_modules.open_sense_map import start_open_sense_map_server, add_sensor_to_account
from online_services_modules.weather_underground import start_weather_underground_server
from online_services_modules.luftdaten import start_luftdaten_server
from http_server.server_http_generic_functions import get_html_checkbox_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page

html_atpro_settings_3rd_party_routes = Blueprint("html_atpro_settings_3rd_party_routes", __name__)


@html_atpro_settings_3rd_party_routes.route("/atpro/settings-osm", methods=["GET", "POST"])
@auth.login_required
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
        return get_message_page("Open Sense Map Settings Updated", return_msg, page_url="sensor-settings")
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


@html_atpro_settings_3rd_party_routes.route("/atpro/settings-osm-registration", methods=["POST"])
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


@html_atpro_settings_3rd_party_routes.route("/atpro/settings-wu", methods=["GET", "POST"])
@auth.login_required
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
        return get_message_page("Weather Underground Settings Updated", return_msg, page_url="sensor-settings")
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-wu.html",
        CheckedWUEnabled=get_html_checkbox_state(weather_underground_config.weather_underground_enabled),
        CheckedWURapidFire=get_html_checkbox_state(weather_underground_config.wu_rapid_fire_enabled),
        WUIntervalSeconds=weather_underground_config.interval_seconds,
        CheckedWUOutdoor=get_html_checkbox_state(weather_underground_config.outdoor_sensor),
        WUStationID=weather_underground_config.station_id,
    )


@html_atpro_settings_3rd_party_routes.route("/atpro/settings-luftdaten", methods=["GET", "POST"])
@auth.login_required
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
        return get_message_page("Luftdaten Settings Updated", return_msg, page_url="sensor-settings")
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-luftdaten.html",
        CheckedLuftdatenEnabled=get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled),
        LuftdatenIntervalSeconds=app_config_access.luftdaten_config.interval_seconds,
        LuftdatenStationID=app_config_access.luftdaten_config.station_id
    )
