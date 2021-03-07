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
import psutil
from time import strftime
from datetime import datetime, timedelta
from flask import Blueprint, render_template, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.sqlite_database import sql_execute_get_data, get_sql_element
from operations_modules.software_version import version
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro import cached_pages
from sensor_modules import sensor_access

html_atpro_admin_routes = Blueprint("html_atpro_admin_routes", __name__)
db_v = app_cached_variables.database_variables


class CreateATProVariablesClass:
    def __init__(self):
        self.notification_count = 0
        self.notifications_list = []

    def init_tests(self):
        self.add_notification_entry("Restart Required",
                                    self.get_button_to_url_script("Restart Service", "/RestartServices"))
        self.add_notification_entry("Reboot", self.get_button_to_url_script("Reboot", "/RebootSystem"))
        self.add_notification_entry("Shutdown", self.get_button_to_url_script("Shutdown", "/ShutdownSystem"))

    def get_notifications_as_string(self):
        return_notes = ""
        for note in self.notifications_list:
            return_notes += str(note)
        return return_notes

    def add_notification_entry(self, notify_text, html_script):
        function_name = "function" + str(app_cached_variables.notes_total_count + 1)

        return_text = """
        <li class="dropdown-menu-item">
            <a onclick="{{ FunctionName }}()" class="dropdown-menu-link">
                <div>
                    <i class="fas fa-gift"></i>
                </div>
                <span>
                    {{ NotificationText }}
                    <br>
                    <span>
                        {{ DateTime }}
                    </span>
                </span>
            </a>
            <script>
                {{ Script }}
            </script>
        </li>
        """
        return_text = return_text.replace("{{ NotificationText }}", notify_text)
        return_text = return_text.replace("{{ DateTime }}", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return_text = return_text.replace("{{ FunctionName }}", function_name)

        html_script = html_script.replace("{{ FunctionName }}", function_name)
        return_text = return_text.replace("{{ Script }}", html_script)

        self.notifications_list.append(return_text)
        self.notification_count = len(self.notifications_list)

    @staticmethod
    def get_button_to_url_script(button_text, html_link):
        html_return_script = """
        function {{ FunctionName }}() {
            let r = confirm("{{ ButtonText }}");
            if (r === true) {
                window.location = "{{ HTMLLink }}"
            }
        }"""
        html_return_script = html_return_script.replace("{{ ButtonText }}", button_text)
        html_return_script = html_return_script.replace("{{ HTMLLink }}", html_link)
        return html_return_script


@html_atpro_admin_routes.route("/atpro/")
def html_atpro_index():
    return render_template("ATPro_admin/index.html",
                           SensorID=app_cached_variables.tmp_sensor_id,
                           MainContent=html_atpro_dashboard(),
                           NotificationCount=str(atpro_variables.notification_count),
                           NotificationsReplacement=atpro_variables.get_notifications_as_string())


@html_atpro_admin_routes.route("/atpro/sensor-dashboard")
def html_atpro_dashboard():
    atpro_variables.init_tests()

    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = round(cpu_temp[app_cached_variables.database_variables.system_temperature], 3)

    enable_debug_logging = app_config_access.primary_config.enable_debug_logging
    enable_high_low_trigger_recording = app_config_access.trigger_high_low.enable_high_low_trigger_recording
    enable_trigger_variance = app_config_access.trigger_variances.enable_trigger_variance
    enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording
    enable_checkin = app_config_access.primary_config.enable_checkin
    enable_checkin_recording = app_config_access.checkin_config.enable_checkin_recording
    return render_template("ATPro_admin/page_templates/dashboard.html",
                           KootnetVersion=version,
                           StdVersion=app_cached_variables.standard_version_available,
                           DevVersion=app_cached_variables.developmental_version_available,
                           LastUpdated=app_cached_variables.program_last_updated,
                           DateTime=strftime("%Y-%m-%d %H:%M:%S - %Z"),
                           DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                           HostName=app_cached_variables.hostname,
                           LocalIP=app_cached_variables.ip,
                           DebugLogging=_get_text_check_enabled(enable_debug_logging),
                           CPUTemperature=str(cpu_temp),
                           SensorReboots=app_cached_variables.reboot_count,
                           RAMUsage=_get_ram_free(),
                           DiskUsage=_get_disk_free(),
                           IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
                           TriggerHighLowRecording=_get_text_check_enabled(enable_high_low_trigger_recording),
                           TriggerVarianceRecording=_get_text_check_enabled(enable_trigger_variance),
                           MQTTPublishing=app_cached_variables.mqtt_publisher_thread.current_state,
                           MQTTSubscriber=app_cached_variables.mqtt_subscriber_thread.current_state,
                           MQTTSubscriberRecording=_get_text_check_enabled(enable_mqtt_sql_recording),
                           SensorCheckins=_get_text_check_enabled(enable_checkin),
                           CheckinServer=_get_text_check_enabled(enable_checkin_recording),
                           OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
                           WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
                           LuftdatenService=app_cached_variables.luftdaten_thread.current_state,
                           InstalledSensors=app_config_access.installed_sensors.get_installed_names_str())


def _get_ram_free():
    try:
        ram_available = psutil.virtual_memory().available
        ram_available = round((ram_available / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.network_logger.error("Dashboard - Getting Free RAM: " + str(error))
        ram_available = "Error"
    return str(ram_available) + " GB"


def _get_disk_free():
    try:
        disk_available = psutil.disk_usage(file_locations.sensor_data_dir).free
        disk_available = round((disk_available / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.network_logger.error("Dashboard - Getting Free Disk Space: " + str(error))
        disk_available = "Error"
    return str(disk_available) + " GB"


@html_atpro_admin_routes.route("/atpro/sensor-readings")
def html_atpro_sensor_readings():
    utc_datetime = datetime.utcnow()
    start_date = (utc_datetime - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")

    var_sql_query_datetime = "SELECT DateTime FROM IntervalData WHERE DateTime" + \
                             " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + "') " + \
                             "AND datetime('" + end_date + "') ORDER BY DateTime DESC LIMIT 100"

    var_sql_query = "SELECT " + db_v.system_temperature + " FROM IntervalData WHERE " + db_v.system_temperature + \
                    " IS NOT NULL AND DateTime BETWEEN datetime('" + start_date + "') " + \
                    "AND datetime('" + end_date + "') ORDER BY DateTime DESC LIMIT 100"

    sql_data_datetime = sql_execute_get_data(var_sql_query_datetime)
    sql_data = sql_execute_get_data(var_sql_query)
    print(str(len(sql_data)))

    data_str = ""
    for data_date, data in zip(sql_data_datetime, sql_data):
        try:
            data_str += "{ x: '" + str(get_sql_element(data_date)) + "', y: " + str(get_sql_element(data)) + " },"
        except Exception as error:
            print(str(error))
    if len(data_str) > 0:
        data_str = data_str[:-1]
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html",
                                SysTempData=data_str)
    return html_page


@html_atpro_admin_routes.route("/atpro/sensor-notes")
def html_atpro_sensor_notes():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_admin_routes.route("/atpro/sensor-graphing")
def html_atpro_sensor_graphing():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_admin_routes.route("/atpro/sensor-rm")
def html_atpro_sensor_remote_management():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_admin_routes.route("/atpro/sensor-settings")
def html_atpro_sensor_settings():
    return "WIP"
    html_page = render_template("ATPro_admin/page_templates/sensor_readings.html")
    return html_page


@html_atpro_admin_routes.route("/atpro/sensor-help")
def html_atpro_sensor_help():
    documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"
    return send_file(documentation_root_dir + "/index.html")


@html_atpro_admin_routes.route("/atpro/logout")
def html_atpro_logout():
    html_page = render_template("ATPro_admin/page_templates/message_return.html",
                                PageURL="/atpro/",
                                TextMessage="Logged out - Click here to return to the Dashboard.")
    return render_template("ATPro_admin/index.html",
                           MainContent=html_page), 401


def _get_text_check_enabled(setting):
    if setting:
        return "Enabled"
    return "Disabled"


atpro_variables = CreateATProVariablesClass()
