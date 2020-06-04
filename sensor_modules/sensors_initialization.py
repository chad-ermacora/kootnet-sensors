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
from os import geteuid
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules import linux_os as _linux_os
from sensor_modules import kootnet_dummy_sensors as _kootnet_dummy_sensors
from sensor_modules import raspberry_pi_system as _raspberry_pi_system
from sensor_modules.pimoroni import pimoroni_enviroplus as _pimoroni_enviroplus
from sensor_modules.pimoroni import pimoroni_vl53l1x as _pimoroni_vl53l1x
from sensor_modules.pimoroni import pimoroni_enviro as _pimoroni_enviro
from sensor_modules.pimoroni import pimoroni_lsm303d as _pimoroni_lsm303d
from sensor_modules.pimoroni import pimoroni_bmp280 as _pimoroni_bmp280
from sensor_modules.pimoroni import pimoroni_bh1745 as _pimoroni_bh1745
from sensor_modules.pimoroni import pimoroni_msa301 as _pimoroni_msa301
from sensor_modules.pimoroni import pimoroni_1_12_mono_oled as _pimoroni_1_12_mono_oled
from sensor_modules.pimoroni import pimoroni_icm20948 as _pimoroni_icm20948
from sensor_modules.pimoroni import pimoroni_0_96_spi_colour_lcd as _pimoroni_0_96_spi_colour_lcd
from sensor_modules.pimoroni import pimoroni_11x7_led_matrix as _pimoroni_11x7_led_matrix
from sensor_modules.pimoroni import pimoroni_bme680 as _pimoroni_bme680
from sensor_modules.pimoroni import pimoroni_mcp9600 as _pimoroni_mcp9600
from sensor_modules.pimoroni import pimoroni_as7262 as _pimoroni_as7262
from sensor_modules.pimoroni import pimoroni_sgp30 as _pimoroni_sgp30
from sensor_modules.pimoroni import pimoroni_veml6075 as _pimoroni_veml6075
from sensor_modules.pimoroni import pimoroni_ltr_559 as _pimoroni_ltr_559
from sensor_modules import raspberry_pi_sensehat as _raspberry_pi_sense_hat
from sensor_modules import sensirion_sps30 as _sensirion_sps30
from sensor_modules.no_sensors_dummy_sensors import CreateNoSensorsDummySensor


