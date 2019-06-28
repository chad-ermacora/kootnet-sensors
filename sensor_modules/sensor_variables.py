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


class CreateInstalledSensors:
    """
    Creates object with default installed sensors (Default = Gnu/Linux Only).
    Also contains human readable sensor names as text.
    """

    def __init__(self):
        self.no_sensors = True
        self.linux_system = 1
        self.raspberry_pi_zero_w = 0
        self.raspberry_pi_3b_plus = 0

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

        self.has_display = 0
        self.has_real_time_clock = 0

        self.has_cpu_temperature = 0
        self.has_env_temperature = 0
        self.has_pressure = 0
        self.has_humidity = 0
        self.has_altitude = 0
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

        self.linux_system_name = "Gnu/Linux - Raspbian"
        self.raspberry_pi_zero_w_name = "Raspberry Pi Zero W"
        self.raspberry_pi_3b_plus_name = "Raspberry Pi 3BPlus"

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

    def get_installed_names_str(self):
        str_installed_sensors = ""
        if self.linux_system:
            str_installed_sensors += self.linux_system_name + " || "
        if self.raspberry_pi_zero_w:
            str_installed_sensors += self.raspberry_pi_zero_w_name + " || "
        if self.raspberry_pi_3b_plus:
            str_installed_sensors += self.raspberry_pi_3b_plus_name + " || "
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

        return str_installed_sensors[:-4]

    def get_installed_sensors_config_as_str(self):
        new_installed_sensors_str = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
                                    str(self.linux_system) + " = " + \
                                    self.linux_system_name + "\n" + \
                                    str(self.raspberry_pi_zero_w) + " = " + \
                                    self.raspberry_pi_zero_w_name + "\n" + \
                                    str(self.raspberry_pi_3b_plus) + " = " + \
                                    self.raspberry_pi_3b_plus_name + "\n" + \
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
                                    self.pimoroni_veml6075_name + "\n"
        return new_installed_sensors_str


def auto_detect_and_set_sensors(self):
    pi_version = os.system("cat /proc/device-tree/model")
    if str(pi_version)[25] == "Raspberry Pi 3 Model B Plus":
        self.linux_system = 1
        self.raspberry_pi_3b_plus = 1
    elif str(pi_version)[16] == "Raspberry Pi Zero":
        self.linux_system = 1
        self.raspberry_pi_zero_w = 1


class CreateRPZeroWTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bmp280 = 0.0  # Untested
        self.pimoroni_bme680 = 0.0  # Preliminary Testing
        self.pimoroni_enviro = -4.5  # Tested
        self.pimoroni_enviroplus = -4.5  # Untested
        self.rp_sense_hat = -5.5  # Untested, guessing


class CreateRP3BPlusTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bmp280 = -2.5  # Untested
        self.pimoroni_bme680 = -2.5  # Tested when Raspberry Pi is on its side
        self.pimoroni_enviro = -6.5  # Untested, guessing
        self.pimoroni_enviroplus = -6.5  # Untested, guessing
        self.rp_sense_hat = -7.0  # Preliminary testing done


class CreateUnknownTemperatureOffsets:
    def __init__(self):
        # No Offset if unknown or unselected
        self.pimoroni_bmp280 = 0.0
        self.pimoroni_bme680 = 0.0
        self.pimoroni_enviro = 0.0
        self.pimoroni_enviroplus = 0.0
        self.rp_sense_hat = 0.0
