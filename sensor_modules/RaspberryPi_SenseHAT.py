"""
This module is for the Raspberry Pi Sense HAT
It Retrieves & Returns Sensor data to be written to the DB

8 by 8 rgb LED matrix
five-button joystick
Gyroscope
Accelerometer
Magnetometer
Temperature
Barometric pressure
Humidity

pip3 install sense-hat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

round_decimal_to = 5
show_led_message = True


class CreateRPSystem:
    def __init__(self):
        self.sense_hat_import = __import__('sense_hat')
        self.sense = self.sense_hat_import.SenseHat()

    def temperature(self):
        try:
            env_temp = float(self.sense.get_temperature())
            logger.debug("Raspberry Pi Sense HAT Temperature - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Temperature - Failed - " + str(error))
            env_temp = 0

        return round(env_temp, round_decimal_to)

    def pressure(self):
        try:
            pressure_hpa = self.sense.get_pressure()
            logger.debug("Raspberry Pi Sense HAT Pressure - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Pressure - Failed - " + str(error))
            pressure_hpa = 0

        return int(pressure_hpa)

    def humidity(self):
        try:
            var_humidity = self.sense.get_humidity()
            logger.debug("Raspberry Pi Sense HAT Humidity - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Humidity - Failed - " + str(error))
            var_humidity = 0.0

        return round(var_humidity, round_decimal_to)

    def magnetometer_xyz(self):
        try:
            tmp_mag = self.sense.get_compass_raw()
            mag_x, mag_y, mag_z = tmp_mag['x'], tmp_mag['y'], tmp_mag['z']
            logger.debug("Raspberry Pi Sense HAT Magnetometer XYZ - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Magnetometer XYZ - Failed - " + str(error))
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0

        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        try:
            tmp_acc = self.sense.get_accelerometer_raw()

            acc_x, acc_y, acc_z = tmp_acc['x'], tmp_acc['y'], tmp_acc['z']
            logger.debug("Raspberry Pi Sense HAT Accelerometer XYZ - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0

        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)

    def gyroscope_xyz(self):
        try:
            tmp_gyro = self.sense.get_gyroscope_raw()
            gyro_x, gyro_y, gyro_z = tmp_gyro['x'], tmp_gyro['y'], tmp_gyro['z']
            logger.debug("Raspberry Pi Sense HAT Gyroscope XYZ - OK")
        except Exception as error:
            logger.error("Raspberry Pi Sense HAT Gyroscope XYZ - Failed - " + str(error))
            gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0

        return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)

    def display_led_message(self, message):
        if show_led_message:
            acc_data = self.accelerometer_xyz()

            if acc_data[0] < -0.5:
                self.sense.set_rotation(90)
            elif acc_data[1] > 0.5:
                self.sense.set_rotation(0)
            elif acc_data[1] < -0.5:
                self.sense.set_rotation(180)
            else:
                self.sense.set_rotation(270)

            self.sense.show_message(str(message), text_colour=(75, 0, 0))
        else:
            logger.info("Raspberry Pi Sense HAT LED message Disabled - Edit RaspberryPi_SenseHAT.py to Enable")
