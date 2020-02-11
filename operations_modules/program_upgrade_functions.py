"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from operations_modules import logger
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import config_trigger_variances


def reset_installed_sensors():
    """ Writes a default installed sensor configuration file. """
    logger.primary_logger.warning(" **** Installed Sensors Configuration Reset ****")
    default_installed_sensors = config_installed_sensors.CreateInstalledSensorsConfiguration(load_from_file=False)
    default_installed_sensors.save_config_to_file()


def reset_main_config():
    """ Writes a default main configuration file. """
    logger.primary_logger.warning(" **** Main Configuration Reset ****")
    default_primary_config = config_primary.CreatePrimaryConfiguration(load_from_file=False)
    default_primary_config.save_config_to_file()


def reset_variance_config():
    """ Writes a default Trigger Variance configuration file. """
    logger.primary_logger.warning(" **** Trigger Variances Configuration Reset ****")
    default_variance = config_trigger_variances.CreateTriggerVariancesConfiguration(load_from_file=False)
    default_variance.save_config_to_file()
