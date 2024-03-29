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
from configuration_modules import app_config_access
from operations_modules import file_locations


class CreateST7735:
    """ Creates Function access to the Pimoroni 10.96" SPI Colour LCD (160x80). """

    def __init__(self):
        self.display_in_use = False
        try:
            self.pill_import = __import__("PIL", fromlist=["Image", "ImageDraw", "ImageFont"])
            st7735_import = __import__("sensor_modules.drivers.ST7735", fromlist=["ST7735", "BG_SPI_CS_FRONT"])
            # Create ST7735 LCD display class.
            self.display = st7735_import.ST7735(
                port=0,
                cs=st7735_import.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
                dc=9,
                backlight=19,  # 18 for back BG slot, 19 for front BG slot.
                rotation=90,
                spi_speed_hz=10000000
            )
            # Initialize display.
            self.display.begin()
            logger.sensors_logger.debug("Pimoroni 10.96 SPI Colour LCD (160x80) Initialization - OK")
        except Exception as error:
            log_message = "Pimoroni 10.96 SPI Colour LCD (160x80) Initialization - Failed: "
            logger.sensors_logger.error(log_message + str(error))
            app_config_access.installed_sensors.pimoroni_st7735 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def display_text(self, message):
        """ Scrolls Provided Text on LED Display. """
        if not self.display_in_use:
            self.display_in_use = True
            try:
                img = self.pill_import.Image.new("RGB", (self.display.width, self.display.height), color=(0, 0, 0))
                draw = self.pill_import.ImageDraw.Draw(img)
                font = self.pill_import.ImageFont.truetype(file_locations.display_font, 30)
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
                logger.sensors_logger.error("Scroll Message on 10.96 SPI Colour LCD - Failed: " + str(error))
            self.display_in_use = False
        else:
            logger.sensors_logger.debug("10.96 SPI Colour LCD - In Use")
