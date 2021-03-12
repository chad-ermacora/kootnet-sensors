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
import re
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, get_list_of_filenames_in_dir
from operations_modules.sqlite_database import get_sqlite_tables_in_list
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from mqtt.server_mqtt_broker import check_mqtt_broker_server_running
from http_server.server_http_generic_functions import get_html_hidden_state, get_html_checkbox_state, \
    get_html_selected_state, message_and_return
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_main_routes import html_atpro_index

html_atpro_settings_routes = Blueprint("html_atpro_settings_routes", __name__)
db_v = app_cached_variables.database_variables


@html_atpro_settings_routes.route("/atpro/sensor-settings")
def html_atpro_sensor_settings(run_script="SelectSettingsNav('settings-main');"):
    return render_template("ATPro_admin/page_templates/settings.html", RunScript=run_script)


@html_atpro_settings_routes.route("/atpro/settings-main", methods=["GET", "POST"])
def html_atpro_sensor_settings_main():
    if request.method == "POST":
        try:
            app_config_access.primary_config.update_with_html_request(request)
            app_config_access.primary_config.save_config_to_file()
            app_cached_variables.restart_sensor_checkin_thread = True
            return html_atpro_sensor_settings()
        except Exception as error:
            logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
            return message_and_return("Bad Configuration POST Request", url="/MainConfigurationsHTML")
    debug_logging = get_html_checkbox_state(app_config_access.primary_config.enable_debug_logging)
    sensor_check_ins = get_html_checkbox_state(app_config_access.primary_config.enable_checkin)
    custom_temp_offset = get_html_checkbox_state(app_config_access.primary_config.enable_custom_temp)
    custom_temp_comp = get_html_checkbox_state(app_config_access.primary_config.enable_temperature_comp_factor)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-main.html",
        IPWebPort=app_config_access.primary_config.web_portal_port,
        CheckedDebug=debug_logging,
        HourOffset=app_config_access.primary_config.utc0_hour_offset,
        CheckedSensorCheckIns=sensor_check_ins,
        CheckinHours=app_config_access.primary_config.checkin_wait_in_hours,
        CheckinAddress=app_config_access.primary_config.checkin_url,
        CheckedCustomTempOffset=custom_temp_offset,
        temperature_offset=float(app_config_access.primary_config.temperature_offset),
        CheckedCustomTempComp=custom_temp_comp,
        CustomTempComp=float(app_config_access.primary_config.temperature_comp_factor)
    )


@html_atpro_settings_routes.route("/atpro/settings-is", methods=["GET", "POST"])
def html_atpro_sensor_settings_installed_sensors():
    installed_sensors = app_config_access.installed_sensors
    if request.method == "POST":
        try:
            app_config_access.installed_sensors.update_with_html_request(request)
            app_config_access.installed_sensors.save_config_to_file()
            sensor_access.sensors_direct.__init__()
            return html_atpro_index(run_script="SelectNav('sensor-settings');")
        except Exception as error:
            msg = "HTML Apply - Installed Sensors - Error: " + str(error)
            logger.primary_logger.error(msg)
            return render_template("ATPro_admin/page_templates/message_return.html",
                                   PageURL="/atpro/",
                                   TextMessage=msg)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-installed-sensors.html",
        PageURL="/MainConfigurationsHTML",
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
        PimoroniEnviro2=get_html_checkbox_state(installed_sensors.pimoroni_enviro2),
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
        PimoroniMonoOLED128x128BW=get_html_checkbox_state(installed_sensors.pimoroni_mono_oled_luma),
        SensirionSPS30=get_html_checkbox_state(installed_sensors.sensirion_sps30),
        W1ThermSensor=get_html_checkbox_state(installed_sensors.w1_therm_sensor)
    )


