from operations_modules import logger
from configuration_modules.old_configuration_conversions.generic_upgrade_functions import reset_primary_config, \
    reset_installed_sensors


def upgrade_alpha_to_beta():
    reset_primary_config()
    reset_installed_sensors()
    logger.set_logging_level()
