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
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import write_file_to_disk
from configuration_modules import app_config_access
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_urls import CreateURLConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_sensor_offsets import CreateSensorOffsetsConfiguration
from configuration_modules.config_check_ins import CreateCheckinConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications
from sensor_modules import sensor_access


def remote_management_receive_configuration(request):
    config_type = str(request.form.get("config_selection"))
    new_config_str = str(request.form.get("new_config_str")).strip()
    logger.network_logger.info("* Received Push Configuration '" + config_type + "' from " + str(request.remote_addr))

    restart_hw_sensors = False
    if config_type == "primary":
        config_instance = CreatePrimaryConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Main")
        if new_config is not None:
            app_config_access.primary_config = new_config
            app_cached_variables.restart_automatic_upgrades_thread = True
    elif config_type == "urls":
        config_instance = CreateURLConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "URLs")
        if new_config is not None:
            app_config_access.urls_config = new_config
            app_cached_variables.restart_automatic_upgrades_thread = True
    elif config_type == "installed_sensors":
        config_instance = CreateInstalledSensorsConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Installed Sensors")
        if new_config is not None:
            app_config_access.installed_sensors = new_config
            restart_hw_sensors = True
    elif config_type == "sensor_offsets":
        config_instance = CreateSensorOffsetsConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Sensor Offsets")
        if new_config is not None:
            app_config_access.sensor_offsets = new_config
    elif config_type == "checkins":
        config_instance = CreateCheckinConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Checkins")
        if new_config is not None:
            app_config_access.checkin_config = new_config
            app_cached_variables.restart_sensor_checkin_thread = True
    elif config_type == "interval_recording":
        config_instance = CreateIntervalRecordingConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Interval Recording")
        if new_config is not None:
            app_config_access.interval_recording_config = new_config
            app_cached_variables.restart_interval_recording_thread = True
    elif config_type == "variance_trigger_recording":
        config_instance = CreateTriggerVariancesConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Trigger Variance Recording")
        if new_config is not None:
            app_config_access.trigger_variances = new_config
            atpro_notifications.manage_service_restart()
    elif config_type == "high_low_recording":
        config_instance = CreateTriggerHighLowConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Trigger High/Low Recording")
        if new_config is not None:
            app_config_access.trigger_high_low = new_config
            atpro_notifications.manage_service_restart()
    elif config_type == "display":
        config_instance = CreateDisplayConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Display")
        if new_config is not None:
            app_config_access.display_config = new_config
            app_cached_variables.restart_mini_display_thread = True
    elif config_type == "email":
        config_instance = CreateEmailConfiguration(load_from_file=False)
        new_config = _apply_config(config_instance, new_config_str, "Email")
        if new_config is not None:
            app_config_access.email_config = new_config
            app_cached_variables.restart_report_email_thread = True
            app_cached_variables.restart_graph_email_thread = True
    elif config_type == "open_sense_map":
        app_config_access.open_sense_map_config.open_sense_map_enabled = _get_3rd_party_active_state(request)
        app_config_access.open_sense_map_config.interval_seconds = _get_3rd_party_interval(request)
        app_config_access.open_sense_map_config.update_configuration_settings_list()
        app_config_access.open_sense_map_config.save_config_to_file()
        app_cached_variables.restart_open_sense_map_thread = True
        logger.network_logger.info("Applied Open Sense Map configuration push successfully")
    elif config_type == "weather_underground":
        app_config_access.weather_underground_config.weather_underground_enabled = _get_3rd_party_active_state(request)
        app_config_access.weather_underground_config.interval_seconds = _get_3rd_party_interval(request)
        app_config_access.weather_underground_config.update_configuration_settings_list()
        app_config_access.weather_underground_config.save_config_to_file()
        app_cached_variables.restart_weather_underground_thread = True
        logger.network_logger.info("Applied Weather Underground configuration push successfully")
    elif config_type == "luftdaten":
        app_config_access.luftdaten_config.luftdaten_enabled = _get_3rd_party_active_state(request)
        app_config_access.luftdaten_config.interval_seconds = _get_3rd_party_interval(request)
        app_config_access.luftdaten_config.update_configuration_settings_list()
        app_config_access.luftdaten_config.save_config_to_file()
        app_cached_variables.restart_luftdaten_thread = True
        logger.network_logger.info("Applied Luftdaten configuration push successfully")
    elif config_type == "wifi":
        if app_cached_variables.running_with_root:
            write_file_to_disk(file_locations.wifi_config_file, new_config_str.strip())
            atpro_notifications.manage_service_restart()
        else:
            logger.primary_logger.warning("Wifi set skipped, not running with root")
    elif config_type == "network":
        if app_cached_variables.running_with_root:
            write_file_to_disk(file_locations.dhcpcd_config_file, new_config_str.strip())
            atpro_notifications.manage_service_restart()
        else:
            logger.primary_logger.warning("Network set skipped, not running with root")
    if restart_hw_sensors:
        # This also restarts most Kootnet Sensors 'servers' (recording for example)
        sensor_access.sensors_direct.__init__()
    return "Received"


def _apply_config(new_config_class_instance, configuration_str, config_name):
    try:
        if (len(configuration_str.split("\n")) - 1) == new_config_class_instance.valid_setting_count:
            new_config_class_instance.set_config_with_str(configuration_str)
            new_config_class_instance.update_configuration_settings_list()
            new_config_class_instance.save_config_to_file()
            logger.network_logger.info("Applied " + config_name + " configuration push successfully")
            return new_config_class_instance
        else:
            log_msg = " does not have a valid setting count - Sent from a different version of Kootnet Sensors?"
            logger.network_logger.warning("Remote Management - Configuration Receive: " + config_name + log_msg)
    except Exception as error:
        logger.network_logger.warning("Unable to set configuration " + str(config_name) + ": " + str(error))
    return None


def _get_3rd_party_active_state(request):
    service_enabled = request.form.get("enable_online_service")
    if service_enabled is not None:
        if service_enabled == "1":
            return 1
    return 0


def _get_3rd_party_interval(request):
    new_interval = request.form.get("online_service_interval")
    if new_interval is not None:
        try:
            new_interval = float(new_interval)
            if new_interval < 10.0:
                new_interval = 10.0
            return new_interval
        except Exception as error:
            logger.network_logger.warning("Remote Management - Set 3rd Party Interval: " + str(error))
    return 300.0
