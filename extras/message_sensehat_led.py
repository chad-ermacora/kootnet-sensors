"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import sense_hat

sense = sense_hat.SenseHat()


def display_led_message(message):
    """
    Scrolls provided text string on the SenseHAT LED grid. Meant to be used directly with a terminal.
    Example: python3 message_sensehat_led.py "My Fancy Message"
    """
    try:
        set_screen_rotation()
        sense.show_message(str(message), text_colour=(75, 0, 0))
        print("Message Printed to LED Grid: " + message)
    except Exception as error:
        print("Error while showing message on SenseHAT's LED grid || " + str(error))


def set_screen_rotation():
    """ Checks the SenseHAT's accelerometer and sets the screen rotation based on the readings. """
    acc_data = sense.get_accelerometer_raw()

    try:
        if acc_data['x'] < -0.5:
            sense.set_rotation(90)
        elif acc_data['y'] > 0.5:
            sense.set_rotation(0)
        elif acc_data['y'] < -0.5:
            sense.set_rotation(180)
        else:
            sense.set_rotation(270)
    except Exception as error:
        print("Set Screen Rotation Failed || " + str(error))


display_led_message(str(sys.argv[1]))
