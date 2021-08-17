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
import requests
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules.software_version import version
from configuration_modules import app_config_access
from sensor_modules import sensor_access

previous_installed_sensors = ""
previous_primary_logs = ""
previous_network_logs = ""
previous_sensors_logs = ""


class CreateCheckinServer:
    def __init__(self):
        logger.primary_logger.debug(" -- Sensor CheckIns Started")
        app_cached_variables.restart_sensor_checkin_thread = False

        if app_config_access.checkin_config.enable_checkin:
            # Sleep delay to allow Cached Sensor Name & IP to populate as well as important logs
            sleep(15)
        else:
            sleep(1)
            app_cached_variables.sensor_checkin_thread.current_state = "Disabled"
            while not app_config_access.checkin_config.enable_checkin:
                sleep(10)

        while not app_cached_variables.restart_sensor_checkin_thread:
            try:
                url = "https://" + app_config_access.checkin_config.checkin_url + "/SensorCheckin"
                data = _get_sensor_checkin_data()
                requests.post(url=url, timeout=10, verify=False, data=data)
            except Exception as error:
                logger.network_logger.debug("Failed to send Checkin ID: " + str(error))
            sleep_duration = app_config_access.checkin_config.checkin_wait_in_hours * 60 * 60
            sleep_total = 0
            while sleep_total < sleep_duration and not app_cached_variables.restart_sensor_checkin_thread:
                sleep(5)
                sleep_total += 5


def start_sensor_checkins():
    text_name = "Sensor Checkins"
    function = CreateCheckinServer
    app_cached_variables.sensor_checkin_thread = CreateMonitoredThread(function, thread_name=text_name)


def _get_sensor_checkin_data():
    try:
        sensor_checkin_data = {"checkin_id": app_config_access.primary_config.sensor_id,
                               "sensor_name": _get_sensor_name(),
                               "ip_address": _get_ip_address(),
                               "program_version": _get_program_version(),
                               "sensor_uptime": _get_sensor_uptime(),
                               "installed_sensors": _get_installed_sensors(),
                               "primary_log": _get_primary_log(),
                               "network_log": _get_network_log(),
                               "sensor_log": _get_sensors_log()}
    except Exception as error:
        logger.primary_logger.error("Sensor CheckIns: " + str(error))
        sensor_checkin_data = {"Error": str(error)}
    return sensor_checkin_data


def _get_sensor_name():
    if app_config_access.checkin_config.send_sensor_name:
        return app_cached_variables.hostname
    return ""


def _get_ip_address():
    if app_config_access.checkin_config.send_ip:
        return app_cached_variables.ip
    return ""


def _get_sensor_uptime():
    if app_config_access.checkin_config.send_system_uptime:
        return sensor_access.get_uptime_minutes()
    return ""


def _get_program_version():
    if app_config_access.checkin_config.send_program_version:
        return version
    return ""


def _get_installed_sensors():
    if app_config_access.checkin_config.send_installed_sensors:
        global previous_installed_sensors

        installed_sensors = app_config_access.installed_sensors.get_installed_names_str()
        if installed_sensors == previous_installed_sensors:
            return ""

        previous_installed_sensors = installed_sensors
        return installed_sensors
    return ""


def _get_primary_log():
    if app_config_access.checkin_config.send_primary_log:
        global previous_primary_logs

        max_log_lines = app_config_access.checkin_config.max_log_lines_to_send
        primary_logs = logger.get_sensor_log(file_locations.primary_log, max_lines=max_log_lines)
        if primary_logs == previous_primary_logs:
            return ""

        previous_primary_logs = primary_logs
        return primary_logs
    return ""


def _get_network_log():
    if app_config_access.checkin_config.send_network_log:
        global previous_network_logs

        max_log_lines = app_config_access.checkin_config.max_log_lines_to_send
        network_logs = logger.get_sensor_log(file_locations.network_log, max_lines=max_log_lines)
        if network_logs == previous_network_logs:
            return ""

        previous_network_logs = network_logs
        return network_logs
    return ""


def _get_sensors_log():
    if app_config_access.checkin_config.send_sensors_log:
        global previous_sensors_logs

        max_log_lines = app_config_access.checkin_config.max_log_lines_to_send
        sensors_logs = logger.get_sensor_log(file_locations.sensors_log, max_lines=max_log_lines)
        if sensors_logs == previous_sensors_logs:
            return ""

        previous_sensors_logs = sensors_logs
        return sensors_logs
    return ""
