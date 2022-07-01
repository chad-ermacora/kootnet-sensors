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
import os
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_disk import write_file_to_disk
from operations_modules.app_validation_checks import wireless_ssid_is_valid
from operations_modules import network_ip
from operations_modules import network_wifi
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page

html_atpro_system_networking_routes = Blueprint("html_atpro_system_networking_routes", __name__)


@html_atpro_system_networking_routes.route("/atpro/system-networking")
@auth.login_required
def html_atpro_system_networking():
    net_device_list = network_ip.get_network_devices_list()
    wifi_ssid_list = network_wifi.wifi_networks_interface.get_network_ssid_list()
    return render_template("ATPro_admin/page_templates/system/system-networking-ip.html",
                           NetDeviceOptionNames=_get_drop_down_net_items(net_device_list),
                           AdapterIPData=_get_html_net_devices_data(net_device_list),
                           WirelessCountryCode=network_wifi.wifi_networks_interface.country_code,
                           NetWifiOptionNames=_get_drop_down_net_items(wifi_ssid_list),
                           WifiSSIDData=_get_html_wifi_networks_data())


def _get_html_net_devices_data(net_device_list):
    html_return_text = "\ndelete DeviceData;\nDeviceData = {"
    for device in net_device_list:
        network_adapter_data = network_ip.CreateNetDeviceInterface(device)
        html_return_text += f"{device}dhcp_set: '{str(network_adapter_data.dhcp_set)}', " \
                            f"{device}ip_address: '{network_adapter_data.ip_address}', " \
                            f"{device}ip_subnet: '{network_adapter_data.ip_subnet}', " \
                            f"{device}ip_gateway: '{network_adapter_data.ip_gateway}', " \
                            f"{device}ip_dns1: '{network_adapter_data.ip_dns1}', " \
                            f"{device}ip_dns2: '{network_adapter_data.ip_dns2}',"
    html_return_text = html_return_text[:-1] + "}\n"
    return html_return_text


def _get_html_wifi_networks_data():
    html_return_text = "\ndelete WifiData;\nWifiData = {"
    for ssid in network_wifi.wifi_networks_interface.get_network_ssid_list():
        wifi_network_psk = network_wifi.wifi_networks_interface.current_wifi_networks_dic[ssid]
        html_return_text += f"ssid_{ssid}: '{str(ssid)}', psk_{ssid}: '{wifi_network_psk}',"
    if len(network_wifi.wifi_networks_interface.get_network_ssid_list()) > 0:
        html_return_text = html_return_text[:-1]
    return html_return_text + "}\n"


def _get_drop_down_net_items(net_device_list):
    custom_drop_downs_html_text = "<option value='{{ NameChangeMe }}'>{{ NameChangeMe }}</option>"
    dropdown_selection = ""
    for net_device_name in net_device_list:
        dropdown_selection += custom_drop_downs_html_text.replace("{{ NameChangeMe }}", net_device_name) + "\n"
    return dropdown_selection


@html_atpro_system_networking_routes.route("/atpro/system-ssl")
@auth.login_required
def html_atpro_system_ssl():
    return render_template("ATPro_admin/page_templates/system/system-networking-ssl.html",
                           SSLFileLocation=file_locations.http_ssl_folder)


