from time import strftime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_text_running_thread_state
from operations_modules import app_cached_variables
from operations_modules import app_config_access
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
    if app_config_access.current_config.enable_debug_logging:
        debug_logging = "Enabled"

    display_enabled = get_text_running_thread_state(app_config_access.current_config.enable_display,
                                                    app_cached_variables.mini_display_thread)

    interval_recording = get_text_running_thread_state(app_config_access.current_config.enable_interval_recording,
                                                       app_cached_variables.interval_recording_thread)

    trigger_recording = "Disabled"
    enable_trigger_button = "disabled"
    if app_config_access.current_config.enable_trigger_recording:
        trigger_recording = "Enabled"
        enable_trigger_button = ""
    if app_config_access.current_config.enable_trigger_recording:
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
                           KootnetVersion=app_config_access.software_version.version,
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
    raw_temp = sensor_access.get_sensor_temperature()
    temp_offset = app_config_access.current_config.temperature_offset
    adjusted_temp = raw_temp
    try:
        if app_config_access.current_config.enable_custom_temp:
            adjusted_temp = round(raw_temp + temp_offset, 2)
    except Exception as error:
        logger.network_logger.error("Failed to calculate Adjusted Env Temp: " + str(error))
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
                           EnvTemperatureOffset=str(temp_offset) + " °C",
                           Pressure=str(sensor_access.get_pressure()) + " hPa",
                           Altitude=str(sensor_access.get_altitude()) + " Meters",
                           Humidity=str(sensor_access.get_humidity()) + " %RH",
                           Distance=str(sensor_access.get_distance()) + " ?",
                           GasResistanceIndex=str(sensor_access.get_gas_resistance_index()) + " kΩ",
                           GasOxidising=str(sensor_access.get_gas_oxidised()) + " kΩ",
                           GasReducing=str(sensor_access.get_gas_reduced()) + " kΩ",
                           GasNH3=str(sensor_access.get_gas_nh3()) + " kΩ",
                           PM1=str(sensor_access.get_particulate_matter_1()) + " µg/m³",
                           PM25=str(sensor_access.get_particulate_matter_2_5()) + " µg/m³",
                           PM10=str(sensor_access.get_particulate_matter_10()) + " µg/m³",
                           Lumen=str(sensor_access.get_lumen()) + " lm",
                           Red=red,
                           Orange=orange,
                           Yellow=yellow,
                           Green=green,
                           Blue=blue,
                           Violet=violet,
                           UVA=sensor_access.get_ultra_violet_a(),
                           UVB=sensor_access.get_ultra_violet_b(),
                           Acc=str(sensor_access.get_accelerometer_xyz()) + " g",
                           Mag=str(sensor_access.get_magnetometer_xyz()) + " μT",
                           Gyro=str(sensor_access.get_gyroscope_xyz()) + " °/s")


def _get_ems_for_render_template():
    ems = sensor_access.get_ems()
    if ems == app_cached_variables.no_sensor_present:
        red = app_cached_variables.no_sensor_present
        orange = app_cached_variables.no_sensor_present
        yellow = app_cached_variables.no_sensor_present
        green = app_cached_variables.no_sensor_present
        blue = app_cached_variables.no_sensor_present
        violet = app_cached_variables.no_sensor_present
    else:
        if len(ems) > 3:
            red = ems[0]
            orange = ems[1]
            yellow = ems[2]
            green = ems[3]
            blue = ems[4]
            violet = ems[5]
        else:
            red = ems[0]
            orange = app_cached_variables.no_sensor_present
            yellow = app_cached_variables.no_sensor_present
            green = ems[1]
            blue = ems[2]
            violet = app_cached_variables.no_sensor_present
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
                           CPUTemperature=str(sensors_latency[0]) + " Seconds",
                           RAWEnvTemperature=str(sensors_latency[1]) + " Seconds",
                           AdjustedEnvTemperature="",
                           EnvTemperatureOffset="",
                           Pressure=str(sensors_latency[2]) + " Seconds",
                           Altitude=str(sensors_latency[3]) + " Seconds",
                           Humidity=str(sensors_latency[4]) + " Seconds",
                           Distance=str(sensors_latency[5]) + " Seconds",
                           GasResistanceIndex=str(sensors_latency[6]) + " Seconds",
                           GasOxidising=str(sensors_latency[7]) + " Seconds",
                           GasReducing=str(sensors_latency[8]) + " Seconds",
                           GasNH3=str(sensors_latency[9]) + " Seconds",
                           PM1=str(sensors_latency[10]) + " Seconds",
                           PM25=str(sensors_latency[11]) + " Seconds",
                           PM10=str(sensors_latency[12]) + " Seconds",
                           Lumen=str(sensors_latency[13]) + " Seconds",
                           Red="All Colours: " + str(sensors_latency[14]) + " Seconds",
                           Orange="",
                           Yellow="",
                           Green="",
                           Blue="",
                           Violet="",
                           UVA=str(sensors_latency[16]) + " Seconds",
                           UVB=str(sensors_latency[17]) + " Seconds",
                           Acc=str(sensors_latency[18]) + " Seconds",
                           Mag=str(sensors_latency[19]) + " Seconds",
                           Gyro=str(sensors_latency[20]) + " Seconds")
