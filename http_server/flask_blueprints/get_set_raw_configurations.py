from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import network_wifi
from operations_modules.config_trigger_variances import write_triggers_to_file
from http_server.server_http_auth import auth
from sensor_modules import sensor_access

html_get_config_routes = Blueprint("html_get_config_routes", __name__)


@html_get_config_routes.route("/GetConfiguration")
def get_primary_configuration():
    logger.network_logger.debug("* Primary Sensor Configuration Sent to " + str(request.remote_addr))
    return app_config_access.current_config.get_config_as_str()


@html_get_config_routes.route("/SetConfiguration", methods=["PUT"])
@auth.login_required
def set_configuration():
    logger.network_logger.info("** Primary Sensor Configuration Set by " + str(request.remote_addr))
    app_config_access.current_config.set_config_with_str(request.form["command_data"])
    app_config_access.current_config.save_config_to_file()
    app_generic_functions.thread_function(sensor_access.restart_services)
    return "OK"


@html_get_config_routes.route("/GetInstalledSensors")
def get_installed_sensors():
    logger.network_logger.debug("* Installed Sensors Sent to " + str(request.remote_addr))
    return app_config_access.installed_sensors.get_config_as_str()


@html_get_config_routes.route("/SetInstalledSensors", methods=["PUT"])
@auth.login_required
def set_installed_sensors():
    logger.network_logger.info("** Installed Sensors Set by " + str(request.remote_addr))
    raw_installed_sensors = request.form["command_data"]
    app_config_access.installed_sensors.set_config_with_str(raw_installed_sensors)
    app_config_access.installed_sensors.save_config_to_file()
    app_generic_functions.thread_function(sensor_access.restart_services)
    return "OK"


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
        new_wifi_config = request.form["command_data"]
        network_wifi.write_wifi_config_to_file(new_wifi_config)
    except Exception as error:
        logger.network_logger.error("* Wifi Set from " + str(request.remote_addr) + " Failed: " + str(error))
    return "OK"


@html_get_config_routes.route("/GetVarianceConfiguration")
def get_variance_config():
    logger.network_logger.debug("* Variance Configuration Sent to " + str(request.remote_addr))
    return send_file(file_locations.trigger_variances_config)


@html_get_config_routes.route("/SetVarianceConfiguration", methods=["PUT"])
@auth.login_required
def set_variance_config():
    logger.network_logger.debug("* Variance Configuration Set by " + str(request.remote_addr))
    try:
        new_variance_config = request.form["command_data"]
        write_triggers_to_file(new_variance_config)
    except Exception as error:
        logger.network_logger.info("* Variance Configuration Set from " + str(request.remote_addr) +
                                   " Failed: " + str(error))
    app_generic_functions.thread_function(sensor_access.restart_services)
    return "OK"
