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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from operations_modules import software_version
from sensor_modules import sensor_access

html_sensor_info_readings_routes = Blueprint("html_sensor_info_readings_routes", __name__)


@html_sensor_info_readings_routes.route("/")
@html_sensor_info_readings_routes.route("/index")
@html_sensor_info_readings_routes.route("/index.html")
def index():
    return render_template("index.html",
                           HostName=app_cached_variables.hostname,
                           SQLDatabaseLocation=file_locations.sensor_database,
                           SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
                           SQLDatabaseSize=sensor_access.get_db_size(),
                           NumberNotes=sensor_access.get_db_notes_count())


@html_sensor_info_readings_routes.route("/About")
@html_sensor_info_readings_routes.route("/SensorInformation")
def html_system_information():
    debug_logging = "Disabled"
    if app_config_access.primary_config.enable_debug_logging:
        debug_logging = "Enabled"

    display_enabled = get_text_running_thread_state(app_config_access.primary_config.enable_display,
                                                    app_cached_variables.mini_display_thread)

    interval_recording = get_text_running_thread_state(app_config_access.primary_config.enable_interval_recording,
                                                       app_cached_variables.interval_recording_thread)

    trigger_recording = "Disabled"
    enable_trigger_button = "disabled"
    if app_config_access.primary_config.enable_trigger_recording:
        trigger_recording = "Enabled"
        enable_trigger_button = ""
    if app_config_access.primary_config.enable_trigger_recording:
        trigger_uptime = get_text_running_thread_state(app_config_access.trigger_variances.sensor_uptime_enabled,
                                                       app_cached_variables.trigger_thread_sensor_uptime)
        trigger_cpu_temp = get_text_running_thread_state(app_config_access.trigger_variances.cpu_temperature_enabled,
                                                         app_cached_variables.trigger_thread_cpu_temp)
        trigger_env_temp = get_text_running_thread_state(app_config_access.trigger_variances.env_temperature_enabled,
                                                         app_cached_variables.trigger_thread_env_temp)
        trigger_pressure = get_text_running_thread_state(app_config_access.trigger_variances.pressure_enabled,
                                                         app_cached_variables.trigger_thread_pressure)
        trigger_altitude = get_text_running_thread_state(app_config_access.trigger_variances.altitude_enabled,
                                                         app_cached_variables.trigger_thread_altitude)
        trigger_humidity = get_text_running_thread_state(app_config_access.trigger_variances.humidity_enabled,
                                                         app_cached_variables.trigger_thread_humidity)
        trigger_distance = get_text_running_thread_state(app_config_access.trigger_variances.distance_enabled,
                                                         app_cached_variables.trigger_thread_distance)
        trigger_lumen = get_text_running_thread_state(app_config_access.trigger_variances.lumen_enabled,
                                                      app_cached_variables.trigger_thread_lumen)
        trigger_visible_ems = get_text_running_thread_state(app_config_access.trigger_variances.colour_enabled,
                                                            app_cached_variables.trigger_thread_visible_ems)
        trigger_accelerometer = get_text_running_thread_state(app_config_access.trigger_variances.accelerometer_enabled,
                                                              app_cached_variables.trigger_thread_accelerometer)
        trigger_magnetometer = get_text_running_thread_state(app_config_access.trigger_variances.magnetometer_enabled,
                                                             app_cached_variables.trigger_thread_magnetometer)
        trigger_gyroscope = get_text_running_thread_state(app_config_access.trigger_variances.gyroscope_enabled,
                                                          app_cached_variables.trigger_thread_gyroscope)
    else:
        trigger_uptime = get_text_running_thread_state(False, None)
        trigger_cpu_temp = get_text_running_thread_state(False, None)
        trigger_env_temp = get_text_running_thread_state(False, None)
        trigger_pressure = get_text_running_thread_state(False, None)
        trigger_altitude = get_text_running_thread_state(False, None)
        trigger_humidity = get_text_running_thread_state(False, None)
        trigger_distance = get_text_running_thread_state(False, None)
        trigger_lumen = get_text_running_thread_state(False, None)
        trigger_visible_ems = get_text_running_thread_state(False, None)
        trigger_accelerometer = get_text_running_thread_state(False, None)
        trigger_magnetometer = get_text_running_thread_state(False, None)
        trigger_gyroscope = get_text_running_thread_state(False, None)

    wu_enabled = app_config_access.weather_underground_config.weather_underground_enabled
    weather_underground = get_text_running_thread_state(wu_enabled, app_cached_variables.weather_underground_thread)

    luftdaten = get_text_running_thread_state(app_config_access.luftdaten_config.luftdaten_enabled,
                                              app_cached_variables.luftdaten_thread)

    open_sense_map = get_text_running_thread_state(app_config_access.open_sense_map_config.open_sense_map_enabled,
                                                   app_cached_variables.open_sense_map_thread)

    total_ram_entry = str(app_cached_variables.total_ram_memory) + app_cached_variables.total_ram_memory_size_type

    return render_template("sensor_information.html",
                           HostName=app_cached_variables.hostname,
                           IPAddress=app_cached_variables.ip,
                           OSVersion=app_cached_variables.operating_system_name,
                           KootnetVersion=software_version.version,
                           LastUpdated=app_cached_variables.program_last_updated,
                           DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                           SystemUptime=sensor_access.get_uptime_str(),
                           SensorReboots=app_cached_variables.reboot_count,
                           CPUTemperature=sensor_access.get_cpu_temperature(),
                           RAMUsage=sensor_access.get_memory_usage_percent(),
                           TotalRAM=total_ram_entry,
                           DiskUsage=sensor_access.get_disk_usage_percent(),
                           DebugLogging=debug_logging,
                           SupportedDisplay=display_enabled,
                           IntervalRecording=interval_recording,
                           TriggerRecording=trigger_recording,
                           TriggerButtonDisabled=enable_trigger_button,
                           TriggerSensorUptime=trigger_uptime,
                           TriggerCPUTemp=trigger_cpu_temp,
                           TriggerEnvTemp=trigger_env_temp,
                           TriggerPressure=trigger_pressure,
                           TriggerAltitude=trigger_altitude,
                           TriggerHumidity=trigger_humidity,
                           TriggerDistance=trigger_distance,
                           TriggerLumen=trigger_lumen,
                           TriggerVisibleEMS=trigger_visible_ems,
                           TriggerAccelerometer=trigger_accelerometer,
                           TriggerMagnetometer=trigger_magnetometer,
                           TriggerGyroscope=trigger_gyroscope,
                           WeatherUndergroundService=weather_underground,
                           LuftdatenService=luftdaten,
                           OpenSenseMapService=open_sense_map,
                           InstalledSensors=app_config_access.installed_sensors.get_installed_names_str())


