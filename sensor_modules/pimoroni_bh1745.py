"""
This module is for the Pimoroni bh1745 rgb + Lumen
It Retrieves & Returns Sensor data to be written to the DB

BH1745 Luminance and Colour Sensor Breakout
Two white illumination LEDs
Red, green, blue, and luminance measurements
0.005 to 40,000 lx detection range
50/60Hz light noise rejection
IR cut filter
16 bit data output
3.3V or 5V compatible
I2C interface, with address select via ADDR cuttable trace (0x38 or 0x39)
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install bh1745

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateBH1745:
    """ Creates Function access to the Pimoroni BH1745. """

    def __init__(self):
        try:
            bh1745_import = __import__('bh1745')
            self.bh1745 = bh1745_import.BH1745()
            self.bh1745.setup()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BH1745 Initialization Failed - " + str(error))
            app_config_access.installed_sensors.pimoroni_bh1745 = 0

    def lumen(self):
        """ Returns Lumen as a Float. """
        try:
            var_lumen = self.bh1745.get_rgbc_raw()[3]
            logger.sensors_logger.debug("Pimoroni BH1745 Lumen - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BH1745 Lumen - Failed - " + str(error))
            var_lumen = 0

        return round(var_lumen, round_decimal_to)

    def ems(self):
        """ Returns Electromagnetic Spectrum of Red, Green, Blue as a list of Floats. """
        try:
            rgb_red, rgb_green, rgb_blue, var_lumen = self.bh1745.get_rgbc_raw()
            logger.sensors_logger.debug("Pimoroni BH1745 RGB - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BH1745 RGB - Failed - " + str(error))
            rgb_red, rgb_green, rgb_blue = 0, 0, 0

        return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)
