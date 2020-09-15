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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration
from operations_modules.app_validation_checks import email_is_valid


class CreateEmailConfiguration(CreateGeneralConfiguration):
    """ Creates the Email Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.email_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 31
        self.config_settings_names = [
            "SMTP send from email address", "SMTP server address", "Enable SMTP SSL/TLS", "SMTP server port #",
            "SMTP user name", "SMTP password", "Enable Reports email server", "Send Report every",
            "Send Report to CSV emails", "Enable Graph email server", "Sending Graph every", "Graph the past hours",
            "Graph type (0=Quick Graph, 1=Plotly Graph)", "Send Graph to CSV emails", "Graph sensor uptime",
            "Graph CPU temperature", "Graph environmental temperature", "Graph pressure", "Graph altitude",
            "Graph humidity", "Graph distance", "Graph GAS", "Graph particulate matter", "Graph lumen", "Graph color",
            "Graph ultra violet", "Graph accelerometer", "Graph magnetometer", "Graph gyroscope",
            "Email Report at time of day", "Email Graph at time of day"
        ]

        # If set to 1+, emails are sent on program start for Graphs and Reports (They must be enabled)
        self.send_on_start = 0

        self.server_sending_email = ""
        self.server_smtp_address = ""
        self.server_smtp_ssl_enabled = 0
        self.server_smtp_port = 587
        self.server_smtp_user = ""
        self.server_smtp_password = ""

        self.enable_combo_report_emails = 0
        self.email_reports_daily = False
        self.email_reports_weekly = False
        self.email_reports_monthly = False
        self.email_reports_yearly = False
        self.email_reports_time_of_day = "07:00"
        self.send_report_to_csv_emails = ""

        self.enable_graph_emails = 0
        self.email_graph_daily = False
        self.email_graph_weekly = False
        self.email_graph_monthly = False
        self.email_graph_yearly = False
        self.email_graph_time_of_day = "07:00"
        self.graph_past_hours = 48
        self.graph_type = 0  # 0 = Quick Graph / 1+ = Plotly Graph
        self.send_graphs_to_csv_emails = ""

        # Enable or Disable Sensors to Graph.  0 = Disabled, 1 = Enabled
        self.sensor_uptime = 1
        self.system_temperature = 1
        self.env_temperature = 1
        self.pressure = 0
        self.altitude = 0
        self.humidity = 1
        self.distance = 0
        self.gas = 0
        self.particulate_matter = 0
        self.lumen = 0
        self.color = 0
        self.ultra_violet = 0
        self.accelerometer = 0
        self.magnetometer = 0
        self.gyroscope = 0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request_reports(self, html_request):
        """ Updates the email reports configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Email Reports Configuration Update Check")

        self.enable_combo_report_emails = 0
        if html_request.form.get("email_combo_report") is not None:
            self.enable_combo_report_emails = 1
        if html_request.form.get("email_reports_send_interval") is not None:
            interval_type = html_request.form.get("email_reports_send_interval")
            self.email_reports_daily = False
            self.email_reports_weekly = False
            self.email_reports_monthly = False
            self.email_reports_yearly = False

            if interval_type == "daily":
                self.email_reports_daily = True
            elif interval_type == "weekly":
                self.email_reports_weekly = True
            elif interval_type == "monthly":
                self.email_reports_monthly = True
            elif interval_type == "yearly":
                self.email_reports_yearly = True
        if html_request.form.get("send_email_report_at_time") is not None:
            self.email_reports_time_of_day = html_request.form.get("send_email_report_at_time")
        if html_request.form.get("send_reports_to_email_address") is not None:
            send_report_to_csv_emails = html_request.form.get("send_reports_to_email_address")
            self.send_report_to_csv_emails = _validate_csv_emails(send_report_to_csv_emails)
        self.update_configuration_settings_list()

    def update_with_html_request_graph(self, html_request):
        """ Updates the email graph configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Email Graph Configuration Update Check")

        self.enable_graph_emails = 0
        if html_request.form.get("email_graphs") is not None:
            self.enable_graph_emails = 1
        if html_request.form.get("email_graph_send_interval") is not None:
            interval_type = html_request.form.get("email_graph_send_interval")
            self.email_graph_daily = False
            self.email_graph_weekly = False
            self.email_graph_monthly = False
            self.email_graph_yearly = False

            if interval_type == "daily":
                self.email_graph_daily = True
            elif interval_type == "weekly":
                self.email_graph_weekly = True
            elif interval_type == "monthly":
                self.email_graph_monthly = True
            elif interval_type == "yearly":
                self.email_graph_yearly = True
        if html_request.form.get("send_email_graph_at_time") is not None:
            self.email_graph_time_of_day = html_request.form.get("send_email_graph_at_time")
        if html_request.form.get("send_graphs_to_email_address") is not None:
            send_graphs_to_csv_emails = html_request.form.get("send_graphs_to_email_address")
            self.send_graphs_to_csv_emails = _validate_csv_emails(send_graphs_to_csv_emails)

        self.sensor_uptime = 0
        self.system_temperature = 0
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.distance = 0
        self.gas = 0
        self.particulate_matter = 0
        self.lumen = 0
        self.color = 0
        self.ultra_violet = 0
        self.accelerometer = 0
        self.magnetometer = 0
        self.gyroscope = 0

        if html_request.form.get("graph_type") == "QuickGraphs":
            self.graph_type = 0
        elif html_request.form.get("graph_type") == "PlotlyGraphs":
            self.graph_type = 1

        if html_request.form.get("graph_past_hours") is not None:
            self.graph_past_hours = float(html_request.form.get("graph_past_hours"))

        if html_request.form.get("SensorUptime") is not None:
            self.sensor_uptime = 1
        if html_request.form.get("CPUTemp") is not None:
            self.system_temperature = 1
        if html_request.form.get("EnvTemp") is not None:
            self.env_temperature = 1
        if html_request.form.get("Pressure") is not None:
            self.pressure = 1
        if html_request.form.get("Altitude") is not None:
            self.altitude = 1
        if html_request.form.get("Humidity") is not None:
            self.humidity = 1
        if html_request.form.get("Distance") is not None:
            self.distance = 1
        if html_request.form.get("Gas") is not None:
            self.gas = 1
        if html_request.form.get("ParticulateMatter") is not None:
            self.particulate_matter = 1
        if html_request.form.get("Lumen") is not None:
            self.lumen = 1
        if html_request.form.get("Colours") is not None:
            self.color = 1
        if html_request.form.get("UltraViolet") is not None:
            self.ultra_violet = 1
        if html_request.form.get("Accelerometer") is not None:
            self.accelerometer = 1
        if html_request.form.get("Magnetometer") is not None:
            self.magnetometer = 1
        if html_request.form.get("Gyroscope") is not None:
            self.gyroscope = 1
        self.update_configuration_settings_list()

    def update_with_html_request_server(self, html_request):
        """ Updates the email server configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Email Server Configuration Update Check")

        if html_request.form.get("server_sending_email") is not None:
            server_sending_email = html_request.form.get("server_sending_email").strip()
            if email_is_valid(server_sending_email):
                self.server_sending_email = server_sending_email
        if html_request.form.get("server_smtp_address") is not None:
            self.server_smtp_address = html_request.form.get("server_smtp_address")

        self.server_smtp_ssl_enabled = 0
        if html_request.form.get("email_ssl") is not None:
            self.server_smtp_ssl_enabled = 1

        if html_request.form.get("server_smtp_port") is not None:
            self.server_smtp_port = int(html_request.form.get("server_smtp_port"))
        if html_request.form.get("server_smtp_user") is not None:
            self.server_smtp_user = html_request.form.get("server_smtp_user")
        if html_request.form.get("server_smtp_password") != "":
            self.server_smtp_password = html_request.form.get("server_smtp_password")
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.server_sending_email), str(self.server_smtp_address), str(self.server_smtp_ssl_enabled),
            str(self.server_smtp_port), str(self.server_smtp_user), str(self.server_smtp_password),
            str(self.enable_combo_report_emails), self._get_report_text_interval(),
            str(self.send_report_to_csv_emails), str(self.enable_graph_emails), self._get_graph_text_interval(),
            str(self.graph_past_hours), str(self.graph_type), str(self.send_graphs_to_csv_emails),
            str(self.sensor_uptime), str(self.system_temperature), str(self.env_temperature), str(self.pressure),
            str(self.altitude), str(self.humidity), str(self.distance), str(self.gas), str(self.particulate_matter),
            str(self.lumen), str(self.color), str(self.ultra_violet), str(self.accelerometer), str(self.magnetometer),
            str(self.gyroscope), str(self.email_reports_time_of_day), str(self.email_graph_time_of_day)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.server_sending_email = self.config_settings[0].strip()
            self.server_smtp_address = self.config_settings[1].strip()
            self.server_smtp_ssl_enabled = int(self.config_settings[2].strip())
            self.server_smtp_port = int(self.config_settings[3].strip())
            self.server_smtp_user = self.config_settings[4].strip()
            self.server_smtp_password = self.config_settings[5].strip()
            self.enable_combo_report_emails = int(self.config_settings[6].strip())

            temp_report_resend = self.config_settings[7].strip()
            self.email_reports_daily = False
            self.email_reports_weekly = False
            self.email_reports_monthly = False
            self.email_reports_yearly = False
            if temp_report_resend == "daily":
                self.email_reports_daily = True
            elif temp_report_resend == "weekly":
                self.email_reports_weekly = True
            elif temp_report_resend == "monthly":
                self.email_reports_monthly = True
            elif temp_report_resend == "yearly":
                self.email_reports_yearly = True

            self.send_report_to_csv_emails = self.config_settings[8].strip()
            self.enable_graph_emails = int(self.config_settings[9].strip())

            temp_graph_resend = self.config_settings[10].strip()
            self.email_graph_daily = False
            self.email_graph_weekly = False
            self.email_graph_monthly = False
            self.email_graph_yearly = False
            if temp_graph_resend == "daily":
                self.email_graph_daily = True
            elif temp_graph_resend == "weekly":
                self.email_graph_weekly = True
            elif temp_graph_resend == "monthly":
                self.email_graph_monthly = True
            elif temp_graph_resend == "yearly":
                self.email_graph_yearly = True

            self.graph_past_hours = float(self.config_settings[11].strip())
            self.graph_type = int(self.config_settings[12].strip())
            self.send_graphs_to_csv_emails = self.config_settings[13].strip()
            self.sensor_uptime = int(self.config_settings[14].strip())
            self.system_temperature = int(self.config_settings[15].strip())
            self.env_temperature = int(self.config_settings[16].strip())
            self.pressure = int(self.config_settings[17].strip())
            self.altitude = int(self.config_settings[18].strip())
            self.humidity = int(self.config_settings[19].strip())
            self.distance = int(self.config_settings[20].strip())
            self.gas = int(self.config_settings[21].strip())
            self.particulate_matter = int(self.config_settings[22].strip())
            self.lumen = int(self.config_settings[23].strip())
            self.color = int(self.config_settings[24].strip())
            self.ultra_violet = int(self.config_settings[25].strip())
            self.accelerometer = int(self.config_settings[26].strip())
            self.magnetometer = int(self.config_settings[27].strip())
            self.gyroscope = int(self.config_settings[28].strip())
            self.email_reports_time_of_day = self.config_settings[29].strip()
            self.email_graph_time_of_day = self.config_settings[30].strip()
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Email Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Email Configuration.")
                self.save_config_to_file()

    def _get_report_text_interval(self):
        if self.email_reports_daily:
            return "daily"
        elif self.email_reports_weekly:
            return "weekly"
        elif self.email_reports_monthly:
            return "monthly"
        elif self.email_reports_yearly:
            return "yearly"

    def _get_graph_text_interval(self):
        if self.email_graph_daily:
            return "daily"
        elif self.email_graph_weekly:
            return "weekly"
        elif self.email_graph_monthly:
            return "monthly"
        elif self.email_graph_yearly:
            return "yearly"


def _validate_csv_emails(csv_emails_string):
    """ Checks provided CSV string of emails for valid emails. Returns CSV string of valid emails. """

    return_string = ""
    try:
        for email in csv_emails_string.split(","):
            if email_is_valid(email.strip()):
                return_string += email.strip() + ","
        if len(return_string) > 0:
            return_string = return_string[:-1]
    except Exception as error:
        logger.primary_logger.error("Error Checking CSV Emails: " + str(error))
    return return_string
