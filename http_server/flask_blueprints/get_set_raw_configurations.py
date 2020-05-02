from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import network_wifi
from http_server.server_http_auth import auth
from sensor_modules import sensor_access

html_get_config_routes = Blueprint("html_get_config_routes", __name__)


@html_get_config_routes.route("/GetConfiguration")
def get_primary_configuration():
    logger.network_logger.debug("* Primary Sensor Configuration Sent to " + str(request.remote_addr))
    return app_config_access.primary_config.get_config_as_str()


@html_get_config_routes.route("/SetPrimaryConfiguration", methods=["PUT"])
@auth.login_required
def set_configuration():
    logger.network_logger.info("** Primary Sensor Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.primary_config.load_from_file = False
        app_config_access.primary_config.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.primary_config.save_config_to_file()
            app_generic_functions.thread_function(sensor_access.restart_services)
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Primary Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetInstalledSensors")
def get_installed_sensors():
    logger.network_logger.debug("* Installed Sensors Sent to " + str(request.remote_addr))
    return app_config_access.installed_sensors.get_config_as_str()


@html_get_config_routes.route("/SetInstalledSensors", methods=["PUT"])
@auth.login_required
def set_installed_sensors():
    logger.network_logger.info("** Installed Sensors Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.installed_sensors.load_from_file = False

        app_config_access.installed_sensors.set_config_with_str(request.form.get("command_data"))

        if request.form.get("test_run") is None:
            app_config_access.installed_sensors.save_config_to_file()
            app_generic_functions.thread_function(sensor_access.restart_services)
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Installed Sensors from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetDisplayConfiguration")
def get_display_config():
    logger.network_logger.debug("* Display Configuration Sent to " + str(request.remote_addr))
    return app_config_access.display_config.get_config_as_str()


@html_get_config_routes.route("/SetDisplayConfiguration", methods=["PUT"])
@auth.login_required
def set_display_config():
    logger.network_logger.info("** Display Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.display_config.load_from_file = False

        app_config_access.display_config.set_config_with_str(request.form.get("command_data"))

        if request.form.get("test_run") is None:
            app_config_access.display_config.save_config_to_file()
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Display Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetVarianceConfiguration")
def get_variance_config():
    logger.network_logger.debug("* Variance Configuration Sent to " + str(request.remote_addr))
    return app_config_access.trigger_variances.get_config_as_str()


@html_get_config_routes.route("/SetVarianceConfiguration", methods=["PUT"])
@auth.login_required
def set_variance_config():
    logger.network_logger.debug("* Variance Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.trigger_variances.load_from_file = False
        app_config_access.trigger_variances.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.trigger_variances.save_config_to_file()
            app_generic_functions.thread_function(sensor_access.restart_services)
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Trigger Variances from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetSensorControlConfiguration")
def get_sensor_control_config():
    logger.network_logger.debug("* Sensor Control Configuration Sent to " + str(request.remote_addr))
    return app_config_access.sensor_control_config.get_config_as_str()


@html_get_config_routes.route("/SetSensorControlConfiguration", methods=["PUT"])
@auth.login_required
def set_sensor_control_config():
    logger.network_logger.debug("* Sensor Control Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.sensor_control_config.load_from_file = False
        app_config_access.sensor_control_config.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.sensor_control_config.save_config_to_file()
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Sensor Control Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetWeatherUndergroundConfiguration")
@auth.login_required
def get_weather_underground_config():
    logger.network_logger.debug("* Weather Underground Configuration Sent to " + str(request.remote_addr))
    return app_config_access.weather_underground_config.get_config_as_str()


@html_get_config_routes.route("/SetWeatherUndergroundConfiguration", methods=["PUT"])
@auth.login_required
def set_weather_underground_config():
    logger.network_logger.debug("* Weather Underground Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.weather_underground_config.load_from_file = False
        app_config_access.weather_underground_config.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.weather_underground_config.save_config_to_file()
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Weather Underground Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetOnlineServicesLuftdaten")
def get_luftdaten_config():
    logger.network_logger.debug("* Luftdaten Configuration Sent to " + str(request.remote_addr))
    return app_config_access.luftdaten_config.get_config_as_str()


@html_get_config_routes.route("/SetLuftdatenConfiguration", methods=["PUT"])
@auth.login_required
def set_luftdaten_config():
    logger.network_logger.debug("* Luftdaten Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.luftdaten_config.load_from_file = False
        app_config_access.luftdaten_config.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.luftdaten_config.save_config_to_file()
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Luftdaten Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetOnlineServicesOpenSenseMap")
@auth.login_required
def get_open_sense_map_config():
    logger.network_logger.debug("* Open Sense Map Configuration Sent to " + str(request.remote_addr))
    return app_config_access.open_sense_map_config.get_config_as_str()


@html_get_config_routes.route("/SetOpenSenseMapConfiguration", methods=["PUT"])
@auth.login_required
def set_open_sense_map_config():
    logger.network_logger.debug("* OpenSenseMap Configuration Set by " + str(request.remote_addr))
    try:
        if request.form.get("test_run"):
            app_config_access.open_sense_map_config.load_from_file = False
        app_config_access.open_sense_map_config.set_config_with_str(request.form.get("command_data"))
        if request.form.get("test_run") is None:
            app_config_access.open_sense_map_config.save_config_to_file()
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Open Sense Map Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"


@html_get_config_routes.route("/GetWifiConfiguration")
@auth.login_required
def get_wifi_config():
    logger.network_logger.debug("* Wifi Sent to " + str(request.remote_addr))
    return send_file(file_locations.wifi_config_file)


@html_get_config_routes.route("/SetWifiConfiguration", methods=["PUT"])
@auth.login_required
def set_wifi_config():
    logger.network_logger.debug("* Wifi Set by " + str(request.remote_addr))
    try:
        new_wifi_config = request.form.get("command_data")
        network_wifi.write_wifi_config_to_file(new_wifi_config)
        return "OK"
    except Exception as error:
        log_msg = "Failed to set Primary Configuration from " + str(request.remote_addr)
        logger.network_logger.error(log_msg + " - " + str(error))
    return "Failed"
