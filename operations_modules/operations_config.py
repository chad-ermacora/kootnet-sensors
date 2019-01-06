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
from sensor_modules.trigger_variances import CreateTriggerVariances

# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

version = "Alpha.23.15"
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

current_config = operations_config_file.get_config_from_file()
installed_sensors = operations_installed_sensors.get_installed_sensors_from_file()

trigger_variances = CreateTriggerVariances(installed_sensors)
current_config.old_config_variance_set(installed_sensors)


def get_old_version():
    old_version_file = open(file_locations.old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version
