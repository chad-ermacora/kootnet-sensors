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
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import software_version
from sensor_modules import sensor_access
from http_server.server_http_generic_functions import get_html_hidden_state

html_sensor_info_readings_routes = Blueprint("html_sensor_info_readings_routes", __name__)


@html_sensor_info_readings_routes.route("/About")
@html_sensor_info_readings_routes.route("/SensorInformation")
def html_system_information():
    debug_logging = "Disabled"
    if app_config_access.primary_config.enable_debug_logging:
        debug_logging = "Enabled"

    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = cpu_temp[app_cached_variables.database_variables.system_temperature]

    total_ram_entry = str(app_cached_variables.total_ram_memory) + app_cached_variables.total_ram_memory_size_type

    enable_high_low_trigger_recording = app_config_access.trigger_high_low.enable_high_low_trigger_recording
    enable_trigger_recording = app_config_access.trigger_variances.enable_trigger_variance

    enable_mqtt_sql_recording = 0
    if app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber:
        enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    current_datetime = (datetime.utcnow() + timedelta(hours=utc0_hour_offset))

    checkin_server_status = "Disabled"
    if app_config_access.checkin_config.enable_checkin_recording:
        checkin_server_status = "Running"

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
        CPUTemperature=str(cpu_temp),
        RAMUsage=sensor_access.get_memory_usage_percent(),
        TotalRAM=total_ram_entry,
        DiskUsage=sensor_access.get_disk_usage_percent(),
        InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
        IntervalRecording=app_cached_variables.interval_recording_thread.current_state,
        TriggerHighLowRecording=_get_text_check_enabled(enable_high_low_trigger_recording),
        TriggerVarianceRecording=_get_text_check_enabled(enable_trigger_recording),
        MQTTPublishing=app_cached_variables.mqtt_publisher_thread.current_state,
        MQTTSubscriber=app_cached_variables.mqtt_subscriber_thread.current_state,
        MQTTSubscriberRecording=_get_text_check_enabled(enable_mqtt_sql_recording),
        SensorCheckins=_get_text_check_enabled(app_config_access.primary_config.enable_checkin),
        CheckinServer=checkin_server_status,
        DebugLogging=debug_logging,
        SupportedDisplay=app_cached_variables.mini_display_thread.current_state,
        OpenSenseMapService=app_cached_variables.open_sense_map_thread.current_state,
        WeatherUndergroundService=app_cached_variables.weather_underground_thread.current_state,
        LuftdatenService=app_cached_variables.luftdaten_thread.current_state
    )


