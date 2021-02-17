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
sensor_replacement_dic = app_config_access.mqtt_publisher_config.get_mqtt_replacements_dictionary()


def start_mqtt_publisher_server():
    text_name = "MQTT Publisher"
    function = _mqtt_publisher_server
    app_cached_variables.mqtt_publisher_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
        logger.primary_logger.debug("MQTT Publisher Disabled in Configuration")
        app_cached_variables.mqtt_publisher_thread.current_state = "Disabled"


def _mqtt_publisher_server():
    """ Starts MQTT Publisher and runs based on settings found in the MQTT Publisher configuration file. """
    selected_mqtt_send_format = app_config_access.mqtt_publisher_config.selected_mqtt_send_format
    mqtt_send_format_kootnet = app_config_access.mqtt_publisher_config.mqtt_send_format_kootnet
    mqtt_send_format_individual_topics = app_config_access.mqtt_publisher_config.mqtt_send_format_individual_topics
    mqtt_send_format_custom_string = app_config_access.mqtt_publisher_config.mqtt_send_format_custom_string

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
        if selected_mqtt_send_format == mqtt_send_format_kootnet or \
                selected_mqtt_send_format == mqtt_send_format_custom_string:
            try:
                topic = app_config_access.mqtt_publisher_config.mqtt_base_topic[:-1]
                publish.single(topic=topic, payload=str(publish_msgs), qos=mqtt_publisher_qos,
                               hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
            except Exception as error:
                logger.network_logger.error("MQTT Publisher Kootnet Sensors Format Send Failure: " + str(error))
        elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
            try:
                publish.multiple(publish_msgs, hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
            except Exception as error:
                logger.network_logger.error("MQTT Publisher Topic Per Sensor Send Failure: " + str(error))

        sleep_fraction_interval = 3
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
    selected_mqtt_send_format = app_config_access.mqtt_publisher_config.selected_mqtt_send_format
    mqtt_send_format_kootnet = app_config_access.mqtt_publisher_config.mqtt_send_format_kootnet
    mqtt_send_format_individual_topics = app_config_access.mqtt_publisher_config.mqtt_send_format_individual_topics
    mqtt_send_format_custom_string = app_config_access.mqtt_publisher_config.mqtt_send_format_custom_string

    # Default publish_msgs used when app_config_access.mqtt_publisher_config.mqtt_send_format_custom_string
    publish_msgs = app_config_access.mqtt_publisher_config.mqtt_custom_data_string
    if selected_mqtt_send_format == mqtt_send_format_kootnet:
        publish_msgs = {}
    elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
        publish_msgs = []

    try:
        if app_config_access.mqtt_publisher_config.sensor_date_time:
            sensor_function = app_config_access.mqtt_publisher_config.get_custom_utc0_datetime
            add_topic = app_config_access.mqtt_publisher_config.sensor_date_time_topic
            if selected_mqtt_send_format == mqtt_send_format_custom_string:
                add_topic = database_variables.all_tables_datetime
            publish_msgs = _add_sensor_to_publish_msgs(sensor_function, publish_msgs, optional_topic=add_topic)

        if app_config_access.mqtt_publisher_config.sensor_host_name:
            sensor_function = sensor_access.get_hostname
            add_topic = app_config_access.mqtt_publisher_config.sensor_host_name_topic
            if selected_mqtt_send_format == mqtt_send_format_custom_string:
                add_topic = database_variables.sensor_name
            publish_msgs = _add_sensor_to_publish_msgs(sensor_function, publish_msgs, optional_topic=add_topic)

        if app_config_access.mqtt_publisher_config.sensor_ip:
            sensor_function = sensor_access.get_ip
            add_topic = app_config_access.mqtt_publisher_config.sensor_ip_topic
            if selected_mqtt_send_format == mqtt_send_format_custom_string:
                add_topic = database_variables.ip
            publish_msgs = _add_sensor_to_publish_msgs(sensor_function, publish_msgs, optional_topic=add_topic)

        if app_config_access.mqtt_publisher_config.sensor_uptime:
            sensor_function = sensor_access.get_uptime_minutes
            add_topic = app_config_access.mqtt_publisher_config.sensor_uptime_topic
            if selected_mqtt_send_format == mqtt_send_format_custom_string:
                add_topic = database_variables.sensor_uptime
            publish_msgs = _add_sensor_to_publish_msgs(sensor_function, publish_msgs, optional_topic=add_topic)

        if app_config_access.mqtt_publisher_config.system_temperature:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_cpu_temperature, publish_msgs)

        if app_config_access.mqtt_publisher_config.env_temperature:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_environment_temperature, publish_msgs)

        if app_config_access.mqtt_publisher_config.pressure:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_pressure, publish_msgs)

        if app_config_access.mqtt_publisher_config.altitude:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_altitude, publish_msgs)

        if app_config_access.mqtt_publisher_config.humidity:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_humidity, publish_msgs)

        if app_config_access.mqtt_publisher_config.distance:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_distance, publish_msgs)

        if app_config_access.mqtt_publisher_config.gas:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_gas, publish_msgs)

        if app_config_access.mqtt_publisher_config.particulate_matter:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_particulate_matter, publish_msgs)

        if app_config_access.mqtt_publisher_config.lumen:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_lumen, publish_msgs)

        if app_config_access.mqtt_publisher_config.color:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_ems_colors, publish_msgs)

        if app_config_access.mqtt_publisher_config.ultra_violet:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_ultra_violet, publish_msgs)

        if app_config_access.mqtt_publisher_config.accelerometer:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_accelerometer_xyz, publish_msgs)

        if app_config_access.mqtt_publisher_config.magnetometer:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_magnetometer_xyz, publish_msgs)

        if app_config_access.mqtt_publisher_config.gyroscope:
            publish_msgs = _add_sensor_to_publish_msgs(sensor_access.get_gyroscope_xyz, publish_msgs)
    except Exception as error:
        log_msg = "MQTT Publisher Sensor Get Failure on " + mqtt_base_topic + ": " + str(error)
        logger.network_logger.error(log_msg)
        add_topic = "Error"
        if selected_mqtt_send_format == mqtt_send_format_kootnet:
            publish_msgs[add_topic] = log_msg
        elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
            publish_msgs.append({"topic": add_topic, "payload": log_msg, "qos": mqtt_publisher_qos})
    return publish_msgs


