import os
import shutil
from os import geteuid
from plotly import __version__ as plotly_version
from gevent import __version__ as gevent_version
from requests import __version__ as requests_version
from werkzeug import __version__ as werkzeug_version
from numpy import __version__ as numpy_version
from flask import Blueprint, render_template, request, __version__ as flask_version
from werkzeug.security import generate_password_hash
from cryptography import x509, __version__ as cryptography_version
from cryptography.hazmat.backends import default_backend
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_cached_variables_update
from operations_modules import software_version
from operations_modules import app_config_access
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules import app_validation_checks
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk, thread_function
from http_server.server_http_auth import auth, save_http_auth_to_file
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return
from online_services_modules.mqtt_publisher import CreateMQTTSensorTopics, mqtt_base_topic
from sensor_modules import sensor_access

html_sensor_config_routes = Blueprint("html_sensor_config_routes", __name__)

mqtt_topics = CreateMQTTSensorTopics()
running_with_root = True
if geteuid():
    running_with_root = False


@html_sensor_config_routes.route("/GetMQTTTopics")
def html_get_mqtt_topics():
    logger.network_logger.debug("** HTML Get MQTT Topics accessed from " + str(request.remote_addr))
    return render_template("non-flask/mqtt_help.html",
                           SystemUpTime=mqtt_base_topic + mqtt_topics.system_uptime,
                           SystemTemperature=mqtt_base_topic + mqtt_topics.system_temperature,
                           EnvironmentTemperature=mqtt_base_topic + mqtt_topics.env_temperature,
                           Pressure=mqtt_base_topic + mqtt_topics.pressure,
                           Altitude=mqtt_base_topic + mqtt_topics.altitude,
                           Humidity=mqtt_base_topic + mqtt_topics.humidity,
                           Distance=mqtt_base_topic + mqtt_topics.distance,
                           Gas=mqtt_base_topic + mqtt_topics.gas,
                           ParticulateMatter=mqtt_base_topic + mqtt_topics.particulate_matter,
                           Lumen=mqtt_base_topic + mqtt_topics.lumen,
                           Color=mqtt_base_topic + mqtt_topics.color,
                           UltraViolet=mqtt_base_topic + mqtt_topics.ultra_violet,
                           Accelerometer=mqtt_base_topic + mqtt_topics.accelerometer,
                           Magnetometer=mqtt_base_topic + mqtt_topics.magnetometer,
                           Gyroscope=mqtt_base_topic + mqtt_topics.gyroscope)


@html_sensor_config_routes.route("/ConfigurationsHTML")
@auth.login_required
def html_edit_configurations():
    logger.network_logger.debug("** HTML Configurations accessed from " + str(request.remote_addr))
    return render_template("edit_configurations.html",
                           PageURL="/ConfigurationsHTML",
                           ConfigPrimaryTab=_get_config_primary_tab(),
                           ConfigInstalledSensorsTab=_get_config_installed_sensors_tab(),
                           ConfigDisplayTab=_get_config_display_tab(),
                           ConfigTriggerVariancesTab=_get_config_trigger_variances_tab(),
                           ConfigMQTTBrokerTab=_get_config_mqtt_broker_tab(),
                           ConfigMQTTPublisherTab=_get_config_mqtt_publisher_tab(),
                           ConfigWUTab=_get_config_weather_underground_tab(),
                           ConfigLuftdatenTab=_get_config_luftdaten_tab(),
                           ConfigOSMTab=_get_config_osm_tab())


