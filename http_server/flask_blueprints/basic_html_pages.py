from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import app_cached_variables


html_basic_routes = Blueprint("html_basic_routes", __name__)


@html_basic_routes.route("/")
@html_basic_routes.route("/index")
@html_basic_routes.route("/index.html")
def index():
    return render_template("index.html", HostName=app_cached_variables.hostname)


@html_basic_routes.route("/Quick")
@html_basic_routes.route("/SystemCommands")
def html_system_management():
    logger.network_logger.debug("** System Commands accessed from " + str(request.remote_addr))
    return render_template("system_commands.html")


@html_basic_routes.route("/SensorHelp")
def view_help_file():
    logger.network_logger.debug("* Sensor Help Viewed from " + str(request.remote_addr))
    return render_template("sensor_helpfile.html")