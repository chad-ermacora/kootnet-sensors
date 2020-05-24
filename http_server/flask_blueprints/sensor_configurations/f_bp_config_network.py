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
import shutil
from flask import Blueprint, render_template, request
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_cached_variables_update
from configuration_modules import app_config_access
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules import app_validation_checks
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return

html_config_network_routes = Blueprint("html_config_network_routes", __name__)


@html_config_network_routes.route("/NetworkConfigurationsHTML")
@auth.login_required
def html_edit_network_configurations():
    logger.network_logger.debug("** HTML Network Configurations accessed from " + str(request.remote_addr))
    try:
        dhcp_checkbox = ""
        ip_disabled = ""
        subnet_disabled = ""
        gateway_disabled = ""
        dns1_disabled = ""
        dns2_disabled = ""
        wifi_security_type_none1 = ""
        wifi_security_type_wpa1 = ""
        if app_config_access.installed_sensors.raspberry_pi:
            dhcpcd_lines = get_file_content(file_locations.dhcpcd_config_file).split("\n")
            if network_ip.check_for_dhcp(dhcpcd_lines):
                dhcp_checkbox = "checked"
                ip_disabled = "disabled"
                subnet_disabled = "disabled"
                gateway_disabled = "disabled"
                dns1_disabled = "disabled"
                dns2_disabled = "disabled"
        if app_cached_variables.wifi_security_type == "" or app_cached_variables.wifi_security_type == "WPA-PSK":
            wifi_security_type_wpa1 = "checked"
        else:
            wifi_security_type_none1 = "checked"

        return render_template("network_configurations.html",
                               PageURL="/NetworkConfigurationsHTML",
                               SSLFileLocation=file_locations.http_ssl_folder,
                               WirelessCountryCode=app_cached_variables.wifi_country_code,
                               SSID1=app_cached_variables.wifi_ssid,
                               CheckedWiFiSecurityWPA1=wifi_security_type_wpa1,
                               CheckedWiFiSecurityNone1=wifi_security_type_none1,
                               CheckedDHCP=dhcp_checkbox,
                               IPHostname=app_cached_variables.hostname,
                               IPv4Address=app_cached_variables.ip,
                               IPv4AddressDisabled=ip_disabled,
                               IPv4Subnet=app_cached_variables.ip_subnet,
                               IPv4SubnetDisabled=subnet_disabled,
                               IPGateway=app_cached_variables.gateway,
                               IPGatewayDisabled=gateway_disabled,
                               IPDNS1=app_cached_variables.dns1,
                               IPDNS1Disabled=dns1_disabled,
                               IPDNS2=app_cached_variables.dns2,
                               IPDNS2Disabled=dns2_disabled)
    except Exception as error:
        logger.network_logger.error("HTML unable to display Networking Configurations: " + str(error))
        msg2 = "Unable to Display Networking Configurations..."
        return message_and_return("Unable to display Network Configurations", text_message2=msg2)


@html_config_network_routes.route("/EditSSL", methods=["GET", "POST"])
@auth.login_required
def set_custom_ssl():
    logger.network_logger.info("* Sensor's Web SSL Replacement accessed by " + str(request.remote_addr))
    return_message_ok = "SSL Certificate and Key files replaced.  Please reboot sensor for changes to take effect."
    return_message_fail = "Failed to set SSL Certificate and Key files.  Invalid Files?"

    try:
        temp_ssl_crt_location = file_locations.http_ssl_folder + "/custom_upload_certificate.crt"
        temp_ssl_key_location = file_locations.http_ssl_folder + "/custom_upload_key.key"
        new_ssl_certificate = request.files["custom_crt"]
        new_ssl_key = request.files["custom_key"]
        new_ssl_certificate.save(temp_ssl_crt_location)
        new_ssl_key.save(temp_ssl_key_location)
        if _is_valid_ssl_certificate(get_file_content(temp_ssl_crt_location)):
            os.system("mv -f " + file_locations.http_ssl_crt + " " + file_locations.http_ssl_folder + "/old_cert.crt")
            os.system("mv -f " + file_locations.http_ssl_key + " " + file_locations.http_ssl_folder + "/old_key.key")
            os.system("mv -f " + temp_ssl_crt_location + " " + file_locations.http_ssl_crt)
            os.system("mv -f " + temp_ssl_key_location + " " + file_locations.http_ssl_key)
            logger.primary_logger.info("Web Portal SSL Certificate and Key replaced successfully")
            return message_and_return("Sensor SSL Certificate OK", text_message2=return_message_ok, url="/")
        logger.network_logger.error("Invalid Uploaded SSL Certificate")
        return message_and_return("Sensor SSL Certificate Failed", text_message2=return_message_fail, url="/")
    except Exception as error:
        logger.network_logger.error("Failed to set Web Portal SSL Certificate and Key - " + str(error))
    return message_and_return("Sensor SSL Certificate Failed", text_message2=return_message_fail, url="/")


