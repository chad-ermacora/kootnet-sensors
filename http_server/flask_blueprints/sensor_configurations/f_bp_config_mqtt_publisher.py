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
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, \
    get_restart_service_text, get_html_selected_state

html_config_mqtt_publisher_routes = Blueprint("html_config_mqtt_publisher_routes", __name__)


@html_config_mqtt_publisher_routes.route("/EditConfigMQTTPublisher", methods=["POST"])
@auth.login_required
def html_set_config_mqtt_publisher():
    logger.network_logger.debug("** HTML Apply - MQTT Publisher Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.mqtt_publisher_config.update_with_html_request(request)
            app_config_access.mqtt_publisher_config.save_config_to_file()
            return_text = get_restart_service_text("MQTT Publisher")
            app_cached_variables.restart_mqtt_publisher_thread = True
            return_page = message_and_return(return_text, url="/MQTTConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML MQTT Publisher Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/MQTTConfigurationsHTML")


@html_config_mqtt_publisher_routes.route("/ResetMQTTPublisherTopics")
@auth.login_required
def html_reset_mqtt_publisher_topics():
    logger.network_logger.debug("** HTML Reset - MQTT Publisher Topics - Source: " + str(request.remote_addr))
    app_config_access.mqtt_publisher_config.reset_publisher_topics()
    app_config_access.mqtt_publisher_config.update_configuration_settings_list()
    app_config_access.mqtt_publisher_config.save_config_to_file()
    page_msg = "MQTT Publisher Topics reset to defaults"
    return message_and_return(page_msg, url="/MQTTConfigurationsHTML")


@html_config_mqtt_publisher_routes.route("/ResetMQTTPublisherCustomFormat")
@auth.login_required
def html_reset_mqtt_publisher_custom_format():
    logger.network_logger.debug("** HTML Reset - MQTT Publisher Custom Format - Source: " + str(request.remote_addr))
    default_custom_format = app_config_access.mqtt_publisher_config.get_mqtt_replacements_dictionary()
    app_config_access.mqtt_publisher_config.mqtt_custom_data_string = str(default_custom_format)
    app_config_access.mqtt_publisher_config.update_configuration_settings_list()
    app_config_access.mqtt_publisher_config.save_config_to_file()
    return message_and_return("MQTT Publisher Custom Format reset to default", url="/MQTTConfigurationsHTML")


def get_config_mqtt_publisher_tab():
    mqtt_publisher_config = app_config_access.mqtt_publisher_config

    try:
        enable_mqtt_publisher = mqtt_publisher_config.enable_mqtt_publisher
        enable_broker_auth = mqtt_publisher_config.enable_broker_auth
        mqtt_publisher_qos = mqtt_publisher_config.mqtt_publisher_qos
        qos_level_0 = ""
        qos_level_1 = ""
        qos_level_2 = ""
        if mqtt_publisher_qos == 0:
            qos_level_0 = get_html_selected_state(True)
        elif mqtt_publisher_qos == 1:
            qos_level_1 = get_html_selected_state(True)
        elif mqtt_publisher_qos == 2:
            qos_level_2 = get_html_selected_state(True)
        sensor_host_name = mqtt_publisher_config.sensor_host_name
        sensor_ip = mqtt_publisher_config.sensor_ip
        sensor_uptime = mqtt_publisher_config.sensor_uptime
        sensor_date_time = mqtt_publisher_config.sensor_date_time
        system_temperature = mqtt_publisher_config.system_temperature
        env_temperature = mqtt_publisher_config.env_temperature
        pressure = mqtt_publisher_config.pressure
        altitude = mqtt_publisher_config.altitude
        humidity = mqtt_publisher_config.humidity
        distance = mqtt_publisher_config.distance
        particulate_matter = mqtt_publisher_config.particulate_matter
        color = mqtt_publisher_config.color
        ultra_violet = mqtt_publisher_config.ultra_violet
        accelerometer = mqtt_publisher_config.accelerometer
        magnetometer = mqtt_publisher_config.magnetometer
        gyroscope = mqtt_publisher_config.gyroscope
        mqtt_send_format_kootnet = mqtt_publisher_config.mqtt_send_format_kootnet
        mqtt_send_format_individual_topics = mqtt_publisher_config.mqtt_send_format_individual_topics
        mqtt_send_format_custom_string = mqtt_publisher_config.mqtt_send_format_custom_string
        return render_template("edit_configurations/config_mqtt_publisher.html",
                               PageURL="/MQTTConfigurationsHTML",
                               MQTTBaseTopic=mqtt_publisher_config.mqtt_base_topic[:-1],
                               MQTTPublisherChecked=get_html_checkbox_state(enable_mqtt_publisher),
                               MQTTBrokerAddress=mqtt_publisher_config.broker_address,
                               MQTTBrokerPort=str(mqtt_publisher_config.broker_server_port),
                               MQTTPublishSecondsWait=str(mqtt_publisher_config.seconds_to_wait),
                               MQTTPublisherAuthChecked=get_html_checkbox_state(enable_broker_auth),
                               MQTTPublisherUsername=mqtt_publisher_config.broker_user,
                               PublisherQoSLevel0=qos_level_0,
                               PublisherQoSLevel1=qos_level_1,
                               PublisherQoSLevel2=qos_level_2,
                               MQTTHostNameChecked=get_html_checkbox_state(sensor_host_name),
                               MQTTSystemIPChecked=get_html_checkbox_state(sensor_ip),
                               MQTTUptimeChecked=get_html_checkbox_state(sensor_uptime),
                               MQTTSystemDateTimeChecked=get_html_checkbox_state(sensor_date_time),
                               MQTTCPUTempChecked=get_html_checkbox_state(system_temperature),
                               MQTTEnvTempChecked=get_html_checkbox_state(env_temperature),
                               MQTTPressureChecked=get_html_checkbox_state(pressure),
                               MQTTAltitudeChecked=get_html_checkbox_state(altitude),
                               MQTTHumidityChecked=get_html_checkbox_state(humidity),
                               MQTTDistanceChecked=get_html_checkbox_state(distance),
                               MQTTGASChecked=get_html_checkbox_state(mqtt_publisher_config.gas),
                               MQTTPMChecked=get_html_checkbox_state(particulate_matter),
                               MQTTLumenChecked=get_html_checkbox_state(mqtt_publisher_config.lumen),
                               MQTTColoursChecked=get_html_checkbox_state(color),
                               MQTTUltraVioletChecked=get_html_checkbox_state(ultra_violet),
                               MQTTAccChecked=get_html_checkbox_state(accelerometer),
                               MQTTMagChecked=get_html_checkbox_state(magnetometer),
                               MQTTGyroChecked=get_html_checkbox_state(gyroscope),
                               SendKSFormat=mqtt_send_format_kootnet,
                               SendIndividualTopics=mqtt_send_format_individual_topics,
                               SendCustomString=mqtt_send_format_custom_string,
                               SASKSChecked=_get_checked_send_as(mqtt_send_format_kootnet),
                               SASIndChecked=_get_checked_send_as(mqtt_send_format_individual_topics),
                               SASCustomChecked=_get_checked_send_as(mqtt_send_format_custom_string),
                               MQTTCustomDataFormat=mqtt_publisher_config.mqtt_custom_data_string,
                               MQTTSystemHostNameTopic=mqtt_publisher_config.sensor_host_name_topic,
                               MQTTIPTopic=mqtt_publisher_config.sensor_ip_topic,
                               MQTTUptimeTopic=mqtt_publisher_config.sensor_uptime_topic,
                               MQTTDateTimeTopic=mqtt_publisher_config.sensor_date_time_topic,
                               MQTTCPUTempTopic=mqtt_publisher_config.system_temperature_topic,
                               MQTTEnvTempTopic=mqtt_publisher_config.env_temperature_topic,
                               MQTTPressureTopic=mqtt_publisher_config.pressure_topic,
                               MQTTAltitudeTopic=mqtt_publisher_config.altitude_topic,
                               MQTTHumidityTopic=mqtt_publisher_config.humidity_topic,
                               MQTTDistanceTopic=mqtt_publisher_config.distance_topic,
                               MQTTGASTopic=mqtt_publisher_config.gas_topic,
                               MQTTGASRestIndexTopic=mqtt_publisher_config.gas_resistance_index_topic,
                               MQTTGASOxidisingTopic=mqtt_publisher_config.gas_oxidising_topic,
                               MQTTGASReducingTopic=mqtt_publisher_config.gas_reducing_topic,
                               MQTTGASNH3Topic=mqtt_publisher_config.gas_nh3_topic,
                               MQTTPMTopic=mqtt_publisher_config.particulate_matter_topic,
                               MQTTPM1Topic=mqtt_publisher_config.particulate_matter_1_topic,
                               MQTTPM2_5Topic=mqtt_publisher_config.particulate_matter_2_5_topic,
                               MQTTPM4Topic=mqtt_publisher_config.particulate_matter_4_topic,
                               MQTTPM10Topic=mqtt_publisher_config.particulate_matter_10_topic,
                               MQTTLumenTopic=mqtt_publisher_config.lumen_topic,
                               MQTTColoursTopic=mqtt_publisher_config.color_topic,
                               MQTTColourRedTopic=mqtt_publisher_config.color_red_topic,
                               MQTTColourOrangeTopic=mqtt_publisher_config.color_orange_topic,
                               MQTTColourYellowTopic=mqtt_publisher_config.color_yellow_topic,
                               MQTTColourGreenTopic=mqtt_publisher_config.color_green_topic,
                               MQTTColourBlueTopic=mqtt_publisher_config.color_blue_topic,
                               MQTTColourVioletTopic=mqtt_publisher_config.color_violet_topic,
                               MQTTUltraVioletTopic=mqtt_publisher_config.ultra_violet_topic,
                               MQTTUVIndexTopic=mqtt_publisher_config.ultra_violet_index_topic,
                               MQTTUVATopic=mqtt_publisher_config.ultra_violet_a_topic,
                               MQTTUVBTopic=mqtt_publisher_config.ultra_violet_b_topic,
                               MQTTAccTopic=mqtt_publisher_config.accelerometer_topic,
                               MQTTAccXTopic=mqtt_publisher_config.accelerometer_x_topic,
                               MQTTAccYTopic=mqtt_publisher_config.accelerometer_y_topic,
                               MQTTAccZTopic=mqtt_publisher_config.accelerometer_z_topic,
                               MQTTMagTopic=mqtt_publisher_config.magnetometer_topic,
                               MQTTMagXTopic=mqtt_publisher_config.magnetometer_x_topic,
                               MQTTMagYTopic=mqtt_publisher_config.magnetometer_y_topic,
                               MQTTMagZTopic=mqtt_publisher_config.magnetometer_z_topic,
                               MQTTGyroTopic=mqtt_publisher_config.gyroscope_topic,
                               MQTTGyroXTopic=mqtt_publisher_config.gyroscope_x_topic,
                               MQTTGyroYTopic=mqtt_publisher_config.gyroscope_y_topic,
                               MQTTGyroZTopic=mqtt_publisher_config.gyroscope_z_topic)
    except Exception as error:
        logger.network_logger.error("Error building MQTT configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-publisher-tab")


def _get_checked_send_as(radio_text):
    if radio_text == app_config_access.mqtt_publisher_config.selected_mqtt_send_format:
        return "checked"
    return ""
