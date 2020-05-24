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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_config_access
from operations_modules.app_generic_functions import get_file_content
from operations_modules.mqtt.server_mqtt_broker import start_mqtt_broker_server, restart_mqtt_broker_server,\
    stop_mqtt_broker_server, check_mqtt_broker_server_running
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, get_restart_service_text

html_config_mqtt_broker_routes = Blueprint("html_config_mqtt_broker_routes", __name__)


@html_config_mqtt_broker_routes.route("/EditConfigMQTTBroker", methods=["POST"])
@auth.login_required
def html_set_config_mqtt_broker():
    logger.network_logger.debug("** HTML Apply - MQTT Broker Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.mqtt_broker_config.update_with_html_request(request)
            app_config_access.mqtt_broker_config.save_config_to_file()
            return_text = "MQTT Broker Configuration Saved"
            if app_config_access.mqtt_broker_config.enable_mqtt_broker:
                return_text = get_restart_service_text("MQTT Broker")
                if check_mqtt_broker_server_running():
                    restart_mqtt_broker_server()
                else:
                    start_mqtt_broker_server()
            else:
                stop_mqtt_broker_server()
            return_page = message_and_return(return_text, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML MQTT Broker Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def get_config_mqtt_broker_tab():
    try:
        mosquitto_configuration = ""
        if os.path.isfile(file_locations.mosquitto_configuration):
            mosquitto_configuration = get_file_content(file_locations.mosquitto_configuration)
        return render_template("edit_configurations/config_mqtt_broker.html",
                               PageURL="/ConfigurationsHTML",
                               BrokerServerChecked=get_html_checkbox_state(check_mqtt_broker_server_running()),
                               BrokerMosquittoConfig=mosquitto_configuration)
    except Exception as error:
        logger.network_logger.error("Error building MQTT Broker configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-broker-tab")
