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
from datetime import datetime
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import software_version
from operations_modules.app_generic_functions import get_file_content


class CreateATProMenuNotificationClass:
    def __init__(self):
        self.notifications_list = []

        self.restart_service_enabled = 0
        self.restart_service_datetime = ""

        self.reboot_system_enabled = 0
        self.reboot_system_datetime = ""

        self.upgrade_program_available = 0
        self.upgrade_program_available_datetime = ""

    def get_notification_count(self):
        self.get_notifications_as_string()

        count = 0
        for enabled_msg in [self.restart_service_enabled, self.reboot_system_enabled,
                            app_cached_variables.software_update_available]:
            if enabled_msg:
                count += 1
        return count

    def manage_service_restart(self):
        if not self.restart_service_enabled:
            self.restart_service_enabled = 1
            self.restart_service_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    def manage_system_reboot(self):
        if not self.reboot_system_enabled:
            self.reboot_system_enabled = 1
            self.reboot_system_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    def get_notifications_as_string(self):
        self.notifications_list = []
        return_notes = ""

        if self.restart_service_enabled:
            name = "Program Restart Required<br>Click Here to Restart now"
            self.add_notification_entry(name, "Restart Program", "/RestartServices", self.restart_service_datetime)

        if self.reboot_system_enabled:
            name = "System Reboot Required<br>Click Here to Reboot now"
            self.add_notification_entry(name, "Reboot System", "/RebootSystem", self.reboot_system_datetime)

        if app_cached_variables.software_update_available:
            current_ver = software_version.CreateRefinedVersion(software_version.version)
            latest_std_ver = software_version.CreateRefinedVersion(app_cached_variables.standard_version_available)

            new_and_current_versions = "<br>Current: " + current_ver.get_version_string() + \
                                       " -> New: " + latest_std_ver.get_version_string() + "<br>"
            upgrade_url = "/UpgradeOnline"
            current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            if latest_std_ver.major_version > current_ver.major_version:
                name = "Major Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
                self.add_notification_entry(name, "Upgrade Program?", upgrade_url, current_datetime)
            elif latest_std_ver.major_version == current_ver.major_version:
                if latest_std_ver.feature_version > current_ver.feature_version:
                    name = "Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
                    self.add_notification_entry(name, "Upgrade Program?", upgrade_url, current_datetime)
                elif latest_std_ver.feature_version == current_ver.feature_version:
                    if latest_std_ver.minor_version > current_ver.minor_version:
                        name = "Minor Update Available" + new_and_current_versions + "Click Here to update now"
                        self.add_notification_entry(name, "Update Program?", upgrade_url, current_datetime)
        for note in self.notifications_list:
            return_notes += str(note)
        return return_notes

    def add_notification_entry(self, notify_text, msg_prompt, msg_url, datetime_entry):
        return_text = """
        <li class="dropdown-menu-item">
            <a onclick="NotificationConfirmAction('{{ MessagePrompt }}', '{{ URL }}')" class="dropdown-menu-link">
                <div>
                    <i class="fas fa-gift"></i>
                </div>
                <span>
                    {{ NotificationText }}
                    <br>
                    <span>
                        {{ DateTime }}
                    </span>
                </span>
            </a>
        </li>
        <br>
        """
        return_text = return_text.replace("{{ NotificationText }}", notify_text)
        return_text = return_text.replace("{{ DateTime }}", datetime_entry)
        return_text = return_text.replace("{{ MessagePrompt }}", msg_prompt)
        return_text = return_text.replace("{{ URL }}", msg_url)

        self.notifications_list.append(return_text)


html_sensor_readings_row = """
    <div class='col-2 col-m-4 col-sm-6'>
        <div class="card">
            <div class="card-content">
                <div class="readings-header">{{ SensorName }}</div>
                <div class="readings">{{ SensorReading }}</div>
            </div>
        </div>
    </div>
"""

# Save disk read time when upgrade in progress
if software_version.old_version == software_version.version:
    html_pure_css = get_file_content(file_locations.html_report_pure_css).strip()
    html_pure_css_menu = get_file_content(file_locations.html_pure_css_menu).strip()
    html_report_css = get_file_content(file_locations.html_report_css).strip()
    html_report_js = get_file_content(file_locations.html_report_js).strip()

    html_report_combo = get_file_content(file_locations.html_combo_report).strip()
    html_report_combo = html_report_combo.replace("{{ ReportCSSStyles }}", html_report_css)
    html_report_combo = html_report_combo.replace("{{ PureCSS }}", html_pure_css)
    html_report_combo = html_report_combo.replace("{{ PureCSSHorizontalMenu }}", html_pure_css_menu)

    html_report_start = get_file_content(file_locations.html_report_all_start).strip()
    html_report_start = html_report_start.replace("{{ ReportCSSStyles }}", html_report_css)
    html_report_end = get_file_content(file_locations.html_report_all_end).strip()
    html_report_end = html_report_end.replace("{{ ReportJavaScript }}", html_report_js)

    html_report_system = get_file_content(file_locations.html_report_system).strip()
    html_report_system_sensor_template = get_file_content(file_locations.html_report_system_sensor_template).strip()

    html_report_config = get_file_content(file_locations.html_report_config).strip()
    html_report_config_sensor_template = get_file_content(file_locations.html_report_config_sensor_template).strip()

    html_report_sensors_readings = get_file_content(file_locations.html_report_sensor_readings).strip()
    html_report_sensor_readings_template = get_file_content(file_locations.html_report_sensor_readings_template).strip()

    html_report_latency = get_file_content(file_locations.html_report_sensor_latency).strip()
    html_report_latency_sensor_template = get_file_content(file_locations.html_report_sensor_latency_template).strip()

atpro_notifications = CreateATProMenuNotificationClass()
