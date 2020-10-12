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
from json import loads as json_loads
from operations_modules.app_generic_functions import get_http_sensor_reading, http_display_text_on_sensor, \
    send_http_command
from operations_modules.app_cached_variables import no_sensor_present, command_data_separator, \
    CreateNetworkGetCommands, CreateNetworkSetCommands
from tests.create_test_configs import *


class TestApp(unittest.TestCase):
    def test_primary_config(self):
        self.assertTrue(self._config_test_changes(primary_config_test,
                                                  remote_get.sensor_configuration_file,
                                                  remote_set.set_primary_configuration,
                                                  config_name="Primary"))

    def test_installed_sensors_config(self):
        self.assertTrue(self._config_test_changes(installed_sensors_config_test,
                                                  remote_get.installed_sensors_file,
                                                  remote_set.set_installed_sensors,
                                                  config_name="Installed Sensors"))

    def test_display_config(self):
        self.assertTrue(self._config_test_changes(display_config_test,
                                                  remote_get.display_configuration_file,
                                                  remote_set.set_display_config,
                                                  config_name="Display"))

    def test_interval_recording_config(self):
        self.assertTrue(self._config_test_changes(interval_recording_config_test,
                                                  remote_get.interval_configuration_file,
                                                  remote_set.set_interval_configuration,
                                                  config_name="Interval Recording"))

    def test_high_low_recording_config(self):
        self.assertTrue(self._config_test_changes(trigger_high_low_config_test,
                                                  remote_get.high_low_trigger_configuration_file,
                                                  remote_set.set_high_low_trigger_config,
                                                  config_name="High/Low Trigger Recording"))

    def test_trigger_variances_config(self):
        self.assertTrue(self._config_test_changes(trigger_variances_config_test,
                                                  remote_get.variance_config_file,
                                                  remote_set.set_variance_configuration,
                                                  config_name="Variance Trigger Recording"))

    def test_email_config(self):
        self.assertTrue(self._config_test_changes(email_config_test,
                                                  remote_get.email_configuration_file,
                                                  remote_set.set_email_configuration,
                                                  config_name="Email"))

    def test_mqtt_publisher_config(self):
        self.assertTrue(self._config_test_changes(mqtt_publisher_config_test,
                                                  remote_get.mqtt_publisher_configuration_file,
                                                  remote_set.set_mqtt_publisher_configuration,
                                                  config_name="MQTT Publisher"))

    def test_mqtt_subscriber_config(self):
        self.assertTrue(self._config_test_changes(mqtt_subscriber_config_test,
                                                  remote_get.mqtt_subscriber_configuration_file,
                                                  remote_set.set_mqtt_subscriber_configuration,
                                                  config_name="MQTT Subscriber"))

    def test_sensor_control_config(self):
        self.assertTrue(self._config_test_changes(sensor_control_config_test,
                                                  remote_get.sensor_control_configuration_file,
                                                  remote_set.set_sensor_control_configuration,
                                                  config_name="Sensor Control"))

    def test_weather_underground_config(self):
        self.assertTrue(self._config_test_changes(weather_underground_config_test,
                                                  remote_get.weather_underground_config_file,
                                                  remote_set.set_weather_underground_configuration,
                                                  config_name="Weather Underground"))

    def test_luftdaten_config(self):
        self.assertTrue(self._config_test_changes(luftdaten_config_test,
                                                  remote_get.luftdaten_config_file,
                                                  remote_set.set_luftdaten_configuration,
                                                  config_name="Luftdaten"))

    def test_open_sense_map_config(self):
        self.assertTrue(self._config_test_changes(open_sense_map_config_test,
                                                  remote_get.open_sense_map_config_file,
                                                  remote_set.set_open_sense_map_configuration,
                                                  config_name="OSM"))

    def _config_test_changes(self, config_instance, config_get_command, config_set_command, config_name=""):
        original_config = get_http_sensor_reading(sensor_address, command=config_get_command)

        config_instance.set_settings_for_test1()

        send_config = config_instance.get_config_as_str()
        send_http_command(sensor_address, command=config_set_command, included_data=send_config, test_run=True)
        first_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), first_set_config, config_name=config_name + " 1"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False

        config_instance.set_settings_for_test2()

        send_config = config_instance.get_config_as_str()
        send_http_command(sensor_address, command=config_set_command, included_data=send_config, test_run=True)
        second_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), second_set_config, config_name=config_name + " 2"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False

        send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)

        original_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(original_config, original_set_config, config_name=config_name + " 3"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False
        return True

    @staticmethod
    def _bad_config(sent_config, received_config, config_name=""):
        if config_name[:-2] == "Installed Sensors":
            list_sent_config = sent_config.strip().split("\n")
            new_sent_config = ""
            for index, line in enumerate(list_sent_config):
                if index == 3:
                    new_sent_config += line.split("=")[0].strip() + " = RPi\n"
                else:
                    new_sent_config += line.strip() + "\n"
            sent_config = new_sent_config.strip()

            list_received_config = received_config.strip().split("\n")
            new_received_config = ""
            for index, line in enumerate(list_received_config):
                if index == 3:
                    new_received_config += line.split("=")[0].strip() + " = RPi\n"
                else:
                    new_received_config += line.strip() + "\n"
            received_config = new_received_config.strip()

        if sent_config.strip() == received_config.strip():
            print("Info: Configuration " + config_name + " Check OK.")
            return False
        print("Error: Sent " + config_name + " Configuration is different from Received Configuration\n")
        print("-Sent Configuration-\n" + str(sent_config) + "\n-Received Configuration-\n" + str(received_config))
        return True


class TestApp2(unittest.TestCase):
    def test_html_display_text(self):
        msg = "This is a Test Message"
        if http_display_text_on_sensor(msg, sensor_address):
            print("Info: Sent Sensor Display Message OK")
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            print("Error: Sent Sensor Display Message Failed")

    def test_sensor_get_commands(self):
        sensor_responses = []
        for command in sensor_get_commands:
            sensor_responses.append(get_http_sensor_reading(sensor_address, command=command, timeout=5))

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
            check_float_reading(sensor_responses[5], sensor_get_commands[5])
            self.assertTrue(isinstance(float(sensor_responses[5]), float))
        if not check_no_sensor_return(sensor_responses[6], sensor_get_commands[6]):
            check_float_reading(sensor_responses[6], sensor_get_commands[6])
            self.assertTrue(isinstance(float(sensor_responses[6]), float))
        if not check_no_sensor_return(sensor_responses[7], sensor_get_commands[7]):
            check_float_reading(sensor_responses[7], sensor_get_commands[7])
            self.assertTrue(isinstance(float(sensor_responses[7]), float))
        if not check_no_sensor_return(sensor_responses[8], sensor_get_commands[8]):
            check_float_reading(sensor_responses[8], sensor_get_commands[8])
            self.assertTrue(isinstance(float(sensor_responses[8]), float))
        if not check_no_sensor_return(sensor_responses[9], sensor_get_commands[9]):
            check_float_reading(sensor_responses[9], sensor_get_commands[9])
            self.assertTrue(isinstance(float(sensor_responses[9]), float))
        if not check_no_sensor_return(sensor_responses[10], sensor_get_commands[10]):
            check_float_reading(sensor_responses[10], sensor_get_commands[10])
            self.assertTrue(isinstance(float(sensor_responses[10]), float))
        if not check_no_sensor_return(sensor_responses[11], sensor_get_commands[11]):
            check_float_reading(sensor_responses[11], sensor_get_commands[11])
            self.assertTrue(isinstance(float(sensor_responses[11]), float))
        if not check_no_sensor_return(sensor_responses[12], sensor_get_commands[12]):
            check_dict_floats(sensor_responses[12], sensor_get_commands[12])
            # self.assertTrue(len(sensor_reading) == 4)
        if not check_no_sensor_return(sensor_responses[13], sensor_get_commands[13]):
            check_dict_floats(sensor_responses[13], sensor_get_commands[13])
            # self.assertTrue(len(sensor_reading) == 3)
        if not check_no_sensor_return(sensor_responses[14], sensor_get_commands[14]):
            check_float_reading(sensor_responses[14], sensor_get_commands[14])
            self.assertTrue(isinstance(float(sensor_responses[14]), float))
        if not check_no_sensor_return(sensor_responses[15], sensor_get_commands[15]):
            check_dict_floats(sensor_responses[15], sensor_get_commands[15])
            # self.assertTrue(isinstance(float(sensor_reading[0]), float))
        if not check_no_sensor_return(sensor_responses[16], sensor_get_commands[16]):
            check_dict_floats(sensor_responses[16], sensor_get_commands[16])
            # self.assertTrue(len(sensor_responses[23][1:-1].split(",")) == 2)
        if not check_no_sensor_return(sensor_responses[17], sensor_get_commands[17]):
            sensor_reading = sensor_responses[17][1:-1].split(",")
            for index, reading in enumerate(sensor_reading):
                check_float_reading(reading, sensor_get_commands[17] + str(index))
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))
        if not check_no_sensor_return(sensor_responses[18], sensor_get_commands[18]):
            sensor_reading = sensor_responses[18][1:-1].split(",")
            for index, reading in enumerate(sensor_reading):
                check_float_reading(reading, sensor_get_commands[18] + str(index))
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))
        if not check_no_sensor_return(sensor_responses[19], sensor_get_commands[19]):
            sensor_reading = sensor_responses[19][1:-1].split(",")
            for index, reading in enumerate(sensor_reading):
                check_float_reading(reading, sensor_get_commands[19] + str(index))
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))


