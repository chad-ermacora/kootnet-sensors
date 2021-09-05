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
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content
from configuration_modules import app_config_access
from mqtt.server_mqtt_broker import start_mqtt_broker_server, restart_mqtt_broker_server, stop_mqtt_broker_server, \
    check_mqtt_broker_server_running
from http_server.server_http_generic_functions import get_html_checkbox_state, get_html_selected_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from http_server.flask_blueprints.atpro.atpro_variables import atpro_notifications

html_atpro_settings_mqtt_routes = Blueprint("html_atpro_settings_mqtt_routes", __name__)
email_config = app_config_access.email_config
db_v = app_cached_variables.database_variables


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-p", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_mqtt_publisher():
    mqtt_publisher_config = app_config_access.mqtt_publisher_config

    if request.method == "POST":
        app_config_access.mqtt_publisher_config.update_with_html_request(request)
        app_config_access.mqtt_publisher_config.save_config_to_file()
        app_cached_variables.restart_mqtt_publisher_thread = True
        return get_message_page("MQTT Publisher Settings Updated", page_url="sensor-settings")

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

    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-publisher.html",
        MQTTBaseTopic=mqtt_publisher_config.mqtt_base_topic[:-1],
        MQTTPublisherChecked=get_html_checkbox_state(mqtt_publisher_config.enable_mqtt_publisher),
        MQTTBrokerAddress=mqtt_publisher_config.broker_address,
        MQTTBrokerPort=str(mqtt_publisher_config.broker_server_port),
        MQTTPublishSecondsWait=str(mqtt_publisher_config.seconds_to_wait),
        MQTTPublisherAuthChecked=get_html_checkbox_state(mqtt_publisher_config.enable_broker_auth),
        MQTTPublisherUsername=mqtt_publisher_config.broker_user,
        PublisherQoSLevel0=qos_level_0,
        PublisherQoSLevel1=qos_level_1,
        PublisherQoSLevel2=qos_level_2,
        CheckedSensorHostName=get_html_checkbox_state(mqtt_publisher_config.sensor_host_name),
        CheckedSensorUptime=get_html_checkbox_state(mqtt_publisher_config.sensor_uptime),
        CheckedSensorIP=get_html_checkbox_state(mqtt_publisher_config.sensor_ip),
        CheckedSensorDateTime=get_html_checkbox_state(mqtt_publisher_config.sensor_date_time),
        CheckedCPUTemperature=get_html_checkbox_state(mqtt_publisher_config.system_temperature),
        CheckedEnvTemperature=get_html_checkbox_state(mqtt_publisher_config.env_temperature),
        CheckedPressure=get_html_checkbox_state(mqtt_publisher_config.pressure),
        CheckedAltitude=get_html_checkbox_state(mqtt_publisher_config.altitude),
        CheckedHumidity=get_html_checkbox_state(mqtt_publisher_config.humidity),
        CheckedDewPoint=get_html_checkbox_state(mqtt_publisher_config.dew_point),
        CheckedDistance=get_html_checkbox_state(mqtt_publisher_config.distance),
        CheckedGas=get_html_checkbox_state(mqtt_publisher_config.gas),
        CheckedPM=get_html_checkbox_state(mqtt_publisher_config.particulate_matter),
        CheckedLumen=get_html_checkbox_state(mqtt_publisher_config.lumen),
        CheckedColour=get_html_checkbox_state(mqtt_publisher_config.color),
        CheckedUltraViolet=get_html_checkbox_state(mqtt_publisher_config.ultra_violet),
        CheckedAccelerometer=get_html_checkbox_state(mqtt_publisher_config.accelerometer),
        CheckedMagnetometer=get_html_checkbox_state(mqtt_publisher_config.magnetometer),
        CheckedGyroscope=get_html_checkbox_state(mqtt_publisher_config.gyroscope),
        SASKSChecked=_get_checked_send_as(mqtt_publisher_config.mqtt_send_format_kootnet),
        SASIndChecked=_get_checked_send_as(mqtt_publisher_config.mqtt_send_format_individual_topics),
        SASCustomChecked=_get_checked_send_as(mqtt_publisher_config.mqtt_send_format_custom_string),
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
        MQTTDewPointTopic=mqtt_publisher_config.dew_point_topic,
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
        MQTTGyroZTopic=mqtt_publisher_config.gyroscope_z_topic
    )


