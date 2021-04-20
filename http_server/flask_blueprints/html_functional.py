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
from flask import Blueprint, send_file, request, send_from_directory
from werkzeug.security import check_password_hash
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_validation_checks import url_is_valid
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_message_page

html_functional_routes = Blueprint("html_functional_routes", __name__)

html_extras_dir = file_locations.program_root_dir + "/http_server/extras"
documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"


@html_functional_routes.route("/documentation/")
def sensor_unit_help():
    return send_file(documentation_root_dir + "/index.html")


# Help file requirements
@html_functional_routes.route("/KootnetSensorHardware.jpg")
def kootnet_sensor_hardware_picture():
    return send_file(file_locations.program_root_dir + "/extras/SensorHardware.jpg")


# New way to get HTTP extras sent for most above things (Does not work for current interface)
@html_functional_routes.route('/extras/<path:filename>')
def html_extras_folder_static_files(filename):
    if url_is_valid(filename):
        extras_folder = file_locations.program_root_dir + "/http_server/extras/"
        return send_from_directory(extras_folder, filename)
    return ""


@html_functional_routes.route('/documentation/css/<path:filename>')
def html_documentation_css_folder_static_files(filename):
    if url_is_valid(filename):
        doc_folder = file_locations.program_root_dir + "/extras/documentation/css/"
        return send_from_directory(doc_folder, filename)
    return ""


@html_functional_routes.route('/documentation/js/<path:filename>')
def html_documentation_js_folder_static_files(filename):
    if url_is_valid(filename):
        doc_folder = file_locations.program_root_dir + "/extras/documentation/js/"
        return send_from_directory(doc_folder, filename)
    return ""


# Start -- HTML JS/assets/fonts/css for 'ATPro admin' interface
@html_functional_routes.route('/atpro/<path:filename>')
def atpro_root_static_files(filename):
    if url_is_valid(filename):
        atpro_folder = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/"
        return send_from_directory(atpro_folder, filename)
    return ""
# End -- HTML assets for 'ATPro admin' interface


@auth.verify_password
def verify_password(username, password):
    if username == app_cached_variables.http_flask_user and \
            check_password_hash(app_cached_variables.http_flask_password, password):
        logger.network_logger.debug("* Login to Web Portal Successful from " + str(request.remote_addr))
        return True
    logger.network_logger.debug("* Login to Web Portal Failed from " + str(request.remote_addr))
    # Sleep on failure to help prevent brute force attempts
    sleep(1)
    return False


@auth.error_handler
def auth_error():
    msg = "Incorrect Username or Password."
    return get_message_page("Unauthorized Access", message=msg)
