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
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from operations_modules import file_locations
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_logs import get_log_view_message
from http_server.flask_blueprints.atpro.atpro_generic import get_uptime_str, get_html_enabled_disabled_text
from operations_modules.software_version import version
from sensor_modules import sensor_access
from sensor_modules import system_access

html_lcars_routes = Blueprint("html_LCARS_routes", __name__)


@html_lcars_routes.route("/LCARS/")
@html_lcars_routes.route("/LCARS/index")
@html_lcars_routes.route("/LCARS/index.html")
def html_lcars_index(main_content=None):
    g_t_c_e = get_html_enabled_disabled_text

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    date_time_now = datetime.utcnow() + timedelta(hours=utc0_hour_offset)
    date_time_now = f"{date_time_now.strftime('%b %d, %Y - %H:%M:%S')} UTC{str(utc0_hour_offset)}"

    if main_content is None:
        lcars_buttons = _get_lcars_html_sensor_buttons()
        main_content = render_template("LCARS/lcars-content-main.html",
                                       SensorButtons=lcars_buttons,
                                       WaterFallData=_get_lcars_html_sensor_readings_waterfall())
    return render_template("LCARS/lcars-index-nemesis-blue.html",
                           SensorName=app_cached_variables.hostname,
                           DateTimeUTC=date_time_now,
                           SystemOS=app_cached_variables.operating_system_name,
                           RAMFree=f"{str(system_access.get_ram_space(return_type=0))} GB",
                           RAMPercent=f"{str(system_access.get_ram_space(return_type=3))} %",
                           DebugLogging=g_t_c_e(app_config_access.primary_config.enable_debug_logging),
                           InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
                           Uptime=get_uptime_str(),
                           IPAddress=app_cached_variables.ip,
                           MainContent=main_content
                           )


def _get_lcars_html_sensor_buttons():
    html_lcars_sensor_button_template = "<a href='/LCARS/{{ SensorName }}' class='bluey two-rows'>" + \
                                        "{{ SensorName }} <br> {{ SensorReading }} {{ ReadingType }}</a>"

    lcars_sensor_buttons = ""
    avail_sensor_dic = sensor_access.get_available_sensors_dic()
    all_sensor_readings = sensor_access.get_all_available_sensor_readings()
    for index, enabled in avail_sensor_dic.items():
        button_name = app_cached_variables.database_variables.get_clean_db_col_name(index)
        reading_type = sensor_access.get_reading_unit(index)
        if index == app_cached_variables.database_variables.env_temperature:
            button_name = "Temperature"
        if index in all_sensor_readings:
            lcars_sensor_buttons += html_lcars_sensor_button_template.replace("{{ SensorName }}", button_name)
            lcars_sensor_buttons = lcars_sensor_buttons.replace("{{ SensorReading }}", str(all_sensor_readings[index]))
            lcars_sensor_buttons = lcars_sensor_buttons.replace("{{ ReadingType }}", reading_type)
    return lcars_sensor_buttons


def _get_lcars_html_sensor_readings_waterfall():
    row_count = 1
    sensor_count = 1

    lcars_readings_data = f"<div class='row-{str(row_count)}'>"
    all_sensor_readings = sensor_access.get_all_available_sensor_readings()
    for index, reading in all_sensor_readings.items():
        sensor_name = app_cached_variables.database_variables.get_clean_db_col_name(index)
        reading_type = sensor_access.get_reading_unit(index)
        if index == app_cached_variables.database_variables.env_temperature:
            sensor_name = "Temperature"
        elif index == app_cached_variables.database_variables.env_temperature_offset:
            sensor_name = "Temperature Offset"
        elif index == app_cached_variables.database_variables.particulate_matter_1:
            sensor_name = "PM 1"
        elif index == app_cached_variables.database_variables.particulate_matter_2_5:
            sensor_name = "PM 2.5"
        elif index == app_cached_variables.database_variables.particulate_matter_4:
            sensor_name = "PM 4"
        elif index == app_cached_variables.database_variables.particulate_matter_10:
            sensor_name = "PM 10"
        elif index == app_cached_variables.database_variables.gps_num_satellites:
            sensor_name = "Connected Satellites"
        elif index == app_cached_variables.database_variables.gps_speed_over_ground:
            sensor_name = "GPS Speed"

        html_lcars_readings_template = f"<div class='dc{str(sensor_count)}'>" + \
                                       "{{ SensorName }} -> {{ SensorReading }} {{ ReadingType }}</div>"

        lcars_readings_data += html_lcars_readings_template.replace("{{ SensorName }}", sensor_name)
        lcars_readings_data = lcars_readings_data.replace("{{ SensorReading }}", str(all_sensor_readings[index]))
        lcars_readings_data = lcars_readings_data.replace("{{ ReadingType }}", reading_type)
        if not sensor_count % 4:
            row_count += 1
            sensor_count = 0
            lcars_readings_data += f"</div>\n\n<div class='row-{str(row_count)}'>\n"
        sensor_count += 1
    return f"{lcars_readings_data}</div>"


@html_lcars_routes.route("/LCARS/ViewGraph", methods=["GET", "POST"])
def html_lcars_view_graph():
    if request.method == "POST":
        graph_to_view = str(request.form.get("graph_selection"))[:55]

    return "WIP"


@html_lcars_routes.route("/LCARS/Logs")
def html_lcars_logs():
    logs = render_template("LCARS/lcars-content-sensor-logs.html",
                           PrimaryLogs=get_log_view_message("Primary Log", file_locations.primary_log),
                           NetworkLogs=get_log_view_message("Network Log", file_locations.network_log),
                           SensorsLogs=get_log_view_message("Sensors Log", file_locations.sensors_log))
    return html_lcars_index(main_content=logs)


@html_lcars_routes.route("/LCARS/About")
def html_lcars_about():
    about = render_template("LCARS/lcars-content-about.html",
                            KootnetVersion=version,
                            SensorID=app_config_access.primary_config.sensor_id
                            )
    return html_lcars_index(main_content=about)
