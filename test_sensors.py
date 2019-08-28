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
import urllib3
from operations_modules import app_config_access
from operations_modules import variance_checks


def get_sensor_reading(command):
    """ Returns requested sensor data (based on the provided command data). """
    url = "https://127.0.0.1:10065/" + command
    tmp_return_data = requests.get(url=url, verify=False)
    return tmp_return_data.text


def get_interval_sensor_data():
    """ Returns requested sensor data (based on the provided command data). """
    url = "https://127.0.0.1:10065/GetIntervalSensorReadings"
    tmp_return_data = requests.get(url=url, verify=False)
    return_data = tmp_return_data.text.split(app_config_access.command_data_separator)
    return [str(return_data[0]), str(return_data[1])]


def display_text_on_sensor(text_message):
    """ Returns requested sensor data (based on the provided command data). """
    url = "https://127.0.0.1:10065/DisplayText"
    requests.put(url=url, data={'command_data': text_message}, verify=False)


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sensor_commands = variance_checks.CreateSensorCommands()

interval_data = get_interval_sensor_data()
sensor_types = interval_data[0].split(",")
sensor_readings = interval_data[1].split(",")

app_config_access.current_config.custom_temperature_offset = app_config_access.current_config.temperature_offset

print("*** Configuration Print || 0 = Disabled | 1 = Enabled ***\n" +
      "Enable Debug Logging: " + str(app_config_access.current_config.enable_debug_logging) +
      "  ||  Record Interval Sensors to SQL Database: " + str(app_config_access.current_config.enable_interval_recording) +
      "\n  Record Trigger Sensors to SQL Database: " + str(app_config_access.current_config.enable_trigger_recording) +
      "\n  Seconds between Interval recordings: " + str(app_config_access.current_config.sleep_duration_interval))
print("\n  Enable Custom Temperature Offset: " + str(app_config_access.current_config.enable_custom_temp) +
      " || Current Temperature Offset: " + str(app_config_access.current_config.temperature_offset))
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

count = 0

if app_config_access.installed_sensors.has_display:
    print("\nShowing Temperature on Installed Display, Please Wait ...")
    cpu_temp = float(get_sensor_reading(sensor_commands.environmental_temp))
    display_text_on_sensor(str(round(cpu_temp, 2)) + "c")

print("\nTesting Complete")
