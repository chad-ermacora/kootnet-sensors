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
from datetime import datetime
from time import strftime
from threading import Thread
from flask import render_template
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import file_locations
from operations_modules import network_ip
from http_server import server_http_sensor_control
from http_server.server_http_flask_post_checks import get_html_checkbox_state


class CreateRenderTemplates:
    def __init__(self, sensor_access):
        self.sensor_access = sensor_access

    @staticmethod
    def index_page():
        return render_template("index.html", HostName=app_cached_variables.hostname)

    @staticmethod
    def message_and_return(return_message, text_message2="", url="/", special_command=""):
        return render_template("message_return.html",
                               TextMessage=return_message,
                               TextMessage2=text_message2,
                               CloseWindow=special_command,
                               URL=url)

    @staticmethod
    def multi_sensor_management(request_type="normal_get", address_list=None):
        radio_checked_online_status = ""
        radio_checked_systems_report = ""
        radio_checked_config_report = ""
        if app_config_access.sensor_control_config.default_action == "online_status":
            radio_checked_online_status = "checked"
        if app_config_access.sensor_control_config.default_action == "systems_report":
            radio_checked_systems_report = "checked"
        if app_config_access.sensor_control_config.default_action == "config_report":
            radio_checked_config_report = "checked"

        sensors_bg_colour_list = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

        if request_type == "online_status":
            new_sensors_responses = []
            threads = []

            for address in address_list:
                if address == "Invalid":
                    new_sensors_responses.append(["bad", "bad"])
                else:
                    threads.append(Thread(target=server_http_sensor_control.check_online_status, args=[address]))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            while not app_cached_variables.data_queue.empty():
                new_sensors_responses.append(app_cached_variables.data_queue.get())
                app_cached_variables.data_queue.task_done()

            count = 0
            for address in address_list:
                for response in new_sensors_responses:
                    if address == response[0]:
                        sensors_bg_colour_list[count] = response[1]
                count += 1
        elif request_type == "systems_report":
            pass
        elif request_type == "config_report":
            pass

        return render_template("multi_manage_sensors.html",
                               CheckedOnlineStatus=radio_checked_online_status,
                               CheckedSystemReports=radio_checked_systems_report,
                               CheckedConfigReports=radio_checked_config_report,
                               SensorIP1=app_config_access.sensor_control_config.sensor_ip_dns1,
                               SensorIP2=app_config_access.sensor_control_config.sensor_ip_dns2,
                               SensorIP3=app_config_access.sensor_control_config.sensor_ip_dns3,
                               SensorIP4=app_config_access.sensor_control_config.sensor_ip_dns4,
                               SensorIP5=app_config_access.sensor_control_config.sensor_ip_dns5,
                               SensorIP6=app_config_access.sensor_control_config.sensor_ip_dns6,
                               SensorIP7=app_config_access.sensor_control_config.sensor_ip_dns7,
                               SensorIP8=app_config_access.sensor_control_config.sensor_ip_dns8,
                               SensorIP9=app_config_access.sensor_control_config.sensor_ip_dns9,
                               SensorIP10=app_config_access.sensor_control_config.sensor_ip_dns10,
                               SensorIP11=app_config_access.sensor_control_config.sensor_ip_dns11,
                               SensorIP12=app_config_access.sensor_control_config.sensor_ip_dns12,
                               SensorIP13=app_config_access.sensor_control_config.sensor_ip_dns13,
                               SensorIP14=app_config_access.sensor_control_config.sensor_ip_dns14,
                               SensorIP15=app_config_access.sensor_control_config.sensor_ip_dns15,
                               SensorIP16=app_config_access.sensor_control_config.sensor_ip_dns16,
                               SensorIP17=app_config_access.sensor_control_config.sensor_ip_dns17,
                               SensorIP18=app_config_access.sensor_control_config.sensor_ip_dns18,
                               SensorIP19=app_config_access.sensor_control_config.sensor_ip_dns19,
                               SensorIP20=app_config_access.sensor_control_config.sensor_ip_dns20,
                               SensorIP1BGColour=sensors_bg_colour_list[0],
                               SensorIP2BGColour=sensors_bg_colour_list[1],
                               SensorIP3BGColour=sensors_bg_colour_list[2],
                               SensorIP4BGColour=sensors_bg_colour_list[3],
                               SensorIP5BGColour=sensors_bg_colour_list[4],
                               SensorIP6BGColour=sensors_bg_colour_list[5],
                               SensorIP7BGColour=sensors_bg_colour_list[6],
                               SensorIP8BGColour=sensors_bg_colour_list[7],
                               SensorIP9BGColour=sensors_bg_colour_list[8],
                               SensorIP10BGColour=sensors_bg_colour_list[9],
                               SensorIP11BGColour=sensors_bg_colour_list[10],
                               SensorIP12BGColour=sensors_bg_colour_list[11],
                               SensorIP13BGColour=sensors_bg_colour_list[12],
                               SensorIP14BGColour=sensors_bg_colour_list[13],
                               SensorIP15BGColour=sensors_bg_colour_list[14],
                               SensorIP16BGColour=sensors_bg_colour_list[15],
                               SensorIP17BGColour=sensors_bg_colour_list[16],
                               SensorIP18BGColour=sensors_bg_colour_list[17],
                               SensorIP19BGColour=sensors_bg_colour_list[18],
                               SensorIP20BGColour=sensors_bg_colour_list[19])

    @staticmethod
    def system_management():
        return render_template("system_commands.html")

    @staticmethod
    def view_https_config_diagnostics():
        main_config = app_generic_functions.get_file_content(file_locations.main_config)
        installed_sensors = app_generic_functions.get_file_content(file_locations.installed_sensors_config)
        networking = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file)
        wifi = app_generic_functions.get_file_content(file_locations.wifi_config_file)
        trigger_variances = app_generic_functions.get_file_content(file_locations.trigger_variances_config)
        sensor_control_config = app_generic_functions.get_file_content(file_locations.html_sensor_control_config)
        weather_underground_config = app_generic_functions.get_file_content(file_locations.weather_underground_config)
        luftdaten_config = app_generic_functions.get_file_content(file_locations.luftdaten_config)
        open_sense_map_config = app_generic_functions.get_file_content(file_locations.osm_config)

        return render_template("http_diagnostics_configurations.html",
                               MainConfiguration=main_config,
                               InstalledSensorsConfiguration=installed_sensors,
                               NetworkConfiguration=networking,
                               WiFiConfiguration=wifi,
                               TriggerConfiguration=trigger_variances,
                               SensorControlConfiguration=sensor_control_config,
                               WeatherUndergroundConfiguration=weather_underground_config,
                               LuftdatenConfiguration=luftdaten_config,
                               OpenSenseMapConfiguration=open_sense_map_config)

    @staticmethod
    def sensor_online_services(weather_underground_config, luftdaten_config):
        wu_checked = get_html_checkbox_state(weather_underground_config.weather_underground_enabled)
        wu_rapid_fire_checked = get_html_checkbox_state(weather_underground_config.wu_rapid_fire_enabled)
        wu_rapid_fire_disabled = "disabled"
        wu_interval_seconds_disabled = "disabled"
        wu_outdoor_disabled = "disabled"
        wu_station_id_disabled = "disabled"
        wu_station_key_disabled = "disabled"
        if weather_underground_config.weather_underground_enabled:
            wu_rapid_fire_disabled = ""
            wu_interval_seconds_disabled = ""
            wu_outdoor_disabled = ""
            wu_station_id_disabled = ""
            wu_station_key_disabled = ""

        wu_interval_seconds = weather_underground_config.interval_seconds
        wu_outdoor = get_html_checkbox_state(weather_underground_config.outdoor_sensor)
        wu_station_id = weather_underground_config.station_id

        luftdaten_checked = get_html_checkbox_state(luftdaten_config.luftdaten_enabled)
        luftdaten_interval_seconds_disabled = "disabled"
        if luftdaten_config.luftdaten_enabled:
            luftdaten_interval_seconds_disabled = ""

        luftdaten_interval_seconds = luftdaten_config.interval_seconds
        luftdaten_station_id = luftdaten_config.station_id

        return render_template("sensor_online_services.html",
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
                               LuftdatenStationID=luftdaten_station_id)

    @staticmethod
    def logout():
        return render_template("message_return.html",
                               TextMessage="Logout OK.  Returning to Home.",
                               URL="/"), 401

    def system_information(self):
        if app_config_access.current_config.enable_debug_logging:
            debug_logging = True
        else:
            debug_logging = False

        if app_config_access.current_config.enable_display:
            display_enabled = True
        else:
            display_enabled = False

        if app_config_access.current_config.enable_interval_recording:
            interval_recording = True
        else:
            interval_recording = False

        if app_config_access.current_config.enable_trigger_recording:
            trigger_recording = True
        else:
            trigger_recording = False

        if app_config_access.current_config.enable_custom_temp:
            custom_temp_enabled = True
        else:
            custom_temp_enabled = False

        return render_template("sensor_information.html",
                               HostName=app_cached_variables.hostname,
                               IPAddress=app_cached_variables.ip,
                               OSVersion=app_cached_variables.operating_system_name,
                               KootnetVersion=app_config_access.software_version.version,
                               LastUpdated=app_cached_variables.program_last_updated,
                               DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                               SystemUptime=self.sensor_access.get_uptime_str(),
                               SensorReboots=app_cached_variables.reboot_count,
                               CPUTemperature=self.sensor_access.get_cpu_temperature(),
                               RAMUsage=self.sensor_access.get_memory_usage_percent(),
                               DiskUsage=self.sensor_access.get_disk_usage_percent(),
                               DebugLogging=debug_logging,
                               SupportedDisplay=display_enabled,
                               IntervalRecording=interval_recording,
                               IntervalDelay=app_config_access.current_config.sleep_duration_interval,
                               TriggerRecording=trigger_recording,
                               ManualTemperatureEnabled=custom_temp_enabled,
                               CurrentTemperatureOffset=app_config_access.current_config.temperature_offset,
                               InstalledSensors=app_config_access.installed_sensors.get_installed_names_str(),
                               SQLDatabaseLocation=file_locations.sensor_database,
                               SQLDatabaseDateRange=self.sensor_access.get_db_first_last_date(),
                               SQLDatabaseSize=self.sensor_access.get_db_size(),
                               NumberNotes=self.sensor_access.get_db_notes_count())

    def sensors_readings(self):
        raw_temp = self.sensor_access.get_sensor_temperature()
        temp_offset = app_config_access.current_config.temperature_offset
        try:
            adjusted_temp = round(raw_temp + temp_offset, 2)
        except Exception as error:
            logger.network_logger.error("Failed to calculate Adjusted Env Temp: " + str(error))
            adjusted_temp = "Calc Error"
        red, orange, yellow, green, blue, violet = self._get_ems_for_render_template()

        return render_template("sensor_readings.html",
                               HostName=app_cached_variables.hostname,
                               IPAddress=app_cached_variables.ip,
                               DateTime=strftime("%Y-%m-%d %H:%M - %Z"),
                               SystemUptime=self.sensor_access.get_uptime_str(),
                               CPUTemperature=self.sensor_access.get_cpu_temperature(),
                               RAWEnvTemperature=raw_temp,
                               AdjustedEnvTemperature=adjusted_temp,
                               EnvTemperatureOffset=temp_offset,
                               Pressure=self.sensor_access.get_pressure(),
                               Altitude=self.sensor_access.get_altitude(),
                               Humidity=self.sensor_access.get_humidity(),
                               Distance=self.sensor_access.get_distance(),
                               GasResistanceIndex=self.sensor_access.get_gas_resistance_index(),
                               GasOxidising=self.sensor_access.get_gas_oxidised(),
                               GasReducing=self.sensor_access.get_gas_reduced(),
                               GasNH3=self.sensor_access.get_gas_nh3(),
                               PM1=self.sensor_access.get_particulate_matter_1(),
                               PM25=self.sensor_access.get_particulate_matter_2_5(),
                               PM10=self.sensor_access.get_particulate_matter_10(),
                               Lumen=self.sensor_access.get_lumen(),
                               Red=red,
                               Orange=orange,
                               Yellow=yellow,
                               Green=green,
                               Blue=blue,
                               Violet=violet,
                               UVA=self.sensor_access.get_ultra_violet_a(),
                               UVB=self.sensor_access.get_ultra_violet_b(),
                               Acc=self.sensor_access.get_accelerometer_xyz(),
                               Mag=self.sensor_access.get_magnetometer_xyz(),
                               Gyro=self.sensor_access.get_gyroscope_xyz())

    def _get_ems_for_render_template(self):
        ems = self.sensor_access.get_ems()
        if ems == "NoSensor":
            red = "NoSensor"
            orange = "NoSensor"
            yellow = "NoSensor"
            green = "NoSensor"
            blue = "NoSensor"
            violet = "NoSensor"
        else:
            if len(ems) > 3:
                red = ems[0]
                orange = ems[1]
                yellow = ems[2]
                green = ems[3]
                blue = ems[4]
                violet = ems[5]
            else:
                red = ems[0]
                orange = "NoSensor"
                yellow = "NoSensor"
                green = ems[1]
                blue = ems[2]
                violet = "NoSensor"
        return [red, orange, yellow, green, blue, violet]

    @staticmethod
    def edit_configurations():
        try:
            variances = app_config_access.trigger_variances

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
            dhcpcd_lines = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file).split("\n")
            if network_ip.check_for_dhcp(dhcpcd_lines):
                dhcp_checkbox = "checked"
                ip_disabled = "disabled"
                subnet_disabled = "disabled"
                gateway_disabled = "disabled"
                dns1_disabled = "disabled"
                dns2_disabled = "disabled"

            if app_cached_variables.wifi_security_type is None or app_cached_variables.wifi_security_type == "WPA-PSK":
                wifi_security_type_wpa1 = "checked"
                wifi_security_type_none1 = ""
            else:
                wifi_security_type_wpa1 = ""
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
                                   GnuLinux=get_html_checkbox_state(app_config_access.installed_sensors.linux_system),
                                   RaspberryPi=get_html_checkbox_state(
                                       app_config_access.installed_sensors.raspberry_pi),
                                   SenseHAT=get_html_checkbox_state(
                                       app_config_access.installed_sensors.raspberry_pi_sense_hat),
                                   PimoroniBH1745=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_bh1745),
                                   PimoroniAS7262=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_as7262),
                                   PimoroniBMP280=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_bmp280),
                                   PimoroniBME680=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_bme680),
                                   PimoroniEnviroPHAT=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_enviro),
                                   PimoroniEnviroPlus=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_enviroplus),
                                   PimoroniPMS5003=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_pms5003),
                                   PimoroniLSM303D=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_lsm303d),
                                   PimoroniICM20948=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_icm20948),
                                   PimoroniVL53L1X=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_vl53l1x),
                                   PimoroniLTR559=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_ltr_559),
                                   PimoroniVEML6075=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_veml6075),
                                   Pimoroni11x7LEDMatrix=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_matrix_11x7),
                                   PimoroniSPILCD10_96=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_st7735),
                                   PimoroniMonoOLED128x128BW=get_html_checkbox_state(
                                       app_config_access.installed_sensors.pimoroni_mono_oled_luma),
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
            return render_template("message_return.html",
                                   message2="Unable to Display Configurations...")

    def get_log_view(self):
        primary_log_lines = logger.get_number_of_log_entries(file_locations.primary_log)
        network_log_lines = logger.get_number_of_log_entries(file_locations.network_log)
        sensors_log_lines = logger.get_number_of_log_entries(file_locations.sensors_log)
        return render_template("log_view.html",
                               LogURL="/GetLogsHTML",
                               PrimaryLog=logger.get_sensor_log(file_locations.primary_log),
                               PrimaryLogLinesText=self._get_log_view_message(primary_log_lines),
                               NetworkLog=logger.get_sensor_log(file_locations.network_log),
                               NetworkLogLinesText=self._get_log_view_message(network_log_lines),
                               SensorsLog=logger.get_sensor_log(file_locations.sensors_log),
                               SensorsLogLinesText=self._get_log_view_message(sensors_log_lines))

    @staticmethod
    def _get_log_view_message(log_lines_length):
        if log_lines_length:
            if logger.max_log_lines_return > log_lines_length:
                text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
            else:
                text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = "0/0"
        return text_log_entries_return

    @staticmethod
    def plotly_graph_main():
        try:
            interval_plotly_file_creation_date_unix = os.path.getmtime(file_locations.save_plotly_html_to +
                                                                       file_locations.interval_plotly_html_filename)
            interval_creation_date = str(datetime.fromtimestamp(interval_plotly_file_creation_date_unix))[:-7]
        except Exception as error:
            logger.primary_logger.debug("No Interval Plotly file created: " + str(error))
            interval_creation_date = "No Plotly Graph Found"

        try:
            triggers_plotly_file_creation_date_unix = os.path.getmtime(file_locations.save_plotly_html_to +
                                                                       file_locations.triggers_plotly_html_filename)
            triggers_creation_date = str(datetime.fromtimestamp(triggers_plotly_file_creation_date_unix))[:-7]
        except Exception as error:
            logger.primary_logger.debug("No Triggers Plotly file: " + str(error))
            triggers_creation_date = "No Plotly Graph Found"

        return render_template("plotly_graph.html",
                               IntervalPlotlyCreationDate=interval_creation_date,
                               TriggerPlotlyCreationDate=triggers_creation_date)

    @staticmethod
    def help_file():
        return render_template("sensor_helpfile.html")
