from time import strftime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from sensor_modules import sensor_access

html_sensor_info_readings_routes = Blueprint("html_sensor_info_readings_routes", __name__)


@html_sensor_info_readings_routes.route("/About")
@html_sensor_info_readings_routes.route("/SensorInformation")
def html_system_information():
    if app_config_access.current_config.enable_debug_logging:
        debug_logging = True
    else:
        debug_logging = False

    if app_config_access.current_config.enable_display:
        display_enabled = True
    else:
        display_enabled = False

    if app_config_access.current_config.enable_interval_recording:
        interval_recording = True
    else:
        interval_recording = False

    if app_config_access.current_config.enable_trigger_recording:
        trigger_recording = True
    else:
        trigger_recording = False

    if app_config_access.current_config.enable_custom_temp:
        custom_temp_enabled = True
    else:
        custom_temp_enabled = False

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
                           IntervalDelay=app_config_access.current_config.sleep_duration_interval,
                           TriggerRecording=trigger_recording,
                           ManualTemperatureEnabled=custom_temp_enabled,
                           CurrentTemperatureOffset=app_config_access.current_config.temperature_offset,
                           InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
                           SQLDatabaseLocation=file_locations.sensor_database,
                           SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
                           SQLDatabaseSize=sensor_access.get_db_size(),
                           NumberNotes=sensor_access.get_db_notes_count())


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
                           HostName=app_cached_variables.hostname,
                           IPAddress=app_cached_variables.ip,
                           DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                           SystemUptime=sensor_access.get_uptime_str(),
                           CPUTemperature=sensor_access.get_cpu_temperature(),
                           RAWEnvTemperature=raw_temp,
                           AdjustedEnvTemperature=adjusted_temp,
                           EnvTemperatureOffset=temp_offset,
                           Pressure=sensor_access.get_pressure(),
                           Altitude=sensor_access.get_altitude(),
                           Humidity=sensor_access.get_humidity(),
                           Distance=sensor_access.get_distance(),
                           GasResistanceIndex=sensor_access.get_gas_resistance_index(),
                           GasOxidising=sensor_access.get_gas_oxidised(),
                           GasReducing=sensor_access.get_gas_reduced(),
                           GasNH3=sensor_access.get_gas_nh3(),
                           PM1=sensor_access.get_particulate_matter_1(),
                           PM25=sensor_access.get_particulate_matter_2_5(),
                           PM10=sensor_access.get_particulate_matter_10(),
                           Lumen=sensor_access.get_lumen(),
                           Red=red,
                           Orange=orange,
                           Yellow=yellow,
                           Green=green,
                           Blue=blue,
                           Violet=violet,
                           UVA=sensor_access.get_ultra_violet_a(),
                           UVB=sensor_access.get_ultra_violet_b(),
                           Acc=sensor_access.get_accelerometer_xyz(),
                           Mag=sensor_access.get_magnetometer_xyz(),
                           Gyro=sensor_access.get_gyroscope_xyz())


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
