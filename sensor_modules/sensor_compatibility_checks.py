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


    Sensor Port list - I2C Ports

    0x10 = VEML6075
    0x19 = MICS6814,
    0x23 = LTR-559,
    0x26 = MSA301,
    0x29 = VL53L1X,
    0x38/0x39 = bh1745,
    0x3C/0x3D = 1.12" Mono OLED (128x128 - white/black),
    0x48/0x49 = ADS1015 ADC,
    0x49 = AS7262,
    0x58 = SGP30,
    0x66/0x67 = MCP9600,
    0x68/0x69 = ICM20948,
    0x75/0x77 = Pimoroni 11x7 LED Matrix,
    0x76/0x77 = BME680/688, BME280, BMP280
    0x1D/0x1E = LSM303D,

"""
from operations_modules import logger
from configuration_modules import app_config_access


def check_installed_sensors_compatibility():
    if app_config_access.installed_sensors.pimoroni_bme680:
        if app_config_access.installed_sensors.pimoroni_bme280:
            log_incompatible_sensor("BME680/688", "BME280")
            app_config_access.installed_sensors.pimoroni_bme280 = 0
        if app_config_access.installed_sensors.pimoroni_bmp280:
            log_incompatible_sensor("BME680/688", "BMP280")
            app_config_access.installed_sensors.pimoroni_bmp280 = 0
        if app_config_access.installed_sensors.pimoroni_matrix_11x7:
            logger.sensors_logger.warning("11x7 Matrix display MAY share a port with BME280/BME680/BME688/BMP280")
    elif app_config_access.installed_sensors.pimoroni_bme280:
        if app_config_access.installed_sensors.pimoroni_bmp280:
            log_incompatible_sensor("BME280", "BMP280")
            app_config_access.installed_sensors.pimoroni_bmp280 = 0
        if app_config_access.installed_sensors.pimoroni_matrix_11x7:
            logger.sensors_logger.warning("11x7 Matrix display MAY share a port with BME280/BME680/BME688/BMP280")


def log_incompatible_sensor(left_enabled_sensor_name, disabled_sensor_name):
    log_msg = left_enabled_sensor_name + " and " + disabled_sensor_name + " share the same port - " \
              + disabled_sensor_name + " has been disabled"
    logger.sensors_logger.warning(log_msg)
