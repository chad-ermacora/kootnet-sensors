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
from os import urandom
from hashlib import sha256
from time import sleep
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, request, send_file, send_from_directory
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import verify_password_to_hash
from operations_modules.app_validation_checks import url_is_valid
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page

html_functional_routes = Blueprint("html_functional_routes", __name__)

html_extras_dir = file_locations.program_root_dir + "/http_server/extras"
documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"


@html_functional_routes.route("/robots.txt")
def no_robots():
    return "User-agent: *\nDisallow: /"


@html_functional_routes.route("/favicon.ico")
def fav_icon():
    return send_file(file_locations.program_root_dir + "/http_server/templates/ATPro_admin/assets/AT-pro-logo.png")


# Start -- HTML assets for 'ATPro admin' interface
@html_functional_routes.route("/documentation/")
def sensor_unit_help():
    return send_file(documentation_root_dir + "/index.html")


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


@html_functional_routes.route('/atpro/<path:filename>')
def atpro_root_static_files(filename):
    if url_is_valid(filename):
        atpro_folder = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/"
        return send_from_directory(atpro_folder, filename)
    return ""
# End -- HTML assets for 'ATPro admin' interface


@html_functional_routes.route("/CheckOnlineStatus")
def check_online():
    logger.network_logger.debug("Sensor Status Checked by " + str(request.remote_addr))
    return "OK"


@html_functional_routes.route("/TestLogin")
@auth.login_required
def test_login():
    logger.network_logger.debug("Sensor Login Test Successful from " + str(request.remote_addr))
    return "OK"


@html_functional_routes.route('/atpro/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login_username']
        password = request.form['login_password']

        if username == app_cached_variables.http_flask_user and verify_password_to_hash(password):
            new_session_id = sha256(urandom(12)).hexdigest()
            session['user_id'] = new_session_id
            app_cached_variables.http_flask_login_session_ids[new_session_id] = datetime.utcnow()
            return redirect('/atpro/')
        # Sleep on failure to help prevent brute force attempts
        sleep(0.25)
        return get_message_page("Incorrect Login Provided", page_url="sensor-settings")
    return render_template("ATPro_admin/page_templates/login.html")


@html_functional_routes.route("/atpro/logout")
def html_atpro_logout():
    session.pop('user_id', None)
    return get_message_page("Logged Out", "You have been logged out")
