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
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import atpro_notifications
from sensor_modules import sensor_access


def remote_management_receive_configuration(request):
    config_type = str(request.form.get("config_selection"))
    new_config_str = str(request.form.get("new_config_str")).strip()
    logger.network_logger.info("* Received Push Configuration '" + config_type + "' from " + str(request.remote_addr))
    initial_error_msg = "* Received Push Configuration "
    end_error_msg = " had an invalid # of entries, settings not applied"
    if config_type == "primary":
        new_config = CreatePrimaryConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.primary_config.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.primary_config = new_config
            app_cached_variables.restart_sensor_checkin_thread = True
            logger.network_logger.info("Applied Primary configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Primary'" + end_error_msg)
    elif config_type == "installed_sensors":
        new_config = CreateInstalledSensorsConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.installed_sensors.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.installed_sensors = new_config
            sensor_access.sensors_direct.__init__()
            logger.network_logger.info("Applied Installed Sensors configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Installed Sensors'" + end_error_msg)
    elif config_type == "interval_recording":
        new_config = CreateIntervalRecordingConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.interval_recording_config.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.interval_recording_config = new_config
            app_cached_variables.restart_interval_recording_thread = True
            logger.network_logger.info("Applied Interval SQL Recording configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Interval SQL Recording'" + end_error_msg)
    elif config_type == "variance_trigger_recording":
        new_config = CreateTriggerVariancesConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.trigger_variances.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.trigger_variances = new_config
            atpro_notifications.restart_service_enabled = 1
            logger.network_logger.info("Applied Trigger Variance SQL Recording configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Trigger Variance SQL Recording'" + end_error_msg)
    elif config_type == "high_low_recording":
        new_config = CreateTriggerHighLowConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.trigger_high_low.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.trigger_high_low = new_config
            atpro_notifications.restart_service_enabled = 1
            logger.network_logger.info("Applied Trigger High/Low SQL Recording configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Trigger High/Low SQL Recording'" + end_error_msg)
    elif config_type == "display":
        new_config = CreateDisplayConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.display_config.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.display_config = new_config
            app_cached_variables.restart_mini_display_thread = True
            logger.network_logger.info("Applied Display configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Display'" + end_error_msg)
    elif config_type == "email":
        new_config = CreateEmailConfiguration(load_from_file=False)
        if (len(new_config_str.split("\n")) - 1) == app_config_access.email_config.valid_setting_count:
            new_config.set_config_with_str(new_config_str)
            new_config.update_configuration_settings_list()
            new_config.save_config_to_file()
            app_config_access.email_config = new_config
            app_cached_variables.restart_report_email_thread = True
            app_cached_variables.restart_graph_email_thread = True
            logger.network_logger.info("Applied Email configuration push successfully")
        else:
            logger.network_logger.error(initial_error_msg + "'Email'" + end_error_msg)
    elif config_type == "open_sense_map":
        active_state = 0
        if request.form.get("enable_online_service") == "1":
            active_state = 1

        send_interval = 10.0
        if float(request.form.get("online_service_interval")) > send_interval:
            send_interval = float(request.form.get("online_service_interval"))
        if send_interval < 10.0:
            send_interval = 10.0

        app_config_access.open_sense_map_config.open_sense_map_enabled = active_state
        app_config_access.open_sense_map_config.interval_seconds = send_interval
        app_config_access.open_sense_map_config.update_configuration_settings_list()
        app_config_access.open_sense_map_config.save_config_to_file()
        app_cached_variables.restart_open_sense_map_thread = True
        logger.network_logger.info("Applied Open Sense Map configuration push successfully")
    elif config_type == "weather_underground":
        active_state = 0
        if request.form.get("enable_online_service") == "1":
            active_state = 1

        send_interval = 10.0
        if float(request.form.get("online_service_interval")) > send_interval:
            send_interval = float(request.form.get("online_service_interval"))
        if send_interval < 2.0:
            send_interval = 2.0

        app_config_access.weather_underground_config.weather_underground_enabled = active_state
        app_config_access.weather_underground_config.interval_seconds = send_interval
        app_config_access.weather_underground_config.update_configuration_settings_list()
        app_config_access.weather_underground_config.save_config_to_file()
        app_cached_variables.restart_weather_underground_thread = True
        logger.network_logger.info("Applied Weather Underground configuration push successfully")
    elif config_type == "luftdaten":
        active_state = 0
        if request.form.get("enable_online_service") == "1":
            active_state = 1

        send_interval = 10.0
        if float(request.form.get("online_service_interval")) > send_interval:
            send_interval = float(request.form.get("online_service_interval"))
        if send_interval < 10.0:
            send_interval = 10.0

        app_config_access.luftdaten_config.luftdaten_enabled = active_state
        app_config_access.luftdaten_config.interval_seconds = send_interval
        app_config_access.luftdaten_config.update_configuration_settings_list()
        app_config_access.luftdaten_config.save_config_to_file()
        app_cached_variables.restart_luftdaten_thread = True
        logger.network_logger.info("Applied Luftdaten configuration push successfully")
    elif config_type == "wifi":
        if app_config_access.running_with_root:
            write_file_to_disk(file_locations.wifi_config_file, new_config_str.strip())
            atpro_notifications.restart_service_enabled = 1
        else:
            logger.primary_logger.warning("Wifi set skipped, not running with root")
    elif config_type == "network":
        if app_config_access.running_with_root:
            write_file_to_disk(file_locations.dhcpcd_config_file, new_config_str.strip())
            atpro_notifications.restart_service_enabled = 1
        else:
            logger.primary_logger.warning("Network set skipped, not running with root")
    return "Received"
