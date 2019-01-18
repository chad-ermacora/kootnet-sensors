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
# from operations_modules import operations_logger
import operations_modules.operations_config_file as operations_config_file
import operations_modules.operations_file_locations as file_locations
import operations_modules.operations_installed_sensors as operations_installed_sensors
from operations_modules.operations_config_db import CreateDatabaseVariables
from sensor_modules.trigger_variances import get_triggers_from_file, CreateTriggerVariances
from sensor_modules.temperature_offsets import CreateRPZeroWTemperatureOffsets, CreateRP3BPlusTemperatureOffsets, \
    CreateUnknownTemperatureOffsets

# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

version = "Alpha.23.19"
sense_hat_show_led_message = False

trigger_pairs = 3

restart_sensor_services_command = "systemctl daemon-reload && " + \
                                  "systemctl restart SensorRecording && " + \
                                  "systemctl restart SensorCommands"

bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_programs_e-Ink.sh",
                 "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/update_programs_online.sh",
                 "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/update_programs_smb.sh",
                 "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                 "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "UpgradeSystemOS": "apt-get update && apt-get upgrade -y && reboot"}


def get_old_version():
    old_version_file = open(file_locations.old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version


def get_sensor_temperature_offset():
    """
     Returns sensors Environmental temperature offset based on system board and sensor.
     You can set an override in the main sensor configuration file.
    """

    if installed_sensors.raspberry_pi_3b_plus:
        sensor_temp_offset = CreateRP3BPlusTemperatureOffsets()
    elif installed_sensors.raspberry_pi_zero_w:
        sensor_temp_offset = CreateRPZeroWTemperatureOffsets()
    else:
        # All offsets are 0.0 for unselected or unsupported system boards
        sensor_temp_offset = CreateUnknownTemperatureOffsets()

    if current_config.enable_custom_temp:
        return current_config.custom_temperature_offset
    elif installed_sensors.pimoroni_enviro:
        return sensor_temp_offset.pimoroni_enviro
    elif installed_sensors.pimoroni_bme680:
        return sensor_temp_offset.pimoroni_bme680
    elif installed_sensors.raspberry_pi_sense_hat:
        return sensor_temp_offset.rp_sense_hat
    else:
        return 0.0


if get_old_version() != version:
    installed_sensors = operations_installed_sensors.CreateInstalledSensors()
    current_config = operations_config_file.CreateConfig()
    trigger_variances = CreateTriggerVariances()
else:
    installed_sensors = operations_installed_sensors.get_installed_sensors_from_file()
    current_config = operations_config_file.get_config_from_file()
    trigger_variances = CreateTriggerVariances()  # Use get_triggers_from_file() when trigger functions are done

    current_config.temperature_offset = get_sensor_temperature_offset()
    trigger_variances.init_trigger_variances(installed_sensors)

database_variables = CreateDatabaseVariables()