def _get_config_primary_tab():
    try:
        debug_logging = get_html_checkbox_state(app_config_access.primary_config.enable_debug_logging)
        display = get_html_checkbox_state(app_config_access.primary_config.enable_display)
        interval_recording = get_html_checkbox_state(app_config_access.primary_config.enable_interval_recording)
        interval_recording_disabled = "disabled"
        if interval_recording:
            interval_recording_disabled = ""
        trigger_recording = get_html_checkbox_state(app_config_access.primary_config.enable_trigger_recording)
        custom_temp_offset = get_html_checkbox_state(app_config_access.primary_config.enable_custom_temp)
        custom_temp_offset_disabled = "disabled"
        if custom_temp_offset:
            custom_temp_offset_disabled = ""
        return render_template("edit_configurations/config_primary.html",
                               PageURL="/ConfigurationsHTML",
                               IPWebPort=app_config_access.primary_config.web_portal_port,
                               CheckedDebug=debug_logging,
                               CheckedDisplay=display,
                               CheckedInterval=interval_recording,
                               DisabledIntervalDelay=interval_recording_disabled,
                               IntervalDelay=float(app_config_access.primary_config.sleep_duration_interval),
                               CheckedTrigger=trigger_recording,
                               CheckedCustomTempOffset=custom_temp_offset,
                               DisabledCustomTempOffset=custom_temp_offset_disabled,
                               temperature_offset=float(app_config_access.primary_config.temperature_offset))
    except Exception as error:
        logger.network_logger.error("Error building Primary configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="primary-config-tab")


def _get_config_installed_sensors_tab():
    try:
        installed_sensors = app_config_access.installed_sensors
        return render_template("edit_configurations/config_installed_sensors.html",
                               PageURL="/ConfigurationsHTML",
                               GnuLinux=get_html_checkbox_state(installed_sensors.linux_system),
                               KootnetDummySensors=get_html_checkbox_state(installed_sensors.kootnet_dummy_sensor),
                               RaspberryPi=get_html_checkbox_state(installed_sensors.raspberry_pi),
                               SenseHAT=get_html_checkbox_state(installed_sensors.raspberry_pi_sense_hat),
                               PimoroniBH1745=get_html_checkbox_state(installed_sensors.pimoroni_bh1745),
                               PimoroniAS7262=get_html_checkbox_state(installed_sensors.pimoroni_as7262),
                               PimoroniMCP9600=get_html_checkbox_state(installed_sensors.pimoroni_mcp9600),
                               PimoroniBMP280=get_html_checkbox_state(installed_sensors.pimoroni_bmp280),
                               PimoroniBME680=get_html_checkbox_state(installed_sensors.pimoroni_bme680),
                               PimoroniEnviroPHAT=get_html_checkbox_state(installed_sensors.pimoroni_enviro),
                               PimoroniEnviroPlus=get_html_checkbox_state(installed_sensors.pimoroni_enviroplus),
                               PimoroniPMS5003=get_html_checkbox_state(installed_sensors.pimoroni_pms5003),
                               PimoroniSGP30=get_html_checkbox_state(installed_sensors.pimoroni_sgp30),
                               PimoroniMSA301=get_html_checkbox_state(installed_sensors.pimoroni_msa301),
                               PimoroniLSM303D=get_html_checkbox_state(installed_sensors.pimoroni_lsm303d),
                               PimoroniICM20948=get_html_checkbox_state(installed_sensors.pimoroni_icm20948),
                               PimoroniVL53L1X=get_html_checkbox_state(installed_sensors.pimoroni_vl53l1x),
                               PimoroniLTR559=get_html_checkbox_state(installed_sensors.pimoroni_ltr_559),
                               PimoroniVEML6075=get_html_checkbox_state(installed_sensors.pimoroni_veml6075),
                               Pimoroni11x7LEDMatrix=get_html_checkbox_state(installed_sensors.pimoroni_matrix_11x7),
                               PimoroniSPILCD10_96=get_html_checkbox_state(installed_sensors.pimoroni_st7735),
                               PimoroniMonoOLED128x128BW=get_html_checkbox_state(installed_sensors.pimoroni_mono_oled_luma))
    except Exception as error:
        logger.network_logger.error("Error building Installed Sensors configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="installed-sensors-tab")


def _get_config_display_tab():
    try:
        display_numerical_checked = ""
        display_graph_checked = ""
        display_type_numerical = app_config_access.display_config.display_type_numerical
        if app_config_access.display_config.display_type == display_type_numerical:
            display_numerical_checked = "checked"
        else:
            display_graph_checked = "checked"

        sensor_uptime = app_config_access.display_config.sensor_uptime
        system_temperature = app_config_access.display_config.system_temperature
        env_temperature = app_config_access.display_config.env_temperature
        pressure = app_config_access.display_config.pressure
        altitude = app_config_access.display_config.altitude
        humidity = app_config_access.display_config.humidity
        distance = app_config_access.display_config.distance
        gas = app_config_access.display_config.gas
        particulate_matter = app_config_access.display_config.particulate_matter
        lumen = app_config_access.display_config.lumen
        color = app_config_access.display_config.color
        ultra_violet = app_config_access.display_config.ultra_violet
        accelerometer = app_config_access.display_config.accelerometer
        magnetometer = app_config_access.display_config.magnetometer
        gyroscope = app_config_access.display_config.gyroscope
        return render_template("edit_configurations/config_display.html",
                               PageURL="/ConfigurationsHTML",
                               DisplayIntervalDelay=app_config_access.display_config.minutes_between_display,
                               DisplayNumericalChecked=display_numerical_checked,
                               DisplayGraphChecked=display_graph_checked,
                               DisplayUptimeChecked=get_html_checkbox_state(sensor_uptime),
                               DisplayCPUTempChecked=get_html_checkbox_state(system_temperature),
                               DisplayEnvTempChecked=get_html_checkbox_state(env_temperature),
                               DisplayPressureChecked=get_html_checkbox_state(pressure),
                               DisplayAltitudeChecked=get_html_checkbox_state(altitude),
                               DisplayHumidityChecked=get_html_checkbox_state(humidity),
                               DisplayDistanceChecked=get_html_checkbox_state(distance),
                               DisplayGASChecked=get_html_checkbox_state(gas),
                               DisplayPMChecked=get_html_checkbox_state(particulate_matter),
                               DisplayLumenChecked=get_html_checkbox_state(lumen),
                               DisplayColoursChecked=get_html_checkbox_state(color),
                               DisplayUltraVioletChecked=get_html_checkbox_state(ultra_violet),
                               DisplayAccChecked=get_html_checkbox_state(accelerometer),
                               DisplayMagChecked=get_html_checkbox_state(magnetometer),
                               DisplayGyroChecked=get_html_checkbox_state(gyroscope))
    except Exception as error:
        logger.network_logger.error("Error building Display configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="displays-tab")


def _get_config_trigger_variances_tab():
    try:
        variances = app_config_access.trigger_variances
        return render_template("edit_configurations/config_trigger_variances.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedSensorUptime=get_html_checkbox_state(variances.sensor_uptime_enabled),
                               DaysSensorUptime=(float(variances.sensor_uptime_wait_seconds) / 60.0 / 60.0 / 24.0),
                               CheckedCPUTemperature=get_html_checkbox_state(variances.cpu_temperature_enabled),
                               TriggerCPUTemperature=variances.cpu_temperature_variance,
                               SecondsCPUTemperature=variances.cpu_temperature_wait_seconds,
                               CheckedEnvTemperature=get_html_checkbox_state(variances.env_temperature_enabled),
                               TriggerEnvTemperature=variances.env_temperature_variance,
                               SecondsEnvTemperature=variances.env_temperature_wait_seconds,
                               CheckedPressure=get_html_checkbox_state(variances.pressure_enabled),
                               TriggerPressure=variances.pressure_variance,
                               SecondsPressure=variances.pressure_wait_seconds,
                               CheckedAltitude=get_html_checkbox_state(variances.altitude_enabled),
                               TriggerAltitude=variances.altitude_variance,
                               SecondsAltitude=variances.altitude_wait_seconds,
                               CheckedHumidity=get_html_checkbox_state(variances.humidity_enabled),
                               TriggerHumidity=variances.humidity_variance,
                               SecondsHumidity=variances.humidity_wait_seconds,
                               CheckedDistance=get_html_checkbox_state(variances.distance_enabled),
                               TriggerDistance=variances.distance_variance,
                               SecondsDistance=variances.distance_wait_seconds,
                               CheckedLumen=get_html_checkbox_state(variances.lumen_enabled),
                               TriggerLumen=variances.lumen_variance,
                               SecondsLumen=variances.lumen_wait_seconds,
                               CheckedColour=get_html_checkbox_state(variances.colour_enabled),
                               TriggerRed=variances.red_variance,
                               TriggerOrange=variances.orange_variance,
                               TriggerYellow=variances.yellow_variance,
                               TriggerGreen=variances.green_variance,
                               TriggerBlue=variances.blue_variance,
                               TriggerViolet=variances.violet_variance,
                               SecondsColour=variances.colour_wait_seconds,
                               CheckedUltraViolet=get_html_checkbox_state(variances.ultra_violet_enabled),
                               TriggerUltraVioletA=variances.ultra_violet_a_variance,
                               TriggerUltraVioletB=variances.ultra_violet_b_variance,
                               SecondsUltraViolet=variances.ultra_violet_wait_seconds,
                               CheckedGas=get_html_checkbox_state(variances.gas_enabled),
                               TriggerGasIndex=variances.gas_resistance_index_variance,
                               TriggerGasOxidising=variances.gas_oxidising_variance,
                               TriggerGasReducing=variances.gas_reducing_variance,
                               TriggerGasNH3=variances.gas_nh3_variance,
                               SecondsGas=variances.gas_wait_seconds,
                               CheckedPM=get_html_checkbox_state(variances.particulate_matter_enabled),
                               TriggerPM1=variances.particulate_matter_1_variance,
                               TriggerPM25=variances.particulate_matter_2_5_variance,
                               TriggerPM10=variances.particulate_matter_10_variance,
                               SecondsPM=variances.particulate_matter_wait_seconds,
                               CheckedAccelerometer=get_html_checkbox_state(variances.accelerometer_enabled),
                               TriggerAccelerometerX=variances.accelerometer_x_variance,
                               TriggerAccelerometerY=variances.accelerometer_y_variance,
                               TriggerAccelerometerZ=variances.accelerometer_z_variance,
                               SecondsAccelerometer=variances.accelerometer_wait_seconds,
                               CheckedMagnetometer=get_html_checkbox_state(variances.magnetometer_enabled),
                               TriggerMagnetometerX=variances.magnetometer_x_variance,
                               TriggerMagnetometerY=variances.magnetometer_y_variance,
                               TriggerMagnetometerZ=variances.magnetometer_z_variance,
                               SecondsMagnetometer=variances.magnetometer_wait_seconds,
                               CheckedGyroscope=get_html_checkbox_state(variances.gyroscope_enabled),
                               TriggerGyroscopeX=variances.gyroscope_x_variance,
                               TriggerGyroscopeY=variances.gyroscope_y_variance,
                               TriggerGyroscopeZ=variances.gyroscope_z_variance,
                               SecondsGyroscope=variances.gyroscope_wait_seconds)
    except Exception as error:
        logger.network_logger.error("Error building Trigger Variances configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="trigger-variances-tab")


def _get_config_mqtt_broker_tab():
    try:
        enable_broker_server = app_config_access.mqtt_broker_config.enable_mqtt_broker
        return render_template("edit_configurations/config_mqtt_broker.html",
                               PageURL="/ConfigurationsHTML",
                               MQTTBrokerServerChecked=_get_checked_text(enable_broker_server),
                               MQTTBrokerUsername=app_config_access.mqtt_broker_config.username)
    except Exception as error:
        logger.network_logger.error("Error building MQTT Broker configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-broker-tab")


def _get_config_mqtt_publisher_tab():
    try:
        base_topic = app_config_access.mqtt_publisher_config.mqtt_base_topic + sensor_access.get_hostname() + "/"
        enable_mqtt_publisher = app_config_access.mqtt_publisher_config.enable_mqtt_publisher
        enable_broker_auth = app_config_access.mqtt_publisher_config.enable_broker_auth
        return render_template("edit_configurations/config_mqtt_publisher.html",
                               PageURL="/ConfigurationsHTML",
                               MQTTBaseTopic=base_topic,
                               MQTTPublisherChecked=_get_checked_text(enable_mqtt_publisher),
                               MQTTBrokerAddress=app_config_access.mqtt_publisher_config.broker_address,
                               MQTTBrokerPort=str(app_config_access.mqtt_publisher_config.broker_server_port),
                               MQTTPublishSecondsWait=str(app_config_access.mqtt_publisher_config.seconds_to_wait),
                               MQTTPublisherAuthChecked=_get_checked_text(enable_broker_auth),
                               MQTTPublisherUsername=app_config_access.mqtt_publisher_config.broker_user,
                               MQTTUptimeChecked=_get_checked_text(app_config_access.mqtt_publisher_config.sensor_uptime),
                               MQTTCPUTempChecked=_get_checked_text(app_config_access.mqtt_publisher_config.system_temperature),
                               MQTTEnvTempChecked=_get_checked_text(app_config_access.mqtt_publisher_config.env_temperature),
                               MQTTPressureChecked=_get_checked_text(app_config_access.mqtt_publisher_config.pressure),
                               MQTTAltitudeChecked=_get_checked_text(app_config_access.mqtt_publisher_config.altitude),
                               MQTTHumidityChecked=_get_checked_text(app_config_access.mqtt_publisher_config.humidity),
                               MQTTDistanceChecked=_get_checked_text(app_config_access.mqtt_publisher_config.distance),
                               MQTTGASChecked=_get_checked_text(app_config_access.mqtt_publisher_config.gas),
                               MQTTPMChecked=_get_checked_text(app_config_access.mqtt_publisher_config.particulate_matter),
                               MQTTLumenChecked=_get_checked_text(app_config_access.mqtt_publisher_config.lumen),
                               MQTTColoursChecked=_get_checked_text(app_config_access.mqtt_publisher_config.color),
                               MQTTUltraVioletChecked=_get_checked_text(app_config_access.mqtt_publisher_config.ultra_violet),
                               MQTTAccChecked=_get_checked_text(app_config_access.mqtt_publisher_config.accelerometer),
                               MQTTMagChecked=_get_checked_text(app_config_access.mqtt_publisher_config.magnetometer),
                               MQTTGyroChecked=_get_checked_text(app_config_access.mqtt_publisher_config.gyroscope))
    except Exception as error:
        logger.network_logger.error("Error building MQTT configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="mqtt-publisher-tab")


def _get_checked_text(setting):
    if setting:
        return "checked"
    return ""


def _get_config_weather_underground_tab():
    try:
        weather_underground_enabled = app_config_access.weather_underground_config.weather_underground_enabled
        wu_rapid_fire_enabled = app_config_access.weather_underground_config.wu_rapid_fire_enabled
        wu_checked = get_html_checkbox_state(weather_underground_enabled)
        wu_rapid_fire_checked = get_html_checkbox_state(wu_rapid_fire_enabled)
        wu_rapid_fire_disabled = "disabled"
        wu_interval_seconds_disabled = "disabled"
        wu_outdoor_disabled = "disabled"
        wu_station_id_disabled = "disabled"
        wu_station_key_disabled = "disabled"
        if app_config_access.weather_underground_config.weather_underground_enabled:
            wu_rapid_fire_disabled = ""
            wu_interval_seconds_disabled = ""
            wu_outdoor_disabled = ""
            wu_station_id_disabled = ""
            wu_station_key_disabled = ""

        wu_interval_seconds = app_config_access.weather_underground_config.interval_seconds
        wu_outdoor = get_html_checkbox_state(app_config_access.weather_underground_config.outdoor_sensor)
        wu_station_id = app_config_access.weather_underground_config.station_id
        return render_template("edit_configurations/config_weather_underground.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedWUEnabled=wu_checked,
                               CheckedWURapidFire=wu_rapid_fire_checked,
                               DisabledWURapidFire=wu_rapid_fire_disabled,
                               WUIntervalSeconds=wu_interval_seconds,
                               DisabledWUInterval=wu_interval_seconds_disabled,
                               CheckedWUOutdoor=wu_outdoor,
                               DisabledWUOutdoor=wu_outdoor_disabled,
                               DisabledStationID=wu_station_id_disabled,
                               WUStationID=wu_station_id,
                               DisabledStationKey=wu_station_key_disabled)
    except Exception as error:
        logger.network_logger.error("Error building Weather Underground configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="weather-underground-tab")


def _get_config_luftdaten_tab():
    try:
        luftdaten_checked = get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled)
        luftdaten_interval_seconds_disabled = "disabled"
        if app_config_access.luftdaten_config.luftdaten_enabled:
            luftdaten_interval_seconds_disabled = ""

        luftdaten_interval_seconds = app_config_access.luftdaten_config.interval_seconds
        luftdaten_station_id = app_config_access.luftdaten_config.station_id
        return render_template("edit_configurations/config_luftdaten.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedLuftdatenEnabled=luftdaten_checked,
                               LuftdatenIntervalSeconds=luftdaten_interval_seconds,
                               DisabledLuftdatenInterval=luftdaten_interval_seconds_disabled,
                               LuftdatenStationID=luftdaten_station_id)
    except Exception as error:
        logger.network_logger.error("Error building Luftdaten configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="luftdaten-tab")


def _get_config_osm_tab():
    try:
        osm_disabled = "disabled"
        osm_enable_checked = ""
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            osm_enable_checked = "checked"
            osm_disabled = ""
        return render_template("edit_configurations/config_open_sense_map.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedOSMEnabled=osm_enable_checked,
                               OSMDisabled=osm_disabled,
                               OSMStationID=app_config_access.open_sense_map_config.sense_box_id,
                               OSMIntervalSeconds=app_config_access.open_sense_map_config.interval_seconds,
                               OSMSEnvTempID=app_config_access.open_sense_map_config.temperature_id,
                               OSMPressureID=app_config_access.open_sense_map_config.pressure_id,
                               OSMAltitudeID=app_config_access.open_sense_map_config.altitude_id,
                               OSMHumidityID=app_config_access.open_sense_map_config.humidity_id,
                               OSMGasIndexID=app_config_access.open_sense_map_config.gas_voc_id,
                               OSMGasNH3ID=app_config_access.open_sense_map_config.gas_nh3_id,
                               OSMOxidisingID=app_config_access.open_sense_map_config.gas_oxidised_id,
                               OSMGasReducingID=app_config_access.open_sense_map_config.gas_reduced_id,
                               OSMPM1ID=app_config_access.open_sense_map_config.pm1_id,
                               OSMPM25ID=app_config_access.open_sense_map_config.pm2_5_id,
                               OSMPM10ID=app_config_access.open_sense_map_config.pm10_id,
                               OSMLumenID=app_config_access.open_sense_map_config.lumen_id,
                               OSMRedID=app_config_access.open_sense_map_config.red_id,
                               OSMOrangeID=app_config_access.open_sense_map_config.orange_id,
                               OSMYellowID=app_config_access.open_sense_map_config.yellow_id,
                               OSMGreenID=app_config_access.open_sense_map_config.green_id,
                               OSMBlueID=app_config_access.open_sense_map_config.blue_id,
                               OSMVioletID=app_config_access.open_sense_map_config.violet_id,
                               OSMUVIndexID=app_config_access.open_sense_map_config.ultra_violet_index_id,
                               OSMUVAID=app_config_access.open_sense_map_config.ultra_violet_a_id,
                               OSMUVBID=app_config_access.open_sense_map_config.ultra_violet_b_id)
    except Exception as error:
        logger.network_logger.error("Error building Open Sense Map configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="open-sense-map-tab")


@html_sensor_config_routes.route("/NetworkConfigurationsHTML")
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


@html_sensor_config_routes.route("/EditConfigMain", methods=["POST"])
@auth.login_required
def html_set_config_main():
    logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.primary_config.update_with_html_request(request)
            app_config_access.primary_config.save_config_to_file()
            page_msg = "Config Set, Please Restart Program"
            if running_with_root:
                page_msg = "Restarting Service, Please Wait ..."
                thread_function(sensor_access.restart_services)
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/EditInstalledSensors", methods=["POST"])
@auth.login_required
def html_set_installed_sensors():
    logger.network_logger.debug("** HTML Apply - Installed Sensors - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.installed_sensors.update_with_html_request(request)
            app_config_access.installed_sensors.save_config_to_file()
            page_msg = "Installed Sensors Set, Please Restart Program"
            if running_with_root:
                page_msg = "Restarting Service, Please Wait ..."
                thread_function(sensor_access.restart_services)
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Apply - Installed Sensors - Error: " + str(error))
            return message_and_return("Bad Installed Sensors POST Request", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/EditDisplayConfiguration", methods=["POST"])
@auth.login_required
def html_set_display_config():
    logger.network_logger.debug("** HTML Apply - Display Configuration - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.display_config.update_with_html_request(request)
            app_config_access.display_config.save_config_to_file()
            page_msg = "Config Set, Please Restart Program"
            if running_with_root:
                page_msg = "Restarting Service, Please Wait ..."
                thread_function(sensor_access.restart_services)
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Apply - Display Configuration - Error: " + str(error))
            return message_and_return("Bad Display Configuration POST Request", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/EditTriggerVariances", methods=["POST"])
@auth.login_required
def html_set_trigger_variances():
    logger.network_logger.debug("** HTML Apply - Trigger Variances - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.trigger_variances.update_with_html_request(request)
            app_config_access.trigger_variances.save_config_to_file()
            return message_and_return("Trigger Variances Set", url="/ConfigurationsHTML")
        except Exception as error:
            logger.primary_logger.warning("HTML Apply - Trigger Variances - Error: " + str(error))
    return message_and_return("Bad Trigger Variances POST Request", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/ResetTriggerVariances")
@auth.login_required
def html_reset_trigger_variances():
    logger.network_logger.info("** Trigger Variances Reset - Source " + str(request.remote_addr))
    app_config_access.trigger_variances.reset_settings()
    return message_and_return("Trigger Variances Reset", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/EditConfigMQTTPublisher", methods=["POST"])
@auth.login_required
def html_set_config_mqtt_publisher():
    logger.network_logger.debug("** HTML Apply - MQTT Publisher Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.mqtt_publisher_config.update_with_html_request(request)
            app_config_access.mqtt_publisher_config.save_config_to_file()
            page_msg = "Config Set, Please Restart Program"
            if running_with_root:
                page_msg = "Restarting Service, Please Wait ..."
                thread_function(sensor_access.restart_services)
            return_page = message_and_return(page_msg, url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML MQTT Publisher Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/EditSSL", methods=["GET", "POST"])
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


@html_sensor_config_routes.route("/EditConfigIPv4", methods=["POST"])
@auth.login_required
def html_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    message = "Network settings have not been changed."
    if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
        if request.form.get("ip_dhcp") is not None:
            message = "You must reboot for all settings to take effect."
            dhcpcd_template = get_file_content(file_locations.dhcpcd_config_file_template)
            dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", "")
            hostname = request.form.get("ip_hostname")
            os.system("hostnamectl set-hostname " + hostname)
            write_file_to_disk(file_locations.dhcpcd_config_file, dhcpcd_template)
            app_cached_variables_update.update_cached_variables()
            msg = "IPv4 Configuration Updated"
            return message_and_return(msg, text_message2=message, url="/NetworkConfigurationsHTML")

        ip_address = request.form.get("ip_address")
        ip_subnet = request.form.get("ip_subnet")
        ip_gateway = request.form.get("ip_gateway")
        ip_dns1 = request.form.get("ip_dns1")
        ip_dns2 = request.form.get("ip_dns2")

        try:
            app_validation_checks.ip_address_is_valid(ip_address)
        except ValueError:
            return message_and_return("Invalid IP Address", text_message2=message, url="/NetworkConfigurationsHTML")
        if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
            return message_and_return("Invalid Subnet Mask", text_message2=message, url="/NetworkConfigurationsHTML")
        if ip_gateway is not "":
            try:
                app_validation_checks.ip_address_is_valid(ip_gateway)
            except ValueError:
                return message_and_return("Invalid Gateway", text_message2=message, url="/NetworkConfigurationsHTML")
        if ip_dns1 is not "":
            try:
                app_validation_checks.ip_address_is_valid(ip_dns1)
            except ValueError:
                title_message = "Invalid Primary DNS Address"
                return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")
        if ip_dns2 is not "":
            title_message = "Invalid Secondary DNS Address"
            try:
                app_validation_checks.ip_address_is_valid(ip_dns2)
            except ValueError:
                return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")

        check_html_config_ipv4(request)
        app_cached_variables_update.update_cached_variables()
        title_message = "IPv4 Configuration Updated"
        message = "You must reboot the sensor to take effect."
        return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")
    else:
        title_message = "Unable to Process IPv4 Configuration"
        message = "Invalid or Missing Hostname.\n\nOnly Alphanumeric Characters, Dashes and Underscores may be used."
        return message_and_return(title_message, text_message2=message, url="/NetworkConfigurationsHTML")


def check_html_config_ipv4(html_request):
    logger.network_logger.debug("Starting HTML IPv4 Configuration Update Check")
    dhcpcd_template = get_file_content(file_locations.dhcpcd_config_file_template)

    hostname = html_request.form.get("ip_hostname")
    os.system("hostnamectl set-hostname " + hostname)
    app_cached_variables.hostname = hostname

    ip_address = html_request.form.get("ip_address")
    ip_subnet_mask = html_request.form.get("ip_subnet")
    ip_gateway = html_request.form.get("ip_gateway")
    ip_dns1 = html_request.form.get("ip_dns1")
    ip_dns2 = html_request.form.get("ip_dns2")

    ip_network_text = "interface wlan0\nstatic ip_address=" + ip_address + ip_subnet_mask + \
                      "\nstatic routers=" + ip_gateway + "\nstatic domain_name_servers=" + ip_dns1 + " " + ip_dns2

    dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", ip_network_text)
    network_ip.write_ipv4_config_to_file(dhcpcd_template)

    shutil.chown(file_locations.dhcpcd_config_file, "root", "netdev")
    os.chmod(file_locations.dhcpcd_config_file, 0o664)


@html_sensor_config_routes.route("/EditConfigWifi", methods=["POST"])
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
                network_wifi.write_wifi_config_to_file(new_wireless_config)
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
                           WeatherUndergroundConfiguration=str(get_file_content(file_locations.weather_underground_config)),
                           WUCLocation=file_locations.weather_underground_config,
                           LuftdatenConfiguration=str(get_file_content(file_locations.luftdaten_config)),
                           LCLocation=file_locations.luftdaten_config,
                           OpenSenseMapConfiguration=str(get_file_content(file_locations.osm_config)),
                           OSMCLocation=file_locations.osm_config)
