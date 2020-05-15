from time import sleep
import psutil
from operations_modules.app_generic_functions import thread_function
from operations_modules import app_cached_variables
from operations_modules import network_wifi
from operations_modules import logger
from operations_modules import network_ip
from sensor_modules import sensor_access


def update_cached_variables(delayed_update=False):
    """ Updates app_cached_variables.py variables. """
    if delayed_update:
        thread_function(_delayed_cache_update)
    else:
        _delayed_cache_update(delay=False)

    app_cached_variables.total_ram_memory = psutil.virtual_memory().total / 1000000
    if app_cached_variables.total_ram_memory > 1000:
        app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
        app_cached_variables.total_ram_memory_size_type = " GB"
        if app_cached_variables.total_ram_memory > 1000:
            app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
            app_cached_variables.total_ram_memory_size_type = " TB"
    app_cached_variables.total_ram_memory = round(app_cached_variables.total_ram_memory, 2)

    os_name = sensor_access.get_operating_system_name()
    if os_name[:8] == "Raspbian":
        try:
            wifi_config_lines = network_wifi.get_wifi_config_from_file().split("\n")
        except Exception as error:
            logger.primary_logger.error("Error checking WiFi configuration: " + str(error))
            wifi_config_lines = []

        app_cached_variables.wifi_country_code = network_wifi.get_wifi_country_code(wifi_config_lines)
        app_cached_variables.wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)
        app_cached_variables.wifi_security_type = network_wifi.get_wifi_security_type(wifi_config_lines)
        app_cached_variables.wifi_psk = network_wifi.get_wifi_psk(wifi_config_lines)

    try:
        dhcpcd_config_lines = network_ip.get_dhcpcd_config_from_file().split("\n")
    except Exception as error:
        logger.primary_logger.debug("Error checking dhcpcd.conf: " + str(error))
        dhcpcd_config_lines = []

    if not network_ip.check_for_dhcp(dhcpcd_config_lines):
        app_cached_variables.ip = network_ip.get_dhcpcd_ip(dhcpcd_config_lines)
        app_cached_variables.ip_subnet = network_ip.get_subnet(dhcpcd_config_lines)
        app_cached_variables.gateway = network_ip.get_gateway(dhcpcd_config_lines)
        app_cached_variables.dns1 = network_ip.get_dns(dhcpcd_config_lines)
        app_cached_variables.dns2 = network_ip.get_dns(dhcpcd_config_lines, dns_server=1)

    app_cached_variables.program_last_updated = sensor_access.get_last_updated()
    app_cached_variables.reboot_count = str(sensor_access.get_system_reboot_count())
    app_cached_variables.operating_system_name = os_name


def _delayed_cache_update(delay=True):
    """
    Updates app_cached_variables.py variables that may require a bit of time before they are ready.
    Gives 5 seconds before updating the variables within.
    Used after the program starts to allow things like the IP address to be obtained.
    """
    if delay:
        sleep(5)
    app_cached_variables.ip = sensor_access.get_ip()
    app_cached_variables.hostname = sensor_access.get_hostname()
