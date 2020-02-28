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
import unittest
from time import sleep
from operations_modules.app_generic_functions import get_http_sensor_reading, http_display_text_on_sensor, \
    send_http_command
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables import no_sensor_present, command_data_separator, \
    CreateNetworkGetCommands, CreateNetworkSetCommands
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration

primary_config_test = CreatePrimaryConfiguration(load_from_file=False)
installed_sensors_config_test = CreateInstalledSensorsConfiguration(load_from_file=False)
trigger_variances_config_test = CreateTriggerVariancesConfiguration(load_from_file=False)
sensor_control_config_test = CreateSensorControlConfiguration(load_from_file=False)
weather_underground_config_test = CreateWeatherUndergroundConfiguration(load_from_file=False)
luftdaten_config_test = CreateLuftdatenConfiguration(load_from_file=False)
open_sense_map_config_test = CreateOpenSenseMapConfiguration(load_from_file=False)

bad_sensor_contact_msg = " --- Sensor appears to be Offline ---"

sensor_address = "localhost"
default_http_port = "10065"
http_login = "Kootnet"
http_password = "sensors"
app_cached_variables.http_login = http_login
app_cached_variables.http_password = http_password

remote_set = CreateNetworkSetCommands()
remote_get = CreateNetworkGetCommands()
sensor_get_commands = [remote_get.check_online_status, remote_get.sensor_name, remote_get.system_uptime,
                       remote_get.sensor_readings, remote_get.sensors_latency, remote_get.cpu_temp,
                       remote_get.environmental_temp, remote_get.env_temp_offset, remote_get.pressure,
                       remote_get.altitude, remote_get.humidity, remote_get.distance, remote_get.all_gas,
                       remote_get.gas_index, remote_get.gas_oxidised, remote_get.gas_reduced, remote_get.gas_nh3,
                       remote_get.all_particulate_matter, remote_get.pm_1, remote_get.pm_2_5, remote_get.pm_10,
                       remote_get.lumen, remote_get.electromagnetic_spectrum, remote_get.all_ultra_violet,
                       remote_get.ultra_violet_a, remote_get.ultra_violet_b, remote_get.accelerometer_xyz,
                       remote_get.magnetometer_xyz, remote_get.gyroscope_xyz]


bad_sensor_contact = True
if get_http_sensor_reading(sensor_address, http_port=default_http_port, timeout=5) == "OK":
    bad_sensor_contact = False


class TestApp(unittest.TestCase):
    def test_primary_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(primary_config_test,
                                                      remote_get.sensor_configuration_file,
                                                      remote_set.set_primary_configuration))

    def test_installed_sensors_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(installed_sensors_config_test,
                                                      remote_get.installed_sensors_file,
                                                      remote_set.set_installed_sensors))

    def test_trigger_variances_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(trigger_variances_config_test,
                                                      remote_get.variance_config,
                                                      remote_set.set_variance_configuration))

    def test_sensor_control_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(sensor_control_config_test,
                                                      remote_get.sensor_control_configuration_file,
                                                      remote_set.set_sensor_control_configuration))

    def test_weather_underground_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(weather_underground_config_test,
                                                      remote_get.weather_underground_config_file,
                                                      remote_set.set_weather_underground_configuration))

    def test_luftdaten_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(luftdaten_config_test,
                                                      remote_get.luftdaten_config_file,
                                                      remote_set.set_luftdaten_configuration))

    def test_open_sense_map_config(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            self.assertTrue(self._config_test_changes(open_sense_map_config_test,
                                                      remote_get.open_sense_map_config_file,
                                                      remote_set.set_open_sense_map_configuration))

    def _config_test_changes(self, config_instance, config_get_command, config_set_command):
        original_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        config_instance.set_settings_for_test1()
        send_http_command(sensor_address, command=config_set_command, http_port=default_http_port,
                          included_data=config_instance.get_config_as_str(), test_run=True)
        first_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), first_set_config):
            return False
        config_instance.set_settings_for_test2()
        send_http_command(sensor_address, command=config_set_command, http_port=default_http_port,
                          included_data=config_instance.get_config_as_str(), test_run=True)
        second_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), second_set_config):
            return False

        send_http_command(sensor_address, command=config_set_command, http_port=default_http_port,
                          included_data=original_config, test_run=True)
        original_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(original_config, original_set_config):
            return False
        return True

    @staticmethod
    def _bad_config(sent_config, received_config):
        if sent_config == received_config:
            print("Info: Configuration Check OK.")
            return False
        print("Error: Sent Configuration is different from Received Configuration\n")
        print("-Sent Configuration-\n" + str(sent_config) + "\n-Received Configuration-\n" + str(received_config))
        return True

    def test_html_display_text(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            msg = "This is a Test Message"
            if http_display_text_on_sensor(msg, sensor_address, http_port=default_http_port):
                print("Info: Sent Sensor Display Message OK")
                self.assertTrue(True)
            else:
                self.assertTrue(False)
                print("Error: Sent Sensor Display Message Failed")

    def test_sensor_get_commands(self):
        if bad_sensor_contact:
            print(bad_sensor_contact_msg)
            self.assertTrue(False)
        else:
            sensor_responses = []
            for command in sensor_get_commands:
                sensor_responses.append(get_http_sensor_reading(sensor_address, command=command,
                                                                http_port=default_http_port, timeout=5))

            bad_count = 0
            for response in sensor_responses:
                if response is None:
                    bad_count += 1

            if bad_count > 0:
                log_msg = "Warning: " + str(bad_count) + " Bad HTTPS Responses out of " + str(len(sensor_get_commands))
                print(log_msg + " - Bad Network Connection?")
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
        sleep(1)


def check_no_sensor_return(sensor_data, data_name):
    if sensor_data == no_sensor_present:
        print("Warning: " + data_name + " Reading as No Sensor Present")
        return True
    print("Info: " + data_name + " OK")
    return False


if __name__ == '__main__':
    unittest.main()
