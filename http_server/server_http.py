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
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateMonitoredThread, thread_function
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import delayed_cache_update

https_import_error_msg = ""
https_import_errors = True
try:
    from http_server import server_http_auth
    from http_server.flask_blueprints.html_functional import html_functional_routes
    from http_server.flask_blueprints.basic_html_pages import html_basic_routes
    from http_server.flask_blueprints.local_sensor_downloads import html_local_download_routes
    from http_server.flask_blueprints.sensor_control_files.sensor_control import html_sensor_control_routes
    from http_server.flask_blueprints.graphing_plotly import html_plotly_graphing_routes
    from http_server.flask_blueprints.system_commands import html_system_commands_routes
    from http_server.flask_blueprints.online_services import html_online_services_routes
    from http_server.flask_blueprints.logs import html_logs_routes
    from http_server.flask_blueprints.html_sensor_configurations import html_sensor_config_routes
    from http_server.flask_blueprints.text_sensor_readings import html_sensor_readings_routes
    from http_server.flask_blueprints.get_set_raw_configurations import html_get_config_routes
    from http_server.flask_blueprints.legacy_control_center import html_legacy_cc_routes
    from http_server.flask_blueprints.sensor_info_and_readings import html_sensor_info_readings_routes
    from flask import Flask
    from flask_compress import Compress
    from gevent.pywsgi import WSGIServer

    https_import_errors = False
except ImportError as https_import_error_msg_raw:
    https_import_error_msg = str(https_import_error_msg_raw)
    server_http_auth, html_functional_routes, html_basic_routes, = None, None, None
    html_download_routes, html_sensor_control_routes, html_plotly_graphing_routes = None, None, None
    html_system_commands_routes, html_online_services_routes, html_logs_routes = None, None, None
    html_sensor_config_routes, html_sensor_readings_routes, html_get_config_routes = None, None, None
    html_legacy_cc_routes, html_sensor_info_readings_routes, html_local_download_routes = None, None, None
    Flask, Compress, WSGIServer = None, None, None

flask_http_ip = ""
flask_http_port = 10065


class CreateSensorHTTP:
    """ Creates an instance of the HTTPS Web Portal server using Flask and WSGIServer from gevent. """

    def __init__(self):
        app = Flask(__name__)
        Compress(app)
        server_http_auth.set_http_auth_from_file()

        app.register_blueprint(html_functional_routes)
        app.register_blueprint(html_basic_routes)
        app.register_blueprint(html_local_download_routes)
        app.register_blueprint(html_sensor_control_routes)
        app.register_blueprint(html_plotly_graphing_routes)
        app.register_blueprint(html_system_commands_routes)
        app.register_blueprint(html_online_services_routes)
        app.register_blueprint(html_logs_routes)
        app.register_blueprint(html_sensor_config_routes)
        app.register_blueprint(html_sensor_readings_routes)
        app.register_blueprint(html_get_config_routes)
        app.register_blueprint(html_legacy_cc_routes)
        app.register_blueprint(html_sensor_info_readings_routes)

        thread_function(delayed_cache_update)

        try:
            http_server = WSGIServer((flask_http_ip, flask_http_port), app,
                                     keyfile=file_locations.http_ssl_key,
                                     certfile=file_locations.http_ssl_crt)
            logger.primary_logger.info(" -- HTTPS Server Started on port " + str(flask_http_port))
            http_server.serve_forever()
        except Exception as error:
            logger.primary_logger.critical("--- Failed to Start HTTPS Server: " + str(error))


def https_start_and_watch():
    """ Starts an instance of the HTTP Flask server if imports are OK. """
    if https_import_errors:
        log_message = "--- Failed to Start HTTPS Server - Missing Required Dependencies: "
        logger.primary_logger.critical(log_message + str(https_import_error_msg))
        while True:
            sleep(600)
    app_cached_variables.http_server_thread = CreateMonitoredThread(CreateSensorHTTP, thread_name="HTTPS Server")
