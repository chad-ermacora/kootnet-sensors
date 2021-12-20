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
from operations_modules import app_cached_variables
from operations_modules.http_generic_network import get_sensor_reading_error_msg, get_http_sensor_reading
from configuration_modules import app_config_access

html_live_graph_sensor_wrappers_routes = Blueprint("html_live_graph_sensor_wrappers_routes", __name__)
database_variables = app_cached_variables.database_variables
db_gc = app_cached_variables.network_get_commands


@html_live_graph_sensor_wrappers_routes.route("/LGWGetSensorID")
def lgw_get_sensor_id():
    logger.network_logger.debug("LGW ** Sensor's ID sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.sensor_id)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetHostName")
def lgw_get_hostname():
    logger.network_logger.debug("LGW ** Sensor's HostName sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.sensor_name)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetSystemDateTime")
def lgw_get_system_date_time():
    logger.network_logger.debug("LGW ** Sensor's Date & Time sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_date_time)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetSystemUptime")
def lgw_get_system_uptime():
    logger.network_logger.debug("LGW ** Sensor's Uptime sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_uptime)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetOSVersion")
def lgw_get_operating_system_version():
    logger.network_logger.debug("LGW ** Sensor's Operating System Version sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.os_version)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetSensorVersion")
def lgw_get_sensor_program_version():
    logger.network_logger.debug("LGW ** Sensor's Version sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.program_version)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetRAMUsed")
def lgw_get_ram_usage_percent():
    logger.network_logger.debug("LGW ** Sensor's RAM % used sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_ram_used)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetRAMFree")
def lgw_get_ram_free():
    logger.network_logger.debug("LGW ** Sensor's Free RAM sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_ram_free)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetRAMTotal")
def lgw_get_ram_total():
    logger.network_logger.debug("LGW ** Sensor's Total RAM amount sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_ram_total)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetUsedDiskSpace")
def lgw_get_disk_usage_gb():
    logger.network_logger.debug("LGW ** Sensor's Used Disk Space as GBs sent to " + str(request.remote_addr))
    return "NA"


@html_live_graph_sensor_wrappers_routes.route("/LGWGetFreeDiskSpace")
def lgw_get_disk_free_gb():
    logger.network_logger.debug("LGW ** Sensor's Free Disk Space as GBs sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_disk_space_free)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetProgramLastUpdated")
def lgw_get_sensor_program_last_updated():
    logger.network_logger.debug("LGW ** Sensor's Program Last Updated sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.program_last_updated)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetSystemUptimeMinutes")
def lgw_get_system_uptime_minutes():
    logger.network_logger.debug("LGW ** Sensor's Uptime in minutes sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.system_uptime_minutes)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetCPUTemperature")
def lgw_get_cpu_temperature():
    logger.network_logger.debug("LGW ** Sensor's CPU Temperature sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.cpu_temp)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetEnvTemperature")
def lgw_get_env_temperature():
    logger.network_logger.debug("LGW ** Environment Temperature sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.environmental_temp)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetTempOffsetEnv")
def lgw_get_env_temp_offset():
    logger.network_logger.debug("LGW ** Environment Temperature Offset sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.env_temp_offset)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetPressure")
def lgw_get_pressure():
    logger.network_logger.debug("LGW ** Pressure sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.pressure)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAltitude")
def lgw_get_altitude():
    logger.network_logger.debug("LGW ** Altitude sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.altitude)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetHumidity")
def lgw_get_humidity():
    logger.network_logger.debug("LGW ** Humidity sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.humidity)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetDistance")
def lgw_get_distance():
    logger.network_logger.debug("LGW ** Distance sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.distance)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetDewPoint")
def lgw_get_dew_point():
    logger.network_logger.debug("LGW ** Dew Point sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.dew_point)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAllGas")
def lgw_get_all_gas():
    logger.network_logger.debug("LGW ** GAS Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.all_gas)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGasResistanceIndex")
def lgw_get_gas_index():
    logger.network_logger.debug("LGW ** GAS Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gas_resistance_index)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGasOxidising")
def lgw_get_gas_oxidising():
    logger.network_logger.debug("LGW ** GAS Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gas_oxidising)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGasReducing")
def lgw_get_gas_reducing():
    logger.network_logger.debug("LGW ** GAS Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gas_reducing)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGasNH3")
def lgw_get_gas_nh3():
    logger.network_logger.debug("LGW ** GAS Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gas_nh3)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAllParticulateMatter")
