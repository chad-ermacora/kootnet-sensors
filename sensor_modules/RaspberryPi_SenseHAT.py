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
import operations_logger

round_decimal_to = 5


class CreateRPSenseHAT:
    def __init__(self):
        self.sense_hat_import = __import__('sense_hat')
        try:
            self.sense = self.sense_hat_import.SenseHat()
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT - Failed - " + str(error))

    def temperature(self):
        try:
            env_temp = float(self.sense.get_temperature())
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Temperature - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Temperature - Failed - " + str(error))
            env_temp = 0

        return round(env_temp, round_decimal_to)

    def pressure(self):
        try:
            pressure_hpa = self.sense.get_pressure()
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Pressure - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Pressure - Failed - " + str(error))
            pressure_hpa = 0

        return int(pressure_hpa)

    def humidity(self):
        try:
            var_humidity = self.sense.get_humidity()
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Humidity - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Humidity - Failed - " + str(error))
            var_humidity = 0.0

        return round(var_humidity, round_decimal_to)

    def magnetometer_xyz(self):
        try:
            tmp_mag = self.sense.get_compass_raw()
            mag_x, mag_y, mag_z = tmp_mag['x'], tmp_mag['y'], tmp_mag['z']
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Magnetometer XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Magnetometer XYZ - Failed - " + str(error))
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0

        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        try:
            tmp_acc = self.sense.get_accelerometer_raw()

            acc_x, acc_y, acc_z = tmp_acc['x'], tmp_acc['y'], tmp_acc['z']
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Accelerometer XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0

        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)

    def gyroscope_xyz(self):
        try:
            tmp_gyro = self.sense.get_gyroscope_raw()
            gyro_x, gyro_y, gyro_z = tmp_gyro['x'], tmp_gyro['y'], tmp_gyro['z']
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Gyroscope XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Gyroscope XYZ - Failed - " + str(error))
            gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0

        return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)

    def display_led_message(self, message):
        try:
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
        except Exception as error:
            operations_logger.sensors_logger.error("Unable to set Message Orientation - " + str(error))
