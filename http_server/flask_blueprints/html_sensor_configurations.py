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
try:
    from plotly import __version__ as plotly_version
    from numpy import __version__ as numpy_version
    from gevent import __version__ as gevent_version
    from requests import __version__ as requests_version
    from werkzeug import __version__ as werkzeug_version
except ImportError as import_error:
    logger.primary_logger.warning("Import Versions Failed: " + str(import_error))
    plotly_version = "Unknown"
    numpy_version = "Unknown"
    gevent_version = "Unknown"
    requests_version = "Unknown"
    werkzeug_version = "Unknown"
from flask import Blueprint, render_template, request, __version__ as flask_version
from werkzeug.security import generate_password_hash
from cryptography import __version__ as cryptography_version
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import software_version
from operations_modules.app_generic_functions import get_file_content
from http_server.server_http_auth import auth, save_http_auth_to_file
from http_server.server_http_generic_functions import message_and_return, get_html_hidden_state
from http_server.flask_blueprints.sensor_configurations.f_bp_config_display import get_config_display_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_installed_sensors import get_config_installed_sensors_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_luftdaten import get_config_luftdaten_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_mqtt_broker import get_config_mqtt_broker_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_mqtt_publisher import get_config_mqtt_publisher_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_mqtt_subscriber import get_config_mqtt_subscriber_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_open_sense_map import get_config_osm_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_primary import get_config_primary_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_trigger_variances import get_config_trigger_variances_tab
from http_server.flask_blueprints.sensor_configurations.f_bp_config_weather_underground import get_config_weather_underground_tab

html_sensor_config_routes = Blueprint("html_sensor_config_routes", __name__)
running_with_root = app_cached_variables.running_with_root


@html_sensor_config_routes.route("/ConfigurationsHTML")
@auth.login_required
def html_edit_configurations():
    logger.network_logger.debug("** HTML Configurations accessed from " + str(request.remote_addr))
    return render_template("edit_configurations.html",
                           PageURL="/ConfigurationsHTML",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           ConfigPrimaryTab=get_config_primary_tab(),
                           ConfigInstalledSensorsTab=get_config_installed_sensors_tab(),
                           ConfigDisplayTab=get_config_display_tab(),
                           ConfigTriggerVariancesTab=get_config_trigger_variances_tab(),
                           ConfigMQTTBrokerTab=get_config_mqtt_broker_tab(),
                           ConfigMQTTPublisherTab=get_config_mqtt_publisher_tab(),
                           ConfigMQTTSubscriberTab=get_config_mqtt_subscriber_tab(),
                           ConfigWUTab=get_config_weather_underground_tab(),
                           ConfigLuftdatenTab=get_config_luftdaten_tab(),
                           ConfigOSMTab=get_config_osm_tab())


@html_sensor_config_routes.route("/EditLogin", methods=["POST"])
@auth.login_required
def html_set_login_credentials():
    logger.primary_logger.warning("*** Login Credentials Changed - Source " + str(request.remote_addr))
    if request.method == "POST":
        if request.form.get("login_username") and request.form.get("login_password"):
            temp_username = str(request.form.get("login_username"))
            temp_password = str(request.form.get("login_password"))
            if len(temp_username) > 3 and len(temp_password) > 3:
                app_cached_variables.http_flask_user = temp_username
                app_cached_variables.http_flask_password = generate_password_hash(temp_password)
                save_http_auth_to_file(temp_username, temp_password)
                msg1 = "Username and Password Updated"
                msg2 = "The Username and Password has been updated"
                return message_and_return(msg1, text_message2=msg2, url="/SystemCommands")
        message = "Username and Password must be 4 to 62 characters long and cannot be blank."
        return message_and_return("Invalid Username or Password", text_message2=message, url="/SystemCommands")
    return message_and_return("Unable to Process Login Credentials", url="/SystemCommands")


@html_sensor_config_routes.route("/HTMLRawConfigurations")
@auth.login_required
def html_raw_configurations_view():
    logger.network_logger.debug("** HTML Raw Configurations viewed by " + str(request.remote_addr))
    module_version_text = "Kootnet Sensors: " + software_version.version + "\n" + \
                          "Flask: " + str(flask_version) + "\n" + \
                          "Gevent: " + str(gevent_version) + "\n" + \
                          "Cryptography: " + str(cryptography_version) + "\n" + \
                          "Werkzeug: " + str(werkzeug_version) + "\n" + \
                          "Requests: " + str(requests_version) + "\n" + \
                          "Plotly Graphing: " + str(plotly_version) + "\n" + \
                          "Numpy: " + str(numpy_version) + "\n"

    return render_template("view_raw_configurations.html",
                           PageURL="/HTMLRawConfigurations",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           ModuleVersions=module_version_text,
                           MainConfiguration=str(get_file_content(file_locations.primary_config)),
                           MCLocation=file_locations.primary_config,
                           InstalledSensorsConfiguration=str(get_file_content(file_locations.installed_sensors_config)),
                           ISLocation=file_locations.installed_sensors_config,
                           DisplayConfiguration=str(get_file_content(file_locations.display_config)),
                           DCLocation=file_locations.display_config,
                           TriggerConfiguration=str(get_file_content(file_locations.trigger_variances_config)),
                           TVLocation=file_locations.trigger_variances_config,
                           SensorControlConfiguration=str(get_file_content(file_locations.html_sensor_control_config)),
                           SCCLocation=file_locations.html_sensor_control_config,
                           NetworkConfiguration=str(get_file_content(file_locations.dhcpcd_config_file)),
                           NCLocation=file_locations.dhcpcd_config_file,
                           WiFiConfiguration=str(get_file_content(file_locations.wifi_config_file)),
                           WCLocation=file_locations.wifi_config_file,
                           BrokerConfiguration=str(get_file_content(file_locations.mqtt_broker_config)),
                           BrokerCLocation=file_locations.mqtt_broker_config,
                           MQTTPublisherConfiguration=str(get_file_content(file_locations.mqtt_publisher_config)),
                           MQTTPublisherCLocation=file_locations.mqtt_publisher_config,
                           MQTTSubscriberConfiguration=str(get_file_content(file_locations.mqtt_subscriber_config)),
                           MQTTSubscriberCLocation=file_locations.mqtt_subscriber_config,
                           WeatherUndergroundConfiguration=str(get_file_content(file_locations.weather_underground_config)),
                           WUCLocation=file_locations.weather_underground_config,
                           LuftdatenConfiguration=str(get_file_content(file_locations.luftdaten_config)),
                           LCLocation=file_locations.luftdaten_config,
                           OpenSenseMapConfiguration=str(get_file_content(file_locations.osm_config)),
                           OSMCLocation=file_locations.osm_config)
