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
import sensor_modules.Pimoroni_BH1745 as Pimoroni_BH1745
import sensor_modules.Pimoroni_BME680 as Pimoroni_BME680
import sensor_modules.Pimoroni_Enviro as Pimoroni_Enviro
import sensor_modules.Pimoroni_LSM303D as Pimoroni_LSM303D
import sensor_modules.RaspberryPi_Sensors as RaspberryPi_Sensors
import sensor_modules.Linux_System as Linux_System
import sensor_modules.RaspberryPi_SenseHAT as RaspberryPi_SenseHAT
from logging.handlers import RotatingFileHandler
from Operations_DB import SensorDatabaseData

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Interval_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def get_rp_system_readings():
    logger.info("Retrieving Raspberry Pi System Readings")
    rp_database_data = SensorDatabaseData()
    rp_database_data.sensor_types = "SensorName, IP, UpTime, CPUtemp"

    rp_database_data.sensor_readings = "'" + str(Linux_System.get_hostname()) + "', '" + \
                                       str(Linux_System.get_ip()) + "', '" + \
                                       str(Linux_System.get_uptime()) + "', '" + \
                                       str(RaspberryPi_Sensors.cpu_temperature()) + "'"

    return rp_database_data


def get_rp_sense_hat_readings():
    logger.info("Retrieving Raspberry Pi SenseHAT Readings")
    rp_sense_hat_database_data = SensorDatabaseData()
    rp_sense_hat_database_data.sensor_types = "EnvironmentTemp, Pressure, Humidity, mg_X, mg_Y, mg_Z"

    mg_xyz = RaspberryPi_SenseHAT.magnetometer_xyz()

    rp_sense_hat_database_data.sensor_readings = "'" + str(RaspberryPi_SenseHAT.temperature()) + "', '" + \
                                                 str(RaspberryPi_SenseHAT.pressure()) + "', '" + \
                                                 str(RaspberryPi_SenseHAT.humidity()) + "', '" + \
                                                 str(mg_xyz[0]) + "', '" + \
                                                 str(mg_xyz[1]) + "', '" + \
                                                 str(mg_xyz[2]) + "'"

    return rp_sense_hat_database_data


def get_pimoroni_bh1745_readings():
    logger.info("Retrieving Pimoroni BH1745 Readings")
    bh1745_database_data = SensorDatabaseData()
    bh1745_database_data.sensor_types = "Lumen, Red, Green, Blue"

    colour_rgb = Pimoroni_BH1745.rgb()

    bh1745_database_data.sensor_readings = "'" + str(Pimoroni_BH1745.lumen()) + "', '" + \
                                           str(colour_rgb[0]) + "', '" + \
                                           str(colour_rgb[1]) + "', '" + \
                                           str(colour_rgb[2]) + "'"

    return bh1745_database_data


def get_pimoroni_bme680_readings():
    logger.info("Retrieving Pimoroni BME680 Readings")
    bme680_database_data = SensorDatabaseData()
    bme680_database_data.sensor_types = "EnvironmentTemp, Pressure, Humidity"

    bme680_database_data.sensor_readings = "'" + str(Pimoroni_BME680.temperature()) + "', '" + \
                                           str(Pimoroni_BME680.pressure()) + "', '" + \
                                           str(Pimoroni_BME680.humidity()) + "'"

    return bme680_database_data


def get_pimoroni_enviro_readings():
    logger.info("Retrieving Pimoroni Enviro Readings")
    enviro_database_data = SensorDatabaseData()
    enviro_database_data.sensor_types = "EnvironmentTemp, Pressure, Lumen, Red, Green, Blue, mg_X, mg_Y, mg_Z"

    colour_rgb = Pimoroni_Enviro.rgb()
    mg_xyz = Pimoroni_Enviro.magnetometer_xyz()

    enviro_database_data.sensor_readings = "'" + str(Pimoroni_Enviro.temperature()) + "', '" + \
                                           str(Pimoroni_Enviro.pressure()) + "', '" + \
                                           str(Pimoroni_Enviro.lumen()) + "', '" + \
                                           str(colour_rgb[0]) + "', '" + \
                                           str(colour_rgb[1]) + "', '" + \
                                           str(colour_rgb[2]) + "', '" + \
                                           str(mg_xyz[0]) + "', '" + \
                                           str(mg_xyz[1]) + "', '" + \
                                           str(mg_xyz[2]) + "'"

    return enviro_database_data


def get_pimoroni_lsm303d_readings():
    logger.info("Retrieving Pimoroni LSM303D Readings")
    lsm303d_database_data = SensorDatabaseData()
    lsm303d_database_data.sensor_types = "mg_X, mg_Y, mg_Z"

    mg_xyz = Pimoroni_LSM303D.magnetometer_xyz()

    lsm303d_database_data.sensor_readings = "'" + str(mg_xyz[0]) + "', '" + \
                                            str(mg_xyz[1]) + "', '" + \
                                            str(mg_xyz[2]) + "'"

    return lsm303d_database_data
