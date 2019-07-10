"""
This module is for the Pimoroni 11x7 LED Matrix
It Retrieves text messages to display on the screen.

11x7 (77 total) bright white LEDs
Uses the IS31FL3731 driver chip
22x14mm active area
2mm LED pitch
I2C interface (address 0x75/0x77 (cut trace))
3.3V or 5V compatible
Reverse polarity protection

pip3 install matrix11x7

Created on Tue July 9 15:53:56 2019

@author: OO-Dragon
"""
import time
from operations_modules import logger


class CreateMatrix11x7:
    """ Creates Function access to the Pimoroni 11x7 LED Matrix. """

    def __init__(self):
        self.matrix_11x7_import = __import__('matrix11x7', fromlist=['Matrix11x7'])
        self.matrix_11x7_fonts_import = __import__('matrix11x7.fonts', fromlist=['font5x7'])
        try:
            self.matrix11x7 = self.matrix_11x7_import.Matrix11x7()
            self.matrix11x7.set_brightness(0.15)
        except Exception as error:
            logger.sensors_logger.error("Pimoroni 11x7 LED Matrix Initialization - Failed - " + str(error))

    def display_led_message(self, message):
        """ Scrolls Provided Text on LED Display. """
        message_length = len(message)
        try:
            self.matrix11x7.write_string(" " + message + "    ")
            # Scroll the buffer content
            count = 0
            while count < (message_length * 6):
                self.matrix11x7.show()
                self.matrix11x7.scroll()
                time.sleep(0.1)
                count += 1
            self.matrix11x7.clear()
            self.matrix11x7.show()
        except Exception as error:
            logger.sensors_logger.error("Scroll Message on Matrix11x7 Failed - " + str(error))
