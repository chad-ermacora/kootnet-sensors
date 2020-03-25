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
restart_sensor_services_command = "systemctl daemon-reload ; " + \
                                  "systemctl restart KootnetSensors"

# TODO: ReInstallRequirements doesn't work Remove it (Clean upgrade does it and then some)
# TODO: Add ability to upgrade net facing pip packages (Flask, gevent)

# Dictionary of Terminal commands
bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_kootnet-sensors_e-ink.sh",
                 "UpgradeOnline": "systemctl start SensorUpgradeOnline",
                 "UpgradeOnlineClean": "systemctl start SensorUpgradeOnlineClean",
                 "UpgradeOnlineCleanDEV": "systemctl start SensorUpgradeOnlineCleanDEV",
                 "UpgradeOnlineDEV": "systemctl start SensorUpgradeOnlineDEV",
                 "UpgradeSMB": "systemctl start SensorUpgradeSMB",
                 "UpgradeSMBClean": "systemctl start SensorUpgradeSMBClean",
                 "UpgradeSMBCleanDEV": "systemctl start SensorUpgradeSMBCleanDEV",
                 "UpgradeSMBDEV": "systemctl start SensorUpgradeSMBDEV",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "SetPermissions": "bash /opt/kootnet-sensors/scripts/set_permissions.sh"}
