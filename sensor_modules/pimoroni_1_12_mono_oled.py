"""
This module is for the Pimoroni 1.12" Mono OLED (128x128, white/black)
It Retrieves text messages to display on the screen.

1.12" white OLED display (128x128 pixels)
Uses the SH1107 driver chip
20x20mm active area
I2C interface (address 0x3C/0x3D (cut trace))
3.3V or 5V compatible
Reverse polarity protection

pip3 install luma.oled

Created on Tue July 9 16:33:56 2019

@author: OO-Dragon
"""
from operations_modules import logger


class CreateLumaOLED:
    """ Creates Function access to the Pimoroni 1.12" Mono OLED (128x128, white/black). """

    def __init__(self):
        self.luma_oled_import = __import__('luma.oled')
        try:
            pass
        except Exception as error:
            logger.sensors_logger.error("Pimoroni 1.12 Mono OLED (128x128, white/black) Initialization- Failed - " + str(error))

    def display_text(self, message):
        """ Scrolls Provided Text on LED Display. """
        try:
            pass
        except Exception as error:
            logger.sensors_logger.error("Scroll Message on 1.12 Mono OLED Failed - " + str(error))
