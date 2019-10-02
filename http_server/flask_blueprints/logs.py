from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from http_server.server_http_auth import auth
from http_server import server_http_generic_functions

html_logs_routes = Blueprint("html_logs_routes", __name__)


@html_logs_routes.route("/GetLogsHTML")
def html_get_log_view():
    logger.network_logger.debug("** HTML Logs accessed from " + str(request.remote_addr))
    primary_log_lines = logger.get_number_of_log_entries(file_locations.primary_log)
    network_log_lines = logger.get_number_of_log_entries(file_locations.network_log)
    sensors_log_lines = logger.get_number_of_log_entries(file_locations.sensors_log)
    return render_template("log_view.html",
                           LogURL="/GetLogsHTML",
                           PrimaryLog=logger.get_sensor_log(file_locations.primary_log),
                           PrimaryLogLinesText=_get_log_view_message(primary_log_lines),
                           NetworkLog=logger.get_sensor_log(file_locations.network_log),
                           NetworkLogLinesText=_get_log_view_message(network_log_lines),
                           SensorsLog=logger.get_sensor_log(file_locations.sensors_log),
                           SensorsLogLinesText=_get_log_view_message(sensors_log_lines))


def _get_log_view_message(log_lines_length):
    if log_lines_length:
        if logger.max_log_lines_return > log_lines_length:
            text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
    else:
        text_log_entries_return = "0/0"
    return text_log_entries_return


@html_logs_routes.route("/GetPrimaryLog")
def get_raw_primary_log():
    logger.network_logger.debug("* Raw Primary Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.primary_log)


@html_logs_routes.route("/GetNetworkLog")
def get_raw_network_log():
    logger.network_logger.debug("* Raw Network Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.network_log)


@html_logs_routes.route("/GetSensorsLog")
def get_raw_sensors_log():
    logger.network_logger.debug("* Raw Sensors Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.sensors_log)


@html_logs_routes.route("/DeletePrimaryLog")
@auth.login_required
def delete_primary_log():
    logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
    logger.clear_primary_log()
    return server_http_generic_functions.message_and_return("Primary Log Deleted", url="/GetLogsHTML")


@html_logs_routes.route("/DeleteNetworkLog")
@auth.login_required
def delete_network_log():
    logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
    logger.clear_network_log()
    return server_http_generic_functions.message_and_return("Network Log Deleted", url="/GetLogsHTML")


@html_logs_routes.route("/DeleteSensorsLog")
@auth.login_required
def delete_sensors_log():
    logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
    logger.clear_sensor_log()
    return server_http_generic_functions.message_and_return("Sensors Log Deleted", url="/GetLogsHTML")
