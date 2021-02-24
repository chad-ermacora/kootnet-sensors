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
from flask import Blueprint, request
from operations_modules import logger
from operations_modules.app_cached_variables import command_data_separator, database_variables
from configuration_modules import app_config_access
from sensor_recording_modules.recording_interval import get_interval_sensor_readings
from sensor_modules import sensor_access

html_sensor_readings_routes = Blueprint("html_sensor_readings_routes", __name__)


@html_sensor_readings_routes.route("/GetIntervalSensorReadings")
def get_interval_readings():
    logger.network_logger.debug("* Interval Sensor Readings sent to " + str(request.remote_addr))
    sensor_readings = get_interval_sensor_readings()
    readings_name = ""
    readings_data = ""
    for index, reading in sensor_readings.items():
        readings_name += str(index) + ","
        readings_data += str(reading) + ","
    readings_name = readings_name[:-1]
    readings_data = readings_data[:-1]
    return str(readings_name + command_data_separator + readings_data)


@html_sensor_readings_routes.route("/GetSensorsLatency")
def get_sensors_latency():
    logger.network_logger.debug("* Sensor Latency sent to " + str(request.remote_addr))
    latency_dic = sensor_access.get_sensors_latency()
    try:
        text_part1 = ""
        text_part2 = ""
        beginning_part = []
        end_part = []
        for name, entry in latency_dic.items():
            if entry is not None:
                beginning_part.append(name)
                end_part.append(entry)
        for name, entry in zip(beginning_part, end_part):
            text_part1 += str(name) + ","
            text_part2 += str(entry) + ","
        text_part1 = text_part1[:-1]
        text_part2 = text_part2[:-1]
    except Exception as error:
        return "Error" + sensor_access.command_data_separator + str(error)
    return text_part1 + sensor_access.command_data_separator + text_part2


@html_sensor_readings_routes.route("/GetCPUTemperature")
def get_cpu_temperature():
    logger.network_logger.debug("* Sensor's CPU Temperature sent to " + str(request.remote_addr))
    cpu_temp = sensor_access.get_cpu_temperature()
    if cpu_temp is not None:
        cpu_temp = cpu_temp[database_variables.system_temperature]
    return str(cpu_temp)


@html_sensor_readings_routes.route("/GetEnvTemperature")
def get_env_temperature():
    logger.network_logger.debug("* Environment Temperature sent to " + str(request.remote_addr))
    env_temp = sensor_access.get_environment_temperature()
    if env_temp is not None:
        env_temp = env_temp[database_variables.env_temperature]
    return str(env_temp)


@html_sensor_readings_routes.route("/GetTempOffsetEnv")
def get_env_temp_offset():
    logger.network_logger.debug("* Environment Temperature Offset sent to " + str(request.remote_addr))
    return str(app_config_access.primary_config.temperature_offset)


@html_sensor_readings_routes.route("/GetPressure")
def get_pressure():
    logger.network_logger.debug("* Pressure sent to " + str(request.remote_addr))
    reading = sensor_access.get_pressure()
    if reading is not None:
        reading = reading[database_variables.pressure]
    return str(reading)


@html_sensor_readings_routes.route("/GetAltitude")
def get_altitude():
    logger.network_logger.debug("* Altitude sent to " + str(request.remote_addr))
    reading = sensor_access.get_altitude()
    if reading is not None:
        reading = reading[database_variables.altitude]
    return str(reading)


@html_sensor_readings_routes.route("/GetHumidity")
def get_humidity():
    logger.network_logger.debug("* Humidity sent to " + str(request.remote_addr))
    reading = sensor_access.get_humidity()
    if reading is not None:
        reading = reading[database_variables.humidity]
    return str(reading)


@html_sensor_readings_routes.route("/GetDistance")
def get_distance():
    logger.network_logger.debug("* Distance sent to " + str(request.remote_addr))
    reading = sensor_access.get_distance()
    if reading is not None:
        reading = reading[database_variables.distance]
    return str(reading)


@html_sensor_readings_routes.route("/GetAllGas")
def get_all_gas():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas())


@html_sensor_readings_routes.route("/GetAllParticulateMatter")
def get_all_particulate_matter():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter())


@html_sensor_readings_routes.route("/GetLumen")
def get_lumen():
    logger.network_logger.debug("* Lumen sent to " + str(request.remote_addr))
    reading = sensor_access.get_lumen()
    if reading is not None:
        reading = reading[database_variables.lumen]
    return str(reading)


@html_sensor_readings_routes.route("/GetEMSColors")
def get_ems_colors():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors())


@html_sensor_readings_routes.route("/GetAllUltraViolet")
def get_all_ultra_violet():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet())


@html_sensor_readings_routes.route("/GetAccelerometerXYZ")
def get_acc_xyz():
    logger.network_logger.debug("* Accelerometer XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_accelerometer_xyz())


@html_sensor_readings_routes.route("/GetMagnetometerXYZ")
def get_mag_xyz():
    logger.network_logger.debug("* Magnetometer XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_magnetometer_xyz())


@html_sensor_readings_routes.route("/GetGyroscopeXYZ")
def get_gyro_xyz():
    logger.network_logger.debug("* Gyroscope XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_gyroscope_xyz())