@html_atpro_settings_routes.route("/atpro/settings-display", methods=["GET", "POST"])
def html_atpro_sensor_settings_display():
    display = get_html_checkbox_state(app_config_access.display_config.enable_display)
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
    return render_template(
        "ATPro_admin/page_templates/settings/settings-display.html",
        PageURL="/DisplayConfigurationsHTML",
        CheckedEnableDisplay=display,
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
        DisplayGyroChecked=get_html_checkbox_state(gyroscope)
    )


@html_atpro_settings_routes.route("/atpro/settings-cs", methods=["GET", "POST"])
def html_atpro_sensor_settings_checkin_server():
    enable_checkin_recording = app_config_access.checkin_config.enable_checkin_recording
    return render_template(
        "ATPro_admin/page_templates/settings/settings-checkin-server.html",
        PageURL="/CheckinServerConfigurationHTML",
        CheckedEnableCheckin=get_html_checkbox_state(enable_checkin_recording),
        ContactInPastDays=app_config_access.checkin_config.count_contact_days,
        DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days
    )


@html_atpro_settings_routes.route("/atpro/settings-db-local")
def html_atpro_sensor_settings_database_information():
    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"

    db_backup_dropdown_selection = ""
    for zip_name in app_cached_variables.zipped_db_backup_list:
        db_backup_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", zip_name) + "\n"
    return render_template(
        "ATPro_admin/page_templates/settings/settings-db-local.html",
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=sensor_access.get_file_size(),
        NumberNotes=sensor_access.get_db_notes_count(),
        SQLMQTTDatabaseLocation=file_locations.mqtt_subscriber_database,
        SQLMQTTDatabaseSize=sensor_access.get_file_size(file_location=file_locations.mqtt_subscriber_database),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=file_locations.sensor_checkin_database,
        SQLCheckinDatabaseSize=sensor_access.get_file_size(file_location=file_locations.sensor_checkin_database),
        SQLCheckinSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        BackupDBOptionNames=db_backup_dropdown_selection
    )


