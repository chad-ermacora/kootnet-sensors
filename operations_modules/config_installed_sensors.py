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
import os
from subprocess import check_output
from operations_modules import file_locations, app_generic_functions, logger


class CreateInstalledSensors:
    """
    Creates object with default installed sensors (Default = Nothing).
    Also contains human readable sensor names as text.
    """

    def __init__(self):
        self.no_sensors = True
        self.linux_system = 0
        self.raspberry_pi = 0

        self.raspberry_pi_sense_hat = 0
        self.pimoroni_bh1745 = 0
        self.pimoroni_as7262 = 0
        self.pimoroni_bmp280 = 0
        self.pimoroni_bme680 = 0
        self.pimoroni_enviro = 0
        self.pimoroni_enviroplus = 0
        self.pimoroni_pms5003 = 0
        self.pimoroni_lsm303d = 0
        self.pimoroni_icm20948 = 0
        self.pimoroni_vl53l1x = 0
        self.pimoroni_ltr_559 = 0
        self.pimoroni_veml6075 = 0

        self.pimoroni_matrix_11x7 = 0
        self.pimoroni_st7735 = 0
        self.pimoroni_mono_oled_luma = 0

        self.has_display = 0
        self.has_real_time_clock = 0

        self.has_cpu_temperature = 0
        self.has_env_temperature = 0
        self.has_pressure = 0
        self.has_altitude = 0
        self.has_humidity = 0
        self.has_distance = 0
        self.has_gas = 0
        self.has_particulate_matter = 0
        self.has_ultra_violet = 0
        self.has_ultra_violet_comparator = 0
        self.has_lumen = 0
        self.has_red = 0
        self.has_orange = 0
        self.has_yellow = 0
        self.has_green = 0
        self.has_blue = 0
        self.has_violet = 0
        self.has_acc = 0
        self.has_mag = 0
        self.has_gyro = 0

        self.linux_system_name = "Gnu/Linux"
        self.raspberry_pi_name = "NA"

        self.raspberry_pi_sense_hat_name = "Raspberry Pi Sense HAT"
        self.pimoroni_bh1745_name = "Pimoroni BH1745"
        self.pimoroni_as7262_name = "Pimoroni AS7262"
        self.pimoroni_bmp280_name = "Pimoroni BMP280"
        self.pimoroni_bme680_name = "Pimoroni BME680"
        self.pimoroni_enviro_name = "Pimoroni EnviroPHAT"
        self.pimoroni_enviroplus_name = "Pimoroni Enviro+"
        self.pimoroni_pms5003_name = "Pimoroni PMS5003"
        self.pimoroni_lsm303d_name = "Pimoroni LSM303D"
        self.pimoroni_icm20948_name = "Pimoroni ICM20948"
        self.pimoroni_vl53l1x_name = "Pimoroni VL53L1X"
        self.pimoroni_ltr_559_name = "Pimoroni LTR-559"
        self.pimoroni_veml6075_name = "Pimoroni VEML6075"

        self.pimoroni_matrix_11x7_name = "Pimoroni 11x7 LED Matrix"
        self.pimoroni_st7735_name = "Pimoroni 10.96'' SPI Colour LCD (160x80)"
        self.pimoroni_mono_oled_luma_name = "Pimoroni 1.12'' Mono OLED (128x128, white/black)"

    def get_installed_names_str(self):
        str_installed_sensors = ""
        if self.linux_system:
            str_installed_sensors += self.linux_system_name + " || "
        if self.raspberry_pi:
            str_installed_sensors += self.raspberry_pi_name + " || "
        if self.raspberry_pi_sense_hat:
            str_installed_sensors += self.raspberry_pi_sense_hat_name + " || "
        if self.pimoroni_bh1745:
            str_installed_sensors += self.pimoroni_bh1745_name + " || "
        if self.pimoroni_as7262:
            str_installed_sensors += self.pimoroni_as7262_name + " || "
        if self.pimoroni_bmp280:
            str_installed_sensors += self.pimoroni_bmp280_name + " || "
        if self.pimoroni_bme680:
            str_installed_sensors += self.pimoroni_bme680_name + " || "
        if self.pimoroni_enviro:
            str_installed_sensors += self.pimoroni_enviro_name + " || "
        if self.pimoroni_enviroplus:
            str_installed_sensors += self.pimoroni_enviroplus_name + " || "
        if self.pimoroni_pms5003:
            str_installed_sensors += self.pimoroni_pms5003_name + " || "
        if self.pimoroni_lsm303d:
            str_installed_sensors += self.pimoroni_lsm303d_name + " || "
        if self.pimoroni_icm20948:
            str_installed_sensors += self.pimoroni_icm20948_name + " || "
        if self.pimoroni_vl53l1x:
            str_installed_sensors += self.pimoroni_vl53l1x_name + " || "
        if self.pimoroni_ltr_559:
            str_installed_sensors += self.pimoroni_ltr_559_name + " || "
        if self.pimoroni_veml6075:
            str_installed_sensors += self.pimoroni_veml6075_name + " || "
        if self.pimoroni_matrix_11x7:
            str_installed_sensors += self.pimoroni_matrix_11x7_name + " || "
        if self.pimoroni_st7735:
            str_installed_sensors += self.pimoroni_st7735_name + " || "
        if self.pimoroni_mono_oled_luma:
            str_installed_sensors += self.pimoroni_mono_oled_luma_name + " || "
        if len(str_installed_sensors) > 4:
            return str_installed_sensors[:-4]
        return "N/A"

    def get_installed_sensors_config_as_str(self):
        new_installed_sensors_str = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
                                    str(self.linux_system) + " = " + \
                                    self.linux_system_name + "\n" + \
                                    str(self.raspberry_pi) + " = " + \
                                    self.raspberry_pi_name + "\n" + \
                                    str(self.raspberry_pi_sense_hat) + " = " + \
                                    self.raspberry_pi_sense_hat_name + "\n" + \
                                    str(self.pimoroni_bh1745) + " = " + \
                                    self.pimoroni_bh1745_name + "\n" + \
                                    str(self.pimoroni_as7262) + " = " + \
                                    self.pimoroni_as7262_name + "\n" + \
                                    str(self.pimoroni_bmp280) + " = " + \
                                    self.pimoroni_bmp280_name + "\n" + \
                                    str(self.pimoroni_bme680) + " = " + \
                                    self.pimoroni_bme680_name + "\n" + \
                                    str(self.pimoroni_enviro) + " = " + \
                                    self.pimoroni_enviro_name + "\n" + \
                                    str(self.pimoroni_enviroplus) + " = " + \
                                    self.pimoroni_enviroplus_name + "\n" + \
                                    str(self.pimoroni_pms5003) + " = " + \
                                    self.pimoroni_pms5003_name + "\n" + \
                                    str(self.pimoroni_lsm303d) + " = " + \
                                    self.pimoroni_lsm303d_name + "\n" + \
                                    str(self.pimoroni_icm20948) + " = " + \
                                    self.pimoroni_icm20948_name + "\n" + \
                                    str(self.pimoroni_vl53l1x) + " = " + \
                                    self.pimoroni_vl53l1x_name + "\n" + \
                                    str(self.pimoroni_ltr_559) + " = " + \
                                    self.pimoroni_ltr_559_name + "\n" + \
                                    str(self.pimoroni_veml6075) + " = " + \
                                    self.pimoroni_veml6075_name + "\n" + \
                                    str(self.pimoroni_matrix_11x7) + " = " + \
                                    self.pimoroni_matrix_11x7_name + "\n" + \
                                    str(self.pimoroni_st7735) + " = " + \
                                    self.pimoroni_st7735_name + "\n" + \
                                    str(self.pimoroni_mono_oled_luma) + " = " + \
                                    self.pimoroni_mono_oled_luma_name + "\n"

        return new_installed_sensors_str

    def get_raspberry_pi_model(self):
        if self.raspberry_pi:
            try:
                pi_version = str(check_output("cat /proc/device-tree/model", shell=True))[2:-5]
                logger.primary_logger.debug("Pi Version: " + str(pi_version))
                if str(pi_version)[:17] == "Raspberry Pi Zero":
                    return "Raspberry Pi Zero"
                elif str(pi_version)[:27] == "Raspberry Pi 3 Model B Plus":
                    return "Raspberry Pi 3 Model B Plus"
                elif str(pi_version)[:22] == "Raspberry Pi 4 Model B":
                    return "Raspberry Pi 4 Model B"
                else:
                    return "Raspberry Pi"
            except Exception as error:
                logger.primary_logger.warning("Unable to get Raspberry Pi Model: " + str(error))
                return "Raspberry Pi"


