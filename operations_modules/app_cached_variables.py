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
from platform import system
from queue import Queue
from operations_modules.sqlite_database import CreateDatabaseVariables

# Static variables
current_platform = system()
database_variables = CreateDatabaseVariables()
command_data_separator = "[new_data_section]"
no_sensor_present = "NoSensor"

# Running "Service" Threads
http_server_thread = None
interval_recording_thread = None
mini_display_thread = None
interactive_sensor_thread = None
weather_underground_thread = None
luftdaten_thread = None
open_sense_map_thread = None

# Possible Trigger "High / Low" States
normal_state = "Normal"
low_state = "Low"
high_state = "High"

state_sensor_uptime = normal_state
state_cpu_temp = normal_state
state_env_temp = normal_state
state_pressure = normal_state
state_altitude = normal_state
state_humidity = normal_state
state_distance = normal_state
state_lumen = normal_state
state_visible_ems = normal_state
state_accelerometer = normal_state
state_magnetometer = normal_state
state_gyroscope = normal_state

# Running Trigger Recording Threads
trigger_thread_sensor_uptime = None
trigger_thread_cpu_temp = None
trigger_thread_env_temp = None
trigger_thread_pressure = None
trigger_thread_altitude = None
trigger_thread_humidity = None
trigger_thread_distance = None
trigger_thread_lumen = None
trigger_thread_visible_ems = None
trigger_thread_accelerometer = None
trigger_thread_magnetometer = None
trigger_thread_gyroscope = None

# This file is updated with variables at runtime.
# This helps lessen disk reads by caching commonly used variables
program_last_updated = ""
reboot_count = ""
total_ram_memory = 0.0
total_ram_memory_size_type = " MB"

operating_system_name = ""
hostname = ""
ip = ""
ip_subnet = ""
gateway = ""
dns1 = ""
dns2 = ""

wifi_country_code = ""
wifi_ssid = ""
wifi_security_type = ""
wifi_psk = ""

# Login to remote sensors (Used primarily in Sensor Control)
http_login = ""
http_password = ""

# Used to get data from multiple remote sensors at the "same" time.
flask_return_data_queue = Queue()
data_queue = Queue()
data_queue2 = Queue()
data_queue3 = Queue()

# Download Sensor SQL Database in a zip placeholder
sensor_database_zipped = b''

# Sensor Control Download placeholders
sc_reports_zip_name = ""
sc_logs_zip_name = ""
sc_databases_zip_name = ""
sc_big_zip_name = ""
sc_databases_zip_in_memory = False
sc_big_zip_in_memory = False
sc_in_memory_zip = b''
