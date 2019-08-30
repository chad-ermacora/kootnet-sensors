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
import logging
import requests

logging.captureWarnings(True)
no_sensor_present = "NoSensor"

http_username = "Kootnet"
http_password = "sensors"

http_ip = "localhost"
http_port = "10065"


def test_html_get_hostname():
    sensor_reading = _get_sensor_reading("GetHostName")
    if type(sensor_reading) == str:
        return True
    return False


def test_html_system_uptime():
    sensor_reading = _get_sensor_reading("GetSystemUptime")
    if type(sensor_reading) == str:
        return True
    return False


def test_html_get_cpu_temperature():
    sensor_reading = _get_sensor_reading("GetCPUTemperature")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_env_temperature():
    sensor_reading = _get_sensor_reading("GetEnvTemperature")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_env_temp_offset():
    sensor_reading = _get_sensor_reading("GetTempOffsetEnv")
    if sensor_reading == "0.0" or float(sensor_reading):
        return True
    return False


def test_html_get_pressure():
    sensor_reading = _get_sensor_reading("GetPressure")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_altitude():
    sensor_reading = _get_sensor_reading("GetAltitude")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_humidity():
    sensor_reading = _get_sensor_reading("GetHumidity")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_distance():
    sensor_reading = _get_sensor_reading("GetDistance")
    if sensor_reading == "0.0" or sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_resistance_index():
    sensor_reading = _get_sensor_reading("GetGasResistanceIndex")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_oxidised():
    sensor_reading = _get_sensor_reading("GetGasOxidised")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_reduced():
    sensor_reading = _get_sensor_reading("GetGasReduced")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_nh3():
    sensor_reading = _get_sensor_reading("GetGasNH3")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter1():
    sensor_reading = _get_sensor_reading("GetParticulateMatter1")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter2_5():
    sensor_reading = _get_sensor_reading("GetParticulateMatter2_5")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter10():
    sensor_reading = _get_sensor_reading("GetParticulateMatter10")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_lumen():
    sensor_reading = _get_sensor_reading("GetLumen")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_visible_ems():
    sensor_readings = _get_sensor_reading("GetEMS")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_uva():
    sensor_reading = _get_sensor_reading("GetUltraVioletA")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_uvb():
    sensor_reading = _get_sensor_reading("GetUltraVioletB")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_accelerometer():
    sensor_readings = _get_sensor_reading("GetAccelerometerXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_magnetometer():
    sensor_readings = _get_sensor_reading("GetMagnetometerXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_gyroscope():
    sensor_readings = _get_sensor_reading("GetGyroscopeXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def _get_sensor_reading(command):
    """ Returns requested sensor data (based on the provided command data). """
    url = "https://" + http_ip + ":" + http_port + "/" + command
    tmp_return_data = requests.get(url=url, timeout=2, auth=(http_username, http_password), verify=False)
    return tmp_return_data.text


def _display_text_on_sensor(text_message):
    """ Returns requested sensor data (based on the provided command data). """
    url = "https://" + http_ip + ":" + http_port + "/DisplayText"
    requests.put(url=url, timeout=2, auth=(http_username, http_password), data={'command_data': text_message}, verify=False)
