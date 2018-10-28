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
import operations_logger

round_decimal_to = 5


class CreateEnviro:
    def __init__(self):
        self.enviro_import = __import__('envirophat')

    def temperature(self):
        try:
            env_temp = float(self.enviro_import.weather.temperature())
            operations_logger.sensors_logger.debug("Pimoroni Enviro Temperature - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni Enviro Temperature - Failed - " + str(error))
            env_temp = 0
        return round(env_temp, round_decimal_to)

    def pressure(self):
        try:
            pressure_hpa = self.enviro_import.weather.pressure(unit='hPa')
            operations_logger.sensors_logger.debug("Pimoroni Enviro Pressure - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni Enviro Pressure - Failed - " + str(error))
            pressure_hpa = 0
        return int(pressure_hpa)

    def lumen(self):
        try:
            var_lumen = self.enviro_import.light.light()
            operations_logger.sensors_logger.debug("Pimoroni Enviro Lumen - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni Enviro Lumen - Failed - " + str(error))
            var_lumen = 0
        return int(var_lumen)

    def rgb(self):
        try:
            rgb_red, rgb_green, rgb_blue = self.enviro_import.light.rgb()
            operations_logger.sensors_logger.debug("Pimoroni Enviro RGB - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni Enviro RGB - Failed - " + str(error))
            rgb_red, rgb_green, rgb_blue = 0, 0, 0
        return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)

    def magnetometer_xyz(self):
        try:
            mag_x, mag_y, mag_z = self.enviro_import.motion.magnetometer()
            operations_logger.sensors_logger.debug("Pimoroni Enviro Magnetometer XYZ - OK")
        except Exception as error:
            mag_x, mag_y, mag_z = 0, 0, 0
            operations_logger.sensors_logger.error("Pimoroni Enviro Magnetometer XYZ - Failed - " + str(error))
        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        try:
            acc_x, acc_y, acc_z = self.enviro_import.motion.accelerometer()
            operations_logger.sensors_logger.debug("Pimoroni Enviro Accelerometer XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni Enviro Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0, 0, 0
        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