@html_sensor_info_readings_routes.route("/TestSensor")
@html_sensor_info_readings_routes.route("/SensorReadings")
def html_sensors_readings():
    logger.network_logger.debug("** Sensor Readings accessed from " + str(request.remote_addr))
    try:
        raw_temp = sensor_access.get_sensor_temperature(temperature_correction=False)
        adjusted_temp = sensor_access.get_sensor_temperature()
        temp_offset = "Disabled"
        if app_config_access.primary_config.enable_custom_temp:
            temp_offset = str(app_config_access.primary_config.temperature_offset) + " °C"

        gas_readings = sensor_access.get_gas(return_as_dictionary=True)
        gas_index = app_cached_variables.no_sensor_present
        gas_oxidising = app_cached_variables.no_sensor_present
        gas_reducing = app_cached_variables.no_sensor_present
        gas_nh3 = app_cached_variables.no_sensor_present
        if gas_readings != app_cached_variables.no_sensor_present:
            if app_cached_variables.database_variables.gas_resistance_index in gas_readings:
                gas_index = gas_readings[app_cached_variables.database_variables.gas_resistance_index]
            if app_cached_variables.database_variables.gas_oxidising in gas_readings:
                gas_oxidising = gas_readings[app_cached_variables.database_variables.gas_oxidising]
            if app_cached_variables.database_variables.gas_reducing in gas_readings:
                gas_reducing = gas_readings[app_cached_variables.database_variables.gas_reducing]
            if app_cached_variables.database_variables.gas_nh3 in gas_readings:
                gas_nh3 = gas_readings[app_cached_variables.database_variables.gas_nh3]

        pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
        pm_1 = app_cached_variables.no_sensor_present
        pm_2_5 = app_cached_variables.no_sensor_present
        pm_10 = app_cached_variables.no_sensor_present
        if pm_readings != app_cached_variables.no_sensor_present:
            if app_cached_variables.database_variables.particulate_matter_1 in pm_readings:
                pm_1 = pm_readings[app_cached_variables.database_variables.particulate_matter_1]
            if app_cached_variables.database_variables.particulate_matter_2_5 in pm_readings:
                pm_2_5 = pm_readings[app_cached_variables.database_variables.particulate_matter_2_5]
            if app_cached_variables.database_variables.particulate_matter_10 in pm_readings:
                pm_10 = pm_readings[app_cached_variables.database_variables.particulate_matter_10]

        uv_readings = sensor_access.get_ultra_violet(return_as_dictionary=True)
        uv_a = app_cached_variables.no_sensor_present
        uv_b = app_cached_variables.no_sensor_present
        if uv_readings != app_cached_variables.no_sensor_present:
            if app_cached_variables.database_variables.ultra_violet_a in uv_readings:
                uv_a = uv_readings[app_cached_variables.database_variables.ultra_violet_a]
            if app_cached_variables.database_variables.ultra_violet_b in uv_readings:
                uv_b = uv_readings[app_cached_variables.database_variables.ultra_violet_b]

        red, orange, yellow, green, blue, violet = _get_ems_for_render_template()
        return render_template("sensor_readings.html",
                               URLRedirect="SensorReadings",
                               HostName=app_cached_variables.hostname,
                               IPAddress=app_cached_variables.ip,
                               DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                               SystemUptime=sensor_access.get_uptime_str(),
                               CPUTemperature=str(sensor_access.get_cpu_temperature()) + " °C",
                               RAWEnvTemperature=str(raw_temp) + " °C",
                               AdjustedEnvTemperature=str(adjusted_temp) + " °C",
                               EnvTemperatureOffset=str(temp_offset),
                               Pressure=str(sensor_access.get_pressure()) + " hPa",
                               Altitude=str(sensor_access.get_altitude()) + " Meters",
                               Humidity=str(sensor_access.get_humidity()) + " %RH",
                               Distance=str(sensor_access.get_distance()) + " ?",
                               GasResistanceIndex=str(gas_index) + " kΩ",
                               GasOxidising=str(gas_oxidising) + " kΩ",
                               GasReducing=str(gas_reducing) + " kΩ",
                               GasNH3=str(gas_nh3) + " kΩ",
                               PM1=str(pm_1) + " µg/m³",
                               PM25=str(pm_2_5) + " µg/m³",
                               PM10=str(pm_10) + " µg/m³",
                               Lumen=str(sensor_access.get_lumen()) + " lm",
                               Red=str(red),
                               Orange=str(orange),
                               Yellow=str(yellow),
                               Green=str(green),
                               Blue=str(blue),
                               Violet=str(violet),
                               UVA=str(uv_a),
                               UVB=str(uv_b),
                               Acc=str(sensor_access.get_accelerometer_xyz()) + " g",
                               Mag=str(sensor_access.get_magnetometer_xyz()) + " μT",
                               Gyro=str(sensor_access.get_gyroscope_xyz()) + " °/s")
    except Exception as error:
        logger.primary_logger.error("Unable to generate Readings Page: " + str(error))
        return render_template("message_return.html", URL="/",
                               TextMessage="Unable to generate Readings Page",
                               message2=str(error))


