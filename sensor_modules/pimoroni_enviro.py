""""
This module is for the Pimoroni Enviro pHAT
It Retrieves & Returns Sensor data to be written to the DB

BMP280 temperature/pressure sensor
TCS3472 light and rgb colour sensor
Two LEDs for illumination
LSM303D accelerometer/magnetometer sensor
ADS1015 4-channel 3.3v, analog to digital sensor (ADC)

pip3 install envirophat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateEnviro:
    """ Creates Function access to the Pimoroni Enviro pHAT. """

    def __init__(self):
        try:
            self.enviro_import = __import__('envirophat')
            self.enviro_import.weather.temperature()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro pHAT Initialization Failed - " + str(error))
            app_config_access.installed_sensors.pimoroni_enviro = 0

    def temperature(self):
        """ Returns Temperature as a Float. """
        try:
            env_temp = float(self.enviro_import.weather.temperature())
            logger.sensors_logger.debug("Pimoroni Enviro Temperature - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro Temperature - Failed - " + str(error))
            env_temp = 0.0
        return round(env_temp, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        try:
            pressure_hpa = self.enviro_import.weather.pressure(unit='hPa')
            logger.sensors_logger.debug("Pimoroni Enviro Pressure - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro Pressure - Failed - " + str(error))
            pressure_hpa = 0
        return int(pressure_hpa)

    def lumen(self):
        """ Returns Lumen as a Integer. """
        try:
            var_lumen = self.enviro_import.light.light()
            logger.sensors_logger.debug("Pimoroni Enviro Lumen - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro Lumen - Failed - " + str(error))
            var_lumen = 0
        return int(var_lumen)

    def ems(self):
        """ Returns Electromagnetic Spectrum of Red, Green, Blue as a list of Floats. """
        try:
            rgb_red, rgb_green, rgb_blue = self.enviro_import.light.rgb()
            logger.sensors_logger.debug("Pimoroni Enviro RGB - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro RGB - Failed - " + str(error))
            rgb_red, rgb_green, rgb_blue = 0.0, 0.0, 0.0
        return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)

    def magnetometer_xyz(self):
        """ Returns Magnetometer X, Y, Z as Floats. """
        try:
            mag_x, mag_y, mag_z = self.enviro_import.motion.magnetometer()
            logger.sensors_logger.debug("Pimoroni Enviro Magnetometer XYZ - OK")
        except Exception as error:
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0
            logger.sensors_logger.error("Pimoroni Enviro Magnetometer XYZ - Failed - " + str(error))
        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        """ Returns Accelerometer X, Y, Z as Floats. """
        try:
            acc_x, acc_y, acc_z = self.enviro_import.motion.accelerometer()
            logger.sensors_logger.debug("Pimoroni Enviro Accelerometer XYZ - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0
        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
