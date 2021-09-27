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
import psutil
import time
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables import database_variables as db_v, current_platform, bash_commands


def get_ram_space(return_type=0):
    """
    return_type options: 0 = Free Space, 1 = Used Space, 2 = Total Space, 3 = Percent Space Used
    Default option = 0, all returns are in GB(s)
    """
    ram_space = None
    try:
        if return_type == 0:
            ram_space = psutil.virtual_memory().free
        elif return_type == 1:
            ram_space = psutil.virtual_memory().used
        elif return_type == 2:
            ram_space = app_cached_variables.total_ram_memory
        elif return_type == 3:
            ram_space = psutil.virtual_memory().percent

        if ram_space is not None:
            ram_space = round((ram_space / 1024 / 1024 / 1024), 3)
    except Exception as error:
        logger.primary_logger.warning("Get RAM Space: " + str(error))
    return ram_space


def get_disk_space(return_type=0):
    """
    return_type options: 0 = Free Space, 1 = Used Space, 2 = Total Space, 3 = Percent Space Used
    Default option = 0, all returns are in GB(s)
    """
    disk_space = None
    try:
        if return_type == 0:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).free
        elif return_type == 1:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).used
        elif return_type == 2:
            disk_space = app_cached_variables.total_disk_space
        elif return_type == 3:
            disk_space = psutil.disk_usage(file_locations.sensor_data_dir).percent

        if disk_space is not None:
            disk_space = round((disk_space / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.primary_logger.warning("Get Disk Space: " + str(error))
    return disk_space


def get_system_datetime():
    """ Returns System DateTime in format YYYY-MM-DD HH:MM - timezone as a String. """
    return time.strftime("%Y-%m-%d %H:%M - %Z")


def get_uptime_minutes():
    """ Returns System UpTime in Minutes as an Integer. """
    if current_platform == "Linux":
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            return {db_v.sensor_uptime: int(uptime_seconds / 60)}
        except Exception as error:
            logger.sensors_logger.warning("Get Sensor Up Time - Failed: " + str(error))
    return None


def restart_services():
    """ Reloads systemd service files & restarts KootnetSensors service. """
    thread_function(_restart_services_thread)


def _restart_services_thread():
    time.sleep(1)
    os.system(bash_commands["RestartService"])
