from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from upgrade_modules.generic_upgrade_functions import successful_upgrade_message, reset_live_graph_config, \
    reset_database_graph_config, reset_email_config, reset_flask_login_credentials, reset_urls_config, \
    reset_checkin_config, reset_email_reports_config, reset_email_db_graphs_config
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_sensor_offsets import CreateSensorOffsetsConfiguration


def upgrade_beta_34_x_to_35_x():
    reset_live_graph_config(log_reset=False)
    reset_database_graph_config(log_reset=False)
    reset_checkin_config(log_reset=False)
    reset_urls_config(log_reset=False)
    reset_email_reports_config(log_reset=False)
    reset_email_db_graphs_config(log_reset=False)
    reset_flask_login_credentials()
    reset_email_config()

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
