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
import re
from datetime import datetime
from flask import render_template
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules import app_config_access


def get_html_atpro_index(run_script="SelectNav('sensor-dashboard');", main_page_view_content=""):
    return render_template("ATPro_admin/index.html",
                           SensorID=app_cached_variables.tmp_sensor_id,
                           OptionalHTML=main_page_view_content,
                           RunScript=run_script)


def get_message_page(title, message="", page_url="sensor-dashboard", full_reload=True, skip_menu_select=False):
    """
    Possible page URL's include:
    sensor-dashboard, sensor-readings, sensor-notes, sensor-graphing, sensor-rm, sensor-settings, sensor-system
    """

    skip_option = "false"
    if skip_menu_select:
        skip_option = "true"

    message_page = render_template("ATPro_admin/page_templates/message-return.html",
                                   NavLocation=page_url,
                                   SkipMenuSelect=skip_option,
                                   TextTitle=title,
                                   TextMessage=message)
    if full_reload:
        return get_html_atpro_index(run_script="CheckNotificationsAsync();", main_page_view_content=message_page)
    return message_page


def get_clean_db_name(db_text_name, find_unique_name=True):
    final_db_name = ""
    for letter in db_text_name:
        if re.match("^[A-Za-z0-9_.-]*$", letter):
            final_db_name += letter
    if final_db_name == "":
        final_db_name = "No_Name"
    if final_db_name.split(".")[-1] == "sqlite":
        final_db_name = final_db_name[:-7]

    db_text_name = final_db_name

    if find_unique_name:
        count_num = 1
        if final_db_name + ".sqlite" in app_cached_variables.uploaded_databases_list:
            while final_db_name + str(count_num) + ".sqlite" in app_cached_variables.uploaded_databases_list:
                count_num += 1
            final_db_name = final_db_name + str(count_num)
            logger.network_logger.warning("Database " + db_text_name + " already exists, renamed to " + final_db_name)
    return final_db_name + ".sqlite"


def get_clean_ip_list_name(ip_list_name):
    final_ip_list_name = ""
    if ip_list_name is not None:
        for letter in ip_list_name:
            if re.match("^[A-Za-z0-9_.-]*$", letter):
                final_ip_list_name += letter

        if final_ip_list_name == "":
            final_ip_list_name = "No_Name"

        if final_ip_list_name.split(".")[-1] == "txt":
            final_ip_list_name = final_ip_list_name[:-4]

        custom_ip_list_names = app_config_access.sensor_control_config.custom_ip_list_names
        count_num = 1
        if final_ip_list_name + ".txt" in custom_ip_list_names:
            while final_ip_list_name + str(count_num) + ".txt" in custom_ip_list_names:
                count_num += 1
            final_ip_list_name = final_ip_list_name + str(count_num)
    return final_ip_list_name + ".txt"


def get_uptime_str():
    """ Returns System UpTime as a human readable String. """
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            var_minutes = int(uptime_seconds / 60)
    except Exception as error:
        logger.sensors_logger.error("Get Linux uptime minutes - Failed: " + str(error))
        var_minutes = 0

    str_day_hour_min = ""
    uptime_days = int(float(var_minutes) // 1440)
    uptime_hours = int((float(var_minutes) % 1440) // 60)
    uptime_min = int(float(var_minutes) % 60)
    if uptime_days:
        if uptime_days >= 365:
            years = uptime_days // 365
            if years > 1:
                str_day_hour_min += str(years) + " Years<br>"
            else:
                str_day_hour_min += str(years) + " Year<br>"
            uptime_days = uptime_days - (365 * years)

        if uptime_days > 1:
            str_day_hour_min += str(uptime_days) + " Days<br>"
        else:
            str_day_hour_min += str(uptime_days) + " Day<br>"
    if uptime_hours:
        if uptime_hours > 1:
            str_day_hour_min += str(uptime_hours) + " Hours & "
        else:
            str_day_hour_min += str(uptime_hours) + " Hour & "
    str_day_hour_min += str(uptime_min) + " Min"
    return str_day_hour_min


def get_text_check_enabled(setting):
    if setting:
        return "Enabled"
    return "Disabled"


def get_file_creation_date(file_location):
    try:
        file_creation_date_unix = os.path.getmtime(file_location)
        creation_date = str(datetime.fromtimestamp(file_creation_date_unix))[:-7]
    except FileNotFoundError:
        creation_date = "File not Found"
    return creation_date
