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
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk
from operations_modules import app_validation_checks
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
    dhcp_checkbox = ""
    wifi_security_type_none1 = ""
    wifi_security_type_wpa1 = ""
    if app_config_access.installed_sensors.raspberry_pi:
        dhcpcd_lines = get_file_content(file_locations.dhcpcd_config_file).split("\n")
        if network_ip.check_for_dhcp(dhcpcd_lines):
            dhcp_checkbox = "checked"

    if app_cached_variables.wifi_security_type == network_wifi.wifi_type_secured:
        wifi_security_type_wpa1 = "checked"
    else:
        wifi_security_type_none1 = "checked"
    return render_template("ATPro_admin/page_templates/system/system-networking-ip.html",
                           CheckedDHCP=dhcp_checkbox,
                           IPHostname=app_cached_variables.hostname,
                           IPv4Address=app_cached_variables.ip,
                           IPv4Subnet=app_cached_variables.ip_subnet,
                           IPGateway=app_cached_variables.gateway,
                           IPDNS1=app_cached_variables.dns1,
                           IPDNS2=app_cached_variables.dns2,
                           WirelessCountryCode=app_cached_variables.wifi_country_code,
                           SSID1=app_cached_variables.wifi_ssid,
                           CheckedWiFiSecurityWPA1=wifi_security_type_wpa1,
                           CheckedWiFiSecurityNone1=wifi_security_type_none1)


@html_atpro_system_networking_routes.route("/atpro/system-ssl")
@auth.login_required
def html_atpro_system_ssl():
    return render_template("ATPro_admin/page_templates/system/system-networking-ssl.html",
                           SSLFileLocation=file_locations.http_ssl_folder)


@html_atpro_system_networking_routes.route("/atpro/system-ssl-new-self-sign")
@auth.login_required
def html_atpro_create_new_self_signed_ssl():
    if app_config_access.primary_config.demo_mode:
        message2 = "Unable to Create New SSL Certificate when in Demo mode"
    else:
        message2 = "Restart Kootnet Sensors to create and use the new SSL Certificate"
        os.system("rm -f -r " + file_locations.http_ssl_folder)
        atpro_notifications.manage_service_restart()
    return get_message_page("New Self-Signed SSL", message2, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_networking_routes.route("/atpro/system-ssl-custom", methods=["POST"])
@auth.login_required
def html_atpro_set_custom_ssl():
    logger.network_logger.info("* Sensor's Web SSL Replacement accessed by " + str(request.remote_addr))
    return_message_ok = "SSL Certificate and Key files replaced.  Please restart program for changes to take effect."
    return_message_fail = "Failed to set SSL Certificate and Key files.  Invalid Files?"
    if app_config_access.primary_config.demo_mode:
        return_message_fail = "Unable to change SSL Certificate when in Demo mode"
    else:
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
                atpro_notifications.manage_service_restart()
                return get_message_page("Sensor SSL Certificate OK", return_message_ok,
                                        page_url="sensor-system", skip_menu_select=True)
            logger.network_logger.error("Invalid Uploaded SSL Certificate")
            return get_message_page("Sensor SSL Certificate Failed", return_message_fail,
                                    page_url="sensor-system", skip_menu_select=True)
        except Exception as error:
            logger.network_logger.error("Failed to set Web Portal SSL Certificate and Key - " + str(error))
    return get_message_page("Sensor SSL Certificate Failed", return_message_fail,
                            page_url="sensor-system", skip_menu_select=True)


def _is_valid_ssl_certificate(cert):
    try:
        x509.load_pem_x509_certificate(str.encode(cert), default_backend())
        return True
    except Exception as error:
        logger.network_logger.debug("Invalid SSL Certificate - " + str(error))
    return False


# TODO: move checks to _set function below. Return check and message for html return
@html_atpro_system_networking_routes.route("/atpro/system-ip", methods=["POST"])
@auth.login_required
def html_atpro_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
        if app_cached_variables.running_with_root:
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
                title_message = ""
                if not app_validation_checks.ip_address_is_valid(ip_address):
                    title_message += "Invalid IP Address "
                if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
                    title_message += "Invalid IP Subnet Mask "
                if not app_validation_checks.ip_address_is_valid(ip_gateway) and ip_gateway != "":
                    title_message += "Invalid Gateway IP Address "
                if not app_validation_checks.ip_address_is_valid(ip_dns1) and ip_dns1 != "":
                    title_message += "Invalid DNS Address "
                if not app_validation_checks.ip_address_is_valid(ip_dns2) and ip_dns2 != "":
                    title_message += "Invalid DNS Address "
                if title_message != "":
                    title_message = "Invalid IP Settings"
                    return get_message_page(title_message, page_url="sensor-system", skip_menu_select=True)

                ip_network_text = "# Custom Static IP set by Kootnet Sensors" + \
                                  "\ninterface wlan0" + \
                                  "\nstatic ip_address=" + ip_address + ip_subnet + \
                                  "\nstatic routers=" + ip_gateway + \
                                  "\nstatic domain_name_servers=" + ip_dns1 + " " + ip_dns2

                new_dhcpcd_config = dhcpcd_template.replace("{{ StaticIPSettings }}", ip_network_text)
                write_file_to_disk(file_locations.dhcpcd_config_file, new_dhcpcd_config)
                shutil.chown(file_locations.dhcpcd_config_file, "root", "netdev")
                os.chmod(file_locations.dhcpcd_config_file, 0o664)

            title_message = "IPv4 Configuration Updated"
            message = "You must reboot for all settings to take effect."
            app_cached_variables_update.update_cached_variables()
            atpro_notifications.manage_system_reboot()
            return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
        else:
            msg2 = "Kootnet Sensors must be running as root"
            return get_message_page("Unable to Apply", msg2, page_url="sensor-system", skip_menu_select=True)
    else:
        title_message = "Unable to Process IPv4 Configuration"
        message = "Invalid or Missing Hostname.\n\nOnly Alphanumeric Characters, Dashes and Underscores may be used."
        return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)


