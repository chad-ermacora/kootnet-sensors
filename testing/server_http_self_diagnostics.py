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

# TODO: Get this working
http_login = "Kootnet"
http_password = "sensors"

sensor_address = "localhost"
no_sensor_present = "NoSensor"
default_http_port = "10065"


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
        requests.put(url=url, timeout=4, data={'command_data': text_message}, verify=False, auth=login_credentials)
        return True
    except Exception as error:
        print("Unable to display text on Sensor: " + str(error))
        return False


def test_html_get_hostname():
    sensor_reading = get_http_sensor_reading("GetHostName")
    if isinstance(sensor_reading, str):
        return True
    return False


def test_html_system_uptime():
    sensor_reading = get_http_sensor_reading("GetSystemUptime")
    if isinstance(sensor_reading, str):
        return True
    return False


def test_html_get_cpu_temperature():
    sensor_reading = get_http_sensor_reading("GetCPUTemperature")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_env_temperature():
    sensor_reading = get_http_sensor_reading("GetEnvTemperature")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_env_temp_offset():
    sensor_reading = get_http_sensor_reading("GetTempOffsetEnv")
    if sensor_reading == "0.0" or float(sensor_reading):
        return True
    return False


def test_html_get_pressure():
    sensor_reading = get_http_sensor_reading("GetPressure")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_altitude():
    sensor_reading = get_http_sensor_reading("GetAltitude")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_humidity():
    sensor_reading = get_http_sensor_reading("GetHumidity")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_distance():
    sensor_reading = get_http_sensor_reading("GetDistance")
    if sensor_reading == "0.0" or sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_resistance_index():
    sensor_reading = get_http_sensor_reading("GetGasResistanceIndex")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_oxidised():
    sensor_reading = get_http_sensor_reading("GetGasOxidised")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_reduced():
    sensor_reading = get_http_sensor_reading("GetGasReduced")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_gas_nh3():
    sensor_reading = get_http_sensor_reading("GetGasNH3")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter1():
    sensor_reading = get_http_sensor_reading("GetParticulateMatter1")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter2_5():
    sensor_reading = get_http_sensor_reading("GetParticulateMatter2_5")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_particulate_matter10():
    sensor_reading = get_http_sensor_reading("GetParticulateMatter10")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_lumen():
    sensor_reading = get_http_sensor_reading("GetLumen")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_visible_ems():
    sensor_readings = get_http_sensor_reading("GetEMS")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_uva():
    sensor_reading = get_http_sensor_reading("GetUltraVioletA")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_uvb():
    sensor_reading = get_http_sensor_reading("GetUltraVioletB")
    if sensor_reading == no_sensor_present or float(sensor_reading):
        return True
    return False


def test_html_get_accelerometer():
    sensor_readings = get_http_sensor_reading("GetAccelerometerXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_magnetometer():
    sensor_readings = get_http_sensor_reading("GetMagnetometerXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False


def test_html_get_gyroscope():
    sensor_readings = get_http_sensor_reading("GetGyroscopeXYZ")
    if sensor_readings == no_sensor_present:
        return True
    else:
        sensor_readings = sensor_readings[1:-1].split(",")
        if float(sensor_readings[0]):
            return True
        return False
