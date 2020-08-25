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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import software_version
from sensor_modules import sensor_access
from http_server.server_http_generic_functions import get_html_hidden_state

html_sensor_info_readings_routes = Blueprint("html_sensor_info_readings_routes", __name__)


@html_sensor_info_readings_routes.route("/")
@html_sensor_info_readings_routes.route("/index")
@html_sensor_info_readings_routes.route("/index.html")
def index():
    return render_template(
        "index.html",
        PageURL="/index",
        RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
        RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
        HostName=app_cached_variables.hostname,
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=sensor_access.get_db_size(),
        NumberNotes=sensor_access.get_db_notes_count()
    )


@html_sensor_info_readings_routes.route("/About")
@html_sensor_info_readings_routes.route("/SensorInformation")
def html_system_information():
    debug_logging = "Disabled"
    if app_config_access.primary_config.enable_debug_logging:
        debug_logging = "Enabled"

    total_ram_entry = str(app_cached_variables.total_ram_memory) + app_cached_variables.total_ram_memory_size_type

    enable_high_low_trigger_recording = app_config_access.trigger_high_low.enable_high_low_trigger_recording
    enable_trigger_recording = app_config_access.trigger_variances.enable_trigger_variance

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    current_datetime = (datetime.utcnow() + timedelta(hours=utc0_hour_offset))

    return render_template(
        "sensor_information.html",
        PageURL="/SensorInformation",
        RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
        RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
        HostName=app_cached_variables.hostname,
        IPAddress=app_cached_variables.ip,
        OSVersion=app_cached_variables.operating_system_name,
        KootnetSensorID=app_config_access.primary_config.sensor_id,
        KootnetVersion=software_version.version,
        NewStandardKootnetVersion=app_cached_variables.standard_version_available,
        NewDevelopmentalKootnetVersion=app_cached_variables.developmental_version_available,
        LastUpdated=app_cached_variables.program_last_updated,
        DateTime=current_datetime.strftime("%Y-%m-%d %H:%M:%S") + " UTC" + str(utc0_hour_offset),
        SystemUptime=sensor_access.get_uptime_str(),
        SensorReboots=app_cached_variables.reboot_count,
        CPUTemperature=sensor_access.get_cpu_temperature(),
        RAMUsage=sensor_access.get_memory_usage_percent(),
        TotalRAM=total_ram_entry,
        DiskUsage=sensor_access.get_disk_usage_percent(),
        InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
        IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
        TriggerHighLowRecording=_get_text_check_enabled(enable_high_low_trigger_recording),
        TriggerVarianceRecording=_get_text_check_enabled(enable_trigger_recording),
        DebugLogging=debug_logging,
        SupportedDisplay=app_cached_variables.mini_display_thread.current_state,
        OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
        WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
        LuftdatenService=app_cached_variables.luftdaten_thread.current_state
    )


@html_sensor_info_readings_routes.route("/SensorTriggerStatus")
def html_trigger_status():
    return render_template(
        "trigger_recording_status.html",
        PageURL="/SensorTriggerStatus",
        TriggerVarianceCPUTemp=app_cached_variables.trigger_variance_thread_cpu_temp.current_state,
        TriggerVarianceEnvTemp=app_cached_variables.trigger_variance_thread_env_temp.current_state,
        TriggerVariancePressure=app_cached_variables.trigger_variance_thread_pressure.current_state,
        TriggerVarianceAltitude=app_cached_variables.trigger_variance_thread_altitude.current_state,
        TriggerVarianceHumidity=app_cached_variables.trigger_variance_thread_humidity.current_state,
        TriggerVarianceDistance=app_cached_variables.trigger_variance_thread_distance.current_state,
        TriggerVarianceLumen=app_cached_variables.trigger_variance_thread_lumen.current_state,
        TriggerVarianceVisibleEMS=app_cached_variables.trigger_variance_thread_visible_ems.current_state,
        TriggerVarianceUltraViolet=str(app_cached_variables.trigger_variance_thread_ultra_violet.current_state),
        TriggerVarianceGAS=str(app_cached_variables.trigger_variance_thread_gas.current_state),
        TriggerVariancePM=str(app_cached_variables.trigger_variance_thread_particulate_matter.current_state),
        TriggerVarianceAccelerometer=app_cached_variables.trigger_variance_thread_accelerometer.current_state,
        TriggerVarianceMagnetometer=app_cached_variables.trigger_variance_thread_magnetometer.current_state,
        TriggerVarianceGyroscope=app_cached_variables.trigger_variance_thread_gyroscope.current_state,
        TriggerHighLowCPUTemp=app_cached_variables.trigger_high_low_cpu_temp.current_state,
        TriggerHighLowEnvTemp=app_cached_variables.trigger_high_low_env_temp.current_state,
        TriggerHighLowPressure=app_cached_variables.trigger_high_low_pressure.current_state,
        TriggerHighLowAltitude=app_cached_variables.trigger_high_low_altitude.current_state,
        TriggerHighLowHumidity=app_cached_variables.trigger_high_low_humidity.current_state,
        TriggerHighLowDistance=app_cached_variables.trigger_high_low_distance.current_state,
        TriggerHighLowLumen=app_cached_variables.trigger_high_low_lumen.current_state,
        TriggerHighLowVisibleEMS=str(app_cached_variables.trigger_high_low_visible_colours.current_state),
        TriggerHighLowUltraViolet=str(app_cached_variables.trigger_high_low_ultra_violet.current_state),
        TriggerHighLowGAS=str(app_cached_variables.trigger_high_low_gas.current_state),
        TriggerHighLowPM=str(app_cached_variables.trigger_high_low_particulate_matter.current_state),
        TriggerHighLowAccelerometer=str(app_cached_variables.trigger_high_low_accelerometer.current_state),
        TriggerHighLowMagnetometer=str(app_cached_variables.trigger_high_low_magnetometer.current_state),
        TriggerHighLowGyroscope=str(app_cached_variables.trigger_high_low_gyroscope.current_state)
    )


