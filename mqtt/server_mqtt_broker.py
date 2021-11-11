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
from subprocess import check_output, SubprocessError
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import write_file_to_disk, thread_function
from operations_modules import app_cached_variables
from configuration_modules import app_config_access

terminal_install_mqtt_mosquitto = "apt-get update && apt-get -y install mosquitto"
terminal_enable_start_mosquitto = "systemctl enable mosquitto && systemctl start mosquitto"
terminal_disable_stop_mosquitto = "systemctl disable mosquitto && systemctl stop mosquitto"
terminal_restart_mosquitto = "systemctl restart mosquitto"


def check_mqtt_broker_server_running():
    """ If MQTT Broker server Mosquitto is running, return True else False. """
    try:
        if len(str(check_output(["pidof", "mosquitto"]))) > 2:
            return True
        return False
    except SubprocessError:
        return False
    except Exception as error:
        logger.primary_logger.warning("MQTT Broker Running Check Error: " + str(error))
        return False


def restart_mqtt_broker_server():
    """ Restarts MQTT Broker server Mosquitto's service. """
    if app_cached_variables.running_with_root:
        if check_mqtt_broker_server_running():
            logger.primary_logger.info("Restarting MQTT Broker Mosquitto")
            os.system(terminal_restart_mosquitto)
            app_cached_variables.mqtt_broker_dummy_thread.current_state = "Running"
        else:
            start_mqtt_broker_server()
    else:
        logger.primary_logger.warning("Unable to Restart MQTT Mosquitto, root required")


def stop_mqtt_broker_server():
    """ Stops MQTT Broker server Mosquitto's service. """
    if app_cached_variables.running_with_root:
        if check_mqtt_broker_server_running():
            logger.primary_logger.info("Stopping MQTT Broker Mosquitto")
            os.system(terminal_disable_stop_mosquitto)
            app_cached_variables.mqtt_broker_dummy_thread.current_state = "Stopped"
        else:
            logger.primary_logger.debug("MQTT Broker Mosquitto already Stopped")
    else:
        logger.primary_logger.warning("Unable to Stop MQTT Mosquitto, root required")


def start_mqtt_broker_server():
    """ Starts MQTT Broker server Mosquitto's service. """
    if app_config_access.mqtt_broker_config.enable_mqtt_broker:
        app_cached_variables.mqtt_broker_dummy_thread.current_state = "Starting"
        if check_mqtt_broker_server_running():
            logger.primary_logger.info(" -- Mosquitto Server already running")
            app_cached_variables.mqtt_broker_dummy_thread.current_state = "Running"
        else:
            if app_cached_variables.running_with_root:
                if os.path.isfile("/usr/sbin/mosquitto") or os.path.isfile("/usr/bin/mosquitto"):
                    os.system(terminal_enable_start_mosquitto)
                    logger.primary_logger.info(" -- Starting Mosquitto Server")
                    app_cached_variables.mqtt_broker_dummy_thread.current_state = "Running"
                else:
                    logger.primary_logger.info("MQTT Mosquitto Broker not installed, attempting install")
                    app_cached_variables.mqtt_broker_dummy_thread.current_state = "Installing"
                    thread_function(_start_mosquitto_install_worker)
            else:
                logger.primary_logger.warning("Unable to Start MQTT Broker Mosquitto, root required")
                app_cached_variables.mqtt_broker_dummy_thread.current_state = "NA"
    else:
        logger.primary_logger.debug("MQTT Broker Disabled in Configuration")


def _start_mosquitto_install_worker():
    os.system(terminal_install_mqtt_mosquitto)
    if not os.path.isfile(file_locations.mosquitto_configuration):
        default_mqtt_config = "listener 1883\nallow_anonymous true"
        write_file_to_disk(file_locations.mosquitto_configuration, default_mqtt_config)
    if os.path.isfile("/usr/sbin/mosquitto") or os.path.isfile("/usr/bin/mosquitto"):
        logger.primary_logger.info("MQTT Mosquitto Broker has been installed")
        os.system(terminal_enable_start_mosquitto)
        logger.primary_logger.info(" -- Starting Mosquitto Server")
        app_cached_variables.mqtt_broker_dummy_thread.current_state = "Running"
    else:
        logger.primary_logger.error("MQTT Mosquitto did not install - Unable to start MQTT Broker")
        app_cached_variables.mqtt_broker_dummy_thread.current_state = "Install Error"
