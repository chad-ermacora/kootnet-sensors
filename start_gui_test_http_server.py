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
from operations_modules.app_cached_variables import CreateNetworkGetCommands
from operations_modules.http_generic_network import get_http_sensor_reading
from operations_modules.software_version import CreateRefinedVersion
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables
from tests import test_http_server

compatible_version_str = "Beta.34.x"
refined_compatible_version = CreateRefinedVersion("Beta.34.144")
remote_sensor_version = CreateRefinedVersion()
sg_commands = CreateNetworkGetCommands()


def button_go():
    Thread(target=run_tests).start()


def run_tests():
    app_text_output.enable()
    app_text_output.value = "Running Tests, Please wait..."
    app_textbox_address.disable()
    app_button_test_sensor.disable()
    app_text_output.disable()
    rm_cached_variables.http_login = app_textbox_user.value
    rm_cached_variables.http_password = app_textbox_password.value

    sensor_address = app_textbox_address.value
    test_http_server.sensor_address = sensor_address

    print("Sensor: " + str(sensor_address) + "\n\n")
    if get_http_sensor_reading(sensor_address, timeout=5) == "OK":
        if get_http_sensor_reading(sensor_address, http_command=sg_commands.check_portal_login, timeout=5) == "OK":
            temp_version = get_http_sensor_reading(sensor_address, http_command=sg_commands.program_version, timeout=5)
            remote_sensor_version.load_from_string(temp_version)
            if remote_sensor_version.major_version == refined_compatible_version.major_version and \
                    remote_sensor_version.feature_version == refined_compatible_version.feature_version and \
                    remote_sensor_version.minor_version >= refined_compatible_version.minor_version:
                print(" ------ Starting Tests ------")
                print("   " + strftime("%B %d, %Y %H:%M:%S") + "\n")
                print("   Configuration Tests\n")
                suite = unittest.TestLoader().loadTestsFromTestCase(test_http_server.TestApp)
                suite.run(unittest.TestResult())
                print("\n\n   Display & Sensor Reading Tests\n")
                suite2 = unittest.TestLoader().loadTestsFromTestCase(test_http_server.TestApp2)
                suite2.run(unittest.TestResult())
            else:
                print("-- Incompatible Version Detected --\n")
                print_msg = "-- Compatible Version: " + refined_compatible_version.get_version_string()
                print(print_msg + " (" + str(refined_compatible_version.minor_version) + " or higher) --")
                print("-- Remote Version: " + remote_sensor_version.get_version_string() + " --")
        else:
            print("-- Incorrect Sensor Login --")
    else:
        print("-- Sensor Offline --\n\n")
        if sensor_address == "localhost":
            print("Local Primary Log\n" + logger.get_sensor_log(file_locations.primary_log))

    print("\n\n ------ End of Tests ------")
    print("   " + strftime("%B %d, %Y %H:%M:%S") + "\n")
    app_text_output.enable()
    app_text_output.value = redirect_string.getvalue()
    app_button_test_sensor.enable()
    app_textbox_address.enable()
    redirect_string.truncate(0)
    redirect_string.seek(0)


redirect_string = io.StringIO()
sys.stdout = redirect_string

app_title_name = "KootNet Sensors - Unit Tester for " + compatible_version_str
app = guizero.App(title=app_title_name, width=622, height=538, layout="grid")
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