def _get_ems_for_render_template():
    colors = sensor_access.get_ems_colors(return_as_dictionary=True)
    if colors == app_cached_variables.no_sensor_present:
        return [app_cached_variables.no_sensor_present, app_cached_variables.no_sensor_present,
                app_cached_variables.no_sensor_present, app_cached_variables.no_sensor_present,
                app_cached_variables.no_sensor_present, app_cached_variables.no_sensor_present]

    red = app_cached_variables.no_sensor_present
    orange = app_cached_variables.no_sensor_present
    yellow = app_cached_variables.no_sensor_present
    green = app_cached_variables.no_sensor_present
    blue = app_cached_variables.no_sensor_present
    violet = app_cached_variables.no_sensor_present

    if app_cached_variables.database_variables.red in colors:
        red = colors[app_cached_variables.database_variables.red]
    if app_cached_variables.database_variables.orange in colors:
        orange = colors[app_cached_variables.database_variables.orange]
    if app_cached_variables.database_variables.yellow in colors:
        yellow = colors[app_cached_variables.database_variables.yellow]
    if app_cached_variables.database_variables.green in colors:
        green = colors[app_cached_variables.database_variables.green]
    if app_cached_variables.database_variables.blue in colors:
        blue = colors[app_cached_variables.database_variables.blue]
    if app_cached_variables.database_variables.violet in colors:
        violet = colors[app_cached_variables.database_variables.violet]
    return [red, orange, yellow, green, blue, violet]


