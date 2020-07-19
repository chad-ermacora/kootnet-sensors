from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import get_file_content
from upgrade_modules.old_configuration_conversions.generic_upgrade_functions import successful_upgrade_message
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration


def upgrade_beta_30_x_to_31_21():
    new_interval_recording = CreateIntervalRecordingConfiguration(load_from_file=False)
    new_primary_config = CreatePrimaryConfiguration(load_from_file=False)
    new_t_v_config = CreateTriggerVariancesConfiguration(load_from_file=False)

    try:
        primary_config_lines = get_file_content(file_locations.primary_config).strip().split("\n")
        primary_config_lines = primary_config_lines[1:]
        new_primary_config.web_portal_port = int(primary_config_lines[0].split("=")[0].strip())
        new_primary_config.enable_debug_logging = int(primary_config_lines[1].split("=")[0].strip())
        new_primary_config.enable_custom_temp = int(primary_config_lines[5].split("=")[0].strip())
        new_primary_config.temperature_offset = float(primary_config_lines[6].split("=")[0].strip())
        new_primary_config.enable_temperature_comp_factor = int(primary_config_lines[7].split("=")[0].strip())
        new_primary_config.temperature_comp_factor = float(primary_config_lines[8].split("=")[0].strip())
        new_primary_config.update_configuration_settings_list()
        new_primary_config.save_config_to_file()
        successful_upgrade_message("Primary")
        if int(primary_config_lines[2].split("=")[0].strip()):
            new_interval_recording.enable_interval_recording = 1
            new_interval_recording.sleep_duration_interval = float(primary_config_lines[4].split("=")[0].strip())
        if int(primary_config_lines[3].split("=")[0].strip()):
            new_t_v_config.enable_trigger_variance = 1
        new_interval_recording.update_configuration_settings_list()
        new_interval_recording.save_config_to_file()
    except Exception as error:
        logger.primary_logger.error("Problem during Primary Configuration Upgrade: " + str(error))

    try:
        variance_trigger_config_lines = get_file_content(file_locations.trigger_variances_config).strip().split("\n")
        variance_trigger_config_lines = variance_trigger_config_lines[1:]
        new_t_v_config.cpu_temperature_enabled = int(variance_trigger_config_lines[2].split("=")[0].strip())
        new_t_v_config.cpu_temperature_variance = float(variance_trigger_config_lines[3].split("=")[0].strip())
        new_t_v_config.cpu_temperature_wait_seconds = float(variance_trigger_config_lines[4].split("=")[0].strip())
        new_t_v_config.env_temperature_enabled = int(variance_trigger_config_lines[5].split("=")[0].strip())
        new_t_v_config.env_temperature_variance = float(variance_trigger_config_lines[6].split("=")[0].strip())
        new_t_v_config.env_temperature_wait_seconds = float(variance_trigger_config_lines[7].split("=")[0].strip())
        new_t_v_config.pressure_enabled = int(variance_trigger_config_lines[8].split("=")[0].strip())
        new_t_v_config.pressure_variance = float(variance_trigger_config_lines[9].split("=")[0].strip())
        new_t_v_config.pressure_wait_seconds = float(variance_trigger_config_lines[10].split("=")[0].strip())
        new_t_v_config.altitude_enabled = int(variance_trigger_config_lines[11].split("=")[0].strip())
        new_t_v_config.altitude_variance = float(variance_trigger_config_lines[12].split("=")[0].strip())
        new_t_v_config.altitude_wait_seconds = float(variance_trigger_config_lines[13].split("=")[0].strip())
        new_t_v_config.humidity_enabled = int(variance_trigger_config_lines[14].split("=")[0].strip())
        new_t_v_config.humidity_variance = float(variance_trigger_config_lines[15].split("=")[0].strip())
        new_t_v_config.humidity_wait_seconds = float(variance_trigger_config_lines[16].split("=")[0].strip())
        new_t_v_config.distance_enabled = int(variance_trigger_config_lines[17].split("=")[0].strip())
        new_t_v_config.distance_variance = float(variance_trigger_config_lines[18].split("=")[0].strip())
        new_t_v_config.distance_wait_seconds = float(variance_trigger_config_lines[19].split("=")[0].strip())
        new_t_v_config.gas_enabled = int(variance_trigger_config_lines[20].split("=")[0].strip())
        new_t_v_config.gas_resistance_index_variance = float(variance_trigger_config_lines[21].split("=")[0].strip())
        new_t_v_config.gas_oxidising_variance = float(variance_trigger_config_lines[22].split("=")[0].strip())
        new_t_v_config.gas_reducing_variance = float(variance_trigger_config_lines[23].split("=")[0].strip())
        new_t_v_config.gas_nh3_variance = float(variance_trigger_config_lines[24].split("=")[0].strip())
        new_t_v_config.gas_wait_seconds = float(variance_trigger_config_lines[25].split("=")[0].strip())
        new_t_v_config.particulate_matter_enabled = int(variance_trigger_config_lines[26].split("=")[0].strip())
        new_t_v_config.particulate_matter_1_variance = float(variance_trigger_config_lines[27].split("=")[0].strip())
        new_t_v_config.particulate_matter_2_5_variance = float(variance_trigger_config_lines[28].split("=")[0].strip())
        new_t_v_config.particulate_matter_10_variance = float(variance_trigger_config_lines[29].split("=")[0].strip())
        new_t_v_config.particulate_matter_wait_seconds = float(variance_trigger_config_lines[30].split("=")[0].strip())
        new_t_v_config.lumen_enabled = int(variance_trigger_config_lines[31].split("=")[0].strip())
        new_t_v_config.lumen_variance = float(variance_trigger_config_lines[32].split("=")[0].strip())
        new_t_v_config.lumen_wait_seconds = float(variance_trigger_config_lines[33].split("=")[0].strip())
        new_t_v_config.colour_enabled = int(variance_trigger_config_lines[34].split("=")[0].strip())
        new_t_v_config.red_variance = float(variance_trigger_config_lines[35].split("=")[0].strip())
        new_t_v_config.orange_variance = float(variance_trigger_config_lines[36].split("=")[0].strip())
        new_t_v_config.yellow_variance = float(variance_trigger_config_lines[37].split("=")[0].strip())
        new_t_v_config.green_variance = float(variance_trigger_config_lines[38].split("=")[0].strip())
        new_t_v_config.blue_variance = float(variance_trigger_config_lines[39].split("=")[0].strip())
        new_t_v_config.violet_variance = float(variance_trigger_config_lines[40].split("=")[0].strip())
        new_t_v_config.colour_wait_seconds = float(variance_trigger_config_lines[41].split("=")[0].strip())
        new_t_v_config.ultra_violet_enabled = int(variance_trigger_config_lines[42].split("=")[0].strip())
        new_t_v_config.ultra_violet_index_variance = float(variance_trigger_config_lines[43].split("=")[0].strip())
        new_t_v_config.ultra_violet_a_variance = float(variance_trigger_config_lines[44].split("=")[0].strip())
        new_t_v_config.ultra_violet_b_variance = float(variance_trigger_config_lines[45].split("=")[0].strip())
        new_t_v_config.ultra_violet_wait_seconds = float(variance_trigger_config_lines[46].split("=")[0].strip())
        new_t_v_config.accelerometer_enabled = int(variance_trigger_config_lines[47].split("=")[0].strip())
        new_t_v_config.accelerometer_x_variance = float(variance_trigger_config_lines[48].split("=")[0].strip())
        new_t_v_config.accelerometer_y_variance = float(variance_trigger_config_lines[49].split("=")[0].strip())
        new_t_v_config.accelerometer_z_variance = float(variance_trigger_config_lines[50].split("=")[0].strip())
        new_t_v_config.accelerometer_wait_seconds = float(variance_trigger_config_lines[51].split("=")[0].strip())
        new_t_v_config.magnetometer_enabled = int(variance_trigger_config_lines[52].split("=")[0].strip())
        new_t_v_config.magnetometer_x_variance = float(variance_trigger_config_lines[53].split("=")[0].strip())
        new_t_v_config.magnetometer_y_variance = float(variance_trigger_config_lines[54].split("=")[0].strip())
        new_t_v_config.magnetometer_z_variance = float(variance_trigger_config_lines[55].split("=")[0].strip())
        new_t_v_config.magnetometer_wait_seconds = float(variance_trigger_config_lines[56].split("=")[0].strip())
        new_t_v_config.gyroscope_enabled = int(variance_trigger_config_lines[57].split("=")[0].strip())
        new_t_v_config.gyroscope_x_variance = float(variance_trigger_config_lines[58].split("=")[0].strip())
        new_t_v_config.gyroscope_y_variance = float(variance_trigger_config_lines[59].split("=")[0].strip())
        new_t_v_config.gyroscope_z_variance = float(variance_trigger_config_lines[60].split("=")[0].strip())
        new_t_v_config.gyroscope_wait_seconds = float(variance_trigger_config_lines[61].split("=")[0].strip())
        new_t_v_config.update_configuration_settings_list()
        new_t_v_config.save_config_to_file()
        successful_upgrade_message("Variance Triggers")
    except Exception as error:
        logger.primary_logger.error("Trigger Variance Config: " + str(error))
