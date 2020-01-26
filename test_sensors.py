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
import logging
import requests
from operations_modules.config_primary import CreatePrimaryConfiguration
from operations_modules.config_installed_sensors import get_installed_sensors_from_file
from operations_modules.app_cached_variables import command_data_separator

logging.captureWarnings(True)
current_config = CreatePrimaryConfiguration()
installed_sensors = get_installed_sensors_from_file()
display_text_on_remote_sensor_command = "DisplayText"


def get_sensor_reading(command):
    """ Returns requested local sensor data (based on the provided command data). """
    url = "https://127.0.0.1:10065/" + command
    tmp_return_data = requests.get(url=url, verify=False)
    return tmp_return_data.text


def get_interval_sensor_data():
    """ Returns local sensor Interval data. """
    url = "https://127.0.0.1:10065/GetIntervalSensorReadings"
    tmp_return_data = requests.get(url=url, verify=False)
    return_data = tmp_return_data.text.split(command_data_separator)
    return [str(return_data[0]), str(return_data[1])]


def display_text_on_sensor(text_message):
    """ Displays text on local sensors display (if any). """
    url = "https://127.0.0.1:10065/DisplayText"
    requests.put(url=url, data={'command_data': text_message}, verify=False)


interval_data = get_interval_sensor_data()
sensor_types = interval_data[0].split(",")
sensor_readings = interval_data[1].split(",")

print("*** Configuration Print || 0 = Disabled | 1 = Enabled ***\n" +
      "Enable Debug Logging: " + str(current_config.enable_debug_logging) +
      "  ||  Record Interval Sensors to SQL Database: " + str(current_config.enable_interval_recording) +
      "\n  Record Trigger Sensors to SQL Database: " + str(current_config.enable_trigger_recording) +
      "\n  Seconds between Interval recordings: " + str(current_config.sleep_duration_interval))
print("\n  Enable Custom Temperature Offset: " + str(current_config.enable_custom_temp) +
      " || Current Temperature Offset: " + str(current_config.temperature_offset))
print("\n*** Sensor Data test ***")
str_message = ""
count = 0
while count < len(sensor_types):
    str_message = str_message + \
                  str(sensor_types[count]) + ": " + \
                  str(sensor_readings[count] + " | ")

    if count is 1 or count is 4 or count is 6 or count is 8 or count is 11 or count is 14 or count == len(sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

if installed_sensors.has_display:
    print("\nShowing Temperature on Installed Display, Please Wait ...")
    cpu_temp = float(get_sensor_reading(display_text_on_remote_sensor_command))
    display_text_on_sensor(str(round(cpu_temp, 2)) + "c")

print("\nTesting Complete")
