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
import psutil
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import software_version
from operations_modules.app_generic_functions import get_file_content


class CreateATProMenuNotificationClass:
    def __init__(self):
        self.notifications_list = []

        self.restart_service_enabled = 0
        self.reboot_system_enabled = 0

    def get_notifications_as_string(self):
        self.notifications_list = []
        return_notes = ""

        if self.restart_service_enabled:
            name = "Program Restart Required<br>Click Here to Restart now"
            html_script = self.get_button_to_url_script("Restart Program", "/RestartServices")
            self.add_notification_entry(name, html_script)
        if self.reboot_system_enabled:
            name = "System Reboot Required<br>Click Here to Reboot now"
            html_script = self.get_button_to_url_script("Reboot System", "/RebootSystem")
            self.add_notification_entry(name, html_script)

        for note in self.notifications_list:
            return_notes += str(note)
        return return_notes

    def add_notification_entry(self, notify_text, html_script):
        function_name = "function" + str(len(self.notifications_list) + 1)

        return_text = """
        <li class="dropdown-menu-item">
            <a onclick="{{ FunctionName }}()" class="dropdown-menu-link">
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
            <script>
                {{ Script }}
            </script>
        </li>
        """
        return_text = return_text.replace("{{ NotificationText }}", notify_text)
        return_text = return_text.replace("{{ DateTime }}", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return_text = return_text.replace("{{ FunctionName }}", function_name)

        html_script = html_script.replace("{{ FunctionName }}", function_name)
        return_text = return_text.replace("{{ Script }}", html_script)

        self.notifications_list.append(return_text)

    @staticmethod
    def get_button_to_url_script(button_text, html_link):
        html_return_script = """
        function {{ FunctionName }}() {
            let r = confirm("{{ ButtonText }}");
            if (r === true) {
                window.location = "{{ HTMLLink }}"
            }
        }"""
        html_return_script = html_return_script.replace("{{ ButtonText }}", button_text)
        html_return_script = html_return_script.replace("{{ HTMLLink }}", html_link)
        return html_return_script


def get_ram_free():
    try:
        ram_available = psutil.virtual_memory().available
        ram_available = round((ram_available / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.network_logger.error("Dashboard - Getting Free RAM: " + str(error))
        ram_available = "Error"
    return ram_available


def get_disk_free():
    try:
        disk_available = psutil.disk_usage(file_locations.sensor_data_dir).free
        disk_available = round((disk_available / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.network_logger.error("Dashboard - Getting Free Disk Space: " + str(error))
        disk_available = "Error"
    return disk_available


html_sensor_readings_row = """
<div class="col-3 col-m-6 col-sm-12">
    <div class="counter bg-primary">
        <span class='sensor-info'>{{ SensorName }}</span><br>
        <span class='reading-value'>{{ SensorReading }}</span>
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
