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
import os


def update_ver_a_22_8(upgrade_data_obj):
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_vl53l1x = upgrade_data_obj.old_installed_sensors.pimoroni_lsm303d
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_lsm303d = upgrade_data_obj.old_installed_sensors.pimoroni_enviro
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_enviro = upgrade_data_obj.old_installed_sensors.pimoroni_bme680
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_bme680 = upgrade_data_obj.old_installed_sensors.pimoroni_bh1745
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_bh1745 = upgrade_data_obj.old_installed_sensors.raspberry_pi_sense_hat
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_sense_hat = upgrade_data_obj.old_installed_sensors.raspberry_pi_3b_plus
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_3b_plus = 0
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_zero_w = upgrade_data_obj.old_installed_sensors.raspberry_pi_zero_w

    os.system("rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null")
    os.system("rm -f /opt/kootnet-sensors/auto_start/SensorHTTP.service 2>/dev/null")
    os.system("/usr/bin/pip3 install gevent")
