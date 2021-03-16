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
from flask import render_template
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import atpro_variables


def get_html_atpro_index(run_script="SelectNav('sensor-dashboard');", main_page_view_content=""):
    return render_template("ATPro_admin/index.html",
                           SensorID=app_cached_variables.tmp_sensor_id,
                           NotificationCount=str(atpro_variables.notification_count),
                           NotificationsReplacement=atpro_variables.get_notifications_as_string(),
                           OptionalHTML=main_page_view_content,
                           RunScript=run_script)


def get_message_page(title, message="", page_url="sensor-dashboard"):
    """
    Possible page URL's include:
    sensor-dashboard, sensor-readings, sensor-notes, sensor-graphing, sensor-rm, sensor-settings, sensor-system
    """
    message_page = render_template("ATPro_admin/page_templates/message_return.html",
                                   NavLocation=page_url,
                                   TextTitle=title,
                                   TextMessage=message)
    return get_html_atpro_index(run_script="", main_page_view_content=message_page)
