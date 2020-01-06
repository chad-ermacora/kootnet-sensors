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
import os
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables

default_http_flask_user = "Kootnet"
default_http_flask_password = "sensors"


def set_http_auth_from_file():
    """ Loads Web Portal (flask app) login credentials from file and updates them in the configuration. """
    logger.primary_logger.debug("Loading HTTP Authentication File")

    if os.path.isfile(file_locations.http_auth):
        try:
            with open(file_locations.http_auth, "r") as auth_file:
                auth_file_lines = auth_file.readlines()
                app_cached_variables.http_flask_user = auth_file_lines[0].strip()
                app_cached_variables.http_flask_password = auth_file_lines[1].strip()
        except Exception as error:
            logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))
            save_http_auth_to_file(default_http_flask_user, default_http_flask_password)
            app_cached_variables.http_flask_user = default_http_flask_user
            app_cached_variables.http_flask_password = generate_password_hash(default_http_flask_password)
    else:
        logger.primary_logger.warning("Configuration file not found, using and saving default")
        save_http_auth_to_file(default_http_flask_user, default_http_flask_password)
        app_cached_variables.http_flask_user = default_http_flask_user
        app_cached_variables.http_flask_password = generate_password_hash(default_http_flask_password)


def _verify_http_credentials(new_http_flask_user, new_http_flask_password):
    if len(new_http_flask_user) > 2 and len(new_http_flask_password) > 2:
        new_http_flask_user = new_http_flask_user
        new_http_flask_password = new_http_flask_password
        return new_http_flask_user, new_http_flask_password
    else:
        logger.primary_logger.warning("HTTP Authentication User or Password are less then 4 chars.  Using default.")
        return "Kootnet", "sensors"


def save_http_auth_to_file(new_http_flask_user, new_http_flask_password):
    """ Saves Web Portal (flask app) login credentials to file. """
    try:
        verified_user, verified_password = _verify_http_credentials(new_http_flask_user, new_http_flask_password)
        save_data = verified_user + "\n" + generate_password_hash(verified_password)
        with open(file_locations.http_auth, "w") as auth_file:
            auth_file.write(save_data)
    except Exception as error:
        logger.primary_logger.error("Error saving Flask HTTPS Authentication: " + str(error))


# Create Flask app HTTP login
auth = HTTPBasicAuth()
