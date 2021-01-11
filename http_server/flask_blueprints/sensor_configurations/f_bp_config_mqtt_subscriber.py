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
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import zip_files, get_file_content
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return, \
    get_html_selected_state, get_html_hidden_state
from sensor_modules.sensor_access import get_file_size

html_config_mqtt_subscriber_routes = Blueprint("html_config_mqtt_subscriber_routes", __name__)


@html_config_mqtt_subscriber_routes.route("/MQTTSubscriberView")
@auth.login_required
def html_get_mqtt_subscriber_view():
    logger.network_logger.debug("** HTML MQTT Subscriber Topic View - Source: " + str(request.remote_addr))
    enabled_text = "Disabled"
    enabled_color = "red"
    if app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber:
        enabled_text = "Enabled"
        enabled_color = "green"

    mqtt_subscriber_log_content = logger.get_sensor_log(file_locations.mqtt_subscriber_log)
    if mqtt_subscriber_log_content == "":
        mqtt_subscriber_log_content = "No MQTT Subscriber Messages"
    return render_template("mqtt_subscriber.html",
                           PageURL="/MQTTSubscriberView",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           MQTTSubscriberServerAddress=app_config_access.mqtt_subscriber_config.broker_address,
                           MQTTSubscriberEnabledText=enabled_text,
                           MQTTEnabledColor=enabled_color,
                           SubscriberTopics=mqtt_subscriber_log_content)


@html_config_mqtt_subscriber_routes.route("/DownloadMQTTSubSQLDatabase")
@auth.login_required
def html_download_mqtt_subscriber_db_zipped():
    log_msg = "** HTML MQTT Subscriber - Download Database Zipped - Source: "
    logger.network_logger.debug(log_msg + str(request.remote_addr))
    zip_name = "MQTT_Database_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
    database_name = "MQTT_Subscriber_Database_" + app_cached_variables.hostname + ".sqlite"
    database_content = get_file_content(file_locations.mqtt_subscriber_database, open_type="rb")
    return_zip_file = zip_files([database_name], [database_content])
    return send_file(return_zip_file, attachment_filename=zip_name, as_attachment=True)


@html_config_mqtt_subscriber_routes.route("/DownloadMQTTSubSQLDatabaseRAW")
@auth.login_required
def html_download_mqtt_subscriber_db_raw():
    log_msg = "** HTML MQTT Subscriber - Download Database raw - Source: "
    logger.network_logger.debug(log_msg + str(request.remote_addr))
    database_name = "MQTT_Subscriber_Database_" + app_cached_variables.hostname + ".sqlite"
    return send_file(file_locations.mqtt_subscriber_database, attachment_filename=database_name, as_attachment=True)


@html_config_mqtt_subscriber_routes.route("/EditConfigMQTTSubscriber", methods=["POST"])
@auth.login_required
def html_set_config_mqtt_subscriber():
    logger.network_logger.debug("** HTML Apply - MQTT Subscriber Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.mqtt_subscriber_config.update_with_html_request(request)
            app_config_access.mqtt_subscriber_config.save_config_to_file()
            return_text = "MQTT Subscriber Configuration Saved"
            app_cached_variables.html_service_restart = True
            return_page = message_and_return(return_text, url="/MQTTConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML MQTT Subscriber Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/MQTTConfigurationsHTML")


@html_config_mqtt_subscriber_routes.route("/ClearMQTTSubscriberLog")
@auth.login_required
def html_clear_mqtt_subscriber_log():
    logger.network_logger.debug("** HTML Clear - MQTT Subscriber Log - Source: " + str(request.remote_addr))
    logger.clear_mqtt_subscriber_log()
    return html_get_mqtt_subscriber_view()


def get_config_mqtt_subscriber_tab():
    try:
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
        return render_template("edit_configurations/config_mqtt_subscriber.html",
                               PageURL="/MQTTConfigurationsHTML",
                               MQTTSubscriberChecked=get_html_checkbox_state(enable_mqtt_subscriber),
                               MQTTSQLRecordingChecked=get_html_checkbox_state(enable_mqtt_sql_recording),
                               MQTTSubDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
                               MQTTBrokerAddress=app_config_access.mqtt_subscriber_config.broker_address,
                               MQTTBrokerPort=str(app_config_access.mqtt_subscriber_config.broker_server_port),
                               MQTTQoSLevel0=qos_level_0,
                               MQTTQoSLevel1=qos_level_1,
                               MQTTQoSLevel2=qos_level_2,
                               MQTTSubscriberAuthChecked=get_html_checkbox_state(enable_broker_auth),
                               MQTTSubscriberUsername=app_config_access.mqtt_subscriber_config.broker_user,
                               SubscriberTopics=csv_mqtt_topics)
    except Exception as error:
        logger.network_logger.error("Error building MQTT configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-subscriber-tab")
