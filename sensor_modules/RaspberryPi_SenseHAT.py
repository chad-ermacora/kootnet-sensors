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
from os import system

import operations_logger
import sensor_modules.Linux_OS as LinuxOS

round_decimal_to = 5


class CreateRPSenseHAT:
    """ Creates Function access to the Raspberry Pi Sense HAT. """

    def __init__(self):
        self.sense_hat_import = __import__("sense_hat")
        try:
            self.sense = self.sense_hat_import.SenseHat()
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT - Failed - " + str(error))

        self.linux_os_access = LinuxOS.CreateLinuxSystem()

        # Use to initialize SenseHAT Joy Stick program in a Thread
        try:
            pass
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT - Failed - " + str(error))

    def temperature(self):
        try:
            env_temp = float(self.sense.get_temperature())
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Temperature - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Temperature - Failed - " + str(error))
            env_temp = 0.0

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
            mag_x, mag_y, mag_z = tmp_mag["x"], tmp_mag["y"], tmp_mag["z"]
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Magnetometer XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Magnetometer XYZ - Failed - " + str(error))
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0

        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        try:
            tmp_acc = self.sense.get_accelerometer_raw()

            acc_x, acc_y, acc_z = tmp_acc["x"], tmp_acc["y"], tmp_acc["z"]
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Accelerometer XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0

        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)

    def gyroscope_xyz(self):
        try:
            tmp_gyro = self.sense.get_gyroscope_raw()
            gyro_x, gyro_y, gyro_z = tmp_gyro["x"], tmp_gyro["y"], tmp_gyro["z"]
            operations_logger.sensors_logger.debug("Raspberry Pi Sense HAT Gyroscope XYZ - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Raspberry Pi Sense HAT Gyroscope XYZ - Failed - " + str(error))
            gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0

        return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)

    def start_joy_stick_commands(self):
        # Makes a nice Rainbow on the LED grid.  Not using right now ...
        # rainbow = [[255, 0, 0], [255, 0, 0], [255, 87, 0], [255, 196, 0],
        #            [205, 255, 0], [95, 255, 0], [0, 255, 13], [0, 255, 122],
        #            [255, 0, 0], [255, 96, 0], [255, 205, 0], [196, 255, 0],
        #            [87, 255, 0], [0, 255, 22], [0, 255, 131], [0, 255, 240],
        #            [255, 105, 0], [255, 214, 0], [187, 255, 0], [78, 255, 0],
        #            [0, 255, 30], [0, 255, 140], [0, 255, 248], [0, 152, 255],
        #            [255, 223, 0], [178, 255, 0], [70, 255, 0], [0, 255, 40],
        #            [0, 255, 148], [0, 253, 255], [0, 144, 255], [0, 34, 255],
        #            [170, 255, 0], [61, 255, 0], [0, 255, 48], [0, 255, 157],
        #            [0, 243, 255], [0, 134, 255], [0, 26, 255], [83, 0, 255],
        #            [52, 255, 0], [0, 255, 57], [0, 255, 166], [0, 235, 255],
        #            [0, 126, 255], [0, 17, 255], [92, 0, 255], [201, 0, 255],
        #            [0, 255, 66], [0, 255, 174], [0, 226, 255], [0, 117, 255],
        #            [0, 8, 255], [100, 0, 255], [210, 0, 255], [255, 0, 192],
        #            [0, 255, 183], [0, 217, 255], [0, 109, 255], [0, 0, 255],
        #            [110, 0, 255], [218, 0, 255], [255, 0, 183], [255, 0, 74]]

        b1 = (102, 51, 0)
        b2 = (0, 0, 255)
        s1 = (205, 133, 63)
        w1 = (100, 100, 100)
        steve = [b1, b1, b1, b1, b1, b1, b1, b1,
                 b1, b1, b1, b1, b1, b1, b1, b1,
                 b1, s1, s1, s1, s1, s1, s1, b1,
                 s1, s1, s1, s1, s1, s1, s1, s1,
                 s1, w1, b2, s1, s1, b2, w1, s1,
                 s1, s1, s1, b1, b1, s1, s1, s1,
                 s1, s1, b1, s1, s1, b1, s1, s1,
                 s1, s1, b1, b1, b1, b1, s1, s1]
        try:
            shutdown_confirm = False
            while True:
                event = self.sense.stick.wait_for_event()

                acc = self.accelerometer_xyz()
                acc_x = round(acc[0], 0)
                acc_y = round(acc[1], 0)

                if acc_x == -1:
                    self.sense.set_rotation(90)
                elif acc_y == 1:
                    self.sense.set_rotation(0)
                elif acc_y == -1:
                    self.sense.set_rotation(180)
                else:
                    self.sense.set_rotation(270)

                if event.direction == "up":
                    shutdown_confirm = False
                    self.display_led_message(self.linux_os_access.get_ip())
                elif event.direction == "down":
                    self.sense.set_pixels(steve)
                    if shutdown_confirm:
                        self.sense.show_message("Shutting Down",
                                                scroll_speed=0.08,
                                                text_colour=(75, 0, 0))
                        system("shutdown -h now")
                elif event.direction == "left":
                    shutdown_confirm = False
                    self.display_led_message(str(int(self.humidity())) + "%RH")
                elif event.direction == "right":
                    shutdown_confirm = False
                    self.display_led_message(str(int(self.temperature())) + "c")
                elif event.action == "held":
                    shutdown_confirm = True
                    self.sense.show_message("Shutdown=down",
                                            scroll_speed=0.08,
                                            text_colour=(75, 0, 0))

                # Clear events to prevent multiple loops if button(s) hit multiple times
                self.sense.stick.get_events()
        except Exception as error:
            operations_logger.sensors_logger.error("Unable start SenseHAT JoyStick Operations - " + str(error))

    def display_led_message(self, message):
        try:
            acc = self.accelerometer_xyz()
            acc_x = round(acc[0], 0)
            acc_y = round(acc[1], 0)

            if acc_x == -1:
                self.sense.set_rotation(90)
            elif acc_y == 1:
                self.sense.set_rotation(0)
            elif acc_y == -1:
                self.sense.set_rotation(180)
            else:
                self.sense.set_rotation(270)

            self.sense.show_message(str(message),
                                    scroll_speed=0.12,
                                    text_colour=(75, 0, 0))
        except Exception as error:
            operations_logger.sensors_logger.error("Unable to set Message Orientation - " + str(error))
