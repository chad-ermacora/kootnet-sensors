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
from time import sleep
from threading import Thread
from operations_modules import logger
from operations_modules import app_config_access

turn_off_display = 30


class CreateLumaOLED:
    """ Creates Function access to the Pimoroni 1.12" Mono OLED (128x128). """

    def __init__(self):
        try:
            self.display_off_count = 0
            self.display_is_on = True
            self.luma_serial_import = __import__('luma.core.interface.serial', fromlist=['i2c'])
            self.luma_sh1106_import = __import__('luma.oled.device', fromlist=['sh1106'])
            self.luma_canvas_import = __import__('luma.core.render', fromlist=['canvas'])
            serial = self.luma_serial_import.i2c(port=1, address=0x3C)
            self.device = self.luma_sh1106_import.sh1106(serial_interface=serial, width=128, height=128, rotate=2)

            self.thread_display_power_saving = Thread(target=self._display_timed_off)
            self.thread_display_power_saving.daemon = True
            self.thread_display_power_saving.start()
            logger.sensors_logger.debug("Pimoroni 1.12 Mono OLED (128x128) Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni 1.12 Mono OLED (128x128) Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_mono_oled_luma = 0
            app_config_access.installed_sensors.has_display = 0

    def _display_timed_off(self):
        while True:
            if self.display_is_on:
                if self.display_off_count > turn_off_display:
                    self.device.hide()
                    self.display_is_on = False
                else:
                    self.display_off_count += 1
            sleep(1)

    @staticmethod
    def _format_message(message):
        """ Formats text message to fit on Display. """
        message_length = len(message)

        return_message = ""
        character_count = 0
        while message_length > character_count:
            if character_count + 20 <= message_length:
                end_character_count = character_count + 20
                return_message += message[character_count:end_character_count] + "\n"
                character_count = end_character_count
            else:
                return_message += message[character_count:]
                character_count = message_length
        return return_message

    def display_text(self, message):
        """ Shows Provided Text on LED Display. """
        self.device.show()
        self.display_off_count = 0
        self.display_is_on = True

        try:
            clean_message = self._format_message(message)
            with self.luma_canvas_import.canvas(self.device) as draw:
                draw.rectangle(self.device.bounding_box, outline="white", fill="black")
                draw.text((5, 5), clean_message, fill="white")
        except Exception as error:
            logger.sensors_logger.error("Message on 1.12 Mono OLED - Failed: " + str(error))
