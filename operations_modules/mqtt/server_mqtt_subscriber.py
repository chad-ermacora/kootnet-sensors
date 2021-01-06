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
from datetime import datetime
from paho.mqtt import subscribe
import sqlite3
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules.sqlite_database import write_to_sql_database
from operations_modules.file_locations import mqtt_subscriber_database as mqtt_sub_db_location


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
                if app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording:
                    _write_mqtt_message_to_sql_database(message)
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


def _write_mqtt_message_to_sql_database(mqtt_message):
    try:
        sensor_topic_as_list = str(mqtt_message.topic).strip().split("/")
        if len(sensor_topic_as_list) > 0:
            current_utc_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            sensor_id_str = sensor_topic_as_list[0]
            try:
                column_and_data_dic = eval(str(mqtt_message.payload.decode("UTF-8")))
                if type(column_and_data_dic) != dict:
                    column_and_data_dic = {sensor_topic_as_list[-1]: str(mqtt_message.payload.decode("UTF-8"))}
            except Exception as error:
                log_msg = "Unable to Convert MQTT subscription data to writable SQL data: "
                logger.network_logger.warning(log_msg + str(error))
                column_and_data_dic = {"Decode": "Error"}

            columns_sql_str = ""
            data_sql_value_place_marks = ""
            data_list = [current_utc_datetime]
            for column_name, column_data in column_and_data_dic.items():
                if column_name.replace("_", "JJ").isalnum():
                    _check_sql_table_column_exists(sensor_id_str, column_name)
                    columns_sql_str += column_name + ","
                    data_sql_value_place_marks += "?,"
                    data_list.append(str(column_data))
                else:
                    log_msg = "MQTT Subscriber SQL Recording: Incorrect sensor ID or Type - "
                    logger.network_logger.warning(log_msg + "Must be Alphanumeric")

            if len(columns_sql_str) > 0:
                columns_sql_str = columns_sql_str[:-1]
                data_sql_value_place_marks = data_sql_value_place_marks[:-1]
                sql_string = "INSERT OR IGNORE INTO " + sensor_id_str + " (" + \
                             app_cached_variables.database_variables.all_tables_datetime + "," + \
                             columns_sql_str + ") VALUES (?," + data_sql_value_place_marks + ")"
                write_to_sql_database(sql_string, data_list, sql_database_location=mqtt_sub_db_location)
    except Exception as error:
        logger.primary_logger.error("MQTT Subscriber Recording Failure: " + str(error))


def _check_sql_table_column_exists(table_name, column_text):
    db_connection = sqlite3.connect(mqtt_sub_db_location)
    db_cursor = db_connection.cursor()
    sql_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table_name + "';"
    db_cursor.execute(sql_query)

    if len(db_cursor.fetchall()) == 0:
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table_name, nf="DateTime", ft="TEXT"))
        for column in app_cached_variables.database_variables.get_sensor_columns_list():
            try:
                db_cursor.execute("ALTER TABLE '" + table_name + "' ADD COLUMN " + column + " TEXT")
            except Exception as error:
                if str(error)[:21] != "duplicate column name":
                    logger.primary_logger.error("MQTT Subscriber SQL Database Error: " + str(error))

    try:
        db_cursor.execute("ALTER TABLE '" + table_name + "' ADD COLUMN " + column_text + " TEXT")
    except Exception as error:
        if str(error)[:21] != "duplicate column name":
            logger.primary_logger.error("MQTT Subscriber SQL Database Error: " + str(error))
    db_connection.commit()
    db_connection.close()
