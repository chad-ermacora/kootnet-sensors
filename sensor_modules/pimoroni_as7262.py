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
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateAS7262:
    """ Creates Function access to the Pimoroni AS7262. """

    def __init__(self):
        try:
            self.as7262_import = __import__('as7262')
            self.as7262_import.soft_reset()
            self.as7262_import.set_gain(64)
            self.as7262_import.set_integration_time(21)
            self.as7262_import.set_measurement_mode(2)
            self.as7262_import.set_illumination_led(0)
        except Exception as error:
            logger.sensors_logger.error("Pimoroni AS7262 Initialization Failed - " + str(error))
            app_config_access.installed_sensors.pimoroni_as7262 = 0

    def spectral_six_channel(self):
        """ Returns Red, Orange, Yellow, Green, Blue and Violet as a list. """
        try:
            red_650, orange_600, yellow_570, green_550, blue_500, violet_450 = self.as7262_import.get_calibrated_values()
            logger.sensors_logger.debug("Pimoroni AS7262 6 channel spectrum - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni AS7262 6 channel spectrum - Failed - " + str(error))
            red_650, orange_600, yellow_570, green_550, blue_500, violet_450 = 0, 0, 0, 0, 0, 0

        return round(red_650, round_decimal_to), round(orange_600, round_decimal_to), \
               round(yellow_570, round_decimal_to), round(green_550, round_decimal_to), \
               round(blue_500, round_decimal_to), round(violet_450, round_decimal_to)