def lgw_get_all_particulate_matter():
    logger.network_logger.debug("LGW ** Particulate Matter Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.all_particulate_matter)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetParticulateMatter1")
def lgw_get_particulate_matter_1():
    logger.network_logger.debug("LGW ** Particulate Matter Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.particulate_matter_1)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetParticulateMatter2_5")
def lgw_get_particulate_matter_2_5():
    logger.network_logger.debug("LGW ** Particulate Matter Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.particulate_matter_2_5)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetParticulateMatter4")
def lgw_get_particulate_matter_4():
    logger.network_logger.debug("LGW ** Particulate Matter Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.particulate_matter_4)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetParticulateMatter10")
def lgw_get_particulate_matter_10():
    logger.network_logger.debug("LGW ** Particulate Matter Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.particulate_matter_10)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetLumen")
def lgw_get_lumen():
    logger.network_logger.debug("LGW ** Lumen sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.lumen)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetEMSColors")
def lgw_get_ems_colors():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.electromagnetic_spectrum)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetRed")
def lgw_get_ems_red():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.red)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetOrange")
def lgw_get_ems_orange():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.orange)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetYellow")
def lgw_get_ems_yellow():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.yellow)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGreen")
def lgw_get_ems_green():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.green)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetBlue")
def lgw_get_ems_blue():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.blue)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetViolet")
def lgw_get_ems_violet():
    logger.network_logger.debug("LGW ** Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.violet)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAllUltraViolet")
def lgw_get_all_ultra_violet():
    logger.network_logger.debug("LGW ** Ultra Violet Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.all_ultra_violet)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetUltraVioletIndex")
def lgw_get_ultra_violet_index():
    logger.network_logger.debug("LGW ** Ultra Violet Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.ultra_violet_index)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetUltraVioletA")
def lgw_get_ultra_violet_a():
    logger.network_logger.debug("LGW ** Ultra Violet Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.ultra_violet_a)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetUltraVioletB")
def lgw_get_ultra_violet_b():
    logger.network_logger.debug("LGW ** Ultra Violet Sensors sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.ultra_violet_b)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAccelerometerXYZ")
def lgw_get_acc_xyz():
    logger.network_logger.debug("LGW ** Accelerometer XYZ sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.accelerometer_xyz)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAccX")
def lgw_get_acc_x():
    logger.network_logger.debug("LGW ** Accelerometer X sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.acc_x)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAccY")
def lgw_get_acc_y():
    logger.network_logger.debug("LGW ** Accelerometer Y sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.acc_y)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetAccZ")
def lgw_get_acc_z():
    logger.network_logger.debug("LGW ** Accelerometer Z sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.acc_z)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetMagnetometerXYZ")
def lgw_get_mag_xyz():
    logger.network_logger.debug("LGW ** Magnetometer XYZ sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.magnetometer_xyz)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetMagX")
def lgw_get_mag_x():
    logger.network_logger.debug("LGW ** Magnetometer X sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.mag_x)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetMagY")
def lgw_get_mag_y():
    logger.network_logger.debug("LGW ** Magnetometer Y sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.mag_y)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetMagZ")
def lgw_get_mag_z():
    logger.network_logger.debug("LGW ** Magnetometer Z sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.mag_z)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGyroscopeXYZ")
def lgw_get_gyro_xyz():
    logger.network_logger.debug("LGW ** Gyroscope XYZ sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gyroscope_xyz)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGyroX")
def lgw_get_gyro_x():
    logger.network_logger.debug("LGW ** Gyroscope X sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gyro_x)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGyroY")
def lgw_get_gyro_y():
    logger.network_logger.debug("LGW ** Gyroscope Y sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gyro_y)


@html_live_graph_sensor_wrappers_routes.route("/LGWGetGyroZ")
def lgw_get_gyro_z():
    logger.network_logger.debug("LGW ** Gyroscope Z sent to " + str(request.remote_addr))
    return _get_sensor_reading(db_gc.gyro_z)


def _get_sensor_reading(sensor_get_command):
    no_sensor_return = "NoSensor"
    graph_sensor_address = app_config_access.live_graphs_config.graph_sensor_address
    remote_reading = get_http_sensor_reading(graph_sensor_address, http_command=sensor_get_command, timeout=0.5)
    if remote_reading == get_sensor_reading_error_msg:
        return no_sensor_return, 503
    elif remote_reading == no_sensor_return:
        return no_sensor_return, 404
    return remote_reading
