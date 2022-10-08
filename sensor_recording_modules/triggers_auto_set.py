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
from operations_modules.app_cached_variables import latency_variables
from sensor_modules import sensor_access


def auto_set_triggers_wait_time(config, multiplier=10.0, set_lowest=False):
    sensor_names_list = latency_variables.get_all_latency_as_list()
    sensor_latencies = {
        latency_variables.cpu_temperature: 0, latency_variables.environment_temperature: 0,
        latency_variables.pressure: 0, latency_variables.altitude: 0, latency_variables.humidity: 0,
        latency_variables.distance: 0, latency_variables.gas: 0, latency_variables.particulate_matter: 0,
        latency_variables.lumen: 0, latency_variables.colours: 0, latency_variables.ultra_violet: 0,
        latency_variables.accelerometer_xyz: 0, latency_variables.magnetometer_xyz: 0,
        latency_variables.gyroscope_xyz: 0, latency_variables.gps: 0
    }

    multi_latency_sets = [
        sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency(),
        sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency(),
        sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency()
    ]

    for sensor_name in sensor_names_list:
        for sensor_latency_pull in multi_latency_sets:
            try:
                if sensor_name in sensor_latency_pull:
                    if sensor_latency_pull[sensor_name] is not None:
                        new_latency_with_multiplier = sensor_latency_pull[sensor_name] * multiplier
                        if new_latency_with_multiplier > sensor_latencies[sensor_name]:
                            sensor_latencies[sensor_name] = new_latency_with_multiplier
                    else:
                        sensor_latencies[sensor_name] = 999.999
            except Exception as error:
                logger.primary_logger.error("Unable to set " + sensor_name + " wait time: " + str(error))
    sensor_latencies = _update_zero_entries(sensor_latencies)
    _set_trigger_config_seconds(config, sensor_latencies, set_lowest)


def _update_zero_entries(sensor_latencies_dic):
    new_sensor_latencies_dic = {}
    for name, entry in sensor_latencies_dic.items():
        try:
            if entry is None or entry == 0:
                entry = 60
            new_sensor_latencies_dic[name] = entry
        except Exception as error:
            logger.primary_logger.error("Updating zero latency entries: " + str(error))
    return new_sensor_latencies_dic


def _set_trigger_config_seconds(config, sensor_latencies, set_lowest):
    try:
        config.cpu_temperature_wait_seconds = round(sensor_latencies[latency_variables.cpu_temperature], 6)
        config.env_temperature_wait_seconds = round(sensor_latencies[latency_variables.environment_temperature], 6)
        config.pressure_wait_seconds = round(sensor_latencies[latency_variables.pressure], 6)
        config.altitude_wait_seconds = round(sensor_latencies[latency_variables.altitude], 6)
        config.humidity_wait_seconds = round(sensor_latencies[latency_variables.humidity], 6)
        config.distance_wait_seconds = round(sensor_latencies[latency_variables.distance], 6)
        config.gas_wait_seconds = round(sensor_latencies[latency_variables.gas], 6)
        config.particulate_matter_wait_seconds = round(sensor_latencies[latency_variables.particulate_matter], 6)
        config.lumen_wait_seconds = round(sensor_latencies[latency_variables.lumen], 6)
        config.colour_wait_seconds = round(sensor_latencies[latency_variables.colours], 6)
        config.ultra_violet_wait_seconds = round(sensor_latencies[latency_variables.ultra_violet], 6)
        config.accelerometer_wait_seconds = round(sensor_latencies[latency_variables.accelerometer_xyz], 6)
        config.magnetometer_wait_seconds = round(sensor_latencies[latency_variables.magnetometer_xyz], 6)
        config.gyroscope_wait_seconds = round(sensor_latencies[latency_variables.gyroscope_xyz], 6)
    except Exception as error:
        logger.primary_logger.error("Round Sensor Latencies: " + str(error))

    if not set_lowest:
        _check_default_triggers(config)

    config.update_configuration_settings_list()
    config.save_config_to_file()


def _check_default_triggers(config):
    try:
        if config.cpu_temperature_wait_seconds < 15:
            config.cpu_temperature_wait_seconds = 15
        if config.env_temperature_wait_seconds < 15:
            config.env_temperature_wait_seconds = 15
        if config.pressure_wait_seconds < 30:
            config.pressure_wait_seconds = 30
        if config.altitude_wait_seconds < 30:
            config.altitude_wait_seconds = 30
        if config.humidity_wait_seconds < 15:
            config.humidity_wait_seconds = 15
        if config.distance_wait_seconds < 1:
            config.distance_wait_seconds = 1
        if config.gas_wait_seconds < 30:
            config.gas_wait_seconds = 30
        if config.particulate_matter_wait_seconds < 30:
            config.particulate_matter_wait_seconds = 30
        if config.lumen_wait_seconds < 1:
            config.lumen_wait_seconds = 1
        if config.colour_wait_seconds < 1:
            config.colour_wait_seconds = 1
        if config.ultra_violet_wait_seconds < 1:
            config.ultra_violet_wait_seconds = 1
        if config.accelerometer_wait_seconds < 0.25:
            config.accelerometer_wait_seconds = 0.25
        if config.magnetometer_wait_seconds < 0.25:
            config.magnetometer_wait_seconds = 0.25
        if config.gyroscope_wait_seconds < 0.25:
            config.gyroscope_wait_seconds = 0.25
    except Exception as error:
        logger.primary_logger.error("Sensor Latencies - Check Default Triggers: " + str(error))
