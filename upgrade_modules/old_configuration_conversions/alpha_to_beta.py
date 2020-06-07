from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from upgrade_modules.old_configuration_conversions.generic_upgrade_functions import reset_primary_config, \
    reset_installed_sensors, successful_upgrade_message, reset_display_config, reset_variance_config, \
    reset_mqtt_broker_config, reset_mqtt_publisher_config, reset_mqtt_subscriber_config


def upgrade_alpha_to_beta():
    # Alpha versions don't have any MQTT or Display Configurations
    reset_primary_config()
    logger.set_logging_level()
    reset_installed_sensors()
    reset_variance_config()
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

    reset_display_config(log_reset=False)
    reset_mqtt_broker_config(log_reset=False)
    reset_mqtt_publisher_config(log_reset=False)
    reset_mqtt_subscriber_config(log_reset=False)
