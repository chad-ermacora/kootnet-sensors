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
import requests
import unittest

http_login = "Kootnet"
http_password = "sensors"

sensor_address = "localhost"
default_http_port = "10065"
no_sensor_present = "NoSensor"
command_data_separator = "[new_data_section]"

sensor_get_commands = ["CheckOnlineStatus", "GetHostName", "GetSystemUptime", "GetIntervalSensorReadings",
                       "GetSensorsLatency", "GetCPUTemperature", "GetEnvTemperature", "GetTempOffsetEnv", "GetPressure",
                       "GetAltitude", "GetHumidity", "GetDistance", "GetAllGas", "GetGasResistanceIndex",
                       "GetGasOxidised", "GetGasReduced", "GetGasNH3", "GetAllParticulateMatter",
                       "GetParticulateMatter1", "GetParticulateMatter2_5", "GetParticulateMatter10", "GetLumen",
                       "GetEMS", "GetAllUltraViolet", "GetUltraVioletA", "GetUltraVioletB", "GetAccelerometerXYZ",
                       "GetMagnetometerXYZ", "GetGyroscopeXYZ"]


class TestApp(unittest.TestCase):
    def test_html_display_text(self):
        self.assertTrue(http_display_text_on_sensor("This is a Test Message"))

    def test_sensor_get_commands(self):
        sensor_responses = []
        for command in sensor_get_commands:
            sensor_responses.append(get_http_sensor_reading(command))

        bad_count = 0
        for response in sensor_responses:
            if response is None:
                bad_count += 1

        if bad_count > 0:
            log_msg = "Warning: " + str(bad_count) + " Bad HTTPS Responses out of " + str(len(sensor_get_commands))
            print(log_msg + " - Server Offline or Bad Network Connection?")
        if not bad_count == len(sensor_get_commands):
            # from routes file system_commands.py
            self.assertTrue(sensor_responses[0] == "OK")
            self.assertTrue(isinstance(sensor_responses[1], str))
            if not check_no_sensor_return(sensor_responses[2], sensor_get_commands[2]):
                self.assertTrue(isinstance(sensor_responses[2], str))
            # from routes file text_sensor_readings.py
            if not check_no_sensor_return(sensor_responses[3], sensor_get_commands[3]):
                sensor_reading = sensor_responses[3].split(command_data_separator)
                self.assertTrue(len(sensor_reading[0].split(",")) > 0)
                self.assertTrue(len(sensor_reading[1].split(",")) > 0)
            if not check_no_sensor_return(sensor_responses[4], sensor_get_commands[4]):
                sensor_reading = sensor_responses[4].split(command_data_separator)
                self.assertTrue(len(sensor_reading[0].split(",")) > 0)
                self.assertTrue(len(sensor_reading[1].split(",")) > 0)
            if not check_no_sensor_return(sensor_responses[5], sensor_get_commands[5]):
                self.assertTrue(isinstance(float(sensor_responses[5]), float))
            if not check_no_sensor_return(sensor_responses[6], sensor_get_commands[6]):
                self.assertTrue(isinstance(float(sensor_responses[6]), float))
            if not check_no_sensor_return(sensor_responses[7], sensor_get_commands[7]):
                self.assertTrue(isinstance(float(sensor_responses[7]), float))
            if not check_no_sensor_return(sensor_responses[8], sensor_get_commands[8]):
                self.assertTrue(isinstance(float(sensor_responses[8]), float))
            if not check_no_sensor_return(sensor_responses[9], sensor_get_commands[9]):
                self.assertTrue(isinstance(float(sensor_responses[9]), float))
            if not check_no_sensor_return(sensor_responses[10], sensor_get_commands[10]):
                self.assertTrue(isinstance(float(sensor_responses[10]), float))
            if not check_no_sensor_return(sensor_responses[11], sensor_get_commands[11]):
                self.assertTrue(isinstance(float(sensor_responses[11]), float))
            if not check_no_sensor_return(sensor_responses[12], sensor_get_commands[12]):
                self.assertTrue(len(sensor_responses[12][1:-1].split(",")) == 4)
            if not check_no_sensor_return(sensor_responses[13], sensor_get_commands[13]):
                self.assertTrue(isinstance(float(sensor_responses[13]), float))
            if not check_no_sensor_return(sensor_responses[14], sensor_get_commands[14]):
                self.assertTrue(isinstance(float(sensor_responses[14]), float))
            if not check_no_sensor_return(sensor_responses[15], sensor_get_commands[15]):
                self.assertTrue(isinstance(float(sensor_responses[15]), float))
            if not check_no_sensor_return(sensor_responses[16], sensor_get_commands[16]):
                self.assertTrue(isinstance(float(sensor_responses[16]), float))
            if not check_no_sensor_return(sensor_responses[17], sensor_get_commands[17]):
                self.assertTrue(len(sensor_responses[17][1:-1].split(",")) == 3)
            if not check_no_sensor_return(sensor_responses[18], sensor_get_commands[18]):
                self.assertTrue(isinstance(float(sensor_responses[18]), float))
            if not check_no_sensor_return(sensor_responses[19], sensor_get_commands[19]):
                self.assertTrue(isinstance(float(sensor_responses[19]), float))
            if not check_no_sensor_return(sensor_responses[20], sensor_get_commands[20]):
                self.assertTrue(isinstance(float(sensor_responses[20]), float))
            if not check_no_sensor_return(sensor_responses[21], sensor_get_commands[21]):
                self.assertTrue(isinstance(float(sensor_responses[21]), float))
            if not check_no_sensor_return(sensor_responses[22], sensor_get_commands[22]):
                sensor_reading = sensor_responses[22][1:-1].split(",")
                self.assertTrue(isinstance(float(sensor_reading[0]), float))
            if not check_no_sensor_return(sensor_responses[23], sensor_get_commands[23]):
                self.assertTrue(len(sensor_responses[23][1:-1].split(",")) == 2)
            if not check_no_sensor_return(sensor_responses[24], sensor_get_commands[24]):
                self.assertTrue(isinstance(float(sensor_responses[24]), float))
            if not check_no_sensor_return(sensor_responses[25], sensor_get_commands[25]):
                self.assertTrue(isinstance(float(sensor_responses[25]), float))
            if not check_no_sensor_return(sensor_responses[26], sensor_get_commands[26]):
                sensor_reading = sensor_responses[26][1:-1].split(",")
                self.assertTrue(isinstance(float(sensor_reading[0]), float))
                self.assertTrue(isinstance(float(sensor_reading[1]), float))
                self.assertTrue(isinstance(float(sensor_reading[2]), float))
            if not check_no_sensor_return(sensor_responses[27], sensor_get_commands[27]):
                sensor_reading = sensor_responses[27][1:-1].split(",")
                self.assertTrue(isinstance(float(sensor_reading[0]), float))
                self.assertTrue(isinstance(float(sensor_reading[1]), float))
                self.assertTrue(isinstance(float(sensor_reading[2]), float))
            if not check_no_sensor_return(sensor_responses[28], sensor_get_commands[28]):
                sensor_reading = sensor_responses[28][1:-1].split(",")
                self.assertTrue(isinstance(float(sensor_reading[0]), float))
                self.assertTrue(isinstance(float(sensor_reading[1]), float))
                self.assertTrue(isinstance(float(sensor_reading[2]), float))
        else:
            self.assertTrue(False)


