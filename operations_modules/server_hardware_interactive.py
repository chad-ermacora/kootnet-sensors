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
from operations_modules.app_generic_classes import CreateMonitoredThread
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules.sensor_access import sensors_direct


def start_hardware_interactive_server():
    """ Starts a Monitored Thread of the Hardware Interactive Server """
    thread_function(_hardware_interactive_server)


def _hardware_interactive_server():
    """ If available starts additional hardware Interaction thread. """
    while not app_config_access.installed_sensors.raspberry_pi_sense_hat:
        sleep(15)
    text_name = "Sensor Interactive Service"
    function = sensors_direct.rp_sense_hat_a.start_joy_stick_commands
    app_cached_variables.interactive_sensor_thread = CreateMonitoredThread(function, thread_name=text_name)
