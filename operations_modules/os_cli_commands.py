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

bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_e-ink.sh",
                 "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_http.sh",
                 "UpgradeOnlineDEV": "bash /opt/kootnet-sensors/scripts/dev_upgrade_http.sh",
                 "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_smb.sh",
                 "UpgradeSMBDEV": "bash /opt/kootnet-sensors/scripts/dev_upgrade_smb.sh",
                 "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                 "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "UpgradeSystemOS": "bash /opt/kootnet-sensors/scripts/linux_system_os_upgrade.sh",
                 "ReInstallRequirements": "bash /opt/kootnet-sensors/scripts/reinstall_requirements.sh",
                 "SetPermissions": "bash /opt/kootnet-sensors/scripts/set_permissions.sh"}
