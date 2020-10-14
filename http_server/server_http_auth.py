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

min_length_username = 4
min_length_password = 4


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
            logger.primary_logger.error("Problem loading Web Login Credentials - Using Defaults: " + str(error))
            save_http_auth_to_file(default_http_flask_user, default_http_flask_password)
            app_cached_variables.http_flask_user = default_http_flask_user
            app_cached_variables.http_flask_password = generate_password_hash(default_http_flask_password)
    else:
        log_msg = "Web Login Credentials not found, using and saving default of Kootnet/sensors"
        logger.primary_logger.warning(log_msg)
        logger.primary_logger.warning("It is Recommended to change default Login Credentials")
        save_http_auth_to_file(default_http_flask_user, default_http_flask_password, logging_enabled=False)
        app_cached_variables.http_flask_user = default_http_flask_user
        app_cached_variables.http_flask_password = generate_password_hash(default_http_flask_password)


def save_http_auth_to_file(new_http_flask_user, new_http_flask_password, logging_enabled=True):
    """ Saves Web Portal (flask app) login credentials to file. """
    try:
        if len(new_http_flask_user) < min_length_username or len(new_http_flask_password) < min_length_password:
            logger.primary_logger.error("Unable to change Web Portal Credentials")
            if len(new_http_flask_user) < min_length_username:
                logger.primary_logger.warning("Web Login user provided is too short")
            if len(new_http_flask_password) < min_length_password:
                logger.primary_logger.warning("Web Login Password provided is too short")
        else:
            save_data = new_http_flask_user + "\n" + generate_password_hash(new_http_flask_password)
            with open(file_locations.http_auth, "w") as auth_file:
                auth_file.write(save_data)
            if logging_enabled:
                logger.primary_logger.info("New Web Portal Username & Password Set")
    except Exception as error:
        logger.primary_logger.error("Error saving Flask HTTPS Authentication: " + str(error))


# Create Flask app HTTP login
auth = HTTPBasicAuth()
