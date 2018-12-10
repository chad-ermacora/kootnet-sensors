"""
This module is for the Pimoroni AS7262 6 spectral channels (450, 500, 550, 570, 600, 650nm)
It Retrieves & Returns Sensor data to be written to the DB

AMS AS7262 6-channel spectral (visible) sensor
I2C interface (address: 0x49)
6 spectral channels (450, 500, 550, 570, 600, 650nm)
2 on-board illumination LEDs
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with Raspberry Pi 3B+, 3, 2, B+, A+, Zero, and Zero W

pip3 install as7262

@author: OO-Dragon
"""
import operations_logger

round_decimal_to = 5


class CreateAS7262:
    """ Creates Function access to the Pimoroni AS7262. """
    def __init__(self):
        self.as7262_import = __import__('as7262')
        self.as7262_import.soft_reset()
        self.as7262_import.set_gain(64)
        self.as7262_import.set_integration_time(17.857)
        self.as7262_import.set_measurement_mode(2)
        self.as7262_import.set_illumination_led(1)

    def spectral_six_channel(self):
        """ Returns Red, Orange, Yellow, Green, Blue and Violet. """
        try:
            red, orange, yellow, green, blue, violet = self.as7262_import.get_calibrated_values()
            operations_logger.sensors_logger.debug("Pimoroni AS7262 6 channel spectrum - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Pimoroni AS7262 6 channel spectrum - Failed - " + str(error))
            red, orange, yellow, green, blue, violet = 0, 0, 0, 0, 0, 0

        return round(red, round_decimal_to), round(orange, round_decimal_to), round(yellow, round_decimal_to), \
               round(green, round_decimal_to), round(blue, round_decimal_to), round(violet, round_decimal_to)