@html_atpro_settings_routes.route("/atpro/settings-db-management", methods=["GET", "POST"])
def html_atpro_sensor_settings_database_management():
    if request.method == "POST":
        upload_db_folder = file_locations.uploaded_databases_folder + "/"

        try:
            db_full_path = upload_db_folder + str(request.form.get("db_selected"))
            if str(request.form.get("db_management")) == "rename_db":
                new_db_full_path = upload_db_folder + _get_clean_db_name(
                    str(request.form.get("rename_db")))
                os.rename(db_full_path, new_db_full_path)
            elif str(request.form.get("db_management")) == "delete_db":
                os.remove(db_full_path)
            uploaded_db_filenames = get_list_of_filenames_in_dir(file_locations.uploaded_databases_folder)
            app_cached_variables.uploaded_databases_list = uploaded_db_filenames
            return html_atpro_index(run_script="SelectNav('sensor-settings');")
        except Exception as error:
            return_text2 = str(error)
            logger.network_logger.error("Unable to rename or delete database: " + return_text2)
        return message_and_return("Unable to rename or delete database", text_message2=return_text2, url="/databases")

    custom_db_option_html_text = "<option value='{{ DBNameChangeMe }}'>{{ DBNameChangeMe }}</option>"
    db_dropdown_selection = ""
    for db_name in app_cached_variables.uploaded_databases_list:
        db_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", db_name) + "\n"

    db_backup_dropdown_selection = ""
    for zip_name in app_cached_variables.zipped_db_backup_list:
        db_backup_dropdown_selection += custom_db_option_html_text.replace("{{ DBNameChangeMe }}", zip_name) + "\n"
    return render_template(
        "ATPro_admin/page_templates/settings/settings-db-management.html",
        HostName=app_cached_variables.hostname,
        SQLDatabaseLocation=file_locations.sensor_database,
        SQLDatabaseDateRange=sensor_access.get_db_first_last_date(),
        SQLDatabaseSize=sensor_access.get_file_size(),
        NumberNotes=sensor_access.get_db_notes_count(),
        SQLMQTTDatabaseLocation=file_locations.mqtt_subscriber_database,
        SQLMQTTDatabaseSize=sensor_access.get_file_size(
            file_location=file_locations.mqtt_subscriber_database),
        SQLMQTTSensorsInDB=str(
            len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        SQLCheckinDatabaseLocation=file_locations.sensor_checkin_database,
        SQLCheckinDatabaseSize=sensor_access.get_file_size(
            file_location=file_locations.sensor_checkin_database),
        SQLCheckinSensorsInDB=str(
            len(get_sqlite_tables_in_list(file_locations.sensor_checkin_database))),
        UploadedDBOptionNames=db_dropdown_selection,
        BackupDBOptionNames=db_backup_dropdown_selection
    )


@html_atpro_settings_routes.route("/atpro/settings-db-uploads", methods=["GET", "POST"])
def html_atpro_sensor_settings_database_uploads():
    return render_template("ATPro_admin/page_templates/settings/settings-db-uploads.html")


@html_atpro_settings_routes.route("/atpro/settings-interval", methods=["GET", "POST"])
def html_atpro_sensor_settings_interval():
    interval_config = app_config_access.interval_recording_config
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-interval.html",
        PageURL="/MainConfigurationsHTML",
        CheckedInterval=get_html_checkbox_state(interval_config.enable_interval_recording),
        IntervalDelay=float(interval_config.sleep_duration_interval),
        CheckedSensorUptime=get_html_checkbox_state(interval_config.sensor_uptime_enabled),
        CheckedCPUTemperature=get_html_checkbox_state(interval_config.cpu_temperature_enabled),
        CheckedEnvTemperature=get_html_checkbox_state(interval_config.env_temperature_enabled),
        CheckedPressure=get_html_checkbox_state(interval_config.pressure_enabled),
        CheckedAltitude=get_html_checkbox_state(interval_config.altitude_enabled),
        CheckedHumidity=get_html_checkbox_state(interval_config.humidity_enabled),
        CheckedDewPoint=get_html_checkbox_state(interval_config.dew_point_enabled),
        CheckedDistance=get_html_checkbox_state(interval_config.distance_enabled),
        CheckedLumen=get_html_checkbox_state(interval_config.lumen_enabled),
        CheckedColour=get_html_checkbox_state(interval_config.colour_enabled),
        CheckedUltraViolet=get_html_checkbox_state(interval_config.ultra_violet_enabled),
        CheckedGas=get_html_checkbox_state(interval_config.gas_enabled),
        CheckedPM=get_html_checkbox_state(interval_config.particulate_matter_enabled),
        CheckedAccelerometer=get_html_checkbox_state(interval_config.accelerometer_enabled),
        CheckedMagnetometer=get_html_checkbox_state(interval_config.magnetometer_enabled),
        CheckedGyroscope=get_html_checkbox_state(interval_config.gyroscope_enabled)
    )


