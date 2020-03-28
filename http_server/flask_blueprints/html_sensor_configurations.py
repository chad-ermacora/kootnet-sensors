import os
import shutil
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
from sensor_modules import sensor_access

html_sensor_config_routes = Blueprint("html_sensor_config_routes", __name__)


@html_sensor_config_routes.route("/ConfigurationsHTML")
@auth.login_required
def html_edit_configurations():
    logger.network_logger.debug("** HTML Configurations accessed from " + str(request.remote_addr))
    try:
        variances = app_config_access.trigger_variances
        sensors_now = app_config_access.installed_sensors

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

        wu_checked = get_html_checkbox_state(app_config_access.weather_underground_config.weather_underground_enabled)
        wu_rapid_fire_checked = get_html_checkbox_state(
            app_config_access.weather_underground_config.wu_rapid_fire_enabled)
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

        luftdaten_checked = get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled)
        luftdaten_interval_seconds_disabled = "disabled"
        if app_config_access.luftdaten_config.luftdaten_enabled:
            luftdaten_interval_seconds_disabled = ""

        luftdaten_interval_seconds = app_config_access.luftdaten_config.interval_seconds
        luftdaten_station_id = app_config_access.luftdaten_config.station_id

        osm_disabled = "disabled"
        osm_enable_checked = ""
        if app_config_access.open_sense_map_config.open_sense_map_enabled:
            osm_enable_checked = "checked"
            osm_disabled = ""

        return render_template("edit_configurations.html",
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
                               temperature_offset=float(app_config_access.primary_config.temperature_offset),
                               GnuLinux=get_html_checkbox_state(sensors_now.linux_system),
                               RaspberryPi=get_html_checkbox_state(sensors_now.raspberry_pi),
                               SenseHAT=get_html_checkbox_state(sensors_now.raspberry_pi_sense_hat),
                               PimoroniBH1745=get_html_checkbox_state(sensors_now.pimoroni_bh1745),
                               PimoroniAS7262=get_html_checkbox_state(sensors_now.pimoroni_as7262),
                               PimoroniMCP9600=get_html_checkbox_state(sensors_now.pimoroni_mcp9600),
                               PimoroniBMP280=get_html_checkbox_state(sensors_now.pimoroni_bmp280),
                               PimoroniBME680=get_html_checkbox_state(sensors_now.pimoroni_bme680),
                               PimoroniEnviroPHAT=get_html_checkbox_state(sensors_now.pimoroni_enviro),
                               PimoroniEnviroPlus=get_html_checkbox_state(sensors_now.pimoroni_enviroplus),
                               PimoroniPMS5003=get_html_checkbox_state(sensors_now.pimoroni_pms5003),
                               PimoroniSGP30=get_html_checkbox_state(sensors_now.pimoroni_sgp30),
                               PimoroniMSA301=get_html_checkbox_state(sensors_now.pimoroni_msa301),
                               PimoroniLSM303D=get_html_checkbox_state(sensors_now.pimoroni_lsm303d),
                               PimoroniICM20948=get_html_checkbox_state(sensors_now.pimoroni_icm20948),
                               PimoroniVL53L1X=get_html_checkbox_state(sensors_now.pimoroni_vl53l1x),
                               PimoroniLTR559=get_html_checkbox_state(sensors_now.pimoroni_ltr_559),
                               PimoroniVEML6075=get_html_checkbox_state(sensors_now.pimoroni_veml6075),
                               Pimoroni11x7LEDMatrix=get_html_checkbox_state(sensors_now.pimoroni_matrix_11x7),
                               PimoroniSPILCD10_96=get_html_checkbox_state(sensors_now.pimoroni_st7735),
                               PimoroniMonoOLED128x128BW=get_html_checkbox_state(sensors_now.pimoroni_mono_oled_luma),
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
                               SecondsGyroscope=variances.gyroscope_wait_seconds,
                               CheckedWUEnabled=wu_checked,
                               CheckedWURapidFire=wu_rapid_fire_checked,
                               DisabledWURapidFire=wu_rapid_fire_disabled,
                               WUIntervalSeconds=wu_interval_seconds,
                               DisabledWUInterval=wu_interval_seconds_disabled,
                               CheckedWUOutdoor=wu_outdoor,
                               DisabledWUOutdoor=wu_outdoor_disabled,
                               DisabledStationID=wu_station_id_disabled,
                               WUStationID=wu_station_id,
                               DisabledStationKey=wu_station_key_disabled,
                               CheckedLuftdatenEnabled=luftdaten_checked,
                               LuftdatenIntervalSeconds=luftdaten_interval_seconds,
                               DisabledLuftdatenInterval=luftdaten_interval_seconds_disabled,
                               LuftdatenStationID=luftdaten_station_id,
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
        logger.network_logger.error("HTML unable to display Configurations: " + str(error))
        return render_template("message_return.html", message2="Unable to Display Configurations...")


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
        return render_template("message_return.html", message2="Unable to Display Networking Configurations...")


@html_sensor_config_routes.route("/EditConfigMain", methods=["POST"])
@auth.login_required
def html_set_config_main():
    logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.primary_config.update_with_html_request(request)
            app_config_access.primary_config.save_config_to_file()
            return_page = message_and_return("Restarting Service, Please Wait ...", url="/ConfigurationsHTML")
            thread_function(sensor_access.restart_services)
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
            return_page = message_and_return("Restarting Service, Please Wait ...", url="/ConfigurationsHTML")
            thread_function(sensor_access.restart_services)
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Apply - Installed Sensors - Error: " + str(error))
            return message_and_return("Bad Installed Sensors POST Request", url="/ConfigurationsHTML")


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
                           MainConfiguration=get_file_content(file_locations.primary_config),
                           InstalledSensorsConfiguration=get_file_content(file_locations.installed_sensors_config),
                           TriggerConfiguration=get_file_content(file_locations.trigger_variances_config),
                           SensorControlConfiguration=get_file_content(file_locations.html_sensor_control_config),
                           NetworkConfiguration=get_file_content(file_locations.dhcpcd_config_file),
                           WiFiConfiguration=get_file_content(file_locations.wifi_config_file),
                           ModuleVersions=module_version_text,
                           WeatherUndergroundConfiguration=get_file_content(file_locations.weather_underground_config),
                           LuftdatenConfiguration=get_file_content(file_locations.luftdaten_config),
                           OpenSenseMapConfiguration=get_file_content(file_locations.osm_config))
