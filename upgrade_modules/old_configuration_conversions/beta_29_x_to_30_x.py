from operations_modules import logger
from operations_modules import file_locations
from upgrade_modules.generic_upgrade_functions import reset_primary_config, \
    reset_installed_sensors, reset_trigger_variance_config, successful_upgrade_message, reset_mqtt_broker_config, \
    reset_mqtt_subscriber_config, reset_mqtt_publisher_config, reset_display_config, reset_checkin_config
from operations_modules.app_generic_functions import get_file_content
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration


def upgrade_beta_29_to_30():
    # Beta.29.x versions don't have any MQTT or Display Configurations
    reset_display_config(log_reset=False)
    reset_checkin_config(log_reset=False)
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)
    try:
        primary_config_lines = get_file_content(file_locations.primary_config).strip().split("\n")
        primary_config_lines = primary_config_lines[1:]
        new_primary_config.enable_debug_logging = int(primary_config_lines[0].split("=")[0].strip())
        new_primary_config.enable_display = int(primary_config_lines[1].split("=")[0].strip())
        new_primary_config.enable_interval_recording = int(primary_config_lines[2].split("=")[0].strip())
        new_primary_config.enable_trigger_recording = int(primary_config_lines[3].split("=")[0].strip())
        new_primary_config.sleep_duration_interval = float(primary_config_lines[4].split("=")[0].strip())
        new_primary_config.enable_custom_temp = int(primary_config_lines[5].split("=")[0].strip())
        new_primary_config.temperature_offset = float(primary_config_lines[6].split("=")[0].strip())
        new_primary_config.web_portal_port = int(primary_config_lines[7].split("=")[0].strip())
        if new_primary_config.enable_display:
            new_display_config = CreateDisplayConfiguration(load_from_file=False)
            new_display_config.enable_display = 1
            new_display_config.system_temperature = 1
            new_display_config.env_temperature = 1
            new_display_config.update_configuration_settings_list()
            new_display_config.save_config_to_file()
            successful_upgrade_message("Display")
        successful_upgrade_message("Primary")
    except Exception as error:
        logger.primary_logger.error("Problem during Primary Configuration Upgrade: " + str(error))
        reset_primary_config()
    new_primary_config.update_configuration_settings_list()
    new_primary_config.save_config_to_file()
    logger.set_logging_level()

    new_installed_sensors = CreateInstalledSensorsConfiguration(load_from_file=False)
    try:
        installed_sensors_config_lines = get_file_content(file_locations.installed_sensors_config).strip().split("\n")
        installed_sensors_config_lines = installed_sensors_config_lines[1:]
        new_installed_sensors.linux_system = int(installed_sensors_config_lines[0].split("=")[0].strip())
        new_installed_sensors.raspberry_pi = int(installed_sensors_config_lines[1].split("=")[0].strip())
        new_installed_sensors.raspberry_pi_sense_hat = int(installed_sensors_config_lines[2].split("=")[0].strip())
        new_installed_sensors.pimoroni_bh1745 = int(installed_sensors_config_lines[3].split("=")[0].strip())
        new_installed_sensors.pimoroni_as7262 = int(installed_sensors_config_lines[4].split("=")[0].strip())
        new_installed_sensors.pimoroni_mcp9600 = int(installed_sensors_config_lines[5].split("=")[0].strip())
        new_installed_sensors.pimoroni_bmp280 = int(installed_sensors_config_lines[6].split("=")[0].strip())
        new_installed_sensors.pimoroni_bme680 = int(installed_sensors_config_lines[7].split("=")[0].strip())
        new_installed_sensors.pimoroni_enviro = int(installed_sensors_config_lines[8].split("=")[0].strip())
        new_installed_sensors.pimoroni_enviroplus = int(installed_sensors_config_lines[9].split("=")[0].strip())
        new_installed_sensors.pimoroni_sgp30 = int(installed_sensors_config_lines[10].split("=")[0].strip())
        new_installed_sensors.pimoroni_pms5003 = int(installed_sensors_config_lines[11].split("=")[0].strip())
        new_installed_sensors.pimoroni_msa301 = int(installed_sensors_config_lines[12].split("=")[0].strip())
        new_installed_sensors.pimoroni_lsm303d = int(installed_sensors_config_lines[13].split("=")[0].strip())
        new_installed_sensors.pimoroni_icm20948 = int(installed_sensors_config_lines[14].split("=")[0].strip())
        new_installed_sensors.pimoroni_vl53l1x = int(installed_sensors_config_lines[15].split("=")[0].strip())
        new_installed_sensors.pimoroni_ltr_559 = int(installed_sensors_config_lines[16].split("=")[0].strip())
        new_installed_sensors.pimoroni_veml6075 = int(installed_sensors_config_lines[17].split("=")[0].strip())
        new_installed_sensors.pimoroni_matrix_11x7 = int(installed_sensors_config_lines[18].split("=")[0].strip())
        new_installed_sensors.pimoroni_st7735 = int(installed_sensors_config_lines[19].split("=")[0].strip())
        new_installed_sensors.pimoroni_mono_oled_luma = int(installed_sensors_config_lines[20].split("=")[0].strip())
        successful_upgrade_message("Installed Sensors")
    except Exception as error:
        logger.primary_logger.error("Problem during Installed Sensors Configuration Upgrade: " + str(error))
        reset_installed_sensors()
    new_installed_sensors.update_configuration_settings_list()
    new_installed_sensors.save_config_to_file()

    try:
        new_osm_config = CreateOpenSenseMapConfiguration(load_from_file=False)
        raw_config_settings = get_file_content(file_locations.osm_config).strip().split("\n")[1:]
        config_settings = []

        for setting in raw_config_settings:
            config_settings.append(setting.split("=")[0].strip())

        new_osm_config.open_sense_map_enabled = int(config_settings[0])
        new_osm_config.sense_box_id = str(config_settings[1])
        new_osm_config.interval_seconds = float(config_settings[2])
        new_osm_config.temperature_id = str(config_settings[3])
        new_osm_config.pressure_id = str(config_settings[4])
        new_osm_config.altitude_id = str(config_settings[5])
        new_osm_config.humidity_id = str(config_settings[6])
        new_osm_config.gas_voc_id = str(config_settings[7])
        new_osm_config.gas_nh3_id = str(config_settings[8])
        new_osm_config.gas_oxidised_id = str(config_settings[9])
        new_osm_config.gas_reduced_id = str(config_settings[10])
        new_osm_config.pm1_id = str(config_settings[11])
        new_osm_config.pm2_5_id = str(config_settings[12])
        new_osm_config.pm10_id = str(config_settings[13])
        new_osm_config.lumen_id = str(config_settings[14])
        new_osm_config.red_id = str(config_settings[15])
        new_osm_config.orange_id = str(config_settings[16])
        new_osm_config.yellow_id = str(config_settings[17])
        new_osm_config.green_id = str(config_settings[18])
        new_osm_config.blue_id = str(config_settings[19])
        new_osm_config.violet_id = str(config_settings[20])
        new_osm_config.ultra_violet_index_id = str(config_settings[21])
        new_osm_config.ultra_violet_a_id = str(config_settings[22])
        new_osm_config.ultra_violet_b_id = str(config_settings[23])
        new_osm_config.update_configuration_settings_list()
        new_osm_config.save_config_to_file()
        successful_upgrade_message("Open Sense Map")
    except Exception as error:
        logger.primary_logger.error("Open Sense Map Configuration conversion error: " + str(error))

    reset_trigger_variance_config()
    reset_mqtt_broker_config(log_reset=False)
    reset_mqtt_publisher_config(log_reset=False)
    reset_mqtt_subscriber_config(log_reset=False)


