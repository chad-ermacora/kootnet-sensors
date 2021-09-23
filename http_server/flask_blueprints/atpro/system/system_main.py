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
from flask import Blueprint, render_template, request
from werkzeug.security import generate_password_hash
from operations_modules import app_cached_variables
from http_server.server_http_auth import auth, save_http_auth_to_file
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from http_server.flask_blueprints.atpro.system.system_sql_database import html_atpro_sensor_settings_database_uploads
from http_server.flask_blueprints.atpro.system.system_networking import html_atpro_system_ssl
from http_server.flask_blueprints.atpro.system.system_commands import html_atpro_system_upgrades_power

html_atpro_system_routes = Blueprint("html_atpro_system_routes", __name__)


@html_atpro_system_routes.route("/atpro/sensor-system")
def html_atpro_sensor_settings_system():
    return render_template("ATPro_admin/page_templates/system.html",
                           SystemDBUploads=html_atpro_sensor_settings_database_uploads(),
                           SystemSSL=html_atpro_system_ssl(),
                           SystemChangeLogin=html_atpro_system_change_login(),
                           SystemUpgradesPower=html_atpro_system_upgrades_power())


@html_atpro_system_routes.route("/atpro/system-change-login", methods=["GET", "POST"])
@auth.login_required
def html_atpro_system_change_login():
    if request.method == "POST":
        temp_username = str(request.form.get("login_username"))
        temp_password = str(request.form.get("login_password"))
        if len(temp_username) > 3 and len(temp_password) > 3:
            app_cached_variables.http_flask_user = temp_username
            app_cached_variables.http_flask_password = generate_password_hash(temp_password)
            save_http_auth_to_file(temp_username, temp_password)
            msg1 = "Username and Password Updated"
            msg2 = "The Username and Password has been updated"
        else:
            msg1 = "Invalid Username or Password"
            msg2 = "Username and Password must be 4 to 62 characters long and cannot be blank"
        return get_message_page(msg1, msg2)
    return render_template("ATPro_admin/page_templates/system/system-change-login.html")
