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
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.initialization_python_modules import load_pip_module_on_demand
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables
requests = load_pip_module_on_demand("requests", "requests")

logging.captureWarnings(True)
get_sensor_reading_error_msg = "Unable to get Sensor Reading/File"
network_get_commands = app_cached_variables.network_get_commands


def get_http_regular_file(file_http_url_location, get_text=True, timeout=10, verify_ssl=False):
    """
    Get a file from an HTTP or HTTPS server (Not from a Kootnet Sensor)
    :param file_http_url_location:
    :param get_text: Return string vs requests 'content'
    :param timeout: Seconds before requests times out getting the file
    :param verify_ssl: Require Sites SSL be verified, default False
    :return: File content
    """
    try:
        tmp_return_data = requests.get(url=file_http_url_location, timeout=timeout, verify=verify_ssl)
        if get_text:
            return tmp_return_data.text
        return tmp_return_data.content
    except requests.exceptions.ConnectionError:
        logger.network_logger.debug("HTTP GET File Connection Failed " + file_http_url_location)
    except Exception as error:
        logger.network_logger.warning("HTTP GET File from " + str(file_http_url_location) + ": " + str(error))
    return "Unable to get file: " + str(file_http_url_location)


def get_http_kootnet_sensor_file(sensor_address, http_command, verify_ssl=False):
    """
    Returns file content from provided remote Kootnet Sensor URL
    :param sensor_address: Sensor IP or DNS address as a string
    :param http_command: Command to be run on Kootnet Sensor (string)
    :param verify_ssl: Require Sites SSL be verified, default False
    :return: File content
    """
    sensor_url = get_http_formatted_sensor_address(sensor_address)
    try:
        authenticated_requests = _get_authenticated_requests(sensor_url, http_command)
        tmp_return_data = authenticated_requests.get(
            url=sensor_url + http_command,
            timeout=(10, 600),
            verify=verify_ssl
        )
        return tmp_return_data.content
    except Exception as error:
        logger.network_logger.warning("HTTP GET File from " + sensor_address + ": " + str(error))
    return get_sensor_reading_error_msg


def get_http_sensor_reading(sensor_address, http_command="CheckOnlineStatus", timeout=10, verify_ssl=False):
    """
    Returns text reading from a Kootnet Sensor based on provided http_command
    :param sensor_address: Sensor IP or DNS address as a string
    :param http_command: Command to be run on Kootnet Sensor (string)
    :param timeout: Seconds before requests times out getting reading
    :param verify_ssl: Require Sites SSL be verified, default False
    :return: Kootnet Sensor reading as a string
    """
    sensor_url = get_http_formatted_sensor_address(sensor_address)
    try:
        authenticated_requests = _get_authenticated_requests(sensor_url, http_command)
        tmp_return_data = authenticated_requests.get(
            url=sensor_url + http_command,
            timeout=timeout,
            verify=verify_ssl
        )
        return tmp_return_data.text
    except requests.exceptions.ConnectionError:
        logger.network_logger.debug("HTTP GET Reading Connection Failed " + sensor_address)
    except Exception as error:
        logger.network_logger.warning("HTTP GET Reading from " + sensor_address + ": " + str(error))
    return get_sensor_reading_error_msg


def send_http_command(sensor_address, http_command, dic_data=None, timeout=10, verify_ssl=False):
    """
    Sends Kootnet Sensors command to a remote Kootnet Sensor
    :param sensor_address: Sensor IP or DNS address as a string
    :param http_command: Command to be run on Kootnet Sensor (string)
    :param dic_data: Dictionary to send with request
    :param timeout: Seconds before requests times out sending reading
    :param verify_ssl: Require Sites SSL be verified, default False
    :return: requests response code
    """
    sensor_url = get_http_formatted_sensor_address(sensor_address)
    try:
        authenticated_requests = _get_authenticated_requests(sensor_url, http_command)
        response = authenticated_requests.put(
            url=sensor_url + http_command,
            timeout=timeout,
            verify=verify_ssl,
            data=dic_data
        )
        return response.status_code
    except requests.exceptions.ConnectionError:
        logger.network_logger.warning("HTTP PUT Connection Failed " + sensor_address + http_command)
    except Exception as error:
        logger.network_logger.warning("HTTP PUT data to " + sensor_address + ": " + str(error))


