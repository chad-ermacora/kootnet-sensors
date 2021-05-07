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
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content, remove_line_from_text

try:
    from plotly import __version__ as plotly_version
    from numpy import __version__ as numpy_version
    from greenlet import __version__ as greenlet_version
    from gevent import __version__ as gevent_version
    from requests import __version__ as requests_version
    from werkzeug import __version__ as werkzeug_version
    from cryptography import __version__ as cryptography_version
    from flask import __version__ as flask_version
    from operations_modules.software_version import version as kootnet_version
except ImportError as import_error:
    logger.primary_logger.warning("Import Versions Failed: " + str(import_error))
    plotly_version = "Unknown"
    numpy_version = "Unknown"
    greenlet_version = "Unknown"
    gevent_version = "Unknown"
    requests_version = "Unknown"
    werkzeug_version = "Unknown"
    cryptography_version = "Unknown"
    flask_version = "Unknown"
    kootnet_version = "Unknown"
from flask import Blueprint, render_template, request
from http_server.server_http_auth import auth

html_atpro_system_raw_configs_routes = Blueprint("html_atpro_system_raw_configs_routes", __name__)


@html_atpro_system_raw_configs_routes.route("/atpro/system/raw-configurations")
@auth.login_required
def atpro_raw_configurations_view():
    logger.network_logger.debug("** HTML Raw Configurations viewed by " + str(request.remote_addr))
    return render_template("ATPro_admin/page_templates/system/system-raw-configurations.html")


def _config_to_html_view(config_name, config_location, config_text_file, split_by_line=True):
    if split_by_line:
        config_lines = config_text_file.strip().split("\n")[1:]
        return_html = ""
        for text_line in config_lines:
            try:
                config_parts = text_line.split("=")
                return_html += "<span class='setting-title'>" + config_parts[-1].strip() + "</span>: " + \
                               "<span class='setting-value'>" + config_parts[0].strip() + "</span><br>"
            except Exception as error:
                log_msg = "HTML Raw Configurations creation error in " + config_location + ": "
                logger.network_logger.warning(log_msg + str(error))
    else:
        return_html = config_text_file.replace("\n", "<br>")
    return render_template("ATPro_admin/page_templates/system/system-raw-configurations-template.html",
                           ConfigName=config_name,
                           ConfigLocation=config_location,
                           Config=return_html)


@html_atpro_system_raw_configs_routes.route('/atpro/system/raw_config/<path:url_path>')
@auth.login_required
def atpro_raw_config_urls(url_path):
    if url_path == "config-software-ver":
        config_name = "Software Versions"
        module_version_text = "This will be removed\n" + \
                              kootnet_version + "=Kootnet Sensors\n" + \
                              str(flask_version) + "=Flask\n" + \
                              str(gevent_version) + "=Gevent\n" + \
                              str(greenlet_version) + "=Greenlet\n" + \
                              str(cryptography_version) + "=Cryptography\n" + \
                              str(werkzeug_version) + "=Werkzeug\n" + \
                              str(requests_version) + "=Requests\n" + \
                              str(plotly_version) + "=Plotly Graphing\n" + \
                              str(numpy_version) + "=Numpy\n"
        return _config_to_html_view(config_name, "NA", module_version_text)
    elif url_path == "config-main":
        config_name = "Main Configuration"
        config_content = get_file_content(file_locations.primary_config)
        return _config_to_html_view(config_name, file_locations.primary_config, config_content)
    elif url_path == "config-is":
        config_name = "Installed Sensors"
        config_content = get_file_content(file_locations.installed_sensors_config)
        return _config_to_html_view(config_name, file_locations.installed_sensors_config, config_content)
    elif url_path == "config-cs":
        config_name = "Checkin Server"
        config_content = get_file_content(file_locations.checkin_configuration)
        return _config_to_html_view(config_name, file_locations.checkin_configuration, config_content)
    elif url_path == "config-display":
        config_name = "Display"
        config_content = get_file_content(file_locations.display_config)
        return _config_to_html_view(config_name, file_locations.display_config, config_content)
    elif url_path == "config-sc":
        config_name = "Remote Management Configuration"
        config_content = get_file_content(file_locations.html_sensor_control_config)
        return _config_to_html_view(config_name, file_locations.html_sensor_control_config, config_content)
    elif url_path == "config-ir":
        config_name = "Interval Recording"
        config_content = get_file_content(file_locations.interval_config)
        return _config_to_html_view(config_name, file_locations.interval_config, config_content)
    elif url_path == "config-high-low":
        config_name = "High/Low Trigger Recording"
        config_content = get_file_content(file_locations.trigger_high_low_config)
        return _config_to_html_view(config_name, file_locations.trigger_high_low_config, config_content)
    elif url_path == "config-variance":
        config_name = "Variance Trigger Recording"
        config_content = get_file_content(file_locations.trigger_variances_config)
        return _config_to_html_view(config_name, file_locations.trigger_variances_config, config_content)
    elif url_path == "config-mqtt-b":
        config_name = "MQTT Broker"
        config_content = get_file_content(file_locations.mqtt_broker_config)
        return _config_to_html_view(config_name, file_locations.mqtt_broker_config, config_content)
    elif url_path == "config-mqtt-p":
        config_name = "MQTT Publisher"
        config_content = remove_line_from_text(get_file_content(file_locations.mqtt_publisher_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.mqtt_publisher_config, config_content)
    elif url_path == "config-mqtt-s":
        config_name = "MQTT Subscriber"
        config_content = remove_line_from_text(get_file_content(file_locations.mqtt_subscriber_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.mqtt_subscriber_config, config_content)
    elif url_path == "config-wu":
        config_name = "Weather Underground"
        config_content = remove_line_from_text(get_file_content(file_locations.weather_underground_config), [4, 5])
        return _config_to_html_view(config_name, file_locations.weather_underground_config, config_content)
    elif url_path == "config-luftdaten":
        config_name = "Luftdaten"
        config_content = get_file_content(file_locations.luftdaten_config)
        return _config_to_html_view(config_name, file_locations.luftdaten_config, config_content)
    elif url_path == "config-osm":
        config_name = "Open Sense Map"
        config_content = remove_line_from_text(get_file_content(file_locations.osm_config), [2])
        return _config_to_html_view(config_name, file_locations.osm_config, config_content)
    elif url_path == "config-email":
        config_name = "Email"
        config_content = remove_line_from_text(get_file_content(file_locations.email_config), [5, 6])
        return _config_to_html_view(config_name, file_locations.email_config, config_content)
    elif url_path == "config-networking":
        config_name = "Networking (dhcpcd.conf)"
        config_content = get_file_content(file_locations.dhcpcd_config_file)
        return _config_to_html_view(config_name, file_locations.dhcpcd_config_file, config_content, split_by_line=False)
    elif url_path == "config-wifi":
        config_name = "WiFi"
        config_content = get_file_content(file_locations.wifi_config_file)
        return _config_to_html_view(config_name, file_locations.wifi_config_file, config_content, split_by_line=False)