def get_http_sensor_reading(command="CheckOnlineStatus", timeout=10):
    """ Returns requested remote sensor data (based on the provided command data). """
    try:
        url = "https://" + sensor_address + ":" + default_http_port + "/" + command
        login_credentials = (http_login, http_password)
        tmp_return_data = requests.get(url=url, timeout=timeout, verify=False, auth=login_credentials)
        if tmp_return_data.status_code == 200:
            return tmp_return_data.text
        return None
    except Exception as error:
        log_msg = "Remote Sensor Data Request - HTTPS GET Error for " + sensor_address + ": " + str(error)
        print(log_msg)
        return None


def http_display_text_on_sensor(text_message):
    """ Sends provided text message to a remote sensor's display. """
    try:
        url = "https://" + sensor_address + ":" + default_http_port + "/DisplayText"
        login_credentials = (http_login, http_password)
        tmp_return_data = requests.put(url=url, timeout=4, data={'command_data': text_message}, verify=False, auth=login_credentials)
        if tmp_return_data.text == "OK":
            return True
    except Exception as error:
        print("Unable to display text on Sensor: " + str(error))
    return False


def check_no_sensor_return(sensor_data, data_name):
    if sensor_data == no_sensor_present:
        print("Warning: " + data_name + " No Sensor Present")
        return True
    return False


if __name__ == '__main__':
    unittest.main()
