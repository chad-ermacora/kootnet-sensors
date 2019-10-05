from flask import Blueprint, request
from operations_modules import logger
from operations_modules import app_config_access
from operations_modules.recording_interval import get_interval_sensor_readings
from sensor_modules import sensor_access

html_sensor_readings_routes = Blueprint("html_sensor_readings_routes", __name__)


# This one isn't in use yet, but there for allowing one sensor to record all readings
@html_sensor_readings_routes.route("/GetIntervalSensorReadings")
def get_interval_readings():
    logger.network_logger.debug("* Interval Sensor Readings sent to " + str(request.remote_addr))
    return str(get_interval_sensor_readings())


@html_sensor_readings_routes.route("/GetCPUTemperature")
def get_cpu_temperature():
    logger.network_logger.debug("* Sensor's CPU Temperature sent to " + str(request.remote_addr))
    return str(sensor_access.get_cpu_temperature())


@html_sensor_readings_routes.route("/GetEnvTemperature")
def get_env_temperature():
    logger.network_logger.debug("* Environment Temperature sent to " + str(request.remote_addr))
    return str(sensor_access.get_sensor_temperature())


@html_sensor_readings_routes.route("/GetTempOffsetEnv")
def get_env_temp_offset():
    logger.network_logger.debug("* Environment Temperature Offset sent to " + str(request.remote_addr))
    return str(app_config_access.current_config.temperature_offset)


@html_sensor_readings_routes.route("/GetPressure")
def get_pressure():
    logger.network_logger.debug("* Pressure sent to " + str(request.remote_addr))
    return str(sensor_access.get_pressure())


@html_sensor_readings_routes.route("/GetAltitude")
def get_altitude():
    logger.network_logger.debug("* Altitude sent to " + str(request.remote_addr))
    return str(sensor_access.get_altitude())


@html_sensor_readings_routes.route("/GetHumidity")
def get_humidity():
    logger.network_logger.debug("* Humidity sent to " + str(request.remote_addr))
    return str(sensor_access.get_humidity())


@html_sensor_readings_routes.route("/GetDistance")
def get_distance():
    logger.network_logger.debug("* Distance sent to " + str(request.remote_addr))
    return str(sensor_access.get_distance())


@html_sensor_readings_routes.route("/GetAllGas")
def get_all_gas():
    logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
    gas_return = [sensor_access.get_gas_resistance_index(),
                  sensor_access.get_gas_oxidised(),
                  sensor_access.get_gas_reduced(),
                  sensor_access.get_gas_nh3()]
    return str(gas_return)


@html_sensor_readings_routes.route("/GetGasResistanceIndex")
def get_gas_resistance_index():
    logger.network_logger.debug("* GAS Resistance Index sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas_resistance_index())


@html_sensor_readings_routes.route("/GetGasOxidised")
def get_gas_oxidised():
    logger.network_logger.debug("* GAS Oxidised sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas_oxidised())


@html_sensor_readings_routes.route("/GetGasReduced")
def get_gas_reduced():
    logger.network_logger.debug("* GAS Reduced sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas_reduced())


@html_sensor_readings_routes.route("/GetGasNH3")
def get_gas_nh3():
    logger.network_logger.debug("* GAS NH3 sent to " + str(request.remote_addr))
    return str(sensor_access.get_gas_nh3())


@html_sensor_readings_routes.route("/GetAllParticulateMatter")
def get_all_particulate_matter():
    logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
    return_pm = [sensor_access.get_particulate_matter_1(),
                 sensor_access.get_particulate_matter_2_5(),
                 sensor_access.get_particulate_matter_10()]

    return str(return_pm)


@html_sensor_readings_routes.route("/GetParticulateMatter1")
def get_particulate_matter_1():
    logger.network_logger.debug("* Particulate Matter 1 sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter_1())


@html_sensor_readings_routes.route("/GetParticulateMatter2_5")
def get_particulate_matter_2_5():
    logger.network_logger.debug("* Particulate Matter 2.5 sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter_2_5())


@html_sensor_readings_routes.route("/GetParticulateMatter10")
def get_particulate_matter_10():
    logger.network_logger.debug("* Particulate Matter 10 sent to " + str(request.remote_addr))
    return str(sensor_access.get_particulate_matter_10())


@html_sensor_readings_routes.route("/GetLumen")
def get_lumen():
    logger.network_logger.debug("* Lumen sent to " + str(request.remote_addr))
    return str(sensor_access.get_lumen())


@html_sensor_readings_routes.route("/GetEMS")
def get_visible_ems():
    logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
    return str(sensor_access.get_ems())


@html_sensor_readings_routes.route("/GetAllUltraViolet")
def get_all_ultra_violet():
    logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
    return_ultra_violet = [sensor_access.get_ultra_violet_a(), sensor_access.get_ultra_violet_b()]
    return str(return_ultra_violet)


@html_sensor_readings_routes.route("/GetUltraVioletA")
def get_ultra_violet_a():
    logger.network_logger.debug("* Ultra Violet A sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet_a())


@html_sensor_readings_routes.route("/GetUltraVioletB")
def get_ultra_violet_b():
    logger.network_logger.debug("* Ultra Violet B sent to " + str(request.remote_addr))
    return str(sensor_access.get_ultra_violet_b())


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
