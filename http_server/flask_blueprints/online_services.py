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
from operations_modules import logger, app_config_access, app_cached_variables
from operations_modules.app_generic_functions import CreateMonitoredThread, thread_function
from online_services_modules.weather_underground import start_weather_underground
from online_services_modules.luftdaten import start_luftdaten
from online_services_modules.open_sense_map import start_open_sense_map
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return
from sensor_modules import sensor_access

html_online_services_routes = Blueprint("html_online_services_routes", __name__)


@html_online_services_routes.route("/OnlineServices")
def html_online_services():
    logger.network_logger.debug("** Online Services accessed from " + str(request.remote_addr))
    wu_checked = get_html_checkbox_state(app_config_access.weather_underground_config.weather_underground_enabled)
    wu_rapid_fire_checked = get_html_checkbox_state(app_config_access.weather_underground_config.wu_rapid_fire_enabled)
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

    luftdaten_checked = get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled)
    luftdaten_interval_seconds_disabled = "disabled"
    if app_config_access.luftdaten_config.luftdaten_enabled:
        luftdaten_interval_seconds_disabled = ""

    luftdaten_interval_seconds = app_config_access.luftdaten_config.interval_seconds
    luftdaten_station_id = app_config_access.luftdaten_config.station_id

    osm_disabled = "disabled"
    osm_enable_checked = ""
    if app_config_access.open_sense_map_config.open_sense_map_enabled:
        osm_enable_checked = "checked"
        osm_disabled = ""

    return render_template("sensor_online_services.html",
                           CheckedWUEnabled=wu_checked,
                           CheckedWURapidFire=wu_rapid_fire_checked,
                           DisabledWURapidFire=wu_rapid_fire_disabled,
                           WUIntervalSeconds=wu_interval_seconds,
                           DisabledWUInterval=wu_interval_seconds_disabled,
                           CheckedWUOutdoor=wu_outdoor,
                           DisabledWUOutdoor=wu_outdoor_disabled,
                           DisabledStationID=wu_station_id_disabled,
                           WUStationID=wu_station_id,
                           DisabledStationKey=wu_station_key_disabled,
                           CheckedLuftdatenEnabled=luftdaten_checked,
                           LuftdatenIntervalSeconds=luftdaten_interval_seconds,
                           DisabledLuftdatenInterval=luftdaten_interval_seconds_disabled,
                           LuftdatenStationID=luftdaten_station_id,
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


@html_online_services_routes.route("/EditOnlineServicesWeatherUnderground", methods=["POST"])
@auth.login_required
def html_edit_online_services_wu():
    logger.network_logger.debug("** Edit Online Services Weather Underground accessed from " + str(request.remote_addr))
    main_message = "Weather Underground Updated - "
    message2 = ""
    if request.method == "POST":
        app_config_access.weather_underground_config.update_with_html_request(request)
        app_config_access.weather_underground_config.save_config_to_file()
        if app_cached_variables.weather_underground_thread is not None:
            main_message += "Restarting Sensor Software"
            message2 = "New Weather Underground settings will take effect after the sensor software restarts"
            thread_function(sensor_access.restart_services)
        else:
            text_name = "Weather Underground"
            function = start_weather_underground
            app_cached_variables.weather_underground_thread = CreateMonitoredThread(function, thread_name=text_name)
            if request.form.get("enable_weather_underground") is not None:
                main_message += "Starting Weather Underground"
    else:
        logger.primary_logger.error("HTML Edit Weather Underground set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")
    return message_and_return(main_message, text_message2=message2, url="/OnlineServices")


@html_online_services_routes.route("/EditOnlineServicesLuftdaten", methods=["POST"])
@auth.login_required
def html_edit_online_services_luftdaten():
    logger.network_logger.debug("** Edit Online Services Luftdaten accessed from " + str(request.remote_addr))
    main_message = "Luftdaten Updated - "
    message2 = ""
    if request.method == "POST":
        app_config_access.luftdaten_config.update_with_html_request(request)
        app_config_access.luftdaten_config.save_config_to_file()
        if app_cached_variables.luftdaten_thread is not None:
            main_message += "Restarting Sensor Software"
            message2 = "New Luftdaten settings will take effect after the sensor software restarts"
            thread_function(sensor_access.restart_services)
        else:
            text_name = "Luftdaten"
            function = start_luftdaten
            app_cached_variables.luftdaten_thread = CreateMonitoredThread(function, thread_name=text_name)
            if request.form.get("enable_luftdaten") is not None:
                main_message += "Starting Luftdaten"
    else:
        logger.primary_logger.error("HTML Edit Luftdaten set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")
    return message_and_return(main_message, text_message2=message2, url="/OnlineServices")


@html_online_services_routes.route("/EditOnlineServicesOSM", methods=["POST"])
@auth.login_required
def html_edit_online_services_open_sense_map():
    logger.network_logger.debug("** Edit Online Services Open Sense Map accessed from " + str(request.remote_addr))
    main_message = "Open Sense Map Updated - "
    message2 = ""
    if request.method == "POST":
        app_config_access.open_sense_map_config.update_with_html_request(request)
        app_config_access.open_sense_map_config.save_config_to_file()
        if app_cached_variables.open_sense_map_thread is not None:
            main_message += "Restarting Sensor Software"
            message2 = "New Open Sense Map settings will take effect after the sensor software restarts"
            thread_function(sensor_access.restart_services)
        else:
            text_name = "Open Sense Map"
            function = start_open_sense_map
            app_cached_variables.open_sense_map_thread = CreateMonitoredThread(function, thread_name=text_name)
            if request.form.get("enable_open_sense_map") is not None:
                main_message += "Starting Open Sense Map"
    else:
        logger.primary_logger.error("HTML Edit Open Sense Map set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")
    return message_and_return(main_message, text_message2=message2, url="/OnlineServices")


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
        return message_and_return(message1, text_message2=message2, url="/OnlineServices")
    else:
        logger.primary_logger.error("HTML Register Sensor with Open Sense Map Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")
