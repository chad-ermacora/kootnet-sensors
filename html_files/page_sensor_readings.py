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
from operations_modules import logger
from operations_modules import sensors


def get_sensor_readings():
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Sensor Readings")

    style_name_start = "<span style='color: #00ffff;'>"
    style_data_start = "<span style='background-color: #ccffcc;'>"
    style_end = "</span>"
    html_divider = "<span style='color: #ffffff;'> || </span>"
    html_colon = "<span style='color: #ffffff;'>: </span>"

    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()
    sensor_uptime = sensors.get_uptime_str()
    sensor_system_temperature = sensors.get_cpu_temperature()
    sensor_env_temperature = sensors.get_sensor_temperature()
    sensor_pressure = sensors.get_pressure()
    sensor_humidity = sensors.get_humidity()
    sensor_lumen = sensors.get_lumen()
    sensor_ems = sensors.get_ems()
    sensor_acc = sensors.get_accelerometer_xyz()
    sensor_mag = sensors.get_magnetometer_xyz()
    sensor_gyro = sensors.get_gyroscope_xyz()
    sensor_ = ""

    return_page_part1 = "<p>" + html_divider + \
                        style_name_start + "HostName" + style_end + html_colon + \
                        style_data_start + sensor_hostname + style_end + html_divider + \
                        style_name_start + "IP" + style_end + html_colon + \
                        style_data_start + sensor_ip + style_end + html_divider + \
                        style_name_start + "Sensor Uptime" + style_end + html_colon + \
                        style_data_start + sensor_uptime + style_end + html_divider + "</p>"

    return return_page_part1
