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
from datetime import datetime
from flask import Blueprint, render_template, send_file
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.software_version import version
from operations_modules.software_version import version as kootnet_version
from operations_modules.software_automatic_upgrades import get_automatic_upgrade_enabled_text
from configuration_modules import app_config_access
from sensor_modules import system_access
from sensor_modules import sensor_access
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index, \
    get_message_page, get_text_check_enabled, get_uptime_str

html_atpro_main_routes = Blueprint("html_atpro_main_routes", __name__)

html_sensor_readings_row = """
    <div class='col-3 col-m-6 col-sm-12'>
        <div class="card">
            <div class="card-content">
                <div class="readings-header">{{ SensorName }}</div>
                <div class="readings">{{ SensorReading }}</div>
            </div>
        </div>
    </div>
"""


@html_atpro_main_routes.route("/atpro/")
def html_atpro_index():
    return get_html_atpro_index()


@html_atpro_main_routes.route("/atpro/sensor-dashboard")
def html_atpro_dashboard():
    g_t_c_e = get_text_check_enabled

    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = round(cpu_temp[app_cached_variables.database_variables.system_temperature], 3)
    return render_template(
        "ATPro_admin/page_templates/dashboard.html",
        AutoUpgrades=get_automatic_upgrade_enabled_text(),
        KootnetVersion=version,
        StdVersion=app_cached_variables.standard_version_available,
        DevVersion=app_cached_variables.developmental_version_available,
        LastUpdated=app_cached_variables.program_last_updated,
        DateTime=strftime("%Y-%m-%d %H:%M:%S %Z"),
        DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        HostName=app_cached_variables.hostname,
        LocalIP=app_cached_variables.ip,
        OperatingSystem=app_cached_variables.operating_system_name,
        DebugLogging=g_t_c_e(app_config_access.primary_config.enable_debug_logging),
        CPUTemperature=str(cpu_temp),
        SensorUptime=get_uptime_str(),
        SensorReboots=app_cached_variables.reboot_count,
        RAMUsage=str(system_access.get_ram_space(return_type=1)) + " GB",
        RAMTotal=str(app_cached_variables.total_ram_memory) + " GB",
        DiskUsage=str(system_access.get_disk_space(return_type=1)) + " GB",
        DiskTotal=str(app_cached_variables.total_disk_space) + " GB",
        InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
        IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
        TriggerHighLowRecording=g_t_c_e(app_config_access.trigger_high_low.enable_high_low_trigger_recording),
        TriggerVarianceRecording=g_t_c_e(app_config_access.trigger_variances.enable_trigger_variance),
        MQTTBroker=app_cached_variables.mqtt_broker_dummy_thread.current_state,
        MQTTPublishing=app_cached_variables.mqtt_publisher_thread.current_state,
        MQTTSubscriber=app_cached_variables.mqtt_subscriber_thread.current_state,
        MQTTSubscriberRecording=g_t_c_e(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        SensorCheckins=g_t_c_e(app_config_access.checkin_config.enable_checkin),
        CheckinServer=g_t_c_e(app_config_access.checkin_config.enable_checkin_recording),
        OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
        WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
        LuftdatenService=app_cached_variables.luftdaten_thread.current_state
    )


@html_atpro_main_routes.route("/atpro/sensor-readings")
def html_atpro_sensor_readings():
    all_readings = sensor_access.get_all_available_sensor_readings()
    html_final_code = ""
    for index, reading in all_readings.items():
        reading_unit = " " + sensor_access.get_reading_unit(index)
        new_reading = html_sensor_readings_row.replace("{{ SensorName }}", index.replace("_", " "))
        new_reading = new_reading.replace("{{ SensorReading }}", str(reading) + reading_unit)
        html_final_code += new_reading + "\n"
    return render_template("ATPro_admin/page_templates/sensor-readings.html", HTMLReplacementCode=html_final_code)


@html_atpro_main_routes.route("/atpro/sensor-latency")
def html_atpro_sensors_latency():
    sensors_latency = sensor_access.get_sensors_latency()
    html_final_code = ""
    for index, reading in sensors_latency.items():
        new_reading = html_sensor_readings_row.replace("{{ SensorName }}", index)
        new_reading = new_reading.replace("{{ SensorReading }}", str(reading) + " Seconds")
        html_final_code += new_reading + "\n"
    return render_template("ATPro_admin/page_templates/sensors-latency.html", HTMLReplacementCode=html_final_code)


@html_atpro_main_routes.route("/atpro/sensor-help")
def html_atpro_sensor_help():
    documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"
    return send_file(documentation_root_dir + "/index.html")


@html_atpro_main_routes.route("/atpro/system-about")
def html_atpro_about():
    return render_template("ATPro_admin/page_templates/system/system-about.html", KootnetVersion=kootnet_version)


@html_atpro_main_routes.route("/atpro/logout")
def html_atpro_logout():
    return get_message_page("Logged Out", "You have been logged out"), 401


@html_atpro_main_routes.route("/atpro/get-notification-count")
def html_atpro_get_notification_count():
    return str(atpro_notifications.notification_count)


@html_atpro_main_routes.route("/atpro/get-notification-messages")
def html_atpro_get_notification_messages():
    return atpro_notifications.notification_str