@html_atpro_settings_routes.route("/atpro/settings-hl", methods=["GET", "POST"])
def html_atpro_sensor_settings_high_low():
    high_low_settings = app_config_access.trigger_high_low
    recording_enabled = get_html_checkbox_state(high_low_settings.enable_high_low_trigger_recording)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-high-low.html",
        PageURL="/MainConfigurationsHTML",
        CheckedEnableHLTRecording=recording_enabled,
        CheckedCPUTemperature=get_html_checkbox_state(high_low_settings.cpu_temperature_enabled),
        TriggerLowCPUTemperature=high_low_settings.cpu_temperature_low,
        TriggerHighCPUTemperature=high_low_settings.cpu_temperature_high,
        SecondsCPUTemperature=high_low_settings.cpu_temperature_wait_seconds,
        CheckedEnvTemperature=get_html_checkbox_state(high_low_settings.env_temperature_enabled),
        TriggerLowEnvTemperature=high_low_settings.env_temperature_low,
        TriggerHighEnvTemperature=high_low_settings.env_temperature_high,
        SecondsEnvTemperature=high_low_settings.env_temperature_wait_seconds,
        CheckedPressure=get_html_checkbox_state(high_low_settings.pressure_enabled),
        TriggerLowPressure=high_low_settings.pressure_low,
        TriggerHighPressure=high_low_settings.pressure_high,
        SecondsPressure=high_low_settings.pressure_wait_seconds,
        CheckedAltitude=get_html_checkbox_state(high_low_settings.altitude_enabled),
        TriggerLowAltitude=high_low_settings.altitude_low,
        TriggerHighAltitude=high_low_settings.altitude_high,
        SecondsAltitude=high_low_settings.altitude_wait_seconds,
        CheckedHumidity=get_html_checkbox_state(high_low_settings.humidity_enabled),
        TriggerLowHumidity=high_low_settings.humidity_low,
        TriggerHighHumidity=high_low_settings.humidity_high,
        SecondsHumidity=high_low_settings.humidity_wait_seconds,
        CheckedDistance=get_html_checkbox_state(high_low_settings.distance_enabled),
        TriggerLowDistance=high_low_settings.distance_low,
        TriggerHighDistance=high_low_settings.distance_high,
        SecondsDistance=high_low_settings.distance_wait_seconds,
        CheckedLumen=get_html_checkbox_state(high_low_settings.lumen_enabled),
        TriggerLowLumen=high_low_settings.lumen_low,
        TriggerHighLumen=high_low_settings.lumen_high,
        SecondsLumen=high_low_settings.lumen_wait_seconds,
        CheckedColour=get_html_checkbox_state(high_low_settings.colour_enabled),
        TriggerLowRed=high_low_settings.red_low,
        TriggerHighRed=high_low_settings.red_high,
        TriggerLowOrange=high_low_settings.orange_low,
        TriggerHighOrange=high_low_settings.orange_high,
        TriggerLowYellow=high_low_settings.yellow_low,
        TriggerHighYellow=high_low_settings.yellow_high,
        TriggerLowGreen=high_low_settings.green_low,
        TriggerHighGreen=high_low_settings.green_high,
        TriggerLowBlue=high_low_settings.blue_low,
        TriggerHighBlue=high_low_settings.blue_high,
        TriggerLowViolet=high_low_settings.violet_low,
        TriggerHighViolet=high_low_settings.violet_high,
        SecondsColour=high_low_settings.colour_wait_seconds,
        CheckedUltraViolet=get_html_checkbox_state(high_low_settings.ultra_violet_enabled),
        TriggerLowUltraVioletA=high_low_settings.ultra_violet_a_low,
        TriggerHighUltraVioletA=high_low_settings.ultra_violet_a_high,
        TriggerLowUltraVioletB=high_low_settings.ultra_violet_b_low,
        TriggerHighUltraVioletB=high_low_settings.ultra_violet_b_high,
        SecondsUltraViolet=high_low_settings.ultra_violet_wait_seconds,
        CheckedGas=get_html_checkbox_state(high_low_settings.gas_enabled),
        TriggerLowGasIndex=high_low_settings.gas_resistance_index_low,
        TriggerHighGasIndex=high_low_settings.gas_resistance_index_high,
        TriggerLowGasOxidising=high_low_settings.gas_oxidising_low,
        TriggerHighGasOxidising=high_low_settings.gas_oxidising_high,
        TriggerLowGasReducing=high_low_settings.gas_reducing_low,
        TriggerHighGasReducing=high_low_settings.gas_reducing_high,
        TriggerLowGasNH3=high_low_settings.gas_nh3_low,
        TriggerHighGasNH3=high_low_settings.gas_nh3_high,
        SecondsGas=high_low_settings.gas_wait_seconds,
        CheckedPM=get_html_checkbox_state(high_low_settings.particulate_matter_enabled),
        TriggerLowPM1=high_low_settings.particulate_matter_1_low,
        TriggerHighPM1=high_low_settings.particulate_matter_1_high,
        TriggerLowPM25=high_low_settings.particulate_matter_2_5_low,
        TriggerHighPM25=high_low_settings.particulate_matter_2_5_high,
        TriggerLowPM4=high_low_settings.particulate_matter_4_low,
        TriggerHighPM4=high_low_settings.particulate_matter_4_high,
        TriggerLowPM10=high_low_settings.particulate_matter_10_low,
        TriggerHighPM10=high_low_settings.particulate_matter_10_high,
        SecondsPM=high_low_settings.particulate_matter_wait_seconds,
        CheckedAccelerometer=get_html_checkbox_state(high_low_settings.accelerometer_enabled),
        TriggerLowAccelerometerX=high_low_settings.accelerometer_x_low,
        TriggerHighAccelerometerX=high_low_settings.accelerometer_x_high,
        TriggerLowAccelerometerY=high_low_settings.accelerometer_y_low,
        TriggerHighAccelerometerY=high_low_settings.accelerometer_y_high,
        TriggerLowAccelerometerZ=high_low_settings.accelerometer_z_low,
        TriggerHighAccelerometerZ=high_low_settings.accelerometer_z_high,
        SecondsAccelerometer=high_low_settings.accelerometer_wait_seconds,
        CheckedMagnetometer=get_html_checkbox_state(high_low_settings.magnetometer_enabled),
        TriggerLowMagnetometerX=high_low_settings.magnetometer_x_low,
        TriggerHighMagnetometerX=high_low_settings.magnetometer_x_high,
        TriggerLowMagnetometerY=high_low_settings.magnetometer_y_low,
        TriggerHighMagnetometerY=high_low_settings.magnetometer_y_high,
        TriggerLowMagnetometerZ=high_low_settings.magnetometer_z_low,
        TriggerHighMagnetometerZ=high_low_settings.magnetometer_z_high,
        SecondsMagnetometer=high_low_settings.magnetometer_wait_seconds,
        CheckedGyroscope=get_html_checkbox_state(high_low_settings.gyroscope_enabled),
        TriggerLowGyroscopeX=high_low_settings.gyroscope_x_low,
        TriggerHighGyroscopeX=high_low_settings.gyroscope_x_high,
        TriggerLowGyroscopeY=high_low_settings.gyroscope_y_low,
        TriggerHighGyroscopeY=high_low_settings.gyroscope_y_high,
        TriggerLowGyroscopeZ=high_low_settings.gyroscope_z_low,
        TriggerHighGyroscopeZ=high_low_settings.gyroscope_z_high,
        SecondsGyroscope=high_low_settings.gyroscope_wait_seconds
    )


