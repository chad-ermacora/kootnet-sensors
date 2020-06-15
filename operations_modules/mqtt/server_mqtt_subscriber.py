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
from time import sleep
from paho.mqtt import subscribe
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from configuration_modules import app_config_access


class CreateMQTTSubscriberTopicRetrieval:
    def __init__(self, topic):
        self.topic = topic
        self.restart_mqtt_subscriber_thread = False

        self.mqtt_qos = app_config_access.mqtt_subscriber_config.mqtt_subscriber_qos
        self.cb_auth = None
        if app_config_access.mqtt_subscriber_config.enable_broker_auth:
            broker_user = app_config_access.mqtt_subscriber_config.broker_user
            broker_password = None
            if app_config_access.mqtt_subscriber_config.broker_user != "":
                if app_config_access.mqtt_subscriber_config.broker_password != "":
                    broker_password = app_config_access.mqtt_subscriber_config.broker_password
                self.cb_auth = {'username': broker_user, 'password': broker_password}

        self.broker_address = app_config_access.mqtt_subscriber_config.broker_address
        self.broker_server_port = app_config_access.mqtt_subscriber_config.broker_server_port
        thread_function(self._start_subscription)
        thread_function(self._watch_for_restart)

    def _start_subscription(self):
        while not self.restart_mqtt_subscriber_thread:
            try:
                message = subscribe.simple(self.topic, hostname=self.broker_address, port=self.broker_server_port,
                                           auth=self.cb_auth, tls=None, qos=self.mqtt_qos)
                logger.mqtt_subscriber_logger.info(str(message.topic) + " = " + str(message.payload.decode("UTF-8")))
            except Exception as error:
                logger.mqtt_subscriber_logger.error("Error processing MQTT Subscriber Message: " + str(error))
                sleep_fraction_interval = 1
                sleep_total = 0
                while sleep_total < 30 and not app_cached_variables.restart_mqtt_subscriber_thread:
                    sleep(sleep_fraction_interval)
                    sleep_total += sleep_fraction_interval

    def _watch_for_restart(self):
        while not self.restart_mqtt_subscriber_thread:
            sleep(2)
            if app_cached_variables.restart_mqtt_subscriber_thread:
                self.restart_mqtt_subscriber_thread = True


def restart_mqtt_subscriber_server():
    """ Restarts MQTT Subscriber server. """
    thread_function(_restart_mqtt_subscriber_server)


def _restart_mqtt_subscriber_server():
    app_cached_variables.restart_mqtt_subscriber_thread = True
    sleep(5)
    app_cached_variables.restart_mqtt_subscriber_thread = False
    start_mqtt_subscriber_server()


def stop_mqtt_subscriber_server():
    """ Stops MQTT Subscriber server. """
    thread_function(_stop_mqtt_subscriber_server)


def _stop_mqtt_subscriber_server():
    app_cached_variables.restart_mqtt_subscriber_thread = True
    sleep(5)
    app_cached_variables.restart_mqtt_subscriber_thread = False


def start_mqtt_subscriber_server():
    """ Starts MQTT Subscriber server. """
    if app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber:
        thread_function(_start_mqtt_subscriber_server)
        logger.primary_logger.info(" -- MQTT Subscriber Started")
    else:
        logger.primary_logger.debug("MQTT Subscriber Disabled in Configuration")


def _start_mqtt_subscriber_server():
    topic_list = app_config_access.mqtt_subscriber_config.subscribed_topics_list
    for topic in topic_list:
        thread_function(CreateMQTTSubscriberTopicRetrieval, args=topic)