def send_http_test_config(sensor_address, http_command, text_config, verify_ssl=False):
    """
    Used to send Kootnet Configurations for testing purposes (Configurations not saved)
    :param sensor_address: Sensor IP or DNS address as a string
    :param http_command: Command to be run on Kootnet Sensor (string)
    :param text_config: Raw text Kootnet Sensors configuration
    :param verify_ssl: Require Sites SSL be verified, default False
    :return: requests response code
    """
    sensor_url = get_http_formatted_sensor_address(sensor_address)
    try:
        authenticated_requests = _get_authenticated_requests(sensor_url, http_command)
        command_data = {"command_data": text_config, "test_run": True}
        resp = authenticated_requests.put(
            url=sensor_url + http_command,
            timeout=5,
            verify=verify_ssl,
            data=command_data
        )
        return resp.status_code
    except Exception as error:
        logger.network_logger.info("HTTP PUT Test Configuration to " + sensor_address + ": " + str(error))


def check_http_file_exist(file_url):
    """
    Checks to see if a file exists using provided http(s) URL
    :param file_url: File location on a HTTP or HTTPS server
    :return: If file exists, return True, else, False
    """
    try:
        response = requests.head(file_url)
        if response.status_code == 200:
            return True
        log_msg = "Check File Exists: Unexpected HTTP status code checking " + file_url + ": "
        logger.network_logger.warning(log_msg + str(response.status_code))
    except requests.exceptions.ConnectionError:
        logger.network_logger.debug("Check HTTP file Connection Failed " + file_url)
    except Exception as error:
        logger.network_logger.warning("Check HTTP file " + file_url + ": " + str(error))
    return False


def check_for_port_in_address(address):
    """ Checks provided remote sensor address text (IP or DNS) for a port and if found, returns True, else False. """

    if "]" in address:
        ip_6_split = address.strip().split("]")[-1]
        if ":" in ip_6_split:
            return True
    elif len(address.strip().split(":")) == 2:
        return True
    return False


def get_ip_and_port_split(address):
    """ Takes a text address (IP or DNS) and returns a text list of address, and if found port number. """
    if check_for_port_in_address(address):
        address = address.strip()
        if "]" in address:
            ip_6_address = address.split("[")[-1].split("]")[0]
            ip_6_port = address.split("]")[-1].split(":")[-1]
            return ["[" + ip_6_address + "]", ip_6_port]
        else:
            return address.split(":")
    return [address, "10065"]


def get_http_formatted_sensor_address(sensor_address):
    """
    Takes provided Kootnet Sensors address and returns a properly formatted URL for use with 'requests'
    Optional: Sensor address can include http:// or https:// as well as port #
    Note: If http:// https:// is not included, uses https://, if port not included, uses 10065
    :param sensor_address: Sensor IP or DNS address as a string
    :return: Properly formatted URL (string) for use with 'requests' Python module
    """
    start_url = "https://"
    http_port = "10065"
    sensor_address = sensor_address.lower().replace(start_url, "")
    if "http://" in sensor_address:
        start_url = "http://"
        sensor_address = sensor_address.replace("http://", "")
    if sensor_address[-1] == "/":
        sensor_address = sensor_address[:-1]
    if check_for_port_in_address(sensor_address):
        sensor_address, http_port = get_ip_and_port_split(sensor_address)
    else:
        if len(sensor_address.split(":")) > 2:
            sensor_address = "[" + sensor_address + "]"
    final_http_sensor_address = start_url + sensor_address + ":" + http_port + "/"
    return final_http_sensor_address


def get_html_response_bg_colour(response_time):
    """ Returns background colour to use in Sensor Control HTML pages based on provided sensor response time. """

    try:
        delay_float = float(response_time)
        background_colour = "darkgreen"
        if 0.0 <= delay_float < 0.5:
            pass
        elif 0.5 < delay_float < 0.75:
            background_colour = "#859B14"
        elif 0.75 < delay_float < 1.5:
            background_colour = "#8b4c00"
        elif 1.5 < delay_float:
            background_colour = "red"
    except Exception as error:
        logger.network_logger.debug("Sensor Control - Check Online Status - Bad Delay")
        logger.network_logger.debug("Check Online Status Error: " + str(error))
        background_colour = "purple"
    return background_colour


def _get_authenticated_requests(sensor_address, http_command, http_login=None, http_password=None, verify=False):
    if http_login is None:
        http_login = rm_cached_variables.http_login
    if http_password is None:
        http_password = rm_cached_variables.http_password

    authenticated_requests = requests.Session()
    if http_command not in network_get_commands.no_http_auth_required_commands_list:
        login_credentials = {"login_username": http_login,
                             "login_password": http_password}
        authenticated_requests.post(sensor_address + "atpro/login", login_credentials, verify=verify)
    return authenticated_requests
