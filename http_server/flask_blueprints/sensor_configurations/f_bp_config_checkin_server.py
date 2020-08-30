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
from operations_modules import logger
from configuration_modules import app_config_access
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return
from http_server.server_http_auth import auth

html_config_checkin_server_routes = Blueprint("html_config_checkin_server_routes", __name__)


@html_config_checkin_server_routes.route("/SaveCheckinSettings", methods=["POST"])
@auth.login_required
def html_set_checkin_settings():
    logger.network_logger.debug("** HTML Apply - Saving Check-ins Settings - Source: " + str(request.remote_addr))
    if request.method == "POST":
        app_config_access.checkin_config.update_with_html_request(request)
        app_config_access.checkin_config.save_config_to_file()
    return message_and_return("Checkin Server Settings Saved", url="/CheckinServerConfigurationHTML")


def get_config_checkin_server_tab():
    enable_checkin_recording = app_config_access.checkin_config.enable_checkin_recording
    return render_template("edit_configurations/config_checkin_server.html",
                           PageURL="/CheckinServerConfigurationHTML",
                           CheckedEnableCheckin=get_html_checkbox_state(enable_checkin_recording),
                           ContactInPastDays=app_config_access.checkin_config.count_contact_days,
                           CheckinHourOffset=app_config_access.checkin_config.hour_offset,
                           DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days)