@html_atpro_system_networking_routes.route("/atpro/system-wifi", methods=["POST"])
@auth.login_required
def html_atpro_set_wifi_config():
    logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
    title_page_msg = "Unable to Process WiFi Configuration"
    page_msg = "Not a POST request or missing SSID in form"
    if request.method == "POST" and "ssid1" in request.form:
        page_msg = "Kootnet Sensors not running as root?"
        if app_cached_variables.running_with_root:
            if app_validation_checks.text_has_no_double_quotes(request.form.get("wifi_key1")):
                pass
            else:
                message = "Do not use double quotes in the Wireless Key Sections."
                return get_message_page("Invalid Wireless Key", message, page_url="sensor-system", skip_menu_select=True)
            if app_validation_checks.wireless_ssid_is_valid(request.form.get("ssid1")):
                new_wireless_config = network_wifi.html_request_to_config_wifi(request)
                if new_wireless_config is not "":
                    title_message = "WiFi Configuration Updated"
                    message = "You must reboot the sensor to take effect."
                    try:
                        write_file_to_disk(file_locations.wifi_config_file, new_wireless_config)
                        app_cached_variables_update.update_cached_variables()
                        atpro_notifications.manage_system_reboot()
                        return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
                    except Exception as error:
                        logger.network_logger.error("Write wpa_supplicant: " + str(error))
            else:
                logger.network_logger.debug("HTML WiFi Configuration Update Failed")
                title_message = "Unable to Process Wireless Configuration"
                message = "Network Names cannot be blank and can only use " + \
                          "Alphanumeric Characters, dashes, underscores and spaces."
                return get_message_page(title_message, message, page_url="sensor-system", skip_menu_select=True)
    return get_message_page(title_page_msg, message=page_msg, page_url="sensor-system", skip_menu_select=True)
