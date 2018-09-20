"""
This module is for the Pimoroni bh1745 rgb + Lumens
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

pip install bh1745

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from bh1745 import BH1745

round_decimal_to = 5


def lumen():
    bh1745 = BH1745()
    bh1745.setup()
    try:
        r, g, b, var_lumen = bh1745.get_rgbc_raw()
    except Exception as error:
        print("Sensor 'bh1745 lumen' Failed - " + str(error))
        var_lumen = 0

    return round(var_lumen, round_decimal_to)


def rgb():
    bh1745 = BH1745()
    bh1745.setup()
    try:
        rgb_red, rgb_green, rgb_blue, var_lumen = bh1745.get_rgbc_raw()
    except Exception as error:
        print("Sensor 'bh1745 rgb' Failed - " + str(error))
        rgb_red, rgb_green, rgb_blue = 0, 0, 0

    return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)