def upgrade_beta_30_90_to_30_138():
    try:
        new_osm_config = CreateOpenSenseMapConfiguration(load_from_file=False)
        raw_config_settings = get_file_content(file_locations.osm_config).strip().split("\n")[1:]
        config_settings = []

        for setting in raw_config_settings:
            config_settings.append(setting.split("=")[0].strip())

        new_osm_config.open_sense_map_enabled = int(config_settings[0])
        new_osm_config.sense_box_id = str(config_settings[1])
        new_osm_config.interval_seconds = float(config_settings[2])
        new_osm_config.temperature_id = str(config_settings[3])
        new_osm_config.pressure_id = str(config_settings[4])
        new_osm_config.altitude_id = str(config_settings[5])
        new_osm_config.humidity_id = str(config_settings[6])
        new_osm_config.gas_voc_id = str(config_settings[7])
        new_osm_config.gas_nh3_id = str(config_settings[8])
        new_osm_config.gas_oxidised_id = str(config_settings[9])
        new_osm_config.gas_reduced_id = str(config_settings[10])
        new_osm_config.pm1_id = str(config_settings[11])
        new_osm_config.pm2_5_id = str(config_settings[12])
        new_osm_config.pm10_id = str(config_settings[13])
        new_osm_config.lumen_id = str(config_settings[14])
        new_osm_config.red_id = str(config_settings[15])
        new_osm_config.orange_id = str(config_settings[16])
        new_osm_config.yellow_id = str(config_settings[17])
        new_osm_config.green_id = str(config_settings[18])
        new_osm_config.blue_id = str(config_settings[19])
        new_osm_config.violet_id = str(config_settings[20])
        new_osm_config.ultra_violet_index_id = str(config_settings[21])
        new_osm_config.ultra_violet_a_id = str(config_settings[22])
        new_osm_config.ultra_violet_b_id = str(config_settings[23])
        new_osm_config.update_configuration_settings_list()
        new_osm_config.save_config_to_file()
        successful_upgrade_message("Open Sense Map")
    except Exception as error:
        logger.primary_logger.error("Open Sense Map Configuration conversion error: " + str(error))


