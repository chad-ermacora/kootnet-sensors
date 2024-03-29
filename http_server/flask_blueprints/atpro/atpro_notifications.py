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
from configuration_modules.app_config_access import upgrades_config
from operations_modules.app_generic_classes import CreateRefinedVersion
from operations_modules.software_version import version

js_function_okay_prompt = "NotificationOkay"
js_function_confirm_prompt = "NotificationConfirmAction"
network_system_commands = app_cached_variables.network_system_commands


class CreateATProMenuNotificationClass:
    def __init__(self):
        self._notifications_dic = {}

        self.notification_count = 0
        self.notification_str = ""

        self._default_login_enabled = None
        self._new_upgrade_available_name = None
        self._upgrade_in_progress_dic_name = None
        self._restart_service_enabled = 0
        self._reboot_system_enabled = 0

    def add_custom_message(self, msg, click_msg, js_action=js_function_okay_prompt, icon="fas fa-info-circle"):
        return self._add_notification_entry(
            [msg, click_msg, "#/", datetime.utcnow().strftime("%Y-%m-%d %H:%M")],
            js_action=js_action, icon=icon
        )

    def manage_default_login_detected(self, enable=True):
        if enable and self._default_login_enabled is None:
            click_msg = "Default login of kootnet/sensors has been detected. "
            click_msg += "Please goto System -> Change Login and update the login"
            notification_short_msg = "Warning: Default Login Detected<br>Click Here for more information"
            self._default_login_enabled = self._add_notification_entry(
                [notification_short_msg, click_msg, "#/", datetime.utcnow().strftime("%Y-%m-%d %H:%M")],
                js_action=js_function_okay_prompt, icon="fas fa-exclamation-triangle"
            )
        if not enable and self._default_login_enabled is not None:
            del self._notifications_dic[self._default_login_enabled]
            self._default_login_enabled = None
            self._update_notification_str()

    def update_ks_upgrade_available(self, new_version_available):
        if self._new_upgrade_available_name is not None:
            del self._notifications_dic[self._new_upgrade_available_name]
            self._update_notification_str()
        current_ver = CreateRefinedVersion(version)
        latest_std_ver = CreateRefinedVersion(new_version_available)
        var_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        upgrade_url = self._get_ks_upgrade_url()
        update_icon = "fas fa-arrow-alt-circle-up"
        click_msg = "Upgrade Program?"
        new_and_current_versions = "<br>Current: " + current_ver.get_version_string() + \
                                   " -> New: " + latest_std_ver.get_version_string() + "<br>"

        dic_index = None
        if latest_std_ver.major_version > current_ver.major_version:
            msg = "Major Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
            dic_index = self._add_notification_entry([msg, click_msg, upgrade_url, var_datetime], icon=update_icon)
        elif latest_std_ver.major_version == current_ver.major_version:
            if latest_std_ver.feature_version > current_ver.feature_version:
                msg = "Upgrade Available" + new_and_current_versions + "Click Here to Upgrade now"
                dic_index = self._add_notification_entry([msg, click_msg, upgrade_url, var_datetime], icon=update_icon)
            elif latest_std_ver.feature_version == current_ver.feature_version:
                if latest_std_ver.minor_version > current_ver.minor_version:
                    msg = "Minor Update Available" + new_and_current_versions + "Click Here to update now"
                    dic_index = self._add_notification_entry(
                        [msg, click_msg, upgrade_url, var_datetime], icon=update_icon
                    )
        self._new_upgrade_available_name = dic_index

    @staticmethod
    def _get_ks_upgrade_url():
        upgrade_url = network_system_commands.upgrade_http
        if upgrades_config.selected_upgrade_type == upgrades_config.upgrade_type_smb:
            upgrade_url = network_system_commands.upgrade_smb
        return "/" + upgrade_url

    def manage_ks_upgrade_running(self, upgrade_type_short_str="", upgrade_type_long_str="", enable=True):
        if enable and self._upgrade_in_progress_dic_name is None:
            msg = "KS " + upgrade_type_short_str + " upgrade in progress ...<br>Click Here for more information"
            click_msg = "Kootnet Sensors is currently doing a " + upgrade_type_long_str + " Upgrade. " + \
                        "Once complete, the software will restart and this message will disappear"
            js_action = js_function_okay_prompt
            icon = "fas fa-info-circle"

            self._upgrade_in_progress_dic_name = self._add_notification_entry(
                [msg, click_msg, "#/", datetime.utcnow().strftime("%Y-%m-%d %H:%M")],
                js_action=js_action, icon=icon
            )
        else:
            if self._upgrade_in_progress_dic_name is not None:
                del self._notifications_dic[self._upgrade_in_progress_dic_name]
                self._upgrade_in_progress_dic_name = None
                self._update_notification_str()

    def manage_service_restart(self):
        click_msg = "Please Restart Kootnet Sensors"
        msg = "Program Restart Required"
        js_action = js_function_okay_prompt
        if app_cached_variables.running_as_service and app_cached_variables.running_with_root:
            msg = "Program Restart Required<br>Click Here to Restart now"
            js_action = js_function_confirm_prompt

        if not self._restart_service_enabled:
            self._restart_service_enabled = 1
            var_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            self._add_notification_entry([msg, click_msg, "/RestartServices", var_datetime], js_action=js_action)

    def manage_system_reboot(self):
        msg = "System Reboot Required"
        js_action = js_function_okay_prompt
        if app_cached_variables.running_with_root:
            msg = "System Reboot Required<br>Click Here to Reboot now"
            js_action = js_function_confirm_prompt

        if not self._reboot_system_enabled:
            self._reboot_system_enabled = 1
            var_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            msg2 = "Please Reboot System"
            self._add_notification_entry([msg, msg2, "/RebootSystem", var_datetime], js_action=js_action)

    def _add_notification_entry(self, options_list, js_action=js_function_confirm_prompt, icon="fas fa-info-circle"):
        return_text = _html_confirm_action_notification_text.replace("{{ NotificationText }}", options_list[0])
        return_text = return_text.replace("{{ MessagePrompt }}", options_list[1])
        return_text = return_text.replace("{{ URL }}", options_list[2])
        return_text = return_text.replace("{{ DateTime }}", options_list[3])
        return_text = return_text.replace("{{ JSAction }}", js_action)
        return_text = return_text.replace("{{ Icon }}", icon)

        notification_name = "notification" + str(self.notification_count + 1)
        self._notifications_dic.update({notification_name: return_text})
        self._update_notification_str()
        return notification_name

    def _update_notification_str(self):
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
