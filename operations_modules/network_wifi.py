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
from operations_modules import logger
from operations_modules import app_generic_functions
from operations_modules import file_locations
from operations_modules import app_cached_variables

wifi_type_secured = "WPA-PSK WPA-EAP SAE"


def get_wifi_country_code(wifi_config_lines):
    """
    Checks the wpa_supplicant.conf file for the set country code and returns it.
    If not found, returns an empty string.
    """
    if wifi_config_lines is not None:
        for line in wifi_config_lines:
            line_stripped = line.strip()
            if line_stripped[:8] == "country=":
                return line_stripped[8:]
    return ""


def get_wifi_ssid(wifi_config_lines):
    """
    Checks the wpa_supplicant.conf file for a wireless network name (SSID) and returns it.
    If not found, returns an empty string.
    """
    if wifi_config_lines is not None:
        for line in wifi_config_lines:
            line_stripped = line.strip()
            if line_stripped[:5] == "ssid=":
                return line_stripped[6:-1]
    return ""


def get_wifi_security_type(wifi_config_lines):
    """
    Checks the wpa_supplicant.conf file for the set wireless's security type and returns it.
    If not found, returns an empty string.
    """
    if wifi_config_lines is not None:
        for line in wifi_config_lines:
            line_stripped = line.strip()
            if line_stripped[:9] == "key_mgmt=":
                return line_stripped[9:]
    return ""


def get_wifi_psk(wifi_config_lines):
    """
    Checks the wpa_supplicant.conf file for the set wireless password and returns it.
    If not found, returns an empty string.
    """
    if wifi_config_lines is not None:
        for line in wifi_config_lines:
            line_stripped = line.strip()
            if line_stripped[:4] == "psk=":
                return line_stripped[5:-1]
    return ""


def html_request_to_config_wifi(html_request):
    """ Takes the provided HTML wireless settings and creates a new WPA Supplicant string and returns it. """
    logger.network_logger.debug("Starting HTML WiFi Configuration Update Check")
    if html_request.form.get("ssid1") is not None:
        wifi_template = app_generic_functions.get_file_content(file_locations.wifi_config_file_template)

        wifi_country_code = "CA"
        if len(html_request.form.get("country_code")) == 2:
            wifi_country_code = html_request.form.get("country_code").upper()

        wifi_ssid1 = html_request.form.get("ssid1")
        wifi_security_type1 = html_request.form.get("wifi_security1")
        wifi_psk1 = html_request.form.get("wifi_key1")

        if wifi_security_type1 == "wireless_wpa":
            wifi_security_type1 = wifi_type_secured
            if wifi_psk1 is not "":
                wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", 'psk="' + wifi_psk1 + '"')
            else:
                wifi_psk1 = app_cached_variables.wifi_psk
                wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", 'psk="' + wifi_psk1 + '"')
        else:
            wifi_security_type1 = "None"
            wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", "")

        wifi_template = wifi_template.replace("{{ WirelessCountryCode }}", wifi_country_code)
        wifi_template = wifi_template.replace("{{ WirelessSSID1 }}", wifi_ssid1)
        wifi_template = wifi_template.replace("{{ WirelessKeyMgmt1 }}", wifi_security_type1)
        return wifi_template
    return ""