@html_atpro_settings_routes.route("/atpro/settings-variances", methods=["GET", "POST"])
def html_atpro_sensor_settings_variances():
    variances = app_config_access.trigger_variances
    return render_template(
        "ATPro_admin/page_templates/settings/settings-recording-variances.html",
        PageURL="/MainConfigurationsHTML",
        CheckedTrigger=get_html_checkbox_state(variances.enable_trigger_variance),
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
        TriggerPM4=variances.particulate_matter_4_variance,
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
        SecondsGyroscope=variances.gyroscope_wait_seconds
    )


@html_atpro_settings_routes.route("/atpro/settings-email-reports", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_reports():
    return render_template("ATPro_admin/page_templates/settings/settings-email-reports.html")


@html_atpro_settings_routes.route("/atpro/settings-email-graphs", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_graphs():
    return render_template("ATPro_admin/page_templates/settings/settings-email-graphs.html")


@html_atpro_settings_routes.route("/atpro/settings-email-settings", methods=["GET", "POST"])
def html_atpro_sensor_settings_email_smtp():
    return render_template("ATPro_admin/page_templates/settings/settings-email-smtp.html")


@html_atpro_settings_routes.route("/atpro/settings-mqtt-p", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_publisher():
    replacement_values = app_config_access.mqtt_publisher_config.get_mqtt_replacements_dictionary()
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-publisher.html",
        SystemHostname=replacement_values[db_v.sensor_name],
        SystemIP=replacement_values[db_v.ip],
        SystemUptime=replacement_values[db_v.sensor_uptime],
        SystemDateTime=replacement_values[db_v.all_tables_datetime],
        SystemTemperature=replacement_values[db_v.system_temperature],
        EnvTemperature=replacement_values[db_v.env_temperature],
        Pressure=replacement_values[db_v.pressure],
        Altitude=replacement_values[db_v.altitude],
        Humidity=replacement_values[db_v.humidity],
        Distance=replacement_values[db_v.distance],
        Lumen=replacement_values[db_v.lumen],
        Red=replacement_values[db_v.red],
        Orange=replacement_values[db_v.orange],
        Yellow=replacement_values[db_v.yellow],
        Green=replacement_values[db_v.green],
        Blue=replacement_values[db_v.blue],
        Violet=replacement_values[db_v.violet],
        UVIndex=replacement_values[db_v.ultra_violet_index],
        UVA=replacement_values[db_v.ultra_violet_a],
        UVB=replacement_values[db_v.ultra_violet_b],
        GASRI=replacement_values[db_v.gas_resistance_index],
        GASOxidising=replacement_values[db_v.gas_oxidising],
        GASReducing=replacement_values[db_v.gas_reducing],
        GASNH3=replacement_values[db_v.gas_nh3],
        PM1=replacement_values[db_v.particulate_matter_1],
        PM2_5=replacement_values[db_v.particulate_matter_2_5],
        PM4=replacement_values[db_v.particulate_matter_4],
        PM10=replacement_values[db_v.particulate_matter_10],
        AccelerometerX=replacement_values[db_v.acc_x],
        AccelerometerY=replacement_values[db_v.acc_y],
        AccelerometerZ=replacement_values[db_v.acc_z],
        MagnetometerX=replacement_values[db_v.mag_x],
        MagnetometerY=replacement_values[db_v.mag_y],
        MagnetometerZ=replacement_values[db_v.mag_z],
        GyroscopeX=replacement_values[db_v.gyro_x],
        GyroscopeY=replacement_values[db_v.gyro_y],
        GyroscopeZ=replacement_values[db_v.gyro_z]
    )


@html_atpro_settings_routes.route("/atpro/settings-mqtt-s", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_subscriber():
    mqtt_qos = app_config_access.mqtt_subscriber_config.mqtt_subscriber_qos
    qos_level_0 = ""
    qos_level_1 = ""
    qos_level_2 = ""
    if mqtt_qos == 0:
        qos_level_0 = get_html_selected_state(True)
    elif mqtt_qos == 1:
        qos_level_1 = get_html_selected_state(True)
    elif mqtt_qos == 2:
        qos_level_2 = get_html_selected_state(True)

    enable_mqtt_subscriber = app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber
    enable_mqtt_sql_recording = app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording
    enable_broker_auth = app_config_access.mqtt_subscriber_config.enable_broker_auth
    csv_mqtt_topics = ""
    for topic in app_config_access.mqtt_subscriber_config.subscribed_topics_list:
        csv_mqtt_topics += topic + ","
    csv_mqtt_topics = csv_mqtt_topics[:-1]
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-subscriber.html",
        PageURL="/MQTTConfigurationsHTML",
        MQTTSubscriberChecked=get_html_checkbox_state(enable_mqtt_subscriber),
        MQTTSQLRecordingChecked=get_html_checkbox_state(enable_mqtt_sql_recording),
        MQTTSubDatabaseSize=sensor_access.get_file_size(file_locations.mqtt_subscriber_database),
        MQTTBrokerAddress=app_config_access.mqtt_subscriber_config.broker_address,
        MQTTBrokerPort=str(app_config_access.mqtt_subscriber_config.broker_server_port),
        MQTTQoSLevel0=qos_level_0,
        MQTTQoSLevel1=qos_level_1,
        MQTTQoSLevel2=qos_level_2,
        MQTTSubscriberAuthChecked=get_html_checkbox_state(enable_broker_auth),
        MQTTSubscriberUsername=app_config_access.mqtt_subscriber_config.broker_user,
        SubscriberTopics=csv_mqtt_topics
    )


@html_atpro_settings_routes.route("/atpro/settings-mqtt-b", methods=["GET", "POST"])
def html_atpro_sensor_settings_mqtt_broker():
    mosquitto_configuration = ""
    if os.path.isfile(file_locations.mosquitto_configuration):
        mosquitto_configuration = get_file_content(file_locations.mosquitto_configuration)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-mqtt-broker.html",
        PageURL="/MQTTConfigurationsHTML",
        BrokerServerChecked=get_html_checkbox_state(check_mqtt_broker_server_running()),
        BrokerMosquittoConfig=mosquitto_configuration
    )


@html_atpro_settings_routes.route("/atpro/settings-osm", methods=["GET", "POST"])
def html_atpro_sensor_settings_osm():
    osm_disabled = "disabled"
    osm_enable_checked = ""
    if app_config_access.open_sense_map_config.open_sense_map_enabled:
        osm_enable_checked = "checked"
        osm_disabled = ""
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-osm.html",
        PageURL="/3rdPartyConfigurationsHTML",
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
        OSMPM4ID=app_config_access.open_sense_map_config.pm4_id,
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
        OSMUVBID=app_config_access.open_sense_map_config.ultra_violet_b_id
    )