class CreateSensorAccess:
    def __init__(self, first_start=False):
        # Initialize sensor access, based on installed sensors file
        if first_start:
            logger.primary_logger.info(" -- Initializing Sensors")
            self._set_dummy_sensors()
            self.operating_system_a = _linux_os.CreateLinuxSystem()
        else:
            logger.primary_logger.info(" -- Re-initializing Sensors")
            app_cached_variables.restart_interval_recording_thread = True
            app_cached_variables.restart_mini_display_thread = True
            app_cached_variables.restart_mqtt_publisher_thread = True
            app_cached_variables.restart_weather_underground_thread = True
            app_cached_variables.restart_luftdaten_thread = True
            app_cached_variables.restart_open_sense_map_thread = True
        if geteuid() == 0:
            installed_sensors = app_config_access.installed_sensors
            # Raspberry Pi System is created first to enable I2C, SPI & Wifi
            # This is to ensure they are enabled for the other hardware Sensors
            if installed_sensors.raspberry_pi and not self.raspberry_pi_a.initialized_sensor:
                self.raspberry_pi_a = _raspberry_pi_system.CreateRPSystem()
                self.raspberry_pi_a.initialized_sensor = True
            if installed_sensors.raspberry_pi_sense_hat and not self.rp_sense_hat_a.initialized_sensor:
                self.rp_sense_hat_a = _raspberry_pi_sense_hat.CreateRPSenseHAT()
                self.rp_sense_hat_a.initialized_sensor = True
            if installed_sensors.pimoroni_bh1745 and not self.pimoroni_bh1745_a.initialized_sensor:
                self.pimoroni_bh1745_a = _pimoroni_bh1745.CreateBH1745()
                self.pimoroni_bh1745_a.initialized_sensor = True
            if installed_sensors.pimoroni_as7262 and not self.pimoroni_as7262_a.initialized_sensor:
                self.pimoroni_as7262_a = _pimoroni_as7262.CreateAS7262()
                self.pimoroni_as7262_a.initialized_sensor = True
            if installed_sensors.pimoroni_bme680 and not self.pimoroni_bme680_a.initialized_sensor:
                if installed_sensors.pimoroni_bmp280:
                    message = "Pimoroni BME680 cannot be installed if the BMP280 is installed. " + \
                              "Skipping BME680 & BMP280 - Please Remove the BMP280 OR the BME680 " + \
                              "physically and from the Installed Sensors configuration"
                    logger.sensors_logger.warning(message)
                    installed_sensors.pimoroni_bme680 = 0
                    installed_sensors.pimoroni_bmp280 = 0
                else:
                    self.pimoroni_bme680_a = _pimoroni_bme680.CreateBME680()
                    self.pimoroni_bme680_a.initialized_sensor = True
            if installed_sensors.pimoroni_mcp9600 and not self.pimoroni_mcp9600_a.initialized_sensor:
                self.pimoroni_mcp9600_a = _pimoroni_mcp9600.CreateMCP9600()
                self.pimoroni_mcp9600_a.initialized_sensor = True
            if installed_sensors.pimoroni_bmp280 and not self.pimoroni_bmp280_a.initialized_sensor:
                self.pimoroni_bmp280_a = _pimoroni_bmp280.CreateBMP280()
                self.pimoroni_bmp280_a.initialized_sensor = True
            if installed_sensors.pimoroni_enviro and not self.pimoroni_enviro_a.initialized_sensor:
                self.pimoroni_enviro_a = _pimoroni_enviro.CreateEnviro()
                self.pimoroni_enviro_a.initialized_sensor = True
            if installed_sensors.pimoroni_enviroplus and not self.pimoroni_enviroplus_a.initialized_sensor:
                self.pimoroni_enviroplus_a = _pimoroni_enviroplus.CreateEnviroPlus()
                self.pimoroni_enviroplus_a.initialized_sensor = True
            if installed_sensors.pimoroni_sgp30 and not self.pimoroni_sgp30_a.initialized_sensor:
                self.pimoroni_sgp30_a = _pimoroni_sgp30.CreateSGP30()
                self.pimoroni_sgp30_a.initialized_sensor = True
            if installed_sensors.pimoroni_msa301 and not self.pimoroni_msa301_a.initialized_sensor:
                self.pimoroni_msa301_a = _pimoroni_msa301.CreateMSA301()
                self.pimoroni_msa301_a.initialized_sensor = True
            if installed_sensors.pimoroni_lsm303d and not self.pimoroni_lsm303d_a.initialized_sensor:
                self.pimoroni_lsm303d_a = _pimoroni_lsm303d.CreateLSM303D()
                self.pimoroni_lsm303d_a.initialized_sensor = True
            if installed_sensors.pimoroni_icm20948 and not self.pimoroni_icm20948_a.initialized_sensor:
                self.pimoroni_icm20948_a = _pimoroni_icm20948.CreateICM20948()
                self.pimoroni_icm20948_a.initialized_sensor = True
            if installed_sensors.pimoroni_ltr_559 and not self.pimoroni_ltr_559_a.initialized_sensor:
                self.pimoroni_ltr_559_a = _pimoroni_ltr_559.CreateLTR559()
                self.pimoroni_ltr_559_a.initialized_sensor = True
            if installed_sensors.pimoroni_vl53l1x and not self.pimoroni_vl53l1x_a.initialized_sensor:
                self.pimoroni_vl53l1x_a = _pimoroni_vl53l1x.CreateVL53L1X()
                self.pimoroni_vl53l1x_a.initialized_sensor = True
            if installed_sensors.pimoroni_veml6075 and not self.pimoroni_veml6075_a.initialized_sensor:
                self.pimoroni_veml6075_a = _pimoroni_veml6075.CreateVEML6075()
                self.pimoroni_veml6075_a.initialized_sensor = True
            if installed_sensors.pimoroni_matrix_11x7 and not self.pimoroni_matrix_11x7_a.initialized_sensor:
                self.pimoroni_matrix_11x7_a = _pimoroni_11x7_led_matrix.CreateMatrix11x7()
                self.pimoroni_matrix_11x7_a.initialized_sensor = True
            if installed_sensors.pimoroni_st7735 and not self.pimoroni_st7735_a.initialized_sensor:
                self.pimoroni_st7735_a = _pimoroni_0_96_spi_colour_lcd.CreateST7735()
                self.pimoroni_st7735_a.initialized_sensor = True
            if installed_sensors.pimoroni_mono_oled_luma and not self.pimoroni_mono_oled_luma_a.initialized_sensor:
                self.pimoroni_mono_oled_luma_a = _pimoroni_1_12_mono_oled.CreateLumaOLED()
                self.pimoroni_mono_oled_luma_a.initialized_sensor = True
            if installed_sensors.sensirion_sps30 and not self.sensirion_sps30_a.initialized_sensor:
                self.sensirion_sps30_a = _sensirion_sps30.CreateSPS30()
                self.sensirion_sps30_a.initialized_sensor = True
        else:
            logger.sensors_logger.info(" -- Hardware Based Sensor Initializations Skipped - root required")

        if app_config_access.installed_sensors.kootnet_dummy_sensor:
            self.dummy_sensors = _kootnet_dummy_sensors.CreateDummySensors()
            log_msg2 = " - Readings will be randomly generated for any missing sensor types"
            logger.sensors_logger.warning(" -- Dummy Sensors Enabled" + log_msg2)
        logger.primary_logger.info(" -- Sensors Initialized")

    def _set_dummy_sensors(self):
        self.raspberry_pi_a = CreateNoSensorsDummySensor()
        self.rp_sense_hat_a = CreateNoSensorsDummySensor()
        self.pimoroni_bh1745_a = CreateNoSensorsDummySensor()
        self.pimoroni_as7262_a = CreateNoSensorsDummySensor()
        self.pimoroni_bme680_a = CreateNoSensorsDummySensor()
        self.pimoroni_mcp9600_a = CreateNoSensorsDummySensor()
        self.pimoroni_bmp280_a = CreateNoSensorsDummySensor()
        self.pimoroni_enviro_a = CreateNoSensorsDummySensor()
        self.pimoroni_enviroplus_a = CreateNoSensorsDummySensor()
        self.pimoroni_sgp30_a = CreateNoSensorsDummySensor()
        self.pimoroni_msa301_a = CreateNoSensorsDummySensor()
        self.pimoroni_lsm303d_a = CreateNoSensorsDummySensor()
        self.pimoroni_icm20948_a = CreateNoSensorsDummySensor()
        self.pimoroni_ltr_559_a = CreateNoSensorsDummySensor()
        self.pimoroni_vl53l1x_a = CreateNoSensorsDummySensor()
        self.pimoroni_veml6075_a = CreateNoSensorsDummySensor()
        self.pimoroni_matrix_11x7_a = CreateNoSensorsDummySensor()
        self.pimoroni_st7735_a = CreateNoSensorsDummySensor()
        self.pimoroni_mono_oled_luma_a = CreateNoSensorsDummySensor()
        self.sensirion_sps30_a = CreateNoSensorsDummySensor()