@html_sensor_info_readings_routes.route("/TestSensor")
@html_sensor_info_readings_routes.route("/SensorReadings")
def html_sensors_readings():
    logger.network_logger.debug("** Sensor Readings accessed from " + str(request.remote_addr))
    try:
        temp_list = sensor_access.get_sensor_temperature(get_both=True)
        raw_temp = "NoSensor"
        adjusted_temp = "NoSensor"
        if len(temp_list) == 2:
            raw_temp = temp_list[0]
            adjusted_temp = temp_list[1]

        temp_offset = "Disabled"
        if app_config_access.primary_config.enable_custom_temp:
            temp_offset = str(app_config_access.primary_config.temperature_offset) + " °C"
        temp_comp = "Disabled"
        if app_config_access.primary_config.enable_temperature_comp_factor:
            temp_comp = str(app_config_access.primary_config.temperature_comp_factor)

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
        pm_4 = app_cached_variables.no_sensor_present
        pm_10 = app_cached_variables.no_sensor_present
        if app_cached_variables.database_variables.particulate_matter_1 in pm_readings:
            pm_1 = pm_readings[app_cached_variables.database_variables.particulate_matter_1]
        if app_cached_variables.database_variables.particulate_matter_2_5 in pm_readings:
            pm_2_5 = pm_readings[app_cached_variables.database_variables.particulate_matter_2_5]
        if app_cached_variables.database_variables.particulate_matter_4 in pm_readings:
            pm_4 = pm_readings[app_cached_variables.database_variables.particulate_matter_4]
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

        utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
        current_datetime = (datetime.utcnow() + timedelta(hours=utc0_hour_offset))
        return render_template(
            "sensor_readings.html",
            PageURL="/SensorReadings",
            RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
            RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
            URLRedirect="SensorReadings",
            HostName=app_cached_variables.hostname,
            IPAddress=app_cached_variables.ip,
            DateTime=current_datetime.strftime("%Y-%m-%d %H:%M:%S") + " UTC" + str(utc0_hour_offset),
            SystemUptime=sensor_access.get_uptime_str(),
            CPUTemperature=str(sensor_access.get_cpu_temperature()) + " °C",
            RAWEnvTemperature=str(raw_temp) + " °C",
            AdjustedEnvTemperature=str(adjusted_temp) + " °C",
            EnvTemperatureOffset=str(temp_offset),
            EnvTemperatureComp=str(temp_comp),
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
            PM4=str(pm_4) + " µg/m³",
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
            Gyro=str(sensor_access.get_gyroscope_xyz()) + " °/s"
        )
    except Exception as error:
        logger.primary_logger.error("Unable to generate Readings Page: " + str(error))
        return render_template(
            "message_return.html",
            PageURL="/",
            RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
            RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
            TextMessage="Unable to generate Readings Page",
            message2=str(error)
        )


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

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    current_datetime = (datetime.utcnow() + timedelta(hours=utc0_hour_offset))
    return render_template(
        "sensor_readings.html",
        PageURL="/TestSensorLatency",
        RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
        RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
        URLRedirect="TestSensorLatency",
        HostName="Sensor Latency",
        IPAddress=app_cached_variables.ip,
        DateTime=current_datetime.strftime("%Y-%m-%d %H:%M:%S") + " UTC" + str(utc0_hour_offset),
        SystemUptime=sensor_access.get_uptime_str(),
        CPUTemperature=str(sensors_latency["cpu_temperature"]) + " Seconds",
        RAWEnvTemperature=str(sensors_latency["environment_temperature"]) + " Seconds",
        AdjustedEnvTemperature="",
        EnvTemperatureOffset="",
        Pressure=str(sensors_latency["pressure"]) + " Seconds",
        Altitude=str(sensors_latency["altitude"]) + " Seconds",
        Humidity=str(sensors_latency["humidity"]) + " Seconds",
        Distance=str(sensors_latency["distance"]) + " Seconds",
        GasResistanceIndex="All GAS: " + str(sensors_latency["gas"]) + " Seconds",
        GasOxidising="",
        GasReducing="",
        GasNH3="",
        PM1="All PM: " + str(sensors_latency["particulate_matter"]) + " Seconds",
        PM25="",
        PM10="",
        Lumen=str(sensors_latency["lumen"]) + " Seconds",
        Red="All EMS Colors: " + str(sensors_latency["colours"]) + " Seconds",
        Orange="",
        Yellow="",
        Green="",
        Blue="",
        Violet="",
        UVA="All UV: " + str(sensors_latency["ultra_violet"]) + " Seconds",
        UVB="",
        Acc=str(sensors_latency["accelerometer_xyz"]) + " Seconds",
        Mag=str(sensors_latency["magnetometer_xyz"]) + " Seconds",
        Gyro=str(sensors_latency["gyroscope_xyz"]) + " Seconds"
    )


def _get_text_check_enabled(setting):
    if setting:
        return "Enabled"
    return "Disabled"
