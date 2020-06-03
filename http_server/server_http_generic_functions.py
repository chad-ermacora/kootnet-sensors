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
from flask import render_template
from operations_modules import app_cached_variables


def message_and_return(return_message, text_message2="", url="/", special_command=""):
    """
    Returns an HTML page of the provided message then redirects to the index web page after 10 seconds.
    Optional: Add a secondary text message, customize the URL or add a special HTML command.
    """
    return render_template("message_return.html",
                           PageURL=url,
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           TextMessage=return_message,
                           TextMessage2=text_message2,
                           CloseWindow=special_command)


def get_html_checkbox_state(config_setting):
    """ Generic function to return HTML code for checkboxes (Used in flask render templates). """
    if config_setting:
        return "checked"
    return ""


def get_html_disabled_state(config_setting):
    """ Generic function used to disable HTML content if config_setting is False (Used in flask render templates). """
    if config_setting:
        return ""
    return "disabled"


def get_html_hidden_state(config_setting):
    """ Generic function used to hide HTML content if config_setting is False (Used in flask render templates). """
    if config_setting:
        return ""
    return "hidden"


def get_html_selected_state(config_setting):
    """ Generic function to return HTML code for checkboxes (Used in flask render templates). """
    if config_setting:
        return "selected"
    return ""


def get_restart_service_text(service_name):
    return "Restarting " + str(service_name) + " Service, This may take up to 10 Seconds"
