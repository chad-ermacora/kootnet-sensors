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

from http_server.flask_blueprints.html_functional import html_functional_routes
from http_server.flask_blueprints.basic_html_pages import html_basic_routes

from http_server.flask_blueprints.atpro.atpro_main_routes import html_atpro_main_routes
from http_server.flask_blueprints.atpro.atpro_notes import html_atpro_notes_routes
from http_server.flask_blueprints.atpro.atpro_graphing import html_atpro_graphing_routes
from http_server.flask_blueprints.atpro.remote_management.rm_routes import html_atpro_remote_management_routes
from http_server.flask_blueprints.atpro.atpro_mqtt_subscriber import html_atpro_mqtt_subscriber_routes
from http_server.flask_blueprints.atpro.atpro_sensor_checkins import html_atpro_sensor_check_ins_routes
from http_server.flask_blueprints.atpro.atpro_logs import html_atpro_logs_routes

from http_server.flask_blueprints.atpro.settings.settings_main import html_atpro_settings_routes
from http_server.flask_blueprints.atpro.settings.settings_sql_recording import html_atpro_settings_sql_recording_routes
from http_server.flask_blueprints.atpro.settings.settings_mqtt import html_atpro_settings_mqtt_routes
from http_server.flask_blueprints.atpro.settings.settings_email import html_atpro_settings_email_routes
from http_server.flask_blueprints.atpro.settings.settings_3rd_party_services import html_atpro_settings_3rd_party_routes

from http_server.flask_blueprints.atpro.system.system_main import html_atpro_system_routes
from http_server.flask_blueprints.atpro.system.system_raw_configs import html_atpro_system_raw_configs_routes
from http_server.flask_blueprints.atpro.system.system_sql_database import html_atpro_system_sql_db_routes
from http_server.flask_blueprints.atpro.system.system_networking import html_atpro_system_networking_routes
from http_server.flask_blueprints.atpro.system.system_commands import html_atpro_system_commands_routes

from http_server.flask_blueprints.text_sensor_readings import html_sensor_readings_routes
from http_server.flask_blueprints.local_sensor_downloads import html_local_download_routes
from http_server.flask_blueprints.get_set_raw_configurations import html_get_set_config_routes
from http_server.flask_blueprints.system_commands import html_system_commands_routes
from http_server.flask_blueprints.sensor_checkin_server import html_sensor_check_ins_routes

https_import_error_msg = ""
https_import_errors = True
try:
    from flask import Flask
    from flask_compress import Compress
    from gevent import pywsgi, hub
    https_import_errors = False
except ImportError as https_import_error_msg_raw:
    https_import_error_msg = str(https_import_error_msg_raw)
    Flask, Compress, pywsgi, hub = None, None, None, None


class CreateSensorHTTP:
    """ Creates an instance of the HTTPS Web Portal server using Flask and WSGIServer from gevent. """

    def __init__(self):
        app = Flask(__name__)
        Compress(app)

        app.register_blueprint(html_functional_routes)
        app.register_blueprint(html_basic_routes)

        app.register_blueprint(html_atpro_main_routes)
        app.register_blueprint(html_atpro_notes_routes)
        app.register_blueprint(html_atpro_graphing_routes)
        app.register_blueprint(html_atpro_remote_management_routes)
        app.register_blueprint(html_atpro_mqtt_subscriber_routes)
        app.register_blueprint(html_atpro_sensor_check_ins_routes)
        app.register_blueprint(html_atpro_logs_routes)

        app.register_blueprint(html_atpro_settings_routes)
        app.register_blueprint(html_atpro_settings_sql_recording_routes)
        app.register_blueprint(html_atpro_settings_mqtt_routes)
        app.register_blueprint(html_atpro_settings_email_routes)
        app.register_blueprint(html_atpro_settings_3rd_party_routes)

        app.register_blueprint(html_atpro_system_routes)
        app.register_blueprint(html_atpro_system_raw_configs_routes)
        app.register_blueprint(html_atpro_system_sql_db_routes)
        app.register_blueprint(html_atpro_system_networking_routes)
        app.register_blueprint(html_atpro_system_commands_routes)

        app.register_blueprint(html_sensor_readings_routes)
        app.register_blueprint(html_local_download_routes)
        app.register_blueprint(html_get_set_config_routes)
        app.register_blueprint(html_system_commands_routes)
        app.register_blueprint(html_sensor_check_ins_routes)

        update_cached_variables()

        try:
            # Removes excessive "SSL Error" messages to console when using a self signed certificate
            hub.Hub.NOT_ERROR = (Exception,)
        except Exception as error:
            logger.primary_logger.warning("Error lowering HTTP Server Logging: " + str(error))

        try:
            flask_http_ip = app_config_access.primary_config.flask_http_ip
            flask_port_number = app_config_access.primary_config.web_portal_port
            http_server = pywsgi.WSGIServer((flask_http_ip, flask_port_number), app,
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