def get_installed_sensors_from_file():
    """ Loads installed sensors from file and returns it as an object. """
    if os.path.isfile(file_locations.installed_sensors_config):
        installed_sensor_lines = app_generic_functions.get_file_content(
            file_locations.installed_sensors_config).strip().split("\n")
        installed_sensors = convert_lines_to_obj(installed_sensor_lines)
    else:
        logger.primary_logger.info("Installed Sensors Configuration file not found - Saving Default")
        installed_sensors = CreateInstalledSensors()
        write_to_file(installed_sensors)

    return installed_sensors


def convert_lines_to_obj(installed_sensor_lines, skip_write=False):
    """ Converts provided installed sensors text as a list of lines into a object and returns it. """
    new_installed_sensors = CreateInstalledSensors()

    installed_sensor_list = []
    count = 0
    for config_line in installed_sensor_lines:
        if count > 0:
            if config_line.strip()[0] == "1":
                installed_sensor_list.append(1)
            else:
                installed_sensor_list.append(0)
        count += 1

    count = 0
    for enabled in installed_sensor_list:
        if enabled:
            if count == 0:
                new_installed_sensors.linux_system = 1
            elif count == 1:
                new_installed_sensors.raspberry_pi = 1
                new_installed_sensors.has_cpu_temperature = 1
            elif count == 2:
                new_installed_sensors.raspberry_pi_sense_hat = 1
                new_installed_sensors.has_display = 1
                new_installed_sensors.has_env_temperature = 1
                new_installed_sensors.has_pressure = 1
                new_installed_sensors.has_humidity = 1
                new_installed_sensors.has_acc = 1
                new_installed_sensors.has_mag = 1
                new_installed_sensors.has_gyro = 1
            elif count == 3:
                new_installed_sensors.pimoroni_bh1745 = 1
                new_installed_sensors.has_lumen = 1
                new_installed_sensors.has_red = 1
                new_installed_sensors.has_green = 1
                new_installed_sensors.has_blue = 1
            elif count == 4:
                new_installed_sensors.pimoroni_as7262 = 1
                new_installed_sensors.has_red = 1
                new_installed_sensors.has_orange = 1
                new_installed_sensors.has_yellow = 1
                new_installed_sensors.has_green = 1
                new_installed_sensors.has_blue = 1
                new_installed_sensors.has_violet = 1
            elif count == 5:
                new_installed_sensors.pimoroni_bmp280 = 1
                new_installed_sensors.has_env_temperature = 1
                new_installed_sensors.has_pressure = 1
                new_installed_sensors.has_altitude = 1
            elif count == 6:
                new_installed_sensors.pimoroni_bme680 = 1
                new_installed_sensors.has_env_temperature = 1
                new_installed_sensors.has_pressure = 1
                new_installed_sensors.has_humidity = 1
                new_installed_sensors.has_gas = 1
            elif count == 7:
                new_installed_sensors.pimoroni_enviro = 1
                new_installed_sensors.has_env_temperature = 1
                new_installed_sensors.has_pressure = 1
                new_installed_sensors.has_lumen = 1
                new_installed_sensors.has_red = 1
                new_installed_sensors.has_green = 1
                new_installed_sensors.has_blue = 1
                new_installed_sensors.has_acc = 1
                new_installed_sensors.has_mag = 1
            elif count == 8:
                new_installed_sensors.pimoroni_enviroplus = 1
                new_installed_sensors.has_display = 1
                new_installed_sensors.has_env_temperature = 1
                new_installed_sensors.has_pressure = 1
                new_installed_sensors.has_humidity = 1
                new_installed_sensors.has_distance = 1
                new_installed_sensors.has_lumen = 1
                new_installed_sensors.has_gas = 1
            elif count == 9:
                new_installed_sensors.pimoroni_pms5003 = 1
                new_installed_sensors.has_particulate_matter = 1
            elif count == 10:
                new_installed_sensors.pimoroni_lsm303d = 1
                new_installed_sensors.has_acc = 1
                new_installed_sensors.has_mag = 1
            elif count == 11:
                new_installed_sensors.pimoroni_icm20948 = 1
                new_installed_sensors.has_acc = 1
                new_installed_sensors.has_mag = 1
                new_installed_sensors.has_gyro = 1
            elif count == 12:
                new_installed_sensors.pimoroni_vl53l1x = 1
                new_installed_sensors.has_distance = 1
            elif count == 13:
                new_installed_sensors.pimoroni_ltr_559 = 1
                new_installed_sensors.has_lumen = 1
                new_installed_sensors.has_distance = 1
            elif count == 14:
                new_installed_sensors.pimoroni_veml6075 = 1
                new_installed_sensors.has_ultra_violet = 1
                new_installed_sensors.has_ultra_violet_comparator = 1
            elif count == 15:
                new_installed_sensors.pimoroni_matrix_11x7 = 1
                new_installed_sensors.has_display = 1
            elif count == 16:
                new_installed_sensors.pimoroni_st7735 = 1
                new_installed_sensors.has_display = 1
            elif count == 17:
                new_installed_sensors.pimoroni_mono_oled_luma = 1
                new_installed_sensors.has_display = 1
        count += 1

    for line in installed_sensor_list:
        if line:
            new_installed_sensors.no_sensors = False

    if not skip_write:
        if len(installed_sensor_lines) != 19:
            logger.primary_logger.warning("Invalid number of Installed Sensors in the configuration file - " +
                                          "Should be 18 but seeing " + str(len(installed_sensor_lines)) + ": " +
                                          "Disabling bad entries. " +
                                          "Please review the Installed Sensors Configuration file.")
            write_to_file(new_installed_sensors)
        if new_installed_sensors.raspberry_pi:
            new_installed_sensors.raspberry_pi_name = new_installed_sensors.get_raspberry_pi_model()
    return new_installed_sensors


def write_to_file(installed_sensors):
    """ Writes provided 'installed sensors' to local disk. The provided sensors can be string or object. """
    try:
        if type(installed_sensors) == str:
            new_installed_sensors = installed_sensors
        else:
            new_installed_sensors = installed_sensors.get_installed_sensors_config_as_str()

        app_generic_functions.write_file_to_disk(file_locations.installed_sensors_config, new_installed_sensors)
    except Exception as error:
        logger.primary_logger.error("Failed to write Installed Sensor Config: " + str(error))
