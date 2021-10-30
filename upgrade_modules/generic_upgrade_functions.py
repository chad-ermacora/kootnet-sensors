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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_content, thread_function
from http_server.server_http_generic_functions import save_http_auth_to_file, default_http_flask_user, \
    default_http_flask_password
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_check_ins import CreateCheckinConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from configuration_modules.config_mqtt_broker import CreateMQTTBrokerConfiguration
from configuration_modules.config_mqtt_publisher import CreateMQTTPublisherConfiguration
from configuration_modules.config_mqtt_subscriber import CreateMQTTSubscriberConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration


def successful_upgrade_message(config_name="Generic"):
    logger.primary_logger.info("Successfully Upgraded " + str(config_name) + " Configuration")


def reset_flask_login_credentials(log_reset=True):
    if log_reset:
        logger.primary_logger.warning(" **** Web Portal Login Reset to Defaults ****")
    save_http_auth_to_file(default_http_flask_user, default_http_flask_password, logging_enabled=False)


def reset_primary_config(log_reset=True):
    """ Writes a default main configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Main Configuration Reset ****")
    CreatePrimaryConfiguration(load_from_file=False).save_config_to_file()


def reset_installed_sensors(log_reset=True):
    """ Writes a default installed sensor configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Installed Sensors Configuration Reset ****")
    CreateInstalledSensorsConfiguration(load_from_file=False).save_config_to_file()


def reset_display_config(log_reset=True):
    """ Writes a default Display configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Display Configuration Reset ****")
    CreateDisplayConfiguration(load_from_file=False).save_config_to_file()


def reset_checkin_config(log_reset=True):
    """ Writes a default Checkin configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Checkin Configuration Reset ****")
    CreateCheckinConfiguration(load_from_file=False).save_config_to_file()


def reset_interval_recording_config(log_reset=True):
    """ Writes a default Trigger Interval Recording configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Trigger Interval Recording Configuration Reset ****")
    CreateIntervalRecordingConfiguration(load_from_file=False).save_config_to_file()


def reset_trigger_high_low_config(log_reset=True):
    """ Writes a default Trigger High/Low configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Trigger High/Low Configuration Reset ****")
    CreateTriggerHighLowConfiguration(load_from_file=False).save_config_to_file()


def reset_trigger_variance_config(log_reset=True):
    """ Writes a default Trigger Variance configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Trigger Variances Configuration Reset ****")
    CreateTriggerVariancesConfiguration(load_from_file=False).save_config_to_file()


def reset_email_config(log_reset=True):
    """ Writes a default Email configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Email Configuration Reset ****")
    CreateEmailConfiguration(load_from_file=False).save_config_to_file()


def reset_mqtt_broker_config(log_reset=True):
    """ Writes a default MQTT Broker configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** MQTT Broker Configuration Reset ****")
    CreateMQTTBrokerConfiguration(load_from_file=False).save_config_to_file()


def reset_mqtt_publisher_config(log_reset=True):
    """ Writes a default MQTT Publisher configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** MQTT Publisher Configuration Reset ****")
    CreateMQTTPublisherConfiguration(load_from_file=False).save_config_to_file()


def reset_mqtt_subscriber_config(log_reset=True):
    """ Writes a default MQTT Subscriber configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** MQTT Subscriber Configuration Reset ****")
    CreateMQTTSubscriberConfiguration(load_from_file=False).save_config_to_file()


def reset_weather_underground_config(log_reset=True):
    """ Writes a default Weather Underground configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Weather Underground Configuration Reset ****")
    CreateWeatherUndergroundConfiguration(load_from_file=False).save_config_to_file()


def reset_luftdaten_config(log_reset=True):
    """ Writes a default Luftdaten configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Luftdaten Configuration Reset ****")
    CreateLuftdatenConfiguration(load_from_file=False).save_config_to_file()


def reset_open_sense_map_config(log_reset=True):
    """ Writes a default Open Sense Map configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Open Sense Map Configuration Reset ****")
    CreateOpenSenseMapConfiguration(load_from_file=False).save_config_to_file()


def reset_sensor_control_config(log_reset=True):
    """ Writes a default Sensor Control configuration file. """
    if log_reset:
        logger.primary_logger.warning(" **** Sensor Control Configuration Reset ****")
    CreateSensorControlConfiguration(load_from_file=False).save_config_to_file()