def _add_sensor_to_publish_msgs(sensor_function, pub_msgs, optional_topic=None):
    selected_mqtt_send_format = app_config_access.mqtt_publisher_config.selected_mqtt_send_format
    mqtt_send_format_kootnet = app_config_access.mqtt_publisher_config.mqtt_send_format_kootnet
    mqtt_send_format_individual_topics = app_config_access.mqtt_publisher_config.mqtt_send_format_individual_topics
    mqtt_send_format_custom_string = app_config_access.mqtt_publisher_config.mqtt_send_format_custom_string
    sensor_data = sensor_function()

    if sensor_data is not None:
        try:
            if optional_topic is None:
                for db_variable_name, reading in sensor_data.items():
                    if selected_mqtt_send_format == mqtt_send_format_kootnet:
                        pub_msgs[db_variable_name] = reading
                    elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
                        add_topic = mqtt_base_topic + _get_database_variable_to_mqtt_publisher_topic()[db_variable_name]
                        pub_msgs.append({"topic": add_topic, "payload": str(reading), "qos": mqtt_publisher_qos})
                    elif selected_mqtt_send_format == mqtt_send_format_custom_string:
                        pub_msgs = pub_msgs.replace(sensor_replacement_dic[db_variable_name], str(reading))
            else:
                if selected_mqtt_send_format == mqtt_send_format_kootnet:
                    pub_msgs[optional_topic] = sensor_data
                elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
                    optional_topic = mqtt_base_topic + optional_topic
                    pub_msgs.append({"topic": optional_topic, "payload": str(sensor_data), "qos": mqtt_publisher_qos})
                elif selected_mqtt_send_format == mqtt_send_format_custom_string:
                    pub_msgs = pub_msgs.replace(sensor_replacement_dic[optional_topic], str(sensor_data))
        except Exception as error:
            logger.network_logger.error("MQTT Publisher - Adding Sensor to Publish Msg Failed: " + str(error))
    return pub_msgs


def _get_database_variable_to_mqtt_publisher_topic():
    mqtt_publisher_config = app_config_access.mqtt_publisher_config
    return {
        database_variables.sensor_uptime: mqtt_publisher_config.sensor_uptime_topic,
        database_variables.system_temperature: mqtt_publisher_config.system_temperature_topic,
        database_variables.env_temperature: mqtt_publisher_config.env_temperature_topic,
        database_variables.pressure: mqtt_publisher_config.pressure_topic,
        database_variables.altitude: mqtt_publisher_config.altitude_topic,
        database_variables.humidity: mqtt_publisher_config.humidity_topic,
        database_variables.distance: mqtt_publisher_config.distance_topic,
        database_variables.gas_resistance_index: mqtt_publisher_config.gas_resistance_index_topic,
        database_variables.gas_oxidising: mqtt_publisher_config.gas_oxidising_topic,
        database_variables.gas_reducing: mqtt_publisher_config.gas_reducing_topic,
        database_variables.gas_nh3: mqtt_publisher_config.gas_nh3_topic,
        database_variables.particulate_matter_1: mqtt_publisher_config.particulate_matter_1_topic,
        database_variables.particulate_matter_2_5: mqtt_publisher_config.particulate_matter_2_5_topic,
        database_variables.particulate_matter_4: mqtt_publisher_config.particulate_matter_4_topic,
        database_variables.particulate_matter_10: mqtt_publisher_config.particulate_matter_10_topic,
        database_variables.lumen: mqtt_publisher_config.lumen_topic,
        database_variables.red: mqtt_publisher_config.color_red_topic,
        database_variables.orange: mqtt_publisher_config.color_orange_topic,
        database_variables.yellow: mqtt_publisher_config.color_yellow_topic,
        database_variables.green: mqtt_publisher_config.color_green_topic,
        database_variables.blue: mqtt_publisher_config.color_blue_topic,
        database_variables.violet: mqtt_publisher_config.color_violet_topic,
        database_variables.ultra_violet_index: mqtt_publisher_config.ultra_violet_index_topic,
        database_variables.ultra_violet_a: mqtt_publisher_config.ultra_violet_a_topic,
        database_variables.ultra_violet_b: mqtt_publisher_config.ultra_violet_b_topic,
        database_variables.acc_x: mqtt_publisher_config.accelerometer_x_topic,
        database_variables.acc_y: mqtt_publisher_config.accelerometer_y_topic,
        database_variables.acc_z: mqtt_publisher_config.accelerometer_z_topic,
        database_variables.mag_x: mqtt_publisher_config.magnetometer_x_topic,
        database_variables.mag_y: mqtt_publisher_config.magnetometer_y_topic,
        database_variables.mag_z: mqtt_publisher_config.magnetometer_z_topic,
        database_variables.gyro_x: mqtt_publisher_config.gyroscope_x_topic,
        database_variables.gyro_y: mqtt_publisher_config.gyroscope_y_topic,
        database_variables.gyro_z: mqtt_publisher_config.gyroscope_z_topic,
    }