def _is_valid_ssl_certificate(cert):
    try:
        x509.load_pem_x509_certificate(str.encode(cert), default_backend())
        return True
    except Exception as error:
        logger.network_logger.debug("Invalid SSL Certificate - " + str(error))
    return False


# TODO: move checks to _set function below. Return check and message for html return
@html_config_network_routes.route("/EditConfigIPv4", methods=["POST"])
@auth.login_required
def html_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
        hostname = request.form.get("ip_hostname")
        app_cached_variables.hostname = hostname
        os.system("hostnamectl set-hostname " + hostname)

        ip_address = request.form.get("ip_address")
        ip_subnet = request.form.get("ip_subnet")
        ip_gateway = request.form.get("ip_gateway")
        ip_dns1 = request.form.get("ip_dns1")
        ip_dns2 = request.form.get("ip_dns2")

        dhcpcd_template = str(get_file_content(file_locations.dhcpcd_config_file_template))
        if request.form.get("ip_dhcp") is not None:
            dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", "")
            write_file_to_disk(file_locations.dhcpcd_config_file, dhcpcd_template)
            app_cached_variables.ip = ""
            app_cached_variables.ip_subnet = ""
            app_cached_variables.gateway = ""
            app_cached_variables.dns1 = ""
            app_cached_variables.dns2 = ""
        else:
            bad_setting_msg = ""
            if not app_validation_checks.ip_address_is_valid(ip_address):
                bad_setting_msg += "Invalid IP Address "
            if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
                bad_setting_msg += "Invalid IP Subnet Mask "
            if not app_validation_checks.ip_address_is_valid(ip_gateway) and ip_gateway != "":
                bad_setting_msg += "Invalid Gateway IP Address "
            if not app_validation_checks.ip_address_is_valid(ip_dns1) and ip_dns1 != "":
                bad_setting_msg += "Invalid DNS Address "
            if not app_validation_checks.ip_address_is_valid(ip_dns2) and ip_dns2 != "":
                bad_setting_msg += "Invalid DNS Address "
            if bad_setting_msg != "":
                msg1 = "Invalid IP Settings"
                return message_and_return(msg1, text_message2=bad_setting_msg, url="/NetworkConfigurationsHTML")

            ip_network_text = "# Custom Static IP set by Kootnet Sensors" + \
                              "\ninterface wlan0" + \
                              "\nstatic ip_address=" + ip_address + ip_subnet + \
                              "\nstatic routers=" + ip_gateway + \
                              "\nstatic domain_name_servers=" + ip_dns1 + " " + ip_dns2

            new_dhcpcd_config = dhcpcd_template.replace("{{ StaticIPSettings }}", ip_network_text)
            write_file_to_disk(file_locations.dhcpcd_config_file, new_dhcpcd_config)
            shutil.chown(file_locations.dhcpcd_config_file, "root", "netdev")
            os.chmod(file_locations.dhcpcd_config_file, 0o664)

        msg1 = "IPv4 Configuration Updated"
        msg2 = "You must reboot for all settings to take effect."
        app_cached_variables_update.update_cached_variables()
        return message_and_return(msg1, text_message2=msg2, url="/NetworkConfigurationsHTML")
    else:
        title_message = "Unable to Process IPv4 Configuration"
        message = "Invalid or Missing Hostname.\n\nOnly Alphanumeric Characters, Dashes and Underscores may be used."
        return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")


@html_config_network_routes.route("/EditConfigWifi", methods=["POST"])
@auth.login_required
def html_set_wifi_config():
    logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
    if request.method == "POST" and "ssid1" in request.form:
        if app_validation_checks.text_has_no_double_quotes(request.form.get("wifi_key1")):
            pass
        else:
            message = "Do not use double quotes in the Wireless Key Sections."
            return message_and_return("Invalid Wireless Key", text_message2=message, url="/NetworkConfigurationsHTML")
        if app_validation_checks.wireless_ssid_is_valid(request.form.get("ssid1")):
            new_wireless_config = network_wifi.html_request_to_config_wifi(request)
            if new_wireless_config is not "":
                write_file_to_disk(file_locations.wifi_config_file, new_wireless_config)
                title_message = "WiFi Configuration Updated"
                message = "You must reboot the sensor to take effect."
                app_cached_variables_update.update_cached_variables()
                return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")
        else:
            logger.network_logger.debug("HTML WiFi Configuration Update Failed")
            title_message = "Unable to Process Wireless Configuration"
            message = "Network Names cannot be blank and can only use " + \
                      "Alphanumeric Characters, dashes, underscores and spaces."
            return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")
    return message_and_return("Unable to Process WiFi Configuration", url="/NetworkConfigurationsHTML")