def check_no_sensor_return(sensor_data, data_name):
    if sensor_data == no_sensor_present:
        print("Warning: " + data_name + " Reading as No Sensor Present")
        return True
    return False


def check_float_reading(sensor_data, data_name):
    try:
        reading = float(sensor_data)
        print("Info: " + data_name + " = " + str(reading))
    except Exception as error:
        print("Error: " + data_name + " - " + str(error))


def check_dict_floats(sensor_data, data_name):
    try:
        readings = json_loads(sensor_data)
        for key in readings:
            if not check_no_sensor_return(readings[key], key):
                reading = float(readings[key])
                print("Info: " + str(key) + " = " + str(reading))
    except Exception as error:
        print("Error: " + data_name + " - " + str(error))


primary_config_test = CreatePrimaryConfigurationTest()
installed_sensors_config_test = CreateInstalledSensorsConfigurationTest()
display_config_test = CreateDisplayConfigurationTest()
interval_recording_config_test = CreateIntervalRecordingConfigurationTest()
trigger_high_low_config_test = CreateTriggerHighLowConfigurationTest()
trigger_variances_config_test = CreateTriggerVariancesConfigurationTest()
email_config_test = CreateEmailConfigurationTest()
mqtt_publisher_config_test = CreateMQTTPublisherConfigurationTest()
mqtt_subscriber_config_test = CreateMQTTSubscriberConfigurationTest()
sensor_control_config_test = CreateSensorControlConfigurationTest()
weather_underground_config_test = CreateWeatherUndergroundConfigurationTest()
luftdaten_config_test = CreateLuftdatenConfigurationTest()
open_sense_map_config_test = CreateOpenSenseMapConfigurationTest()

sensor_address = "localhost"

remote_set = CreateNetworkSetCommands()
remote_get = CreateNetworkGetCommands()
sensor_get_commands = [
    remote_get.check_online_status, remote_get.sensor_name, remote_get.system_uptime,
    remote_get.sensor_readings, remote_get.sensors_latency, remote_get.cpu_temp,
    remote_get.environmental_temp, remote_get.env_temp_offset, remote_get.pressure,
    remote_get.altitude, remote_get.humidity, remote_get.distance, remote_get.all_gas,  # gas = 12
    remote_get.all_particulate_matter, remote_get.lumen, remote_get.electromagnetic_spectrum,
    remote_get.all_ultra_violet, remote_get.accelerometer_xyz, remote_get.magnetometer_xyz,
    remote_get.gyroscope_xyz
]

if __name__ == '__main__':
    if get_http_sensor_reading(sensor_address, timeout=5) == "OK":
        if get_http_sensor_reading(sensor_address, command="TestLogin", timeout=5) == "OK":
            unittest.main()
        else:
            print("\n-- Incorrect Sensor Login --\n")
    else:
        print("\n-- Sensor Offline --\n")
