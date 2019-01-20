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

# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

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

