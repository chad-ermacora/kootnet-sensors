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
from extras.python_modules.paho.mqtt import client as mqtt
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from sensor_recording_modules.recording_interval import available_sensors


def start_mqtt_publisher_server():
    if app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
        text_name = "MQTT Publisher"
        function = _mqtt_publisher_server
        app_cached_variables.mqtt_publisher_thread = CreateMonitoredThread(function, thread_name=text_name)
    else:
        logger.primary_logger.debug("MQTT Publisher Disabled in Configuration")


def _mqtt_publisher_server():
    """ Starts MQTT Publisher and runs based on settings found in the MQTT Publisher configuration file. """
    app_cached_variables.restart_mqtt_publisher_thread = False
    if app_config_access.mqtt_broker_config.enable_mqtt_broker:
        # Sleep a few seconds to allow the local broker to start first
        sleep(3)
    broker_address = app_config_access.mqtt_publisher_config.broker_address
    broker_server_port = app_config_access.mqtt_publisher_config.broker_server_port
    client = mqtt.Client()

    not_connected = True
    max_tries_log = 0
    while not_connected and not app_cached_variables.restart_mqtt_publisher_thread:
        try:
            if app_config_access.mqtt_publisher_config.enable_broker_auth and \
                    app_config_access.mqtt_publisher_config.broker_user != "":
                user = app_config_access.mqtt_publisher_config.broker_user
                password = app_config_access.mqtt_publisher_config.broker_password
                if password != "":
                    client.username_pw_set(user, password=password)
                else:
                    client.username_pw_set(user)
            mqtt_return_code = client.connect(broker_address, broker_server_port)
            logger.network_logger.debug("MQTT Publisher Connection Code: " + str(mqtt_return_code))
            client.loop_start()
            not_connected = False
            log_msg = " -- MQTT Publisher Started publishing to "
            logger.primary_logger.info(log_msg + str(app_config_access.mqtt_publisher_config.broker_address))
        except Exception as error:
            seconds_to_wait = 10
            if max_tries_log < 5:
                logger.network_logger.warning("MQTT Publisher Client Connection Failure: " + str(error))
            elif max_tries_log == 5:
                log_msg1 = "MQTT Publisher Client Connection has failed 5 times in a row. "
                logger.primary_logger.error(log_msg1 + "Attempts limited to every 5 minutes. Logging Disabled.")
            if max_tries_log >= 5:
                logger.network_logger.debug("MQTT Publisher Connection Failure # " + str(max_tries_log))
                seconds_to_wait = 300
            max_tries_log += 1

            sleep_fraction_interval = 5
            sleep_total = 0
            while sleep_total < seconds_to_wait and not app_cached_variables.restart_mqtt_publisher_thread:
                sleep(sleep_fraction_interval)
                sleep_total += sleep_fraction_interval

    while not app_cached_variables.restart_mqtt_publisher_thread:
        mqtt_publisher_qos = app_config_access.mqtt_publisher_config.mqtt_publisher_qos
        try:
            if app_config_access.mqtt_publisher_config.sensor_uptime:
                client.publish(app_config_access.mqtt_publisher_config.sensor_uptime_topic,
                               payload=str(sensor_access.get_uptime_minutes()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.system_temperature and available_sensors.has_cpu_temperature:
                client.publish(app_config_access.mqtt_publisher_config.system_temperature_topic,
                               payload=str(sensor_access.get_cpu_temperature()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.env_temperature and available_sensors.has_env_temperature:
                client.publish(app_config_access.mqtt_publisher_config.env_temperature_topic,
                               payload=str(sensor_access.get_sensor_temperature()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.pressure and available_sensors.has_pressure:
                client.publish(app_config_access.mqtt_publisher_config.pressure_topic,
                               payload=str(sensor_access.get_pressure()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.altitude and available_sensors.has_altitude:
                client.publish(app_config_access.mqtt_publisher_config.altitude_topic,
                               payload=str(sensor_access.get_altitude()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.humidity and available_sensors.has_humidity:
                client.publish(app_config_access.mqtt_publisher_config.humidity_topic,
                               payload=str(sensor_access.get_humidity()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.distance and available_sensors.has_distance:
                client.publish(app_config_access.mqtt_publisher_config.distance_topic,
                               payload=str(sensor_access.get_distance()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.gas and available_sensors.has_gas:
                client.publish(app_config_access.mqtt_publisher_config.gas_topic,
                               payload=_readings_to_text(sensor_access.get_gas()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.particulate_matter and available_sensors.has_particulate_matter:
                client.publish(app_config_access.mqtt_publisher_config.particulate_matter_topic,
                               payload=_readings_to_text(sensor_access.get_particulate_matter()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.lumen and available_sensors.has_lumen:
                client.publish(app_config_access.mqtt_publisher_config.lumen_topic,
                               payload=str(sensor_access.get_lumen()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.color and available_sensors.has_color:
                client.publish(app_config_access.mqtt_publisher_config.color_topic,
                               payload=_readings_to_text(sensor_access.get_ems_colors()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.ultra_violet and available_sensors.has_ultra_violet:
                client.publish(app_config_access.mqtt_publisher_config.ultra_violet_topic,
                               payload=_readings_to_text(sensor_access.get_ultra_violet()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.accelerometer and available_sensors.has_acc:
                client.publish(app_config_access.mqtt_publisher_config.accelerometer_topic,
                               payload=_readings_to_text(sensor_access.get_accelerometer_xyz()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.magnetometer and available_sensors.has_mag:
                client.publish(app_config_access.mqtt_publisher_config.magnetometer_topic,
                               payload=_readings_to_text(sensor_access.get_magnetometer_xyz()),
                               qos=mqtt_publisher_qos)
            if app_config_access.mqtt_publisher_config.gyroscope and available_sensors.has_gyro:
                client.publish(app_config_access.mqtt_publisher_config.gyroscope_topic,
                               payload=_readings_to_text(sensor_access.get_gyroscope_xyz()),
                               qos=mqtt_publisher_qos)
        except Exception as error:
            logger.primary_logger.error("MQTT Publisher Failure: " + str(error))

        sleep_fraction_interval = 5
        sleep_total = 0
        seconds_to_wait = app_config_access.mqtt_publisher_config.seconds_to_wait
        while sleep_total < seconds_to_wait and not app_cached_variables.restart_mqtt_publisher_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval
    client.disconnect(reasoncode=0)
    client.connected_flag = False
    client.disconnect_flag = True


def _readings_to_text(readings):
    return_text = ""
    if type(readings) is not list and type(readings) is not tuple:
        return str(readings)
    elif len(readings) > 0:
        for reading in readings:
            return_text += str(reading) + ","
        return_text = return_text[:-1]
    else:
        return app_cached_variables.no_sensor_present
    return return_text
