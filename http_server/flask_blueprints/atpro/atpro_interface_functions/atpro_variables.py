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
import psutil
from operations_modules import logger
from operations_modules import file_locations
from datetime import datetime, timedelta
from operations_modules import app_cached_variables


class CreateATProVariablesClass:
    def __init__(self):
        self.notification_count = 0
        self.notifications_list = []

    def init_tests(self):
        self.add_notification_entry("Restart Required",
                                    self.get_button_to_url_script("Restart Service", "/RestartServices"))
        self.add_notification_entry("Reboot", self.get_button_to_url_script("Reboot", "/RebootSystem"))
        self.add_notification_entry("Shutdown", self.get_button_to_url_script("Shutdown", "/ShutdownSystem"))

    def get_notifications_as_string(self):
        return_notes = ""
        for note in self.notifications_list:
            return_notes += str(note)
        return return_notes

    def add_notification_entry(self, notify_text, html_script):
        function_name = "function" + str(app_cached_variables.notes_total_count + 1)

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
        self.notification_count = len(self.notifications_list)

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
    return str(ram_available) + " GB"


def get_disk_free():
    try:
        disk_available = psutil.disk_usage(file_locations.sensor_data_dir).free
        disk_available = round((disk_available / 1024 / 1024 / 1024), 2)
    except Exception as error:
        logger.network_logger.error("Dashboard - Getting Free Disk Space: " + str(error))
        disk_available = "Error"
    return str(disk_available) + " GB"


html_sensor_readings_row = """
<div class="row">
    <div class="col-6 col-m-8 col-sm-12">
        <div class="card">
            <div class="card-content">
                <table>
                    <thead>
                        <tr>
                            <th>Sensor Name</th>
                            <th>Sensor Reading</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{ Readings }}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
"""

atpro_variables = CreateATProVariablesClass()
