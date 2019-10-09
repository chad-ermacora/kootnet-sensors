from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
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


@html_online_services_routes.route("/GetOnlineServicesWeatherUnderground")
@auth.login_required
def html_get_raw_online_services_config_wu():
    logger.network_logger.debug("** Get Online Services - Weather Underground accessed from " + str(request.remote_addr))
    return send_file(file_locations.weather_underground_config)


@html_online_services_routes.route("/GetOnlineServicesLuftdaten")
def html_get_raw_online_services_config_luftdaten():
    logger.network_logger.debug("** Get Online Services - Luftdaten accessed from " + str(request.remote_addr))
    return send_file(file_locations.luftdaten_config)


@html_online_services_routes.route("/GetOnlineServicesOpenSenseMap")
@auth.login_required
def html_get_raw_online_services_config_open_sense_map():
    logger.network_logger.debug("** Get Online Services - Open Sense Map accessed from " + str(request.remote_addr))
    return send_file(file_locations.osm_config)


@html_online_services_routes.route("/EditOnlineServicesWeatherUnderground", methods=["POST"])
@auth.login_required
def html_edit_online_services_wu():
    logger.network_logger.debug("** Edit Online Services Weather Underground accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.weather_underground_config.update_weather_underground_html(request, skip_write=False)
        if app_config_access.wu_thread_running:
            main_message = "Weather Underground Updated - Restarting Sensor Software"
            message2 = "New Weather Underground settings will take effect after the sensor software restarts"
            app_generic_functions.thread_function(sensor_access.restart_services)
        else:
            start_weather_underground = app_config_access.weather_underground_config.start_weather_underground
            app_generic_functions.thread_function(start_weather_underground)
            main_message = "Weather Underground Updated"
            message2 = ""
            if request.form.get("enable_weather_underground") is not None:
                main_message += " - Weather Underground Started"
        return message_and_return(main_message, text_message2=message2, url="/OnlineServices")
    else:
        logger.primary_logger.error("HTML Edit Weather Underground set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")


@html_online_services_routes.route("/EditOnlineServicesLuftdaten", methods=["POST"])
@auth.login_required
def html_edit_online_services_luftdaten():
    logger.network_logger.debug("** Edit Online Services Luftdaten accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.luftdaten_config.update_luftdaten_html(request)
        if app_config_access.luftdaten_thread_running:
            main_message = "Luftdaten Updated - Restarting Sensor Software"
            message2 = "New Luftdaten settings will take effect after the sensor software restarts"
            app_generic_functions.thread_function(sensor_access.restart_services)
        else:
            app_generic_functions.thread_function(app_config_access.luftdaten_config.start_luftdaten)
            main_message = "Luftdaten Updated"
            message2 = ""
            if request.form.get("enable_luftdaten") is not None:
                main_message += " - Luftdaten Started"
        return message_and_return(main_message, text_message2=message2, url="/OnlineServices")
    else:
        logger.primary_logger.error("HTML Edit Luftdaten set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")


@html_online_services_routes.route("/EditOnlineServicesOSM", methods=["POST"])
@auth.login_required
def html_edit_online_services_open_sense_map():
    logger.network_logger.debug("** Edit Online Services Open Sense Map accessed from " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.open_sense_map_config.update_open_sense_map_html(request)
        if app_config_access.open_sense_map_thread_running:
            main_message = "Open Sense Map Updated - Restarting Sensor Software"
            message2 = "New Open Sense Map settings will take effect after the sensor software restarts"
            app_generic_functions.thread_function(sensor_access.restart_services)
        else:
            app_generic_functions.thread_function(app_config_access.open_sense_map_config.start_open_sense_map)
            main_message = "Open Sense Map Updated"
            message2 = ""
            if request.form.get("enable_open_sense_map") is not None:
                main_message += " - Open Sense Map Started"
        return message_and_return(main_message, text_message2=message2, url="/OnlineServices")
    else:
        logger.primary_logger.error("HTML Edit Open Sense Map set Error")
        return message_and_return("Bad Configuration POST Request", url="/OnlineServices")


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
