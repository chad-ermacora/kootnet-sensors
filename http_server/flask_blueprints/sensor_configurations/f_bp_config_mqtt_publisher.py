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
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, get_restart_service_text
from online_services_modules.mqtt_publisher import start_mqtt_publisher_server

html_config_mqtt_publisher_routes = Blueprint("html_config_mqtt_publisher_routes", __name__)


@html_config_mqtt_publisher_routes.route("/EditConfigMQTTPublisher", methods=["POST"])
@auth.login_required
def html_set_config_mqtt_publisher():
    logger.network_logger.debug("** HTML Apply - MQTT Publisher Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.mqtt_publisher_config.update_with_html_request(request)
            app_config_access.mqtt_publisher_config.save_config_to_file()
            return_text = "MQTT Publisher Configuration Saved"
            if app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
                return_text = get_restart_service_text("MQTT Publisher")
                if app_cached_variables.mqtt_publisher_thread is not None:
                    if app_cached_variables.mqtt_publisher_thread.monitored_thread.is_alive():
                        app_cached_variables.restart_mqtt_publisher_thread = True
                    else:
                        start_mqtt_publisher_server()
                else:
                    start_mqtt_publisher_server()
            else:
                if app_cached_variables.mqtt_publisher_thread is not None:
                    app_cached_variables.mqtt_publisher_thread.shutdown_thread = True
                    app_cached_variables.restart_mqtt_publisher_thread = True
            return_page = message_and_return(return_text, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML MQTT Publisher Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


def get_config_mqtt_publisher_tab():
    try:
        enable_mqtt_publisher = app_config_access.mqtt_publisher_config.enable_mqtt_publisher
        enable_broker_auth = app_config_access.mqtt_publisher_config.enable_broker_auth
        return render_template("edit_configurations/config_mqtt_publisher.html",
                               PageURL="/ConfigurationsHTML",
                               MQTTBaseTopic=app_config_access.mqtt_publisher_config.mqtt_base_topic,
                               MQTTPublisherChecked=get_html_checkbox_state(enable_mqtt_publisher),
                               MQTTBrokerAddress=app_config_access.mqtt_publisher_config.broker_address,
                               MQTTBrokerPort=str(app_config_access.mqtt_publisher_config.broker_server_port),
                               MQTTPublishSecondsWait=str(app_config_access.mqtt_publisher_config.seconds_to_wait),
                               MQTTPublisherAuthChecked=get_html_checkbox_state(enable_broker_auth),
                               MQTTPublisherUsername=app_config_access.mqtt_publisher_config.broker_user,
                               MQTTUptimeChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.sensor_uptime),
                               MQTTCPUTempChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.system_temperature),
                               MQTTEnvTempChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.env_temperature),
                               MQTTPressureChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.pressure),
                               MQTTAltitudeChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.altitude),
                               MQTTHumidityChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.humidity),
                               MQTTDistanceChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.distance),
                               MQTTGASChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.gas),
                               MQTTPMChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.particulate_matter),
                               MQTTLumenChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.lumen),
                               MQTTColoursChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.color),
                               MQTTUltraVioletChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.ultra_violet),
                               MQTTAccChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.accelerometer),
                               MQTTMagChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.magnetometer),
                               MQTTGyroChecked=get_html_checkbox_state(app_config_access.mqtt_publisher_config.gyroscope),
                               MQTTUptimeTopic=app_config_access.mqtt_publisher_config.sensor_uptime_topic,
                               MQTTCPUTempTopic=app_config_access.mqtt_publisher_config.system_temperature_topic,
                               MQTTEnvTempTopic=app_config_access.mqtt_publisher_config.env_temperature_topic,
                               MQTTPressureTopic=app_config_access.mqtt_publisher_config.pressure_topic,
                               MQTTAltitudeTopic=app_config_access.mqtt_publisher_config.altitude_topic,
                               MQTTHumidityTopic=app_config_access.mqtt_publisher_config.humidity_topic,
                               MQTTDistanceTopic=app_config_access.mqtt_publisher_config.distance_topic,
                               MQTTGASTopic=app_config_access.mqtt_publisher_config.gas_topic,
                               MQTTPMTopic=app_config_access.mqtt_publisher_config.particulate_matter_topic,
                               MQTTLumenTopic=app_config_access.mqtt_publisher_config.lumen_topic,
                               MQTTColoursTopic=app_config_access.mqtt_publisher_config.color_topic,
                               MQTTUltraVioletTopic=app_config_access.mqtt_publisher_config.ultra_violet_topic,
                               MQTTAccTopic=app_config_access.mqtt_publisher_config.accelerometer_topic,
                               MQTTMagTopic=app_config_access.mqtt_publisher_config.magnetometer_topic,
                               MQTTGyroTopic=app_config_access.mqtt_publisher_config.gyroscope_topic)
    except Exception as error:
        logger.network_logger.error("Error building MQTT configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-publisher-tab")