def _get_checked_send_as(radio_text):
    if radio_text == app_config_access.mqtt_publisher_config.selected_mqtt_send_format:
        return "checked"
    return ""


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-p-reset-topics")
@auth.login_required
def html_atpro_sensor_settings_mqtt_publisher_reset_topics():
    app_config_access.mqtt_publisher_config.reset_publisher_topics()
    app_config_access.mqtt_publisher_config.update_configuration_settings_list()
    app_config_access.mqtt_publisher_config.save_config_to_file()
    return get_message_page("MQTT Publisher Topics Reset", page_url="sensor-settings")


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-p-reset-custom-format")
@auth.login_required
def html_atpro_reset_mqtt_publisher_custom_format():
    default_custom_format = app_config_access.mqtt_publisher_config.get_mqtt_replacements_dictionary()
    app_config_access.mqtt_publisher_config.mqtt_custom_data_string = str(default_custom_format)
    app_config_access.mqtt_publisher_config.update_configuration_settings_list()
    app_config_access.mqtt_publisher_config.save_config_to_file()
    return get_message_page("MQTT Publisher Custom Format Reset", page_url="sensor-settings")


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-p-custom-help")
def html_atpro_mqtt_publisher_custom_help():
    mqtt_pub_custom_vars = app_config_access.mqtt_publisher_config.get_mqtt_replacements_dictionary()
    return render_template("ATPro_admin/page_templates/settings/settings-mqtt-publisher-variable-help.html",
                           SystemHostname=mqtt_pub_custom_vars[db_v.sensor_name],
                           SystemIP=mqtt_pub_custom_vars[db_v.ip],
                           SystemUptime=mqtt_pub_custom_vars[db_v.sensor_uptime],
                           SystemDateTime=mqtt_pub_custom_vars[db_v.all_tables_datetime],
                           SystemTemperature=mqtt_pub_custom_vars[db_v.system_temperature],
                           EnvTemperature=mqtt_pub_custom_vars[db_v.env_temperature],
                           Pressure=mqtt_pub_custom_vars[db_v.pressure],
                           Altitude=mqtt_pub_custom_vars[db_v.altitude],
                           Humidity=mqtt_pub_custom_vars[db_v.humidity],
                           Distance=mqtt_pub_custom_vars[db_v.distance],
                           Lumen=mqtt_pub_custom_vars[db_v.lumen],
                           Red=mqtt_pub_custom_vars[db_v.red],
                           Orange=mqtt_pub_custom_vars[db_v.orange],
                           Yellow=mqtt_pub_custom_vars[db_v.yellow],
                           Green=mqtt_pub_custom_vars[db_v.green],
                           Blue=mqtt_pub_custom_vars[db_v.blue],
                           Violet=mqtt_pub_custom_vars[db_v.violet],
                           UVIndex=mqtt_pub_custom_vars[db_v.ultra_violet_index],
                           UVA=mqtt_pub_custom_vars[db_v.ultra_violet_a],
                           UVB=mqtt_pub_custom_vars[db_v.ultra_violet_b],
                           GASRI=mqtt_pub_custom_vars[db_v.gas_resistance_index],
                           GASOxidising=mqtt_pub_custom_vars[db_v.gas_oxidising],
                           GASReducing=mqtt_pub_custom_vars[db_v.gas_reducing],
                           GASNH3=mqtt_pub_custom_vars[db_v.gas_nh3],
                           PM1=mqtt_pub_custom_vars[db_v.particulate_matter_1],
                           PM2_5=mqtt_pub_custom_vars[db_v.particulate_matter_2_5],
                           PM4=mqtt_pub_custom_vars[db_v.particulate_matter_4],
                           PM10=mqtt_pub_custom_vars[db_v.particulate_matter_10],
                           AccelerometerX=mqtt_pub_custom_vars[db_v.acc_x],
                           AccelerometerY=mqtt_pub_custom_vars[db_v.acc_y],
                           AccelerometerZ=mqtt_pub_custom_vars[db_v.acc_z],
                           MagnetometerX=mqtt_pub_custom_vars[db_v.mag_x],
                           MagnetometerY=mqtt_pub_custom_vars[db_v.mag_y],
                           MagnetometerZ=mqtt_pub_custom_vars[db_v.mag_z],
                           GyroscopeX=mqtt_pub_custom_vars[db_v.gyro_x],
                           GyroscopeY=mqtt_pub_custom_vars[db_v.gyro_y],
                           GyroscopeZ=mqtt_pub_custom_vars[db_v.gyro_z])


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-s", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_mqtt_subscriber():
    if request.method == "POST":
        app_config_access.mqtt_subscriber_config.update_with_html_request(request)
        app_config_access.mqtt_subscriber_config.save_config_to_file()
        atpro_notifications.manage_service_restart()
        return get_message_page("MQTT Subscriber Settings Updated", page_url="sensor-settings")

    mqtt_qos = app_config_access.mqtt_subscriber_config.mqtt_subscriber_qos
    qos_level_0 = ""
    qos_level_1 = ""
    qos_level_2 = ""
    if mqtt_qos == 0:
        qos_level_0 = get_html_selected_state(True)
    elif mqtt_qos == 1:
        qos_level_1 = get_html_selected_state(True)
    elif mqtt_qos == 2:
        qos_level_2 = get_html_selected_state(True)

    enable_mqtt_subscriber = app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber
    enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording
    enable_broker_auth = app_config_access.mqtt_subscriber_config.enable_broker_auth
    csv_mqtt_topics = ""
    for topic in app_config_access.mqtt_subscriber_config.subscribed_topics_list:
        csv_mqtt_topics += topic + ","
    csv_mqtt_topics = csv_mqtt_topics[:-1]
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-subscriber.html",
        MaxSensorPosts=app_config_access.mqtt_subscriber_config.mqtt_page_view_max_entries,
        MQTTSubscriberChecked=get_html_checkbox_state(enable_mqtt_subscriber),
        MQTTSQLRecordingChecked=get_html_checkbox_state(enable_mqtt_sql_recording),
        MQTTBrokerAddress=app_config_access.mqtt_subscriber_config.broker_address,
        MQTTBrokerPort=str(app_config_access.mqtt_subscriber_config.broker_server_port),
        MQTTQoSLevel0=qos_level_0,
        MQTTQoSLevel1=qos_level_1,
        MQTTQoSLevel2=qos_level_2,
        MQTTSubscriberAuthChecked=get_html_checkbox_state(enable_broker_auth),
        MQTTSubscriberUsername=app_config_access.mqtt_subscriber_config.broker_user,
        SubscriberTopics=csv_mqtt_topics
    )


@html_atpro_settings_mqtt_routes.route("/atpro/settings-mqtt-b", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_mqtt_broker():
    if request.method == "POST":
        app_config_access.mqtt_broker_config.update_with_html_request(request)
        app_config_access.mqtt_broker_config.save_config_to_file()
        if app_config_access.mqtt_broker_config.enable_mqtt_broker:
            if check_mqtt_broker_server_running():
                return_text = "MQTT Broker Service Re-Started"
                restart_mqtt_broker_server()
            else:
                return_text = "MQTT Broker Service Starting"
                start_mqtt_broker_server()
        else:
            return_text = "MQTT Broker Service Stopped"
            stop_mqtt_broker_server()
        return get_message_page("MQTT Broker Settings Updated", return_text, page_url="sensor-settings")
    mosquitto_configuration = ""
    if os.path.isfile(file_locations.mosquitto_configuration):
        mosquitto_configuration = get_file_content(file_locations.mosquitto_configuration)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-broker.html",
        BrokerServerChecked=get_html_checkbox_state(check_mqtt_broker_server_running()),
        BrokerMosquittoConfig=mosquitto_configuration
    )
