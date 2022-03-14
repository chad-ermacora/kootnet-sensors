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
from operations_modules.app_generic_classes import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules import system_access
from sensor_modules import sensor_access

db_v = app_cached_variables.database_variables
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
    while not app_config_access.mqtt_publisher_config.enable_mqtt_publisher:
        sleep(1)
        app_cached_variables.mqtt_publisher_thread.current_state = "Disabled"
        sleep(10)
    app_cached_variables.mqtt_publisher_thread.current_state = "Running"
    app_cached_variables.restart_mqtt_publisher_thread = False
    if app_config_access.mqtt_broker_config.enable_mqtt_broker:
        # Sleep a few seconds to allow the local broker to start first
        sleep(3)

    while not app_cached_variables.restart_mqtt_publisher_thread:
        _publish_mqtt_message()

        sleep_fraction_interval = 3
        sleep_total = 0
        seconds_to_wait = app_config_access.mqtt_publisher_config.seconds_to_wait
        if 0 < seconds_to_wait < 3:
            sleep_fraction_interval = seconds_to_wait
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


def _publish_mqtt_message():
    mqtt_pc = app_config_access.mqtt_publisher_config
    mqtt_base_topic = app_config_access.mqtt_publisher_config.mqtt_base_topic
    mqtt_publisher_qos = app_config_access.mqtt_publisher_config.mqtt_publisher_qos

    selected_mqtt_send_format = app_config_access.mqtt_publisher_config.selected_mqtt_send_format
    mqtt_send_format_kootnet = app_config_access.mqtt_publisher_config.mqtt_send_format_kootnet
    mqtt_send_format_individual_topics = app_config_access.mqtt_publisher_config.mqtt_send_format_individual_topics
    mqtt_send_format_custom_string = app_config_access.mqtt_publisher_config.mqtt_send_format_custom_string

    # MQTT Publisher enabled sensors & get sensor reading functions lists
    sensors_enabled_list = [
        mqtt_pc.sensor_date_time, mqtt_pc.sensor_host_name, mqtt_pc.sensor_ip, mqtt_pc.sensor_uptime,
        mqtt_pc.gps_latitude, mqtt_pc.gps_longitude, mqtt_pc.system_temperature, mqtt_pc.env_temperature,
        mqtt_pc.pressure, mqtt_pc.altitude, mqtt_pc.humidity, mqtt_pc.dew_point, mqtt_pc.distance, mqtt_pc.gas,
        mqtt_pc.particulate_matter, mqtt_pc.lumen, mqtt_pc.color, mqtt_pc.ultra_violet, mqtt_pc.accelerometer,
        mqtt_pc.magnetometer, mqtt_pc.gyroscope
    ]
    sensors_function_list = [
        _get_mqtt_formatted_datetime, _get_hostname, _get_ip, system_access.get_uptime_minutes, _get_gps_latitude,
        _get_gps_longitude, sensor_access.get_cpu_temperature, sensor_access.get_environment_temperature,
        sensor_access.get_pressure, sensor_access.get_altitude, sensor_access.get_humidity, sensor_access.get_dew_point,
        sensor_access.get_distance, sensor_access.get_gas, sensor_access.get_particulate_matter,
        sensor_access.get_lumen, sensor_access.get_ems_colors, sensor_access.get_ultra_violet,
        sensor_access.get_accelerometer_xyz, sensor_access.get_magnetometer_xyz, sensor_access.get_gyroscope_xyz
    ]

    pub_msgs = {}
    db_vars_to_mqtt_pub = {}
    if selected_mqtt_send_format == mqtt_send_format_individual_topics:
        pub_msgs = []
        db_vars_to_mqtt_pub = _get_database_variable_to_mqtt_publisher_topic()
    elif selected_mqtt_send_format == mqtt_send_format_custom_string:
        pub_msgs = app_config_access.mqtt_publisher_config.mqtt_custom_data_string

    try:
        for sensor_enabled, sensor_function in zip(sensors_enabled_list, sensors_function_list):
            if sensor_enabled:
                sensor_data = sensor_function()
                if sensor_data is not None:
                    for db_variable_name, reading in sensor_data.items():
                        if selected_mqtt_send_format == mqtt_send_format_kootnet:
                            pub_msgs[db_variable_name] = reading
                        elif selected_mqtt_send_format == mqtt_send_format_individual_topics:
                            add_topic = mqtt_base_topic + str(db_vars_to_mqtt_pub[db_variable_name])
                            pub_msgs.append({"topic": add_topic, "payload": str(reading), "qos": mqtt_publisher_qos})
                        elif selected_mqtt_send_format == mqtt_send_format_custom_string:
                            pub_msgs = pub_msgs.replace(str(sensor_replacement_dic[db_variable_name]), str(reading))
        _send_mqtt_pub_message(pub_msgs)
    except Exception as error:
        log_msg = "MQTT Publisher - Adding Sensor to Publish Msg Failed: "
        logger.network_logger.error(log_msg + str(error))


