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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import update_cached_variables
from configuration_modules import app_config_access

https_import_error_msg = ""
https_import_errors = True
try:
    from http_server import server_http_auth
    from http_server.flask_blueprints.atpro.atpro_main_routes import html_atpro_main_routes
    from http_server.flask_blueprints.atpro.atpro_settings_routes import html_atpro_settings_routes
    from http_server.flask_blueprints.atpro.atpro_system_routes import html_atpro_system_routes
    from http_server.flask_blueprints.atpro.atpro_sensor_checkins import html_atpro_sensor_check_ins_routes
    from http_server.flask_blueprints.atpro.atpro_remote_management import html_atpro_remote_management_routes
    from http_server.flask_blueprints.html_functional import html_functional_routes
    from http_server.flask_blueprints.basic_html_pages import html_basic_routes
    from http_server.flask_blueprints.text_sensor_readings import html_sensor_readings_routes
    from http_server.flask_blueprints.sensor_checkin_server import html_sensor_check_ins_routes
    from http_server.flask_blueprints.system_commands import html_system_commands_routes
    from http_server.flask_blueprints.get_set_raw_configurations import html_get_set_config_routes
    from http_server.flask_blueprints.local_sensor_downloads import html_local_download_routes
    from http_server.flask_blueprints.logs import html_logs_routes

    from http_server.flask_blueprints.atpro.atpro_graphing import html_atpro_graphing_routes
    from http_server.flask_blueprints.graphing_quick import html_quick_graphing_routes

    from flask import Flask
    from flask_compress import Compress
    from gevent.pywsgi import WSGIServer

    https_import_errors = False
except ImportError as https_import_error_msg_raw:
    https_import_error_msg = str(https_import_error_msg_raw)
    html_atpro_main_routes, html_atpro_settings_routes, html_database_routes = None, None, None
    html_atpro_system_routes, html_atpro_remote_management_routes, html_atpro_sensor_check_ins_routes = None, None, None
    server_http_auth, html_functional_routes, Flask, Compress, WSGIServer = None, None, None, None, None
    html_basic_routes, html_sensor_check_ins_routes, html_quick_graphing_routes = None, None, None
    html_system_commands_routes, html_get_set_config_routes, html_atpro_graphing_routes = None, None, None
    html_local_download_routes, html_logs_routes, html_sensor_readings_routes = None, None, None


class CreateSensorHTTP:
    """ Creates an instance of the HTTPS Web Portal server using Flask and WSGIServer from gevent. """

    def __init__(self):
        app = Flask(__name__)
        Compress(app)
        server_http_auth.set_http_auth_from_file()

        app.register_blueprint(html_atpro_main_routes)
        app.register_blueprint(html_atpro_settings_routes)
        app.register_blueprint(html_atpro_system_routes)
        app.register_blueprint(html_atpro_sensor_check_ins_routes)
        app.register_blueprint(html_atpro_remote_management_routes)
        app.register_blueprint(html_functional_routes)
        app.register_blueprint(html_basic_routes)
        app.register_blueprint(html_sensor_readings_routes)
        app.register_blueprint(html_sensor_check_ins_routes)
        app.register_blueprint(html_system_commands_routes)
        app.register_blueprint(html_get_set_config_routes)
        app.register_blueprint(html_local_download_routes)
        app.register_blueprint(html_logs_routes)

        app.register_blueprint(html_quick_graphing_routes)
        app.register_blueprint(html_atpro_graphing_routes)

        update_cached_variables()

        try:
            flask_http_ip = app_config_access.primary_config.flask_http_ip
            flask_port_number = app_config_access.primary_config.web_portal_port
            http_server = WSGIServer((flask_http_ip, flask_port_number), app,
                                     keyfile=file_locations.http_ssl_key,
                                     certfile=file_locations.http_ssl_crt)
            logger.primary_logger.info(" -- HTTPS Server Started on port " + str(flask_port_number))
            http_server.serve_forever()
        except Exception as error:
            logger.primary_logger.critical("--- Failed to Start HTTPS Server: " + str(error))


def start_https_server():
    if https_import_errors:
        log_message = "--- Failed to Start HTTPS Server - Missing Required Dependencies: "
        logger.primary_logger.critical(log_message + str(https_import_error_msg))
    else:
        text_name = "HTTPS Server"
        function = CreateSensorHTTP
        app_cached_variables.http_server_thread = CreateMonitoredThread(function, thread_name=text_name)
