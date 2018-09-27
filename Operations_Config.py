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
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Operations_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sensor_ver_file = "/home/pi/KootNetSensors/installed_sensors.txt"


class CreateInstalledSensors:
    def __init__(self):
        self.linux_system = False
        self.raspberry_pi_sense_hat = False
        self.pimoroni_bh1745 = False
        self.pimoroni_bme680 = False
        self.pimoroni_enviro = False
        self.pimoroni_lsm303d = False
        self.pimoroni_vl53l1x = False

    def check_ok_write_to_database(self):
        write_to_database = False

        if self.pimoroni_lsm303d:
            write_to_database = True
        elif self.raspberry_pi_sense_hat:
            write_to_database = True
        elif self.pimoroni_enviro:
            write_to_database = True
        elif self.linux_system:
            write_to_database = True
        elif self.pimoroni_bme680:
            write_to_database = True
        elif self.pimoroni_bh1745:
            write_to_database = True
        elif self.pimoroni_vl53l1x:
            write_to_database = True

        return write_to_database

    def check_config_file(self):
        try:
            sensor_list_file = open(sensor_ver_file, 'r')
            sensor_list = sensor_list_file.readlines()

            if int(sensor_list[1][:1]):
                self.linux_system = True
            else:
                self.linux_system = False

            if int(sensor_list[2][:1]):
                self.raspberry_pi_sense_hat = True
            else:
                self.raspberry_pi_sense_hat = False

            if int(sensor_list[3][:1]):
                self.pimoroni_bh1745 = True
            else:
                self.pimoroni_bh1745 = False

            if int(sensor_list[4][:1]):
                self.pimoroni_bme680 = True
            else:
                self.pimoroni_bme680 = False

            if int(sensor_list[5][:1]):
                self.pimoroni_enviro = True
            else:
                self.pimoroni_enviro = False

            if int(sensor_list[6][:1]):
                self.pimoroni_lsm303d = True
            else:
                self.pimoroni_lsm303d = False

            if int(sensor_list[7][:1]):
                self.pimoroni_vl53l1x = True
            else:
                self.pimoroni_vl53l1x = False

        except Exception as error:
            logger.error("Unable to open: " + sensor_ver_file + " - " + str(error))