@html_atpro_system_networking_routes.route("/atpro/system-ssl-new-self-sign")
@auth.login_required
def html_atpro_create_new_self_signed_ssl():
    if app_config_access.primary_config.demo_mode:
        message2 = "Unable to Create New SSL Certificate in Demo mode"
    else:
        message2 = "Restart Kootnet Sensors to create and use the new SSL Certificate"
        os.system("rm -f -r " + file_locations.http_ssl_folder)
        atpro_notifications.manage_service_restart()
    return get_message_page("New Self-Signed SSL", message2, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_networking_routes.route("/atpro/system-ssl-custom", methods=["POST"])
@auth.login_required
def html_atpro_set_custom_ssl():
    logger.network_logger.info("* Sensor's Web SSL Replacement accessed by " + str(request.remote_addr))
    title_message = "Sensor SSL Certificate Upload Failed"
    return_message_ok = "SSL Certificate and Key files replaced.  Please restart program for changes to take effect."
    return_message_fail = "Failed to set SSL Certificate and Key files.  Invalid Files?"
    if app_config_access.primary_config.demo_mode:
        title_message = "Function Disabled"
        return_message_fail = "Function Disabled in Demo mode"
    else:
        try:
            move_old_key_to = file_locations.http_ssl_folder + "/old_key.key"
            move_old_crt_to = file_locations.http_ssl_folder + "/old_cert.crt"
            new_ssl_key = request.files["custom_key"].stream.read().decode()
            new_ssl_certificate = request.files["custom_crt"].stream.read().decode()
            if _is_valid_ssl_key(new_ssl_key) and _is_valid_ssl_certificate(new_ssl_certificate):
                os.system("mv -f " + file_locations.http_ssl_key + " " + move_old_key_to)
                os.system("mv -f " + file_locations.http_ssl_crt + " " + move_old_crt_to)
                write_file_to_disk(file_locations.http_ssl_key, new_ssl_key)
                write_file_to_disk(file_locations.http_ssl_crt, new_ssl_certificate)
                logger.primary_logger.info("Web Portal SSL Certificate and Key replaced successfully")
                atpro_notifications.manage_service_restart()
                return get_message_page("Sensor SSL Certificate Upload OK", return_message_ok,
                                        page_url="sensor-system", skip_menu_select=True)
            return get_message_page("Sensor SSL Certificate Upload Failed", return_message_fail,
                                    page_url="sensor-system", skip_menu_select=True)
        except Exception as error:
            logger.network_logger.error("Sensor SSL Certificate Upload Failed - " + str(error))
    return get_message_page(title_message, return_message_fail, page_url="sensor-system", skip_menu_select=True)


def _is_valid_ssl_key(ssl_key):
    if type(ssl_key) is str:
        if "BEGIN PRIVATE KEY" in ssl_key.upper():
            return True
    logger.network_logger.warning("Invalid SSL Key")
    return False


def _is_valid_ssl_certificate(ssl_cert):
    if type(ssl_cert) is str:
        if "BEGIN CERTIFICATE" in str(ssl_cert).upper():
            return True
    logger.network_logger.warning("Invalid SSL Certificate")
    return False


@html_atpro_system_networking_routes.route("/atpro/system-ip", methods=["POST"])
@auth.login_required
def html_atpro_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    if app_config_access.primary_config.demo_mode:
        message = "Function Disabled in Demo mode"
        return get_message_page("Function Disabled", message, page_url="sensor-system", skip_menu_select=True)
    if not app_cached_variables.running_with_root:
        message = "Kootnet Sensors must be running as root"
        return get_message_page("Unable to Apply", message, page_url="sensor-system", skip_menu_select=True)
    if network_ip.adapter_resetting:
        message = "A Network Adapter is still resetting, please try again"
        return get_message_page("Unable to Apply", message, page_url="sensor-system", skip_menu_select=True)

    net_device_name = request.form.get("net_device_selection")
    ip_address_data = network_ip.CreateNetDeviceInterface(net_device_name, auto_fill_address_info=False)
    if request.form.get("ip_dhcp") is not None:
        ip_address_data.remove_device_enable_dhcp()
    else:
        ip_address_data.ip_address = request.form.get("ip_address")
        ip_address_data.ip_subnet = request.form.get("ip_subnet")
        ip_address_data.ip_gateway = request.form.get("ip_gateway")
        ip_address_data.ip_dns1 = request.form.get("ip_dns1")
        ip_address_data.ip_dns2 = request.form.get("ip_dns2")

        if not ip_address_data.valid_net_addresses():
            invalid_msg = ip_address_data.get_validation_msg()
            return get_message_page(invalid_msg, page_url="sensor-system", skip_menu_select=True)
        else:
            ip_address_data.save_static_network_config()

    title_message = "IPv4 Configuration Updated"
    message = "Resetting Network Adapter, this may take up to 2 minutes."
    return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_networking_routes.route("/atpro/system-wifi", methods=["POST"])
@auth.login_required
def html_atpro_set_wifi_config():
    logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
    if app_config_access.primary_config.demo_mode:
        title_msg = "Function Disabled"
        page_msg = "Function Disabled in Demo mode"
    else:
        title_msg = "root required"
        page_msg = "Kootnet Sensors not running as root?"
        if app_cached_variables.running_with_root:
            wifi_country_code = "CA"
            if len(request.form.get("country_code")) == 2:
                wifi_country_code = request.form.get("country_code").upper()
            network_wifi.wifi_networks_interface.country_code = wifi_country_code

            wifi_ssid1 = request.form.get("ssid1")
            wifi_security = request.form.get("wifi_secured")
            wifi_psk1 = request.form.get("wifi_key1")
            if wireless_ssid_is_valid(wifi_ssid1):
                if request.form.get("button_function") == "remove":
                    title_msg = "Wi-Fi Network Not Found"
                    page_msg = f"The Wi-Fi network {wifi_ssid1} was not found in the WPA Supplicant file"
                    if wifi_ssid1 in network_wifi.wifi_networks_interface.current_wifi_networks_dic:
                        network_wifi.wifi_networks_interface.remove_wifi_network(wifi_ssid1)
                        title_msg = "Wi-Fi Network Removed"
                        page_msg = f"The Wi-Fi network {wifi_ssid1} has been removed"
                    return get_message_page(title_msg, page_msg, page_url="sensor-system", skip_menu_select=True)
                if wifi_security is not None:
                    if request.form.get("wifi_key1") == "":
                        title_msg = "Invalid Wi-Fi Key"
                        page_msg = "The Wi-Fi key cannot be blank"
                        return get_message_page(title_msg, page_msg, page_url="sensor-system", skip_menu_select=True)
                    elif "'" in wifi_psk1 or '"' in wifi_psk1:
                        title_msg = "Invalid Wi-Fi Key"
                        page_msg = "Do not use single or double quotes in the Wi-Fi Key"
                        return get_message_page(title_msg, page_msg, page_url="sensor-system", skip_menu_select=True)

                if request.form.get("button_function") == "update":
                    if wifi_security is not None:
                        network_wifi.wifi_networks_interface.add_wifi_network(wifi_ssid1, wifi_psk1)
                    else:
                        network_wifi.wifi_networks_interface.add_wifi_network(wifi_ssid1)
                title_msg = "Wi-Fi Networks Updated"
                page_msg = f"Wi-Fi Network {wifi_ssid1} Added/Updated"
            else:
                logger.network_logger.debug("HTML WiFi Configuration Update Failed")
                title_msg = "Unable to Process Wi-Fi Network"
                page_msg = "Wi-Fi SSID Names cannot be blank and can only use " + \
                           "Alphanumeric Characters, dashes, underscores"
    return get_message_page(title_msg, message=page_msg, page_url="sensor-system", skip_menu_select=True)
