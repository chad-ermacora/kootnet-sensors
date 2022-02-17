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
import re
from io import BytesIO
from os import urandom
from hashlib import sha256
from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, redirect, request, send_file, send_from_directory, make_response
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import verify_password_to_hash
from operations_modules.app_generic_disk import get_file_content
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page

html_functional_routes = Blueprint("html_functional_routes", __name__)

html_extras_dir = file_locations.program_root_dir + "/http_server/extras"
documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"
fav_icon_file_content = None
help_index_page = None
charts_min_js = None
jquery_min_js = None


@html_functional_routes.route("/robots.txt")
def no_robots():
    return "User-agent: *\nDisallow: /"


@html_functional_routes.route("/favicon.ico")
@html_functional_routes.route("/AT-pro-logo.png")
def fav_icon_func():
    global fav_icon_file_content
    fav_icon_loc = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/assets/AT-pro-logo.png"
    if fav_icon_file_content is None:
        fav_icon_file_content = get_file_content(fav_icon_loc, open_type="rb")
    return_response = make_response(send_file(BytesIO(fav_icon_file_content), mimetype="image/jpeg"))
    return_response.headers["Cache-Control"] = "public, max-age=432000"
    return return_response


@html_functional_routes.route("/chart.min.js")
def charts_min_js_fun():
    global charts_min_js
    charts_min_js_loc = file_locations.program_root_dir + "/http_server/extras/chart.min.js"
    if charts_min_js is None:
        charts_min_js = get_file_content(charts_min_js_loc)
    return_response = make_response(charts_min_js)
    return_response.headers["Cache-Control"] = "public, max-age=432000"
    return return_response


@html_functional_routes.route("/jquery.min.js")
def jquery_min_js_fun():
    global jquery_min_js
    jquery_min_js_loc = file_locations.program_root_dir + "/http_server/extras/jquery-3.6.0.min.js"
    if jquery_min_js is None:
        jquery_min_js = get_file_content(jquery_min_js_loc)
    return_response = make_response(jquery_min_js)
    return_response.headers["Cache-Control"] = "public, max-age=432000"
    return return_response


# Start -- HTML assets for 'ATPro admin' interface
@html_functional_routes.route("/documentation/")
def sensor_unit_help():
    global help_index_page
    if help_index_page is None:
        help_index_page = get_file_content(documentation_root_dir + "/index.html")
    return_response = make_response(help_index_page)
    return_response.headers["Cache-Control"] = "public, max-age=432000"
    return return_response


@html_functional_routes.route('/documentation/css/<path:filename>')
def html_documentation_css_folder_static_files(filename):
    if _is_valid_filename(filename):
        doc_folder = file_locations.program_root_dir + "/extras/documentation/css/"
        return send_from_directory(doc_folder, filename)
    return ""


@html_functional_routes.route('/documentation/js/<path:filename>')
def html_documentation_js_folder_static_files(filename):
    if _is_valid_filename(filename):
        doc_folder = file_locations.program_root_dir + "/extras/documentation/js/"
        return send_from_directory(doc_folder, filename)
    return ""


@html_functional_routes.route('/extras/<path:filename>')
def html_extras_folder_static_files(filename):
    if _is_valid_filename(filename):
        extras_folder = file_locations.program_root_dir + "/http_server/extras/"
        return send_from_directory(extras_folder, filename)
    return ""


@html_functional_routes.route('/atpro/<path:filename>')
def atpro_root_static_files(filename):
    if _is_valid_filename(filename):
        atpro_folder = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/"
        return send_from_directory(atpro_folder, filename)
    return ""


def _is_valid_filename(filename):
    """
    If provided filename is using valid characters and, it's length is <= 256, returns True, else False
    :param filename: Name of a file as text
    :return: True/False
    """
    filename = str(filename)
    if len(filename) <= 256:
        if re.match('[0-9a-zA-Z_./-]+$', filename):
            return True
    return False
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
        ip_address = str(request.remote_addr)
        if _address_is_banned(ip_address):
            _ip_failed_login(ip_address)
            return_msg = "Too many failed login attempts, your IP address has been banned for 15 Min"
            return get_message_page("IP Banned from Logins", message=return_msg)
        else:
            username = str(request.form['login_username']).lower()
            password = request.form['login_password']

            if username == app_cached_variables.http_flask_user.lower() and verify_password_to_hash(password):
                new_session_id = sha256(urandom(12)).hexdigest()
                session['user_id'] = new_session_id
                app_cached_variables.http_flask_login_session_ids[new_session_id] = datetime.utcnow()
                return redirect('/atpro/')
        _ip_failed_login(ip_address)
        return get_message_page("Login Failed", page_url="sensor-settings")
    return render_template("ATPro_admin/page_templates/login.html")


@html_functional_routes.route("/atpro/logout")
def html_atpro_logout():
    session.pop('user_id', None)
    return get_message_page("Logged Out", "You have been logged out")


def _address_is_banned(ip_address):
    """
    Checks to see if an IP is banned
    If the last failed login was more than 15 minutes ago, reset failed login attempts to 0
    Returns True if there are more then 10 failed logins, else, False
    :param ip_address: IP address as a string
    :return: True/False
    """
    if ip_address in app_cached_variables.failed_flask_logins_dic:
        if datetime.utcnow() - app_cached_variables.failed_flask_logins_dic[ip_address][0] > timedelta(minutes=10):
            app_cached_variables.failed_flask_logins_dic[ip_address][1] = 0
        elif app_cached_variables.failed_flask_logins_dic[ip_address][1] > 30:
            log_msg = ip_address + " Banned || " + str(app_cached_variables.failed_flask_logins_dic[ip_address][1])
            logger.network_logger.warning(log_msg + " Failed Logins")
            return True
    return False


def _ip_failed_login(ip_address):
    """
    Runs on login failure to adds the failed attempt to a "watch list" of addresses
    :param ip_address: IP address as a string
    :return: Nothing
    """
    if ip_address not in app_cached_variables.failed_flask_logins_dic:
        app_cached_variables.failed_flask_logins_dic[ip_address] = [datetime.utcnow(), 1]
    else:
        app_cached_variables.failed_flask_logins_dic[ip_address][0] = datetime.utcnow()
        app_cached_variables.failed_flask_logins_dic[ip_address][1] += 1
