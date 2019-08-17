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
# This file is updated with variables at runtime.
# This helps lessen disk reads by caching commonly used variables
program_last_updated = ""
reboot_count = ""

hostname = ""
ip = ""
ip_subnet = "/24"
gateway = ""
dns1 = ""
dns2 = ""

wifi_country_code = ""
wifi_ssid = ""
wifi_security_type = ""
wifi_psk = ""
