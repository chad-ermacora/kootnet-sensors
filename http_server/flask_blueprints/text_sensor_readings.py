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
from sensor_modules import sensor_access

html_sensor_readings_routes = Blueprint("html_sensor_readings_routes", __name__)


@html_sensor_readings_routes.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@html_sensor_readings_routes.route("/GetAllSensorReadings")
def get_all_sensor_readings():
    logger.network_logger.debug("* All Sensor Readings sent to " + str(request.remote_addr))
    sensor_readings = sensor_access.get_all_available_sensor_readings(include_system_info=True)
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
        return "Error" + command_data_separator + str(error)
    return text_part1 + command_data_separator + text_part2


@html_sensor_readings_routes.route("/GetSystemUptimeMinutes")
def get_system_uptime_minutes():
    logger.network_logger.debug("* Sensor's Uptime in minutes sent to " + str(request.remote_addr))
    return str(sensor_access.get_uptime_minutes()[database_variables.sensor_uptime])


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
    return str(app_config_access.sensor_offsets.temperature_offset)


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


@html_sensor_readings_routes.route("/GetDewPoint")
def get_dew_point():
    logger.network_logger.debug("* Dew Point sent to " + str(request.remote_addr))
    reading = sensor_access.get_dew_point()
    if reading is not None:
        reading = reading[database_variables.dew_point]
    return str(reading)


@html_sensor_readings_routes.route("/GetAllGas")
def get_all_gas():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas())


@html_sensor_readings_routes.route("/GetGasResistanceIndex")
def get_gas_index():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas()[database_variables.gas_resistance_index])


@html_sensor_readings_routes.route("/GetGasOxidising")
def get_gas_oxidising():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas()[database_variables.gas_oxidising])


@html_sensor_readings_routes.route("/GetGasReducing")
def get_gas_reducing():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas()[database_variables.gas_reducing])


@html_sensor_readings_routes.route("/GetGasNH3")
def get_gas_nh3():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas()[database_variables.gas_nh3])


@html_sensor_readings_routes.route("/GetAllParticulateMatter")
def get_all_particulate_matter():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter())


@html_sensor_readings_routes.route("/GetParticulateMatter1")
def get_particulate_matter_1():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter()[database_variables.particulate_matter_1])


@html_sensor_readings_routes.route("/GetParticulateMatter2_5")
def get_particulate_matter_2_5():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter()[database_variables.particulate_matter_2_5])


@html_sensor_readings_routes.route("/GetParticulateMatter4")
def get_particulate_matter_4():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter()[database_variables.particulate_matter_4])


@html_sensor_readings_routes.route("/GetParticulateMatter10")
def get_particulate_matter_10():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter()[database_variables.particulate_matter_10])


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


@html_sensor_readings_routes.route("/GetRed")
def get_ems_red():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.red])


@html_sensor_readings_routes.route("/GetOrange")
def get_ems_orange():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.orange])


@html_sensor_readings_routes.route("/GetYellow")
def get_ems_yellow():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.yellow])


@html_sensor_readings_routes.route("/GetGreen")
def get_ems_green():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.green])


@html_sensor_readings_routes.route("/GetBlue")
def get_ems_blue():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.blue])


@html_sensor_readings_routes.route("/GetViolet")
def get_ems_violet():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems_colors()[database_variables.violet])


@html_sensor_readings_routes.route("/GetAllUltraViolet")
def get_all_ultra_violet():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet())


@html_sensor_readings_routes.route("/GetUltraVioletIndex")
def get_ultra_violet_index():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet()[database_variables.ultra_violet_index])


@html_sensor_readings_routes.route("/GetUltraVioletA")
def get_ultra_violet_a():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet()[database_variables.ultra_violet_a])


@html_sensor_readings_routes.route("/GetUltraVioletB")
def get_ultra_violet_b():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet()[database_variables.ultra_violet_b])


@html_sensor_readings_routes.route("/GetAccelerometerXYZ")
def get_acc_xyz():
    logger.network_logger.debug("* Accelerometer XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_accelerometer_xyz())


@html_sensor_readings_routes.route("/GetAccX")
def get_acc_x():
    logger.network_logger.debug("* Accelerometer X sent to " + str(request.remote_addr))
    return str(sensor_access.get_accelerometer_xyz()[database_variables.acc_x])


@html_sensor_readings_routes.route("/GetAccY")
def get_acc_y():
    logger.network_logger.debug("* Accelerometer Y sent to " + str(request.remote_addr))
    return str(sensor_access.get_accelerometer_xyz()[database_variables.acc_y])


@html_sensor_readings_routes.route("/GetAccZ")
def get_acc_z():
    logger.network_logger.debug("* Accelerometer Z sent to " + str(request.remote_addr))
    return str(sensor_access.get_accelerometer_xyz()[database_variables.acc_z])


@html_sensor_readings_routes.route("/GetMagnetometerXYZ")
def get_mag_xyz():
    logger.network_logger.debug("* Magnetometer XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_magnetometer_xyz())


@html_sensor_readings_routes.route("/GetMagX")
def get_mag_x():
    logger.network_logger.debug("* Magnetometer X sent to " + str(request.remote_addr))
    return str(sensor_access.get_magnetometer_xyz()[database_variables.mag_x])


@html_sensor_readings_routes.route("/GetMagY")
def get_mag_y():
    logger.network_logger.debug("* Magnetometer Y sent to " + str(request.remote_addr))
    return str(sensor_access.get_magnetometer_xyz()[database_variables.mag_y])


@html_sensor_readings_routes.route("/GetMagZ")
def get_mag_z():
    logger.network_logger.debug("* Magnetometer Z sent to " + str(request.remote_addr))
    return str(sensor_access.get_magnetometer_xyz()[database_variables.mag_z])


@html_sensor_readings_routes.route("/GetGyroscopeXYZ")
def get_gyro_xyz():
    logger.network_logger.debug("* Gyroscope XYZ sent to " + str(request.remote_addr))
    return str(sensor_access.get_gyroscope_xyz())


@html_sensor_readings_routes.route("/GetGyroX")
def get_gyro_x():
    logger.network_logger.debug("* Gyroscope X sent to " + str(request.remote_addr))
    return str(sensor_access.get_gyroscope_xyz()[database_variables.gyro_x])


@html_sensor_readings_routes.route("/GetGyroY")
def get_gyro_y():
    logger.network_logger.debug("* Gyroscope Y sent to " + str(request.remote_addr))
    return str(sensor_access.get_gyroscope_xyz()[database_variables.gyro_y])


@html_sensor_readings_routes.route("/GetGyroZ")
def get_gyro_z():
    logger.network_logger.debug("* Gyroscope Z sent to " + str(request.remote_addr))
    return str(sensor_access.get_gyroscope_xyz()[database_variables.gyro_z])
