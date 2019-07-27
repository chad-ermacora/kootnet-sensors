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
from time import strftime
from operations_modules import logger
from operations_modules.configuration_main import command_data_separator
from sensor_modules import sensor_access
from html_files import html_templates


def get_sensor_readings_page():
    """ Returns a HTML formatted string of the Local Sensor's 'sensor' readings. """
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Sensor Readings")

    style_text_small = "<span style='font-size: 14px;'>"
    style_red = "<span style='color: red;'><strong>"
    style_pre_text_orange = "<span style='color: #F4A460;'><strong>"
    style_name_start = "<td span style='text-align: center;'><span style='background-color: #00ffff;'><strong>"
    style_data_start = "<td span style='text-align: center;'><span style='background-color: #0BB10D;'><strong>"
    style_end = "</strong></span>"
    style_end_sensors = "</strong></span></td>"

    current_datetime = strftime("%Y-%m-%d %H:%M - %Z")
    sensor_hostname = sensor_access.get_hostname()
    sensor_ip = sensor_access.get_ip()

    sensor_types_and_readings_list = sensor_access.get_interval_sensor_readings().split(command_data_separator)

    sensor_types = sensor_types_and_readings_list[0].split(",")
    sensor_readings = sensor_types_and_readings_list[1].split(",")

    text_date_taken = "<h3>" + style_pre_text_orange + \
                      "Date taken " + current_datetime + \
                      style_text_small + \
                      "<br>Date format: YYYY-MM-DD hh:mm - Time Zone" + \
                      style_end + style_end + "</h3>"

    sensor_type_html = ""
    sensor_data_html = ""
    big_return = "<table>"
    count = 0
    for sensor_type, sensor_reading in zip(sensor_types, sensor_readings):
        sensor_type_html += style_name_start + sensor_type + style_end_sensors
        sensor_data_html += style_data_start + sensor_reading + style_end_sensors

        count += 1
        if count > 4:
            count = 0
            big_return += "<tr>" + sensor_type_html + "</tr><tr>" + sensor_data_html + "</tr></table><table>"
            sensor_type_html = ""
            sensor_data_html = ""

    if count > 0:
        big_return += "<tr>" + sensor_type_html + "</tr><tr>" + sensor_data_html + "</tr></table><table>"

    final_return = html_templates.sensor_readings_start + \
                   "<H1>" + style_red + "<u><a href='/TestSensor' style='color: red'>" + \
                   sensor_hostname + " // " + sensor_ip + style_end + "</a></u></H1>" + \
                   text_date_taken + big_return

    return final_return