@html_sensor_info_readings_routes.route("/SensorRecordingStatus")
def html_sql_recording_status():
    interval_recording_config = app_config_access.interval_recording_config
    return render_template(
        "sql_recording_status.html",
        PageURL="/SensorRecordingStatus",
        IntervalCPUTemp=_get_enabled_state(interval_recording_config.cpu_temperature_enabled),
        IntervalEnvTemp=_get_enabled_state(interval_recording_config.env_temperature_enabled),
        IntervalPressure=_get_enabled_state(interval_recording_config.pressure_enabled),
        IntervalAltitude=_get_enabled_state(interval_recording_config.altitude_enabled),
        IntervalHumidity=_get_enabled_state(interval_recording_config.humidity_enabled),
        IntervalDistance=_get_enabled_state(interval_recording_config.distance_enabled),
        IntervalLumen=_get_enabled_state(interval_recording_config.lumen_enabled),
        IntervalVisibleEMS=_get_enabled_state(interval_recording_config.colour_enabled),
        IntervalUltraViolet=_get_enabled_state(interval_recording_config.ultra_violet_enabled),
        IntervalGAS=_get_enabled_state(interval_recording_config.gas_enabled),
        IntervalPM=_get_enabled_state(interval_recording_config.particulate_matter_enabled),
        IntervalAccelerometer=_get_enabled_state(interval_recording_config.accelerometer_enabled),
        IntervalMagnetometer=_get_enabled_state(interval_recording_config.magnetometer_enabled),
        IntervalGyroscope=_get_enabled_state(interval_recording_config.gyroscope_enabled),
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


def _get_enabled_state(state):
    if state:
        return "Enabled"
    return "Disabled"


@html_sensor_info_readings_routes.route("/TestSensor")
@html_sensor_info_readings_routes.route("/SensorReadings")
def html_sensors_readings():
    logger.network_logger.debug("** Sensor Readings accessed from " + str(request.remote_addr))
    db_v = app_cached_variables.database_variables
    try:
        cpu_temp = sensor_access.get_cpu_temperature()
        if cpu_temp is not None:
            cpu_temp = cpu_temp[db_v.system_temperature]

        raw_temp = sensor_access.get_environment_temperature(temperature_correction=False)
        adjusted_temp = sensor_access.get_environment_temperature()
        if raw_temp is not None:
            raw_temp = raw_temp[db_v.env_temperature]
            adjusted_temp = adjusted_temp[db_v.env_temperature]

        temp_offset = "Disabled"
        if app_config_access.primary_config.enable_custom_temp:
            temp_offset = str(app_config_access.primary_config.temperature_offset) + " °C"
        temp_comp = "Disabled"
        if app_config_access.primary_config.enable_temperature_comp_factor:
            temp_comp = str(app_config_access.primary_config.temperature_comp_factor)

        pressure = sensor_access.get_pressure()
        if pressure is not None:
            pressure = pressure[db_v.pressure]

        altitude = sensor_access.get_altitude()
        if altitude is not None:
            altitude = altitude[db_v.altitude]

        humidity = sensor_access.get_humidity()
        if humidity is not None:
            humidity = humidity[db_v.humidity]

        distance = sensor_access.get_distance()
        if distance is not None:
            distance = distance[db_v.distance]

        gas_readings = sensor_access.get_gas()
        gas_index = None
        gas_oxidising = None
        gas_reducing = None
        gas_nh3 = None
        if gas_readings is not None:
            if db_v.gas_resistance_index in gas_readings:
                gas_index = gas_readings[db_v.gas_resistance_index]
            if db_v.gas_oxidising in gas_readings:
                gas_oxidising = gas_readings[db_v.gas_oxidising]
            if db_v.gas_reducing in gas_readings:
                gas_reducing = gas_readings[db_v.gas_reducing]
            if db_v.gas_nh3 in gas_readings:
                gas_nh3 = gas_readings[db_v.gas_nh3]

        pm_readings = sensor_access.get_particulate_matter()
        pm_1 = None
        pm_2_5 = None
        pm_4 = None
        pm_10 = None
        if pm_readings is not None:
            if db_v.particulate_matter_1 in pm_readings:
                pm_1 = pm_readings[db_v.particulate_matter_1]
            if db_v.particulate_matter_2_5 in pm_readings:
                pm_2_5 = pm_readings[db_v.particulate_matter_2_5]
            if db_v.particulate_matter_4 in pm_readings:
                pm_4 = pm_readings[db_v.particulate_matter_4]
            if db_v.particulate_matter_10 in pm_readings:
                pm_10 = pm_readings[db_v.particulate_matter_10]

        lumen = sensor_access.get_lumen()
        if lumen is not None:
            lumen = lumen[db_v.lumen]

        red = None
        orange = None
        yellow = None
        green = None
        blue = None
        violet = None
        colors = sensor_access.get_ems_colors()
        if colors is not None:
            if db_v.red in colors:
                red = colors[db_v.red]
            if db_v.orange in colors:
                orange = colors[db_v.orange]
            if db_v.yellow in colors:
                yellow = colors[db_v.yellow]
            if db_v.green in colors:
                green = colors[db_v.green]
            if db_v.blue in colors:
                blue = colors[db_v.blue]
            if db_v.violet in colors:
                violet = colors[db_v.violet]

        uv_readings = sensor_access.get_ultra_violet()
        uv_a = None
        uv_b = None
        if uv_readings is not None:
            if db_v.ultra_violet_a in uv_readings:
                uv_a = uv_readings[db_v.ultra_violet_a]
            if db_v.ultra_violet_b in uv_readings:
                uv_b = uv_readings[db_v.ultra_violet_b]

        utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
        current_datetime = (datetime.utcnow() + timedelta(hours=utc0_hour_offset))

        return render_template(
            "sensor_readings.html",
            PageURL="/SensorReadings",
            RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
            RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
            URLRedirect="SensorReadings",
            HostName=str(app_cached_variables.hostname),
            IPAddress=str(app_cached_variables.ip),
            DateTime=str(current_datetime.strftime("%Y-%m-%d %H:%M:%S")) + " UTC" + str(utc0_hour_offset),
            SystemUptime=str(sensor_access.get_uptime_str()),
            CPUTemperature=str(cpu_temp) + " °C",
            RAWEnvTemperature=str(raw_temp) + " °C",
            AdjustedEnvTemperature=str(adjusted_temp) + " °C",
            EnvTemperatureOffset=str(temp_offset),
            EnvTemperatureComp=str(temp_comp),
            Pressure=str(pressure) + " hPa",
            Altitude=str(altitude) + " Meters",
            Humidity=str(humidity) + " %RH",
            Distance=str(distance) + " ?",
            GasResistanceIndex=str(gas_index) + " kΩ",
            GasOxidising=str(gas_oxidising) + " kΩ",
            GasReducing=str(gas_reducing) + " kΩ",
            GasNH3=str(gas_nh3) + " kΩ",
            PM1=str(pm_1) + " µg/m³",
            PM25=str(pm_2_5) + " µg/m³",
            PM4=str(pm_4) + " µg/m³",
            PM10=str(pm_10) + " µg/m³",
            Lumen=str(lumen) + " lm",
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
