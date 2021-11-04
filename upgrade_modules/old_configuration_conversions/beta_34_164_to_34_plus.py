from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from upgrade_modules.generic_upgrade_functions import successful_upgrade_message
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_check_ins import CreateCheckinConfiguration
from configuration_modules.config_sensor_offsets import CreateSensorOffsetsConfiguration
from configuration_modules.config_urls import CreateURLConfiguration


def upgrade_beta_34_164_to_34_plus():
    CreateURLConfiguration(load_from_file=False).save_config_to_file()

    sensor_offsets_config = CreateSensorOffsetsConfiguration(load_from_file=False)
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)
    try:
        old_primary_config_string = get_file_content(file_locations.primary_config).strip()
        old_primary_config_list = old_primary_config_string.split("\n")[1:]

        new_primary_config.web_portal_port = int(old_primary_config_list[0].split("=")[0].strip())
        new_primary_config.enable_debug_logging = int(old_primary_config_list[1].split("=")[0].strip())
        sensor_offsets_config.enable_temp_offset = int(old_primary_config_list[2].split("=")[0].strip())
        sensor_offsets_config.temperature_offset = float(old_primary_config_list[3].split("=")[0].strip())
        sensor_offsets_config.enable_temperature_comp_factor = int(old_primary_config_list[4].split("=")[0].strip())
        sensor_offsets_config.temperature_comp_factor = float(old_primary_config_list[5].split("=")[0].strip())
        new_primary_config.utc0_hour_offset = float(old_primary_config_list[6].split("=")[0].strip())
        new_primary_config.enable_automatic_upgrades_feature = int(old_primary_config_list[7].split("=")[0].strip())
        new_primary_config.enable_automatic_upgrades_minor = int(old_primary_config_list[8].split("=")[0].strip())
        new_primary_config.enable_automatic_upgrades_developmental = int(old_primary_config_list[9].split("=")[0].strip())
        new_primary_config.automatic_upgrade_delay_hours = float(old_primary_config_list[10].split("=")[0].strip())

        new_primary_config.update_configuration_settings_list()
        new_primary_config.save_config_to_file()
        sensor_offsets_config.update_configuration_settings_list()
        sensor_offsets_config.save_config_to_file()
        successful_upgrade_message("Primary & Sensor Offsets")
    except Exception as error:
        logger.primary_logger.warning("Primary & Sensor Offsets Config Upgrade: " + str(error))
        new_primary_config.save_config_to_file()
        sensor_offsets_config.save_config_to_file()

    new_checkins_config = CreateCheckinConfiguration(load_from_file=False)
    try:
        old_checkins_config_string = get_file_content(file_locations.checkin_configuration).strip()
        old_checkins_config_list = old_checkins_config_string.split("\n")[1:]

        new_checkins_config.enable_checkin_recording = int(old_checkins_config_list[0].split("=")[0].strip())
        new_checkins_config.count_contact_days = float(old_checkins_config_list[1].split("=")[0].strip())
        new_checkins_config.delete_sensors_older_days = float(old_checkins_config_list[2].split("=")[0].strip())
        new_checkins_config.send_sensor_name = int(old_checkins_config_list[3].split("=")[0].strip())
        new_checkins_config.send_ip = int(old_checkins_config_list[4].split("=")[0].strip())
        new_checkins_config.send_program_version = int(old_checkins_config_list[5].split("=")[0].strip())
        new_checkins_config.send_installed_sensors = int(old_checkins_config_list[6].split("=")[0].strip())
        new_checkins_config.send_system_uptime = int(old_checkins_config_list[7].split("=")[0].strip())
        new_checkins_config.send_system_temperature = int(old_checkins_config_list[8].split("=")[0].strip())
        new_checkins_config.max_log_lines_to_send = int(old_checkins_config_list[9].split("=")[0].strip())
        new_checkins_config.send_primary_log = int(old_checkins_config_list[10].split("=")[0].strip())
        new_checkins_config.send_network_log = int(old_checkins_config_list[11].split("=")[0].strip())
        new_checkins_config.send_sensors_log = int(old_checkins_config_list[12].split("=")[0].strip())
        new_checkins_config.enable_checkin = int(old_checkins_config_list[13].split("=")[0].strip())
        new_checkins_config.checkin_wait_in_hours = float(old_checkins_config_list[14].split("=")[0].strip())
        new_checkins_config.main_page_max_sensors = int(old_checkins_config_list[16].strip().split("=")[0].strip())

        new_checkins_config.update_configuration_settings_list()
        new_checkins_config.save_config_to_file()
        successful_upgrade_message("Checkin & URL")
    except Exception as error:
        logger.primary_logger.warning("Checkins/URL Configs Upgrade: " + str(error))
        new_checkins_config.save_config_to_file()
