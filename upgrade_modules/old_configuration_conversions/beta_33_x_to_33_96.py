from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from upgrade_modules.generic_upgrade_functions import CreateCheckinConfiguration, upgrade_config_load_and_save
from configuration_modules.config_primary import CreatePrimaryConfiguration


def upgrade_beta_33_x_to_33_96():
    config_class = CreateCheckinConfiguration
    upgrade_config_load_and_save(config_class)

    old_primary_config_string = get_file_content(file_locations.primary_config).strip()
    old_primary_config_list = old_primary_config_string.split("\n")[1:]
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)

    web_portal_port = None
    enable_debug_logging = None
    enable_custom_temp = None
    temperature_offset = None
    enable_temperature_comp_factor = None
    temperature_comp_factor = None
    # enable_checkin = None
    # checkin_url = None
    # checkin_wait_in_hours = None
    utc0_hour_offset = None

    try:
        web_portal_port = int(old_primary_config_list[0])
        enable_debug_logging = int(old_primary_config_list[1])
        enable_custom_temp = int(old_primary_config_list[2])
        temperature_offset = float(old_primary_config_list[3])
        enable_temperature_comp_factor = int(old_primary_config_list[4])
        temperature_comp_factor = float(old_primary_config_list[5])
        # enable_checkin = int(old_primary_config_list[6])
        # checkin_url = old_primary_config_list[7].strip()
        # checkin_wait_in_hours = float(old_primary_config_list[8].strip())
        utc0_hour_offset = float(old_primary_config_list[9].strip())
    except Exception as error:
        logger.primary_logger.warning("Primary Config Upgrade: " + str(error))

    if web_portal_port is not None:
        new_primary_config.web_portal_port = web_portal_port
    if enable_debug_logging is not None:
        new_primary_config.enable_debug_logging = enable_debug_logging
    if enable_custom_temp is not None:
        new_primary_config.enable_custom_temp = enable_custom_temp
    if temperature_offset is not None:
        new_primary_config.temperature_offset = temperature_offset
    if enable_temperature_comp_factor is not None:
        new_primary_config.enable_temperature_comp_factor = enable_temperature_comp_factor
    if temperature_comp_factor is not None:
        new_primary_config.temperature_comp_factor = temperature_comp_factor
    if utc0_hour_offset is not None:
        new_primary_config.utc0_hour_offset = utc0_hour_offset

    new_primary_config.save_config_to_file()
