import os
import shutil
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_cached_variables_update
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules import app_validation_checks
from http_server.server_http_auth import auth
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

        debug_logging = get_html_checkbox_state(app_config_access.current_config.enable_debug_logging)
        display = get_html_checkbox_state(app_config_access.current_config.enable_display)
        interval_recording = get_html_checkbox_state(app_config_access.current_config.enable_interval_recording)
        interval_recording_disabled = "disabled"
        if interval_recording:
            interval_recording_disabled = ""
        trigger_recording = get_html_checkbox_state(app_config_access.current_config.enable_trigger_recording)
        custom_temp_offset = get_html_checkbox_state(app_config_access.current_config.enable_custom_temp)
        custom_temp_offset_disabled = "disabled"
        if custom_temp_offset:
            custom_temp_offset_disabled = ""

        dhcp_checkbox = ""
        ip_disabled = ""
        subnet_disabled = ""
        gateway_disabled = ""
        dns1_disabled = ""
        dns2_disabled = ""
        wifi_security_type_none1 = ""
        wifi_security_type_wpa1 = ""
        if sensors_now.raspberry_pi:
            dhcpcd_lines = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file).split("\n")
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

        return render_template("edit_configurations.html",
                               PageURL="/ConfigurationsHTML",
                               CheckedDebug=debug_logging,
                               CheckedDisplay=display,
                               CheckedInterval=interval_recording,
                               DisabledIntervalDelay=interval_recording_disabled,
                               IntervalDelay=float(app_config_access.current_config.sleep_duration_interval),
                               CheckedTrigger=trigger_recording,
                               CheckedCustomTempOffset=custom_temp_offset,
                               DisabledCustomTempOffset=custom_temp_offset_disabled,
                               temperature_offset=float(app_config_access.current_config.temperature_offset),
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
        logger.network_logger.error("HTML unable to display Configurations: " + str(error))
        return render_template("message_return.html", message2="Unable to Display Configurations...")


@html_sensor_config_routes.route("/EditConfigMain", methods=["POST"])
@auth.login_required
def html_set_config_main():
    logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.current_config.update_with_html_request(request)
            app_config_access.current_config.save_config_to_file()
            return_page = message_and_return("Restarting Service, Please Wait ...", url="/ConfigurationsHTML")
            app_generic_functions.thread_function(sensor_access.restart_services)
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
            app_generic_functions.thread_function(sensor_access.restart_services)
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


@html_sensor_config_routes.route("/EditConfigIPv4", methods=["POST"])
@auth.login_required
def html_set_ipv4_config():
    logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
    message = "Network settings have not been changed."
    if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
        if request.form.get("ip_dhcp") is not None:
            message = "You must reboot for all settings to take effect."
            dhcpcd_template = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file_template)
            dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", "")
            hostname = request.form.get("ip_hostname")
            os.system("hostnamectl set-hostname " + hostname)
            app_generic_functions.write_file_to_disk(file_locations.dhcpcd_config_file, dhcpcd_template)
            app_cached_variables_update.update_cached_variables()
            return message_and_return("IPv4 Configuration Updated", text_message2=message, url="/ConfigurationsHTML")

        ip_address = request.form.get("ip_address")
        ip_subnet = request.form.get("ip_subnet")
        ip_gateway = request.form.get("ip_gateway")
        ip_dns1 = request.form.get("ip_dns1")
        ip_dns2 = request.form.get("ip_dns2")

        try:
            app_validation_checks.ip_address_is_valid(ip_address)
        except ValueError:
            return message_and_return("Invalid IP Address", text_message2=message, url="/ConfigurationsHTML")
        if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
            return message_and_return("Invalid Subnet Mask", text_message2=message, url="/ConfigurationsHTML")
        if ip_gateway is not "":
            try:
                app_validation_checks.ip_address_is_valid(ip_gateway)
            except ValueError:
                return message_and_return("Invalid Gateway", text_message2=message, url="/ConfigurationsHTML")
        if ip_dns1 is not "":
            try:
                app_validation_checks.ip_address_is_valid(ip_dns1)
            except ValueError:
                title_message = "Invalid Primary DNS Address"
                return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")
        if ip_dns2 is not "":
            title_message = "Invalid Secondary DNS Address"
            try:
                app_validation_checks.ip_address_is_valid(ip_dns2)
            except ValueError:
                return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")

        check_html_config_ipv4(request)
        app_cached_variables_update.update_cached_variables()
        title_message = "IPv4 Configuration Updated"
        message = "You must reboot the sensor to take effect."
        return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")
    else:
        title_message = "Unable to Process IPv4 Configuration"
        message = "Invalid or Missing Hostname.\n\nOnly Alphanumeric Characters, Dashes and Underscores may be used."
        return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")


def check_html_config_ipv4(html_request):
    logger.network_logger.debug("Starting HTML IPv4 Configuration Update Check")
    dhcpcd_template = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file_template)

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
            return message_and_return("Invalid Wireless Key", text_message2=message, url="/ConfigurationsHTML")
        if app_validation_checks.wireless_ssid_is_valid(request.form.get("ssid1")):
            new_wireless_config = network_wifi.html_request_to_config_wifi(request)
            if new_wireless_config is not "":
                network_wifi.write_wifi_config_to_file(new_wireless_config)
                title_message = "WiFi Configuration Updated"
                message = "You must reboot the sensor to take effect."
                app_cached_variables_update.update_cached_variables()
                return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")
        else:
            logger.network_logger.debug("HTML WiFi Configuration Update Failed")
            title_message = "Unable to Process Wireless Configuration"
            message = "Network Names cannot be blank and can only use " + \
                             "Alphanumeric Characters, dashes, underscores and spaces."
            return message_and_return(title_message, text_message2=message, url="/ConfigurationsHTML")
    return message_and_return("Unable to Process WiFi Configuration", url="/ConfigurationsHTML")


@html_sensor_config_routes.route("/HTMLRawConfigurations")
@auth.login_required
def html_raw_configurations_view():
    logger.network_logger.debug("** HTML Raw Configurations viewed by " + str(request.remote_addr))
    primary_config = app_generic_functions.get_file_content(file_locations.primary_config)
    installed_sensors = app_generic_functions.get_file_content(file_locations.installed_sensors_config)
    networking = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file)
    wifi = app_generic_functions.get_file_content(file_locations.wifi_config_file)
    trigger_variances = app_generic_functions.get_file_content(file_locations.trigger_variances_config)
    sensor_control_config = app_generic_functions.get_file_content(file_locations.html_sensor_control_config)
    weather_underground_config = app_generic_functions.get_file_content(file_locations.weather_underground_config)
    luftdaten_config = app_generic_functions.get_file_content(file_locations.luftdaten_config)
    open_sense_map_config = app_generic_functions.get_file_content(file_locations.osm_config)
    return render_template("view_raw_configurations.html",
                           MainConfiguration=primary_config,
                           InstalledSensorsConfiguration=installed_sensors,
                           NetworkConfiguration=networking,
                           WiFiConfiguration=wifi,
                           TriggerConfiguration=trigger_variances,
                           SensorControlConfiguration=sensor_control_config,
                           WeatherUndergroundConfiguration=weather_underground_config,
                           LuftdatenConfiguration=luftdaten_config,
                           OpenSenseMapConfiguration=open_sense_map_config)
