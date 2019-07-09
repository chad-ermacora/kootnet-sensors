"""
This module is for the Pimoroni 11x7 LED Matrix
It Retrieves & Returns Sensor data to be written to the DB

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
from operations_modules import logger


class CreateMatrix11x7:
    """ Creates Function access to the Pimoroni 11x7 LED Matrix. """

    def __init__(self):
        self.matrix_11x7_import = __import__('matrix11x7', fromlist=['Matrix11x7'])
        self.matrix_11x7_fonts_import = __import__('matrix11x7.fonts', fromlist=['font3x5'])
        try:
            self.matrix11x7 = self.matrix_11x7_import.Matrix11x7()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni 11x7 LED Matrix - Failed - " + str(error))

        self.matrix11x7.set_brightness(0.5)

    def display_led_message(self, message):
        """ Scrolls Provided Text on LED Display. """
        try:
            self.matrix11x7.write_string(message, y=1, font=self.matrix_11x7_fonts_import.font3x5)
            # Show the buffer
            self.matrix11x7.show()
            # Scroll the buffer content
            self.matrix11x7.scroll()
        except Exception as error:
            logger.sensors_logger.error("Scroll Message on Matrix11x7 Failed - " + str(error))
