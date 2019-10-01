from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_config_access
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import network_wifi
from operations_modules.config_trigger_variances import write_triggers_to_file
from http_server.server_http_auth import auth
from sensor_modules import sensor_access

html_get_config_routes = Blueprint("html_get_config_routes", __name__)


@html_get_config_routes.route("/GetInstalledSensors")
def get_installed_sensors():
    logger.network_logger.debug("* Installed Sensors Sent to " + str(request.remote_addr))
    return app_config_access.installed_sensors.get_installed_sensors_config_as_str()


@html_get_config_routes.route("/GetConfiguration")
def get_primary_configuration():
    logger.network_logger.debug("* Primary Sensor Configuration Sent to " + str(request.remote_addr))
    return app_config_access.config_primary.convert_config_to_str(app_config_access.current_config)


@html_get_config_routes.route("/GetWifiConfiguration")
@auth.login_required
def get_wifi_config():
    logger.network_logger.debug("* Wifi Sent to " + str(request.remote_addr))
    return send_file(file_locations.wifi_config_file)


@html_get_config_routes.route("/SetWifiConfiguration", methods=["PUT"])
@auth.login_required
def set_wifi_config():
    logger.network_logger.debug("* set Wifi Accessed by " + str(request.remote_addr))
    try:
        new_wifi_config = request.form['command_data']
        network_wifi.write_wifi_config_to_file(new_wifi_config)
        logger.network_logger.info("** Wifi WPA Supplicant Changed by " + str(request.remote_addr))
    except Exception as error:
        logger.network_logger.error("* Failed to change Wifi WPA Supplicant sent from " +
                                    str(request.remote_addr) + " - " +
                                    str(error))
    return "OK"


@html_get_config_routes.route("/GetVarianceConfiguration")
def get_variance_config():
    logger.network_logger.debug("* Variance Configuration Sent to " + str(request.remote_addr))
    return send_file(file_locations.trigger_variances_config)


@html_get_config_routes.route("/SetVarianceConfiguration", methods=["PUT"])
@auth.login_required
def cc_set_variance_config():
    logger.network_logger.debug("* CC set Wifi Accessed by " + str(request.remote_addr))
    try:
        new_variance_config = request.form['command_data']
        write_triggers_to_file(new_variance_config)
        logger.network_logger.info("** Variance Configuration Changed by " + str(request.remote_addr))
    except Exception as error:
        logger.network_logger.info("* Failed to change Variance Configuration sent from " +
                                   str(request.remote_addr) + " - " +
                                   str(error))
    sensor_access.restart_services()
    return "OK"


@html_get_config_routes.route("/SetConfiguration", methods=["PUT"])
@auth.login_required
def cc_set_configuration():
    logger.network_logger.info("** CC Sensor Configuration set by " + str(request.remote_addr))
    raw_config = request.form['command_data'].splitlines()
    new_config = config_primary.convert_config_lines_to_obj(raw_config)
    config_primary.write_config_to_file(new_config)
    sensor_access.restart_services()


@html_get_config_routes.route("/SetInstalledSensors", methods=["PUT"])
@auth.login_required
def cc_set_installed_sensors():
    logger.network_logger.info("** CC Installed Sensors set by " + str(request.remote_addr))
    raw_installed_sensors = request.form['command_data'].splitlines()
    new_installed_sensors = config_installed_sensors.convert_lines_to_obj(raw_installed_sensors)
    config_installed_sensors.write_to_file(new_installed_sensors)
    sensor_access.restart_services()
