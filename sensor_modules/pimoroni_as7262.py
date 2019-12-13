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
import time
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.5


class CreateAS7262:
    """ Creates Function access to the Pimoroni AS7262. """
    def __init__(self):
        self.sensor_in_use = False
        try:
            as7262_import = __import__("sensor_modules.drivers.as7262", fromlist=["AS7262"])
            self.as7262_access = as7262_import.AS7262()
            self.as7262_access.soft_reset()
            self.as7262_access.set_gain(64)
            self.as7262_access.set_integration_time(21)
            self.as7262_access.set_measurement_mode(2)
            self.as7262_access.set_illumination_led(0)
            logger.sensors_logger.debug("Pimoroni AS7262 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni AS7262 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_as7262 = 0
            app_config_access.installed_sensors.has_red = 0
            app_config_access.installed_sensors.has_orange = 0
            app_config_access.installed_sensors.has_yellow = 0
            app_config_access.installed_sensors.has_green = 0
            app_config_access.installed_sensors.has_blue = 0
            app_config_access.installed_sensors.has_violet = 0

    def spectral_six_channel(self):
        """ Returns Red, Orange, Yellow, Green, Blue and Violet as a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            red_650, orange_600, yellow_570, green_550, blue_500, violet_450 = self.as7262_access.get_calibrated_values()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni AS7262 6 channel spectrum - Failed: " + str(error))
            red_650, orange_600, yellow_570, green_550, blue_500, violet_450 = 0, 0, 0, 0, 0, 0
        self.sensor_in_use = False
        return round(red_650, round_decimal_to), round(orange_600, round_decimal_to), \
               round(yellow_570, round_decimal_to), round(green_550, round_decimal_to), \
               round(blue_500, round_decimal_to), round(violet_450, round_decimal_to)
