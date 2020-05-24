from configuration_modules.old_configuration_conversions.config_reset import reset_primary_config, \
    reset_installed_sensors


def upgrade_alpha_to_beta():
    reset_primary_config()
    reset_installed_sensors()
