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
from sensor_recording_modules.recording_interval import available_sensors

database_variables = app_cached_variables.database_variables


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
        if password != "":
            mqtt_pub_auth = {"username": user}
        else:
            mqtt_pub_auth = {"username": user, "password": password}

    while not app_cached_variables.restart_mqtt_publisher_thread:
        publish_msgs = get_publish_messages()
        try:
            publish.multiple(publish_msgs, hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
        except Exception as error:
            logger.primary_logger.error("MQTT Publisher Send Failure: " + str(error))

        sleep_fraction_interval = 5
        sleep_total = 0
        seconds_to_wait = app_config_access.mqtt_publisher_config.seconds_to_wait
        while sleep_total < seconds_to_wait and not app_cached_variables.restart_mqtt_publisher_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


def get_publish_messages():
    publish_msgs = []
    mqtt_publisher_qos = app_config_access.mqtt_publisher_config.mqtt_publisher_qos
    try:
        if app_config_access.mqtt_publisher_config.sensor_uptime:
            add_topic = app_config_access.mqtt_publisher_config.sensor_uptime_topic
            sensor_data = str(sensor_access.get_uptime_minutes())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.system_temperature and available_sensors.has_cpu_temperature:
            add_topic = app_config_access.mqtt_publisher_config.system_temperature_topic
            sensor_data = str(sensor_access.get_cpu_temperature())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.env_temperature and available_sensors.has_env_temperature:
            add_topic = app_config_access.mqtt_publisher_config.env_temperature_topic
            sensor_data = str(sensor_access.get_sensor_temperature())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.pressure and available_sensors.has_pressure:
            add_topic = app_config_access.mqtt_publisher_config.pressure_topic
            sensor_data = str(sensor_access.get_pressure())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.altitude and available_sensors.has_altitude:
            add_topic = app_config_access.mqtt_publisher_config.altitude_topic
            sensor_data = str(sensor_access.get_altitude())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.humidity and available_sensors.has_humidity:
            add_topic = app_config_access.mqtt_publisher_config.humidity_topic
            sensor_data = str(sensor_access.get_humidity())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.distance and available_sensors.has_distance:
            add_topic = app_config_access.mqtt_publisher_config.distance_topic
            sensor_data = str(sensor_access.get_distance())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.gas and available_sensors.has_gas:
            add_topic = app_config_access.mqtt_publisher_config.gas_topic
            sensor_data = str(sensor_access.get_gas(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.particulate_matter and available_sensors.has_particulate_matter:
            add_topic = app_config_access.mqtt_publisher_config.particulate_matter_topic
            sensor_data = str(sensor_access.get_particulate_matter(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.lumen and available_sensors.has_lumen:
            add_topic = app_config_access.mqtt_publisher_config.lumen_topic
            sensor_data = str(sensor_access.get_lumen())
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.color and available_sensors.has_color:
            add_topic = app_config_access.mqtt_publisher_config.color_topic
            sensor_data = str(sensor_access.get_ems_colors(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.ultra_violet and available_sensors.has_ultra_violet:
            add_topic = app_config_access.mqtt_publisher_config.ultra_violet_topic
            sensor_data = str(sensor_access.get_ultra_violet(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.accelerometer and available_sensors.has_acc:
            add_topic = app_config_access.mqtt_publisher_config.accelerometer_topic
            sensor_data = str(sensor_access.get_accelerometer_xyz(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.magnetometer and available_sensors.has_mag:
            add_topic = app_config_access.mqtt_publisher_config.magnetometer_topic
            sensor_data = str(sensor_access.get_magnetometer_xyz(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        if app_config_access.mqtt_publisher_config.gyroscope and available_sensors.has_gyro:
            add_topic = app_config_access.mqtt_publisher_config.gyroscope_topic
            sensor_data = str(sensor_access.get_gyroscope_xyz(return_as_dictionary=True))
            publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})

        return publish_msgs
    except Exception as error:
        logger.primary_logger.error("MQTT Publisher Sensor Get Failure: " + str(error))
        add_topic = "Getting Sensor Data Failed for " + app_config_access.mqtt_publisher_config.mqtt_base_topic
        sensor_data = "Error"
        publish_msgs.append({"topic": add_topic, "payload": sensor_data, "qos": mqtt_publisher_qos})
        return publish_msgs
