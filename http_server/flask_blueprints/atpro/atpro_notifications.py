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
from operations_modules import app_cached_variables
from operations_modules import software_version


class CreateATProMenuNotificationClass:
    def __init__(self):
        self._notifications_dic = {}

        self.notification_count = 0
        self.notification_str = ""

        self._restart_service_enabled = 0
        self._reboot_system_enabled = 0
        self._upgrade_program_enabled = 0

    def add_custom_message(self, msg, click_msg, js_action="NotificationOkay", icon="fas fa-info-circle"):
        self._add_notification_entry([msg, click_msg, "#/", datetime.utcnow().strftime("%Y-%m-%d %H:%M")],
                                     js_action=js_action, icon=icon)

    def manage_service_restart(self):
        click_msg = "Please Restart Kootnet Sensors"
        msg = "Program Restart Required"
        js_action = "NotificationOkay"
        if app_cached_variables.running_as_service and app_cached_variables.running_with_root:
            msg = "Program Restart Required<br>Click Here to Restart now"
            js_action = "NotificationConfirmAction"

        if not self._restart_service_enabled:
            self._restart_service_enabled = 1
            restart_service_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            self._add_notification_entry([msg, click_msg, "/RestartServices", restart_service_datetime],
                                         js_action=js_action)

    def manage_system_reboot(self):
        msg = "System Reboot Required"
        js_action = "NotificationOkay"
        if app_cached_variables.running_with_root:
            msg = "System Reboot Required<br>Click Here to Reboot now"
            js_action = "NotificationConfirmAction"

        if not self._reboot_system_enabled:
            self._reboot_system_enabled = 1
            reboot_system_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            self._add_notification_entry([msg, "Please Reboot System", "/RebootSystem", reboot_system_datetime],
                                         js_action=js_action)

    def check_updates(self):
        if app_cached_variables.running_with_root and app_cached_variables.running_as_service:
            if app_cached_variables.software_update_available and not self._upgrade_program_enabled:
                self._upgrade_program_enabled = 1
                current_ver = software_version.CreateRefinedVersion(software_version.version)
                latest_std_ver = software_version.CreateRefinedVersion(app_cached_variables.standard_version_available)

                current_ver_str = current_ver.get_version_string()
                latest_std_ver_str = latest_std_ver.get_version_string()
                new_and_current_versions = "<br>Current: " + current_ver_str + " -> New: " + latest_std_ver_str + "<br>"
                upgrade_url = "/UpgradeOnline"
                current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                update_icon = "fas fa-arrow-alt-circle-up"
                if latest_std_ver.major_version > current_ver.major_version:
                    msg = "Major Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
                    self._add_notification_entry([msg, "Upgrade Program?", upgrade_url,
                                                 current_datetime], icon=update_icon)
                elif latest_std_ver.major_version == current_ver.major_version:
                    if latest_std_ver.feature_version > current_ver.feature_version:
                        msg = "Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
                        self._add_notification_entry([msg, "Upgrade Program?", upgrade_url,
                                                     current_datetime], icon=update_icon)
                    elif latest_std_ver.feature_version == current_ver.feature_version:
                        if latest_std_ver.minor_version > current_ver.minor_version:
                            msg = "Minor Update Available" + new_and_current_versions + "Click Here to update now"
                            self._add_notification_entry([msg, "Update Program?", upgrade_url,
                                                         current_datetime], icon=update_icon)

    def _add_notification_entry(self, options_list, js_action="NotificationConfirmAction", icon="fas fa-info-circle"):
        return_text = _html_confirm_action_notification_text.replace("{{ NotificationText }}", options_list[0])
        return_text = return_text.replace("{{ MessagePrompt }}", options_list[1])
        return_text = return_text.replace("{{ URL }}", options_list[2])
        return_text = return_text.replace("{{ DateTime }}", options_list[3])
        return_text = return_text.replace("{{ JSAction }}", js_action)
        return_text = return_text.replace("{{ Icon }}", icon)

        notification_name = "notification" + str(len(self._notifications_dic))
        self._notifications_dic.update({notification_name: return_text})
        self.notification_count = len(self._notifications_dic)

        self.notification_str = ""
        for notification in self._notifications_dic:
            self.notification_str += self._notifications_dic[notification]


_html_confirm_action_notification_text = """
<li class="dropdown-menu-item">
    <a onclick="{{ JSAction }}('{{ MessagePrompt }}', '{{ URL }}')" class="dropdown-menu-link">
        <div>
            <i class="{{ Icon }}"></i>
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

atpro_notifications = CreateATProMenuNotificationClass()
