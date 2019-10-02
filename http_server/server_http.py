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
from threading import Thread
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions

try:
    from operations_modules.app_cached_variables_update import delayed_cache_update
    from http_server import server_http_auth
    from http_server.flask_blueprints.html_functional import html_functional_routes
    from http_server.flask_blueprints.basic_html_pages import html_basic_routes
    from http_server.flask_blueprints.local_sensor_downloads import html_local_download_routes
    from http_server.flask_blueprints.sensor_control import html_sensor_control_routes
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

    import_errors = False
except ImportError as import_error:
    logger.primary_logger.critical("**** Missing Required HTTPS Dependencies: " + str(import_error))
    delayed_cache_update, server_http_auth, html_functional_routes, html_basic_routes, = None, None, None, None
    html_download_routes, html_sensor_control_routes, html_plotly_graphing_routes = None, None, None
    html_system_commands_routes, html_online_services_routes, html_logs_routes = None, None, None
    html_sensor_config_routes, html_sensor_readings_routes, html_get_config_routes = None, None, None
    html_legacy_cc_routes, html_sensor_info_readings_routes, Flask, Compress, WSGIServer = None, None, None, None, None
    import_errors = True

flask_http_ip = ""
flask_http_port = 10065


class CreateSensorHTTP:
    def __init__(self):
        if import_errors:
            logger.network_logger.critical("**** Unable to load HTTPS Server, missing Python Modules")
            while True:
                sleep(600)

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

        app_generic_functions.thread_function(delayed_cache_update)

        try:
            http_server = WSGIServer((flask_http_ip, flask_http_port), app,
                                     keyfile=file_locations.http_ssl_key,
                                     certfile=file_locations.http_ssl_crt)
            logger.primary_logger.info(" -- HTTPS Server Started on port " + str(flask_http_port))
            http_server.serve_forever()
        except Exception as error:
            logger.primary_logger.critical(" -- HTTPS Server Failed to Start: " + str(error))


def https_start_and_watch():
    # Start the HTTP Server for remote access
    sensor_http_server_thread = Thread(target=CreateSensorHTTP)
    sensor_http_server_thread.daemon = True
    sensor_http_server_thread.start()
    logger.primary_logger.debug("HTTPS Server Thread Started")

    while True:
        sleep(30)
        if not sensor_http_server_thread.is_alive():
            logger.primary_logger.error("HTTPS Server Stopped Unexpectedly - Restarting...")
            sensor_http_server_thread = Thread(target=CreateSensorHTTP)
            sensor_http_server_thread.daemon = True
            sensor_http_server_thread.start()