@html_sensor_info_readings_routes.route("/TestSensorLatency")
def html_sensors_latency():
    logger.network_logger.debug("** Sensor Latency accessed from " + str(request.remote_addr))
    sensors_latency = sensor_access.get_sensors_latency()
    return render_template("sensor_readings.html",
                           URLRedirect="TestSensorLatency",
                           HostName="Sensor Latency",
                           IPAddress=app_cached_variables.ip,
                           DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                           SystemUptime=sensor_access.get_uptime_str(),
                           CPUTemperature=str(sensors_latency[1][0]) + " Seconds",
                           RAWEnvTemperature=str(sensors_latency[1][1]) + " Seconds",
                           AdjustedEnvTemperature="",
                           EnvTemperatureOffset="",
                           Pressure=str(sensors_latency[1][2]) + " Seconds",
                           Altitude=str(sensors_latency[1][3]) + " Seconds",
                           Humidity=str(sensors_latency[1][4]) + " Seconds",
                           Distance=str(sensors_latency[1][5]) + " Seconds",
                           GasResistanceIndex="All GAS: " + str(sensors_latency[1][6]) + " Seconds",
                           GasOxidising="",
                           GasReducing="",
                           GasNH3="",
                           PM1="All PM: " + str(sensors_latency[1][7]) + " Seconds",
                           PM25="",
                           PM10="",
                           Lumen=str(sensors_latency[1][8]) + " Seconds",
                           Red="All EMS Colors: " + str(sensors_latency[1][9]) + " Seconds",
                           Orange="",
                           Yellow="",
                           Green="",
                           Blue="",
                           Violet="",
                           UVA="All UV: " + str(sensors_latency[1][10]) + " Seconds",
                           UVB="",
                           Acc=str(sensors_latency[1][11]) + " Seconds",
                           Mag=str(sensors_latency[1][12]) + " Seconds",
                           Gyro=str(sensors_latency[1][13]) + " Seconds")


def get_text_running_thread_state(service_enabled, thread_variable):
    """ Checks to see if a 'service' thread is running and returns the result as text. """
    if service_enabled:
        return_text = "Stopped"
        if thread_variable is None:
            return_text = "Missing Sensor"
        elif thread_variable.is_running:
            return_text = "Running"
        return return_text
    return "Disabled"
