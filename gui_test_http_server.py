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
from operations_modules import app_generic_functions
from operations_modules import logger
import test_http_server


def button_go():
    Thread(target=run_tests).start()


def run_tests():
    app_text_output.enable()
    app_text_output.value = "Running Tests, Please wait..."
    app_textbox_address.disable()
    app_button_test_sensor.disable()
    app_text_output.disable()
    tmp_ip = app_textbox_address.value
    tmp_port = test_http_server.default_http_port
    if app_generic_functions.check_for_port_in_address(tmp_ip):
        ip_port_list = app_generic_functions.get_ip_and_port_split(tmp_ip)
        tmp_ip = ip_port_list[0].strip()
        tmp_port = ip_port_list[1].strip()
    test_http_server.sensor_address = tmp_ip
    test_http_server.default_http_port = tmp_port

    test_http_server.bad_sensor_contact = True
    if test_http_server.get_http_sensor_reading(tmp_ip, http_port=tmp_port, timeout=5) == "OK":
        test_http_server.bad_sensor_contact = False

    print("Sensor: " + str(test_http_server.sensor_address) + ":" + str(test_http_server.default_http_port))
    print("DateTime: " + strftime("%B %d, %Y %H:%M - %Z") + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(test_http_server.TestApp)
    suite.run(unittest.TestResult())
    new_text = redirect_string.getvalue()
    app_text_output.enable()
    if test_http_server.bad_sensor_contact:
        if test_http_server.sensor_address == "localhost":
            new_text += "\nLocal Primary Log\n" + logger.get_sensor_log(file_locations.primary_log)
    app_text_output.value = new_text
    app_button_test_sensor.enable()
    app_textbox_address.enable()
    redirect_string.truncate(0)
    redirect_string.seek(0)


redirect_string = io.StringIO()
sys.stdout = redirect_string

app = guizero.App(title="KootNet Sensors - Unit Tester for Beta.29.x", width=622, height=518, layout="grid")
app_address_text = guizero.Text(app, text="Sensor Address", grid=[1, 1], align="left")
app_textbox_address = guizero.TextBox(app, text="localhost", width=40, grid=[2, 1], align="left")
app_button_test_sensor = guizero.PushButton(app, text="Start Tests", command=button_go, grid=[3, 1], align="right")

note_text = "Note: Use a custom port with Address:Port\nExamples: 10.0.1.1:1655 or sensor.location.com:4445"
app_note_text = guizero.Text(app, text=note_text, grid=[1, 2, 3, 1], align="top")

default_output_text = "Test Output will be shown here"
app_text_output = guizero.TextBox(app, text=default_output_text, multiline=True, scrollbar=True, width=75, height=25,
                                  grid=[1, 3, 3, 1], align="left")
app_text_output.disable()
app.tk.resizable(False, False)
app.display()
