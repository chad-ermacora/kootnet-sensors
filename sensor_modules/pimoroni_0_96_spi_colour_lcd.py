"""
This module is for the Pimoroni 0.96" SPI Colour LCD (160x80)
It Retrieves text messages to display on the screen.

0.96" colour LCD (160x80 pixels)
SPI interface
3.3V or 5V compatible
Reverse polarity protection
Compatible with all models of Raspberry Pi and Arduino

pip3 install st7735

Created on Tue July 9 15:53:56 2019

@author: OO-Dragon
"""
import time
from operations_modules import logger


class CreateST7735:
    """ Creates Function access to the Pimoroni 10.96" SPI Colour LCD (160x80). """

    def __init__(self):
        self.st7735_import = __import__('ST7735')
        self.image_import = __import__('PIL', fromlist=['Image'])
        self.image_draw_import = __import__('PIL', fromlist=['ImageDraw'])
        self.image_font_import = __import__('PIL', fromlist=['ImageFont'])
        try:
            # Create ST7735 LCD display class.
            self.display = self.st7735_import.ST7735(
                port=0,
                cs=self.st7735_import.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
                dc=9,
                backlight=19,  # 18 for back BG slot, 19 for front BG slot.
                rotation=90,
                spi_speed_hz=10000000
            )
            # Initialize display.
            self.display.begin()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni 10.96 SPI Colour LCD (160x80) Initialization- Failed - " + str(error))

    def display_led_message(self, message):
        """ Scrolls Provided Text on LED Display. """
        try:
            img = self.image_import.new('RGB', (self.display.width, self.display.height), color=(0, 0, 0))
            draw = self.image_draw_import.Draw(img)
            font = self.image_font_import.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            size_x, size_y = draw.textsize(message, font)

            text_x = 160
            text_y = (80 - size_y) // 2

            t_start = time.time()
            while True:
                x = (time.time() - t_start) * 100
                x %= (size_x + 160)
                draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                draw.text((int(text_x - x), text_y), message, font=font, fill=(255, 255, 255))
                self.display.display(img)
        except Exception as error:
            logger.sensors_logger.error("Scroll Message on 10.96 SPI Colour LCD Failed - " + str(error))
