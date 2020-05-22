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
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from operations_modules.app_generic_functions import thread_function
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, get_html_disabled_state, \
    message_and_return
from sensor_modules import sensor_access

html_config_primary_routes = Blueprint("html_config_primary_routes", __name__)
running_with_root = app_cached_variables.running_with_root


@html_config_primary_routes.route("/EditConfigMain", methods=["POST"])
@auth.login_required
def html_set_config_main():
    logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.primary_config.update_with_html_request(request)
            app_config_access.primary_config.save_config_to_file()
            page_msg = "Config Set, Please Restart Program"
            if running_with_root:
                page_msg = "Restarting Service, Please Wait ..."
                thread_function(sensor_access.restart_services)
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def get_config_primary_tab():
    try:
        debug_logging = get_html_checkbox_state(app_config_access.primary_config.enable_debug_logging)
        interval_recording = get_html_checkbox_state(app_config_access.primary_config.enable_interval_recording)
        trigger_recording = get_html_checkbox_state(app_config_access.primary_config.enable_trigger_recording)
        custom_temp_offset = get_html_checkbox_state(app_config_access.primary_config.enable_custom_temp)
        custom_temp_comp = get_html_checkbox_state(app_config_access.primary_config.enable_temperature_comp_factor)

        return render_template("edit_configurations/config_primary.html",
                               PageURL="/ConfigurationsHTML",
                               IPWebPort=app_config_access.primary_config.web_portal_port,
                               CheckedDebug=debug_logging,
                               CheckedInterval=interval_recording,
                               DisabledIntervalDelay=get_html_disabled_state(interval_recording),
                               IntervalDelay=float(app_config_access.primary_config.sleep_duration_interval),
                               CheckedTrigger=trigger_recording,
                               CheckedCustomTempOffset=custom_temp_offset,
                               DisabledCustomTempOffset=get_html_disabled_state(custom_temp_offset),
                               temperature_offset=float(app_config_access.primary_config.temperature_offset),
                               CheckedCustomTempComp=custom_temp_comp,
                               CustomTempComp=float(app_config_access.primary_config.temperature_comp_factor),
                               DisabledCustomTempComp=get_html_disabled_state(custom_temp_comp))
    except Exception as error:
        logger.network_logger.error("Error building Primary configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="primary-config-tab")
