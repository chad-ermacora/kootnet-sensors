from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from configuration_modules.old_configuration_conversions.generic_upgrade_functions import reset_display_config, \
    reset_mqtt_publisher_config, reset_mqtt_subscriber_config, successful_upgrade_message
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration


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
