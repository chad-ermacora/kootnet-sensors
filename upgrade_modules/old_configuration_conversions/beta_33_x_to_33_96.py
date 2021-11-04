from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from upgrade_modules.generic_upgrade_functions import CreateCheckinConfiguration, upgrade_config_load_and_save, \
    successful_upgrade_message
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_sensor_offsets import CreateSensorOffsetsConfiguration


def upgrade_beta_33_x_to_33_96():
    config_class = CreateCheckinConfiguration
    upgrade_config_load_and_save(config_class)

    sensor_offsets_config = CreateSensorOffsetsConfiguration(load_from_file=False)
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)
    try:
        old_primary_config_string = get_file_content(file_locations.primary_config).strip()
        old_primary_config_list = old_primary_config_string.split("\n")[1:]

        web_portal_port = int(old_primary_config_list[0].split("=")[0].strip())
        enable_debug_logging = int(old_primary_config_list[1].split("=")[0].strip())
        enable_temp_offset = int(old_primary_config_list[2].split("=")[0].strip())
        temperature_offset = float(old_primary_config_list[3].split("=")[0].strip())
        enable_temperature_comp_factor = int(old_primary_config_list[4].split("=")[0].strip())
        temperature_comp_factor = float(old_primary_config_list[5].split("=")[0].strip())
        # enable_checkin = int(old_primary_config_list[6])
        # checkin_url = old_primary_config_list[7].strip()
        # checkin_wait_in_hours = float(old_primary_config_list[8].strip())
        utc0_hour_offset = float(old_primary_config_list[9].split("=")[0].strip())

        new_primary_config.web_portal_port = web_portal_port
        new_primary_config.enable_debug_logging = enable_debug_logging
        sensor_offsets_config.enable_temp_offset = enable_temp_offset
        sensor_offsets_config.temperature_offset = temperature_offset
        sensor_offsets_config.enable_temperature_comp_factor = enable_temperature_comp_factor
        sensor_offsets_config.temperature_comp_factor = temperature_comp_factor
        new_primary_config.utc0_hour_offset = utc0_hour_offset

        new_primary_config.update_configuration_settings_list()
        new_primary_config.save_config_to_file()
        sensor_offsets_config.update_configuration_settings_list()
        sensor_offsets_config.save_config_to_file()
        successful_upgrade_message("Primary & Sensor Offsets")
    except Exception as error:
        logger.primary_logger.warning("Primary Config Upgrade: " + str(error))
        new_primary_config.save_config_to_file()
        sensor_offsets_config.save_config_to_file()
