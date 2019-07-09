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
from time import sleep
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

logger.primary_logger.info("Sensors Access Initializing ...")

if software_version.old_version == software_version.version:
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
            sleep(5)
            try:
                system_sensor_access = raspberry_pi_system.CreateRPSystem()
                logger.primary_logger.info("Raspberry Pi Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Raspberry Pi Sensor Attempt 2 Failed Skipping Sensor - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.raspberry_pi_sense_hat:
        try:
            rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
        except Exception as sensor_error:
            logger.primary_logger.warning("RP SenseHAT Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
                logger.primary_logger.info("RP SenseHAT Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("RP SenseHAT Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bh1745:
        try:
            pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BH1745 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
                logger.primary_logger.info("Pimoroni BH1745 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BH1745 Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_as7262:
        try:
            pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni AS7262 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
                logger.primary_logger.info("Pimoroni AS7262 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni AS7262 Sensor Attempt 2 Failed Skipping Sensor - " +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bme680:
        try:
            pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BME680 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
                logger.primary_logger.info("Pimoroni BME680 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BME680 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_bmp280:
        try:
            pimoroni_bmp280_sensor_access = pimoroni_bmp280.CreateBMP280()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni BMP280 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_bmp280_sensor_access = pimoroni_bmp280.CreateBMP280()
                logger.primary_logger.info("Pimoroni BMP280 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni BMP280 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviro:
        try:
            pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni EnviroPHAT Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
                logger.primary_logger.info("Pimoroni EnviroPHAT Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni EnviroPHAT Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_enviroplus:
        try:
            pimoroni_enviroplus_sensor_access = pimoroni_enviroplus.CreateEnviroPlus()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni Enviro+ Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_enviroplus_sensor_access = pimoroni_enviroplus.CreateEnviroPlus()
                logger.primary_logger.info("Pimoroni Enviro+ Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni Enviro+ Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_lsm303d:
        try:
            pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LSM303D Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
                logger.primary_logger.info("Pimoroni LSM303D Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni LSM303D Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_icm20948:
        try:
            pimoroni_icm20948_sensor_access = pimoroni_icm20948.CreateICM20948()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni ICM20948 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_icm20948_sensor_access = pimoroni_icm20948.CreateICM20948()
                logger.primary_logger.info("Pimoroni ICM20948 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni ICM20948 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_ltr_559:
        try:
            pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni LTR559 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
                logger.primary_logger.info("Pimoroni LTR559 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni LTR559 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_vl53l1x:
        try:
            pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VL53L1X Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
                logger.primary_logger.info("Pimoroni VL53L1X Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni VL53L1X Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))

    if configuration_main.installed_sensors.pimoroni_veml6075:
        try:
            pimoroni_veml6075_sensor_access = pimoroni_veml6075.CreateVEML6075()
        except Exception as sensor_error:
            logger.primary_logger.warning("Pimoroni VEML6075 Sensor Failed - " + str(sensor_error))
            sleep(5)
            try:
                pimoroni_veml6075_sensor_access = pimoroni_veml6075.CreateVEML6075()
                logger.primary_logger.info("Pimoroni VEML6075 Sensor Attempt 2 OK")
            except Exception as sensor_error:
                logger.primary_logger.error("Pimoroni VEML6075 Sensor Attempt 2 Failed Skipping Sensor -" +
                                            "SPI or I2C Disabled? - " +
                                            str(sensor_error))
else:
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    pass
