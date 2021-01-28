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
from paho.mqtt import publish
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules import sensor_access

database_variables = app_cached_variables.database_variables
mqtt_base_topic = app_config_access.mqtt_publisher_config.mqtt_base_topic
mqtt_publisher_qos = app_config_access.mqtt_publisher_config.mqtt_publisher_qos


def start_mqtt_publisher_server():
    text_name = "MQTT Publisher"
    function = _mqtt_publisher_server
    app_cached_variables.mqtt_publisher_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
        logger.primary_logger.debug("MQTT Publisher Disabled in Configuration")
        app_cached_variables.mqtt_publisher_thread.current_state = "Disabled"


def _mqtt_publisher_server():
    """ Starts MQTT Publisher and runs based on settings found in the MQTT Publisher configuration file. """
    app_cached_variables.mqtt_publisher_thread.current_state = "Disabled"
    while not app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
        sleep(5)
    app_cached_variables.mqtt_publisher_thread.current_state = "Running"
    app_cached_variables.restart_mqtt_publisher_thread = False
    if app_config_access.mqtt_broker_config.enable_mqtt_broker:
        # Sleep a few seconds to allow the local broker to start first
        sleep(3)

    broker_address = app_config_access.mqtt_publisher_config.broker_address
    broker_server_port = app_config_access.mqtt_publisher_config.broker_server_port
    mqtt_pub_auth = None
    if app_config_access.mqtt_publisher_config.enable_broker_auth and \
            app_config_access.mqtt_publisher_config.broker_user != "":
        user = app_config_access.mqtt_publisher_config.broker_user
        password = app_config_access.mqtt_publisher_config.broker_password
        if password == "":
            mqtt_pub_auth = {"username": user, "password": None}
        else:
            mqtt_pub_auth = {"username": user, "password": password}

    while not app_cached_variables.restart_mqtt_publisher_thread:
        publish_msgs = get_publish_messages()
        try:
            publish.multiple(publish_msgs, hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
        except Exception as error:
            logger.network_logger.error("MQTT Publisher Send Failure: " + str(error))

        sleep_fraction_interval = 5
        sleep_total = 0
        seconds_to_wait = app_config_access.mqtt_publisher_config.seconds_to_wait
        while sleep_total < seconds_to_wait and not app_cached_variables.restart_mqtt_publisher_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


# When using publish.multiple you CANNOT use callbacks. It prevents data transmission (stops after connecting)
# Keeping for diagnostics only
def _publish_on_connect(client, userdata, flags, rc):
    logger.network_logger.debug("MQTT Publisher Connection Code: " + str(rc))
    print("MQTT Publisher Connection Code: " + str(rc))


# When using publish.multiple you CANNOT use callbacks. It prevents data transmission (stops after connecting)
# Keeping for diagnostics only
def _publish_on_pub(client, userdata, mid):
    logger.network_logger.debug("MQTT Publisher Pub Code: " + str(mid))
    print("MQTT Publisher Pub Code: " + str(mid))


def get_publish_messages():
    publish_msgs = []
    try:
        if app_config_access.mqtt_publisher_config.sensor_uptime:
            sensor_data = sensor_access.get_uptime_minutes()
            if sensor_data is not None:
                sensor_data = {database_variables.sensor_uptime: sensor_data}
                add_topic = mqtt_base_topic + app_config_access.mqtt_publisher_config.sensor_uptime_topic
                publish_msgs.append({"topic": add_topic, "payload": str(sensor_data), "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.system_temperature:
            topic = app_config_access.mqtt_publisher_config.system_temperature_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_cpu_temperature, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.env_temperature:
            topic = app_config_access.mqtt_publisher_config.env_temperature_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_environment_temperature, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.pressure:
            topic = app_config_access.mqtt_publisher_config.pressure_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_pressure, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.altitude:
            topic = app_config_access.mqtt_publisher_config.altitude_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_altitude, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.humidity:
            topic = app_config_access.mqtt_publisher_config.humidity_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_humidity, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.distance:
            topic = app_config_access.mqtt_publisher_config.distance_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_distance, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.gas:
            topic = app_config_access.mqtt_publisher_config.gas_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_gas, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.particulate_matter:
            topic = app_config_access.mqtt_publisher_config.particulate_matter_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_particulate_matter, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.lumen:
            topic = app_config_access.mqtt_publisher_config.lumen_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_lumen, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.color:
            topic = app_config_access.mqtt_publisher_config.color_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_ems_colors, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.ultra_violet:
            topic = app_config_access.mqtt_publisher_config.ultra_violet_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_ultra_violet, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.accelerometer:
            topic = app_config_access.mqtt_publisher_config.accelerometer_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_accelerometer_xyz, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.magnetometer:
            topic = app_config_access.mqtt_publisher_config.magnetometer_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_magnetometer_xyz, topic, publish_msgs)

        if app_config_access.mqtt_publisher_config.gyroscope:
            topic = app_config_access.mqtt_publisher_config.gyroscope_topic
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_gyroscope_xyz, topic, publish_msgs)
    except Exception as error:
        logger.primary_logger.error("MQTT Publisher Sensor Get Failure: " + str(error))
        add_topic = "Getting Sensor Data Failed for " + app_config_access.mqtt_publisher_config.mqtt_base_topic
        sensor_data = "Error"
        publish_msgs.append({"topic": add_topic, "payload": str(sensor_data), "qos": mqtt_publisher_qos})
    return publish_msgs


def _add_sensor_to_publish_msgs(sensor_function, sensor_topic_text, publish_msgs_list):
    add_topic = mqtt_base_topic + sensor_topic_text
    sensor_data = sensor_function()
    if sensor_data is not None:
        publish_msgs_list.append({"topic": add_topic, "payload": str(sensor_data), "qos": mqtt_publisher_qos})
    return publish_msgs_list
