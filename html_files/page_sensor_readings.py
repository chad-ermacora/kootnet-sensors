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
from operations_modules import sensors
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
    td_end = "</td>"

    current_datetime = strftime("%Y-%m-%d %H:%M - %Z")
    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()
    sensor_env_temperature = str(round(sensors.get_sensor_temperature(), 2))
    sensors_env_temperature_offset = sensors.configuration_main.current_config.temperature_offset
    sensor_env_temperature_adjusted = str(round(float(sensor_env_temperature) + sensors_env_temperature_offset, 2))
    sensor_pressure = str(sensors.get_pressure())
    sensor_humidity = str(sensors.get_humidity())
    sensor_lumen = str(sensors.get_lumen())
    sensor_ems = str(sensors.get_ems())
    sensor_acc = str(sensors.get_accelerometer_xyz())
    sensor_mag = str(sensors.get_magnetometer_xyz())
    sensor_gyro = str(sensors.get_gyroscope_xyz())

    text_date_taken = "<h3>" + style_pre_text_orange + \
                      "Date taken " + current_datetime + \
                      style_text_small + \
                      "<br>Date format: YYYY-MM-DD hh:mm - Time Zone" + \
                      style_end + style_end + "</h3>"

    return_html1 = "<table><tr>" + \
                   style_name_start + "Env Temperature" + style_end + td_end + \
                   style_name_start + "Pressure" + style_end + td_end + \
                   style_name_start + "Humidity" + style_end + td_end + \
                   "</tr><tr>" + \
                   style_data_start + \
                   "Raw: " + sensor_env_temperature + " °C" + \
                   " / Adjusted: " + sensor_env_temperature_adjusted + " °C" + \
                   style_end + td_end + \
                   style_data_start + sensor_pressure + style_end + td_end + \
                   style_data_start + sensor_humidity + style_end + td_end + \
                   "</tr></table>"

    return_html2 = "<table><tr>" + \
                   style_name_start + "Lumen" + style_end + td_end + \
                   style_name_start + "Visible EMS - RGB or ROYGBV" + style_end + td_end + \
                   "</tr><tr>" + \
                   style_data_start + sensor_lumen + style_end + td_end + \
                   style_data_start + sensor_ems + style_end + td_end + \
                   "</tr></table><table><tr>"

    return_html3 = "<table><tr>" + \
                   style_name_start + "Accelerometer XYZ" + style_end + td_end + \
                   style_name_start + "Magnetometer XYZ" + style_end + td_end + \
                   style_name_start + "Gyroscope XYZ" + style_end + td_end + \
                   "</tr><tr>" + \
                   style_data_start + sensor_acc + style_end + td_end + \
                   style_data_start + sensor_mag + style_end + td_end + \
                   style_data_start + sensor_gyro + style_end + td_end + \
                   "</tr></table>"

    final_return = html_templates.sensor_readings_start + "<H1>" + style_red + \
                   "<u><a href='/TestSensor' style='color: red'>" + \
                   sensor_hostname + " // " + sensor_ip + \
                   style_end + "</a></u></H1>" + text_date_taken + \
                   return_html1 + return_html2 + return_html3

    return final_return