@html_atpro_settings_routes.route("/atpro/settings-wu", methods=["GET", "POST"])
def html_atpro_sensor_settings_wu():
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
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-wu.html",
        PageURL="/3rdPartyConfigurationsHTML",
        CheckedWUEnabled=wu_checked,
        CheckedWURapidFire=wu_rapid_fire_checked,
        DisabledWURapidFire=wu_rapid_fire_disabled,
        WUIntervalSeconds=wu_interval_seconds,
        DisabledWUInterval=wu_interval_seconds_disabled,
        CheckedWUOutdoor=wu_outdoor,
        DisabledWUOutdoor=wu_outdoor_disabled,
        DisabledStationID=wu_station_id_disabled,
        WUStationID=wu_station_id,
        DisabledStationKey=wu_station_key_disabled
    )


@html_atpro_settings_routes.route("/atpro/settings-luftdaten", methods=["GET", "POST"])
def html_atpro_sensor_settings_luftdaten():
    luftdaten_checked = get_html_checkbox_state(app_config_access.luftdaten_config.luftdaten_enabled)

    luftdaten_interval_seconds = app_config_access.luftdaten_config.interval_seconds
    luftdaten_station_id = app_config_access.luftdaten_config.station_id
    return render_template(
        "ATPro_admin/page_templates/settings/settings-3rd-p-luftdaten.html",
        PageURL="/3rdPartyConfigurationsHTML",
        CheckedLuftdatenEnabled=luftdaten_checked,
        LuftdatenIntervalSeconds=luftdaten_interval_seconds,
        LuftdatenStationID=luftdaten_station_id
    )

# @html_atpro_settings_routes.route("/atpro/settings-Change", methods=["GET", "POST"])
# def html_atpro_sensor_settings_():
#     return "timmy"


def _get_clean_db_name(db_text_name):
    final_db_name = ""
    for letter in db_text_name:
        if re.match("^[A-Za-z0-9_.-]*$", letter):
            final_db_name += letter

    if final_db_name == "":
        final_db_name = "No_Name"

    if final_db_name.split(".")[-1] == "sqlite":
        final_db_name = final_db_name[:-7]

    count_num = 1
    if final_db_name + ".sqlite" in app_cached_variables.uploaded_databases_list:
        while final_db_name + str(count_num) + ".sqlite" in app_cached_variables.uploaded_databases_list:
            count_num += 1
        final_db_name = final_db_name + str(count_num)
    return final_db_name + ".sqlite"
