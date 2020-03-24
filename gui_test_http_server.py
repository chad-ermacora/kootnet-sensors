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
import io
import sys
import unittest
import guizero
from time import strftime
from threading import Thread
from operations_modules import file_locations
from operations_modules import logger
from operations_modules import app_cached_variables
import test_http_server


def button_go():
    Thread(target=run_tests).start()


def run_tests():
    app_text_output.enable()
    app_text_output.value = "Running Tests, Please wait..."
    app_textbox_address.disable()
    app_button_test_sensor.disable()
    app_text_output.disable()
    test_http_server.sensor_address = app_textbox_address.value
    app_cached_variables.http_login = app_textbox_user.value
    app_cached_variables.http_password = app_textbox_password.value

    test_http_server.bad_sensor_contact = True
    test_http_server.bad_sensor_login = True
    sensor_address = test_http_server.sensor_address
    if test_http_server.get_http_sensor_reading(sensor_address, timeout=5) == "OK":
        test_http_server.bad_sensor_contact = False
        if test_http_server.get_http_sensor_reading(sensor_address, command="TestLogin", timeout=5) == "OK":
            test_http_server.bad_sensor_login = False

    print("Sensor: " + str(test_http_server.sensor_address))
    print("DateTime: " + strftime("%B %d, %Y %H:%M - %Z") + "\n")

    if not test_http_server.bad_sensor_login and not test_http_server.bad_sensor_contact:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_http_server.TestApp)
        suite.run(unittest.TestResult())
    new_text = redirect_string.getvalue()
    app_text_output.enable()
    if test_http_server.bad_sensor_contact:
        new_text += "-- Sensor Offline --\n\n"
        if test_http_server.sensor_address == "localhost":
            new_text += "\nLocal Primary Log\n" + logger.get_sensor_log(file_locations.primary_log)
    elif test_http_server.bad_sensor_login:
        new_text += "-- Incorrect Sensor Login --"
    app_text_output.value = new_text
    app_button_test_sensor.enable()
    app_textbox_address.enable()
    redirect_string.truncate(0)
    redirect_string.seek(0)


redirect_string = io.StringIO()
sys.stdout = redirect_string

app = guizero.App(title="KootNet Sensors - Unit Tester for Beta.29.x", width=622, height=518, layout="grid")
app_text_address = guizero.Text(app, text="Sensor Address", grid=[1, 1], align="left")
app_textbox_address = guizero.TextBox(app, text="localhost", width=40, grid=[2, 1], align="left")
app_button_test_sensor = guizero.PushButton(app, text="Start Tests", command=button_go, grid=[3, 1], align="right")

note_text = "Note: Use a custom port with Address:Port\nExamples: 10.0.1.1:1655 or sensor.location.com:4445"
app_note_text = guizero.Text(app, text=note_text, grid=[1, 2, 3, 1], align="top")

app_text_user = guizero.Text(app, text="Username", grid=[1, 4], align="right")
app_textbox_user = guizero.TextBox(app, text="Kootnet", width=10, grid=[2, 4], align="left")
app_text_password = guizero.Text(app, text="Password", grid=[2, 4], align="right")
app_textbox_password = guizero.TextBox(app, text="sensors", width=10, grid=[3, 4], hide_text=True, align="left")

default_output_text = "Test Output will be shown here"
app_text_output = guizero.TextBox(app, text=default_output_text, multiline=True, scrollbar=True, width=75, height=25,
                                  grid=[1, 6, 3, 1], align="left")
app_text_output.disable()
app.tk.resizable(False, False)
app.display()
