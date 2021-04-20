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
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
# Update readings in seconds
sleep_between_readings_seconds = 1


class CreateAS7262:
    """ Creates Function access to the Pimoroni AS7262. """

    def __init__(self):
        self.sensor_in_use = False
        self.red_650 = 0.0
        self.orange_600 = 0.0
        self.yellow_570 = 0.0
        self.green_550 = 0.0
        self.blue_500 = 0.0
        self.violet_450 = 0.0
        self.sensor_latency = 0.0

        try:
            as7262_import = __import__("sensor_modules.drivers.as7262", fromlist=["AS7262"])
            self.as7262_access = as7262_import.AS7262()
            self.as7262_access.soft_reset()
            self.as7262_access.set_gain(64)
            self.as7262_access.set_integration_time(17.857)
            self.as7262_access.set_measurement_mode(2)
            self.as7262_access.set_illumination_led(0)

            self.thread_readings_updater = Thread(target=self._readings_updater)
            self.thread_readings_updater.daemon = True
            self.thread_readings_updater.start()
            logger.sensors_logger.debug("Pimoroni AS7262 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni AS7262 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_as7262 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _readings_updater(self):
        logger.sensors_logger.debug("Pimoroni AS7262 readings updater started")
        while True:
            try:
                start_time = time.time()
                ems_colors_list = self.as7262_access.get_calibrated_values()
                end_time = time.time()
                self.sensor_latency = float(end_time - start_time)

                self.red_650 = round(ems_colors_list.red, round_decimal_to)
                self.orange_600 = round(ems_colors_list.orange, round_decimal_to)
                self.yellow_570 = round(ems_colors_list.yellow, round_decimal_to)
                self.green_550 = round(ems_colors_list.green, round_decimal_to)
                self.blue_500 = round(ems_colors_list.blue, round_decimal_to)
                self.violet_450 = round(ems_colors_list.violet, round_decimal_to)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni AS7262 6 channel spectrum - Failed: " + str(error))
                self.red_650 = 0.0
                self.orange_600 = 0.0
                self.yellow_570 = 0.0
                self.green_550 = 0.0
                self.blue_500 = 0.0
                self.violet_450 = 0.0
            time.sleep(sleep_between_readings_seconds)

    def spectral_six_channel(self):
        """ Returns Red, Orange, Yellow, Green, Blue and Violet as a list. """
        return [self.red_650, round_decimal_to, self.orange_600, round_decimal_to,
                self.yellow_570, round_decimal_to, self.green_550, round_decimal_to,
                self.blue_500, round_decimal_to, self.violet_450, round_decimal_to]