def reset_all_configurations(log_reset=True):
    """
    Resets all configuration files to Default settings.
    If log_reset is True, adds log entry for each reset.  Default True.
    """
    reset_primary_config(log_reset=log_reset)
    reset_installed_sensors(log_reset=log_reset)
    reset_display_config(log_reset=log_reset)
    reset_checkin_config(log_reset=log_reset)
    reset_interval_recording_config(log_reset=log_reset)
    reset_trigger_high_low_config(log_reset=log_reset)
    reset_trigger_variance_config(log_reset=log_reset)
    reset_email_config(log_reset=log_reset)
    reset_mqtt_broker_config(log_reset=log_reset)
    reset_mqtt_publisher_config(log_reset=log_reset)
    reset_mqtt_subscriber_config(log_reset=log_reset)
    reset_weather_underground_config(log_reset=log_reset)
    reset_luftdaten_config(log_reset=log_reset)
    reset_open_sense_map_config(log_reset=log_reset)
    reset_sensor_control_config(log_reset=log_reset)


def upgrade_config_load_and_save(configuration_creation_class, upgrade_msg=True):
    """ Creates configuration class, loads the config and saves it without logging. """
    new_config_instance = configuration_creation_class(load_from_file=False)
    try:
        old_config_text = get_file_content(new_config_instance.config_file_location)
        new_config_instance.set_config_with_str(old_config_text)
        new_config_instance.save_config_to_file()
        if upgrade_msg:
            logger.primary_logger.info(" ** Configuration " + new_config_instance.config_file_location + " Upgraded")
    except Exception as error:
        log_msg = " ***** Configuration " + new_config_instance.config_file_location
        logger.primary_logger.error(log_msg + " Upgrade Failed: " + str(error))


def load_and_save_all_configs_silently():
    ccl = [CreatePrimaryConfiguration, CreateInstalledSensorsConfiguration, CreateIntervalRecordingConfiguration,
           CreateTriggerHighLowConfiguration, CreateTriggerVariancesConfiguration, CreateDisplayConfiguration,
           CreateEmailConfiguration, CreateMQTTBrokerConfiguration, CreateMQTTPublisherConfiguration,
           CreateMQTTSubscriberConfiguration, CreateWeatherUndergroundConfiguration, CreateLuftdatenConfiguration,
           CreateOpenSenseMapConfiguration, CreateSensorControlConfiguration, CreateCheckinConfiguration]
    for config in ccl:
        upgrade_config_load_and_save(config, upgrade_msg=False)


def upgrade_python_pip_modules():
    if os.path.isfile(file_locations.program_root_dir + "/requirements.txt"):
        requirements_text = get_file_content(file_locations.program_root_dir + "/requirements.txt").strip()
        requirements_list = requirements_text.split("\n")
        thread_function(_pip_upgrades_thread, args=requirements_list)


def _pip_upgrades_thread(requirements_list):
    logger.primary_logger.info("Python3 Module Upgrades Started")
    try:
        app_cached_variables.sensor_ready_for_upgrade = False
        for requirement in requirements_list:
            if requirement[0] != "#":
                command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + requirement.strip()
                os.system(command)
        logger.primary_logger.info("Python3 Module Upgrades Complete")
        os.system(app_cached_variables.bash_commands["RestartService"])
    except Exception as error:
        logger.primary_logger.error("Python3 Module Upgrades Error: " + str(error))
        app_cached_variables.sensor_ready_for_upgrade = True


def upgrade_linux_os():
    thread_function(_upgrade_linux_os_thread)


def _upgrade_linux_os_thread():
    """ Runs a bash command to upgrade the Linux System with apt-get. """
    try:
        app_cached_variables.sensor_ready_for_upgrade = False
        os.system(app_cached_variables.bash_commands["UpgradeSystemOS"])
        logger.primary_logger.warning("Linux OS Upgrade Done")
        logger.primary_logger.info("Rebooting System")
        os.system(app_cached_variables.bash_commands["RebootSystem"])
    except Exception as error:
        logger.primary_logger.error("Linux OS Upgrade Error: " + str(error))
        app_cached_variables.sensor_ready_for_upgrade = True


def create_secondary_python_venv():
    """
    Checks to see if the secondary Python virtual environment is present, if not, creates it
    Used for software upgrades and Kootnet Sensor's TCT
    :return: Nothing
    """
    if app_cached_variables.running_as_service and app_cached_variables.running_with_root:
        upgrade_env_dir = file_locations.sensor_data_dir + "/upgrade_env/"
        try:
            if not os.path.isdir(upgrade_env_dir):
                os.mkdir(upgrade_env_dir)
            if not os.path.isfile(upgrade_env_dir + "bin/python"):
                logger.primary_logger.info(" - Creating Kootnet Sensor's Upgrade & TCT Python Virtual Environment")
                os.system("python3 -m venv " + upgrade_env_dir)
                os.system(upgrade_env_dir + "bin/pip install requests")
                logger.primary_logger.info(" - Python Virtual Environment Created Successfully")
        except Exception as error:
            logger.primary_logger.critical("-- Unable to create Python virtual environment for upgrades: " + str(error))