def upgrade_beta_30_x_to_30_90():
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)
    try:
        primary_config_lines = get_file_content(file_locations.primary_config).strip().split("\n")
        primary_config_lines = primary_config_lines[1:]
        new_primary_config.enable_debug_logging = int(primary_config_lines[0].split("=")[0].strip())
        new_primary_config.enable_interval_recording = int(primary_config_lines[2].split("=")[0].strip())
        new_primary_config.enable_trigger_recording = int(primary_config_lines[3].split("=")[0].strip())
        new_primary_config.sleep_duration_interval = float(primary_config_lines[4].split("=")[0].strip())
        new_primary_config.enable_custom_temp = int(primary_config_lines[5].split("=")[0].strip())
        new_primary_config.temperature_offset = float(primary_config_lines[6].split("=")[0].strip())
        new_primary_config.web_portal_port = int(primary_config_lines[7].split("=")[0].strip())
        successful_upgrade_message("Primary")
    except Exception as error:
        logger.primary_logger.error("Problem during Primary Configuration Upgrade: " + str(error))
    new_primary_config.update_configuration_settings_list()
    new_primary_config.save_config_to_file()
    logger.set_logging_level()

    new_installed_sensors = CreateInstalledSensorsConfiguration(load_from_file=False)
    try:
        installed_sensors_config_lines = get_file_content(file_locations.installed_sensors_config).strip().split("\n")
        installed_sensors_config_lines = installed_sensors_config_lines[1:]
        new_installed_sensors.linux_system = int(installed_sensors_config_lines[0].split("=")[0].strip())
        new_installed_sensors.raspberry_pi = int(installed_sensors_config_lines[1].split("=")[0].strip())
        new_installed_sensors.raspberry_pi_sense_hat = int(installed_sensors_config_lines[2].split("=")[0].strip())
        new_installed_sensors.pimoroni_bh1745 = int(installed_sensors_config_lines[3].split("=")[0].strip())
        new_installed_sensors.pimoroni_as7262 = int(installed_sensors_config_lines[4].split("=")[0].strip())
        new_installed_sensors.pimoroni_mcp9600 = int(installed_sensors_config_lines[5].split("=")[0].strip())
        new_installed_sensors.pimoroni_bmp280 = int(installed_sensors_config_lines[6].split("=")[0].strip())
        new_installed_sensors.pimoroni_bme680 = int(installed_sensors_config_lines[7].split("=")[0].strip())
        new_installed_sensors.pimoroni_enviro = int(installed_sensors_config_lines[8].split("=")[0].strip())
        new_installed_sensors.pimoroni_enviroplus = int(installed_sensors_config_lines[9].split("=")[0].strip())
        new_installed_sensors.pimoroni_sgp30 = int(installed_sensors_config_lines[10].split("=")[0].strip())
        new_installed_sensors.pimoroni_pms5003 = int(installed_sensors_config_lines[11].split("=")[0].strip())
        new_installed_sensors.pimoroni_msa301 = int(installed_sensors_config_lines[12].split("=")[0].strip())
        new_installed_sensors.pimoroni_lsm303d = int(installed_sensors_config_lines[13].split("=")[0].strip())
        new_installed_sensors.pimoroni_icm20948 = int(installed_sensors_config_lines[14].split("=")[0].strip())
        new_installed_sensors.pimoroni_vl53l1x = int(installed_sensors_config_lines[15].split("=")[0].strip())
        new_installed_sensors.pimoroni_ltr_559 = int(installed_sensors_config_lines[16].split("=")[0].strip())
        new_installed_sensors.pimoroni_veml6075 = int(installed_sensors_config_lines[17].split("=")[0].strip())
        new_installed_sensors.pimoroni_matrix_11x7 = int(installed_sensors_config_lines[18].split("=")[0].strip())
        new_installed_sensors.pimoroni_st7735 = int(installed_sensors_config_lines[19].split("=")[0].strip())
        new_installed_sensors.pimoroni_mono_oled_luma = int(installed_sensors_config_lines[20].split("=")[0].strip())
        new_installed_sensors.kootnet_dummy_sensor = int(installed_sensors_config_lines[21].split("=")[0].strip())
        new_installed_sensors.sensirion_sps30 = int(installed_sensors_config_lines[22].split("=")[0].strip())
        successful_upgrade_message("Installed Sensors")
    except Exception as error:
        logger.primary_logger.error("Problem during Installed Sensors Configuration Upgrade: " + str(error))
    new_installed_sensors.update_configuration_settings_list()
    new_installed_sensors.save_config_to_file()

    reset_display_config()
    reset_mqtt_publisher_config()
    reset_mqtt_subscriber_config()