def _send_mqtt_pub_message(publish_msgs):
    broker_address = app_config_access.mqtt_publisher_config.broker_address
    broker_server_port = app_config_access.mqtt_publisher_config.broker_server_port
    mqtt_pub_auth = _get_mqtt_publisher_auth()
    mqtt_publisher_qos = app_config_access.mqtt_publisher_config.mqtt_publisher_qos
    selected_mqtt_send_format = app_config_access.mqtt_publisher_config.selected_mqtt_send_format
    mqtt_send_format_individual_topics = app_config_access.mqtt_publisher_config.mqtt_send_format_individual_topics

    try:
        if selected_mqtt_send_format == mqtt_send_format_individual_topics:
            publish.multiple(publish_msgs, hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
        else:
            topic = app_config_access.mqtt_publisher_config.mqtt_base_topic[:-1]
            publish.single(topic=topic, payload=str(publish_msgs), qos=mqtt_publisher_qos,
                           hostname=broker_address, port=broker_server_port, auth=mqtt_pub_auth)
    except Exception as error:
        logger.network_logger.error("MQTT Publisher Send Failure: " + str(error))


def _get_mqtt_publisher_auth():
    mqtt_pub_auth = None
    try:
        if app_config_access.mqtt_publisher_config.enable_broker_auth and \
                app_config_access.mqtt_publisher_config.broker_user != "":
            user = app_config_access.mqtt_publisher_config.broker_user
            password = app_config_access.mqtt_publisher_config.broker_password
            if password == "":
                mqtt_pub_auth = {"username": user, "password": None}
            else:
                mqtt_pub_auth = {"username": user, "password": password}
    except Exception as error:
        logger.network_logger.warning("MQTT Publisher Get Authorization Failure: " + str(error))
    return mqtt_pub_auth


def _get_database_variable_to_mqtt_publisher_topic():
    mqtt_publisher_config = app_config_access.mqtt_publisher_config
    sensor_date_time_topic = app_config_access.mqtt_publisher_config.sensor_date_time_topic
    return {
        sensor_date_time_topic: sensor_date_time_topic,
        db_v.sensor_name: mqtt_publisher_config.sensor_host_name_topic,
        db_v.ip: mqtt_publisher_config.sensor_ip_topic,
        db_v.latitude: mqtt_publisher_config.gps_latitude_topic,
        db_v.longitude: mqtt_publisher_config.gps_longitude_topic,
        db_v.sensor_uptime: mqtt_publisher_config.sensor_uptime_topic,
        db_v.system_temperature: mqtt_publisher_config.system_temperature_topic,
        db_v.env_temperature: mqtt_publisher_config.env_temperature_topic,
        db_v.dew_point: mqtt_publisher_config.dew_point_topic,
        db_v.pressure: mqtt_publisher_config.pressure_topic,
        db_v.altitude: mqtt_publisher_config.altitude_topic,
        db_v.humidity: mqtt_publisher_config.humidity_topic,
        db_v.distance: mqtt_publisher_config.distance_topic,
        db_v.gas_resistance_index: mqtt_publisher_config.gas_resistance_index_topic,
        db_v.gas_oxidising: mqtt_publisher_config.gas_oxidising_topic,
        db_v.gas_reducing: mqtt_publisher_config.gas_reducing_topic,
        db_v.gas_nh3: mqtt_publisher_config.gas_nh3_topic,
        db_v.particulate_matter_1: mqtt_publisher_config.particulate_matter_1_topic,
        db_v.particulate_matter_2_5: mqtt_publisher_config.particulate_matter_2_5_topic,
        db_v.particulate_matter_4: mqtt_publisher_config.particulate_matter_4_topic,
        db_v.particulate_matter_10: mqtt_publisher_config.particulate_matter_10_topic,
        db_v.lumen: mqtt_publisher_config.lumen_topic,
        db_v.red: mqtt_publisher_config.color_red_topic,
        db_v.orange: mqtt_publisher_config.color_orange_topic,
        db_v.yellow: mqtt_publisher_config.color_yellow_topic,
        db_v.green: mqtt_publisher_config.color_green_topic,
        db_v.blue: mqtt_publisher_config.color_blue_topic,
        db_v.violet: mqtt_publisher_config.color_violet_topic,
        db_v.ultra_violet_index: mqtt_publisher_config.ultra_violet_index_topic,
        db_v.ultra_violet_a: mqtt_publisher_config.ultra_violet_a_topic,
        db_v.ultra_violet_b: mqtt_publisher_config.ultra_violet_b_topic,
        db_v.acc_x: mqtt_publisher_config.accelerometer_x_topic,
        db_v.acc_y: mqtt_publisher_config.accelerometer_y_topic,
        db_v.acc_z: mqtt_publisher_config.accelerometer_z_topic,
        db_v.mag_x: mqtt_publisher_config.magnetometer_x_topic,
        db_v.mag_y: mqtt_publisher_config.magnetometer_y_topic,
        db_v.mag_z: mqtt_publisher_config.magnetometer_z_topic,
        db_v.gyro_x: mqtt_publisher_config.gyroscope_x_topic,
        db_v.gyro_y: mqtt_publisher_config.gyroscope_y_topic,
        db_v.gyro_z: mqtt_publisher_config.gyroscope_z_topic
    }


def _get_mqtt_formatted_datetime():
    date_time_data = app_config_access.mqtt_publisher_config.get_custom_utc0_datetime()
    return {app_config_access.mqtt_publisher_config.sensor_date_time_topic: date_time_data}


def _get_ip():
    return {db_v.ip: app_cached_variables.ip}


def _get_hostname():
    return {db_v.sensor_name: app_cached_variables.hostname}


def _get_gps_latitude():
    gps_data = sensor_access.get_gps_data()
    if gps_data is not None:
        return {db_v.latitude: gps_data[db_v.latitude]}
    return None


def _get_gps_longitude():
    gps_data = sensor_access.get_gps_data()
    if gps_data is not None:
        return {db_v.longitude: gps_data[db_v.longitude]}
    return None
