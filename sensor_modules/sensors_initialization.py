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
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import software_version
from sensor_modules import linux_os
from sensor_modules import pimoroni_as7262
from sensor_modules import pimoroni_bh1745
from sensor_modules import pimoroni_bme680
from sensor_modules import pimoroni_bmp280
from sensor_modules import pimoroni_enviro
from sensor_modules import pimoroni_enviroplus
from sensor_modules import pimoroni_lsm303d
from sensor_modules import pimoroni_icm20948
from sensor_modules import pimoroni_ltr_559
from sensor_modules import pimoroni_vl53l1x
from sensor_modules import pimoroni_veml6075
from sensor_modules import raspberry_pi_sensehat
from sensor_modules import raspberry_pi_system
from sensor_modules import pimoroni_11x7_led_matrix
from sensor_modules import pimoroni_0_96_spi_colour_lcd
from sensor_modules import pimoroni_1_12_mono_oled

if software_version.old_version == software_version.version:
    logger.primary_logger.info(" -- Initializing Sensors ...")
    # Initialize sensor access, based on installed sensors file
    if configuration_main.installed_sensors.linux_system:
        try:
            os_sensor_access = linux_os.CreateLinuxSystem()
        except Exception as sensor_error:
            logger.primary_logger.error("Linux OS Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.raspberry_pi_zero_w or \
            configuration_main.installed_sensors.raspberry_pi_3b_plus:
        try:
            system_sensor_access = raspberry_pi_system.CreateRPSystem()
        except Exception as sensor_error:
            logger.primary_logger.warning("Raspberry Pi Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        try:
            rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
        except Exception as sensor_error:
            logger.primary_logger.warning("RP SenseHAT Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bh1745:
        try:
            pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BH1745 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_as7262:
        try:
            pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni AS7262 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bme680:
        if configuration_main.installed_sensors.pimoroni_bmp280:
            logger.primary_logger.warning("Pimoroni BME680 cannot be installed if the BMP280 is installed. " +
                                          "Skipping BME680 & BMP280 - Please Remove the BMP280 OR the BME680 " +
                                          "physically and from the Installed Sensors configuration")
            configuration_main.installed_sensors.pimoroni_bme680 = 0
            configuration_main.installed_sensors.pimoroni_bmp280 = 0
        else:
            try:
                pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
            except Exception as sensor_error:
                logger.primary_logger.warning("Pimoroni BME680 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bmp280:
        try:
            pimoroni_bmp280_sensor_access = pimoroni_bmp280.CreateBMP280()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BMP280 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviro:
        try:
            pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni EnviroPHAT Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviroplus:
        try:
            pimoroni_enviroplus_sensor_access = pimoroni_enviroplus.CreateEnviroPlus()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni Enviro+ Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        try:
            pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LSM303D Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_icm20948:
        try:
            pimoroni_icm20948_sensor_access = pimoroni_icm20948.CreateICM20948()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni ICM20948 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_ltr_559:
        try:
            pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LTR559 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_vl53l1x:
        try:
            pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VL53L1X Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_veml6075:
        try:
            pimoroni_veml6075_sensor_access = pimoroni_veml6075.CreateVEML6075()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VEML6075 Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_matrix_11x7:
        try:
            pimoroni_matrix_11x7_sensor_access = pimoroni_11x7_led_matrix.CreateMatrix11x7()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni 11x7 LED Matrix Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_st7735:
        try:
            pimoroni_st7735_sensor_access = pimoroni_0_96_spi_colour_lcd.CreateST7735()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni Pimoroni 10.96'' SPI Colour LCD (160x80) Sensor Failed - " + str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_mono_oled_luma:
        try:
            pimoroni_mono_oled_luma_sensor_access = pimoroni_1_12_mono_oled.CreateLumaOLED()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni 1.12'' Mono OLED (128x128, white/black) Sensor Failed - " + str(sensor_error))

else:
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    pass
