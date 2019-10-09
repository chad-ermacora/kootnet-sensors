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
from operations_modules import app_config_access
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
    # Initialize sensor access, based on installed sensors file
    if app_config_access.current_platform == "Linux":
        operating_system_a = linux_os.CreateLinuxSystem()
    if app_config_access.installed_sensors.raspberry_pi:
        raspberry_pi_a = raspberry_pi_system.CreateRPSystem()
    if app_config_access.installed_sensors.raspberry_pi_sense_hat:
        rp_sense_hat_a = raspberry_pi_sensehat.CreateRPSenseHAT()
    if app_config_access.installed_sensors.pimoroni_bh1745:
        pimoroni_bh1745_a = pimoroni_bh1745.CreateBH1745()
    if app_config_access.installed_sensors.pimoroni_as7262:
        pimoroni_as7262_a = pimoroni_as7262.CreateAS7262()
    if app_config_access.installed_sensors.pimoroni_bme680:
        if app_config_access.installed_sensors.pimoroni_bmp280:
            message = "Pimoroni BME680 cannot be installed if the BMP280 is installed. " + \
                      "Skipping BME680 & BMP280 - Please Remove the BMP280 OR the BME680 " + \
                      "physically and from the Installed Sensors configuration"
            logger.sensors_logger.warning(message)
            app_config_access.installed_sensors.pimoroni_bme680 = 0
            app_config_access.installed_sensors.pimoroni_bmp280 = 0
        else:
            pimoroni_bme680_a = pimoroni_bme680.CreateBME680()
    if app_config_access.installed_sensors.pimoroni_bmp280:
        pimoroni_bmp280_a = pimoroni_bmp280.CreateBMP280()
    if app_config_access.installed_sensors.pimoroni_enviro:
        pimoroni_enviro_a = pimoroni_enviro.CreateEnviro()
    if app_config_access.installed_sensors.pimoroni_enviroplus:
        pimoroni_enviroplus_a = pimoroni_enviroplus.CreateEnviroPlus()
    if app_config_access.installed_sensors.pimoroni_lsm303d:
        pimoroni_lsm303d_a = pimoroni_lsm303d.CreateLSM303D()
    if app_config_access.installed_sensors.pimoroni_icm20948:
        pimoroni_icm20948_a = pimoroni_icm20948.CreateICM20948()
    if app_config_access.installed_sensors.pimoroni_ltr_559:
        pimoroni_ltr_559_a = pimoroni_ltr_559.CreateLTR559()
    if app_config_access.installed_sensors.pimoroni_vl53l1x:
        pimoroni_vl53l1x_a = pimoroni_vl53l1x.CreateVL53L1X()
    if app_config_access.installed_sensors.pimoroni_veml6075:
        pimoroni_veml6075_a = pimoroni_veml6075.CreateVEML6075()
    if app_config_access.installed_sensors.pimoroni_matrix_11x7:
        pimoroni_matrix_11x7_a = pimoroni_11x7_led_matrix.CreateMatrix11x7()
    if app_config_access.installed_sensors.pimoroni_st7735:
        pimoroni_st7735_a = pimoroni_0_96_spi_colour_lcd.CreateST7735()
    if app_config_access.installed_sensors.pimoroni_mono_oled_luma:
        pimoroni_mono_oled_luma_a = pimoroni_1_12_mono_oled.CreateLumaOLED()
    logger.primary_logger.info(" -- Sensors Initialized")
else:
    # Skip Sensor Initializations on upgrade
    # They won't be used & program will be restarted when the upgrade is done.
    pass
