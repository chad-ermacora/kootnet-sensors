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
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 15
        self.config_settings_names = [
            "SMTP send from email address", "SMTP server address", "Enable SMTP SSL",
            "SMTP server port #", "SMTP user name", "SMTP password", "Enable Reports email server",
            "Send Report every (daily, weekly, monthly, yearly)", "Send Report to CSV emails",
            "Enable Graph email server", "Sending Graph every (daily, weekly, monthly, yearly)",
            "Send Graph to CSV emails", "Email Report at time of day", "Email Graph at time of day", "Enable SMTP TLS"
        ]

        # If set to 1+, emails are sent on program start for Graphs and Reports (They must be enabled)
        self.send_on_start = 0

        self.server_sending_email = ""
        self.server_smtp_address = ""
        self.server_smtp_ssl_enabled = 0
        self.server_smtp_tls_enabled = 0
        self.server_smtp_port = 25
        self.server_smtp_user = ""
        self.server_smtp_password = ""

        self.send_option_daily = "daily"
        self.send_option_weekly = "weekly"
        self.send_option_monthly = "monthly"
        self.send_option_yearly = "yearly"

        self.enable_combo_report_emails = 0
        self.send_report_every = self.send_option_monthly
        self.email_reports_time_of_day = "07:00"
        self.send_report_to_csv_emails = ""

        self.enable_graph_emails = 0
        self.send_graph_every = self.send_option_monthly
        self.email_graph_time_of_day = "07:00"
        self.send_graphs_to_csv_emails = ""

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
            self.send_report_every = html_request.form.get("email_reports_send_interval")
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
            self.send_graph_every = html_request.form.get("email_graph_send_interval")
        if html_request.form.get("send_email_graph_at_time") is not None:
            self.email_graph_time_of_day = html_request.form.get("send_email_graph_at_time")
        if html_request.form.get("send_graphs_to_email_address") is not None:
            send_graphs_to_csv_emails = html_request.form.get("send_graphs_to_email_address")
            self.send_graphs_to_csv_emails = _validate_csv_emails(send_graphs_to_csv_emails)
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
        self.server_smtp_tls_enabled = 0
        email_security = html_request.form.get("email_security")
        if email_security is not None:
            if email_security == "email_security_ssl":
                self.server_smtp_ssl_enabled = 1
            elif email_security == "email_security_tls":
                self.server_smtp_tls_enabled = 1

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
            str(self.enable_combo_report_emails), self.send_report_every, str(self.send_report_to_csv_emails),
            str(self.enable_graph_emails), self.send_graph_every, str(self.send_graphs_to_csv_emails),
            str(self.email_reports_time_of_day), str(self.email_graph_time_of_day), str(self.server_smtp_tls_enabled)
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
            self.send_report_every = self.config_settings[7].strip()
            self.send_report_to_csv_emails = self.config_settings[8].strip()

            self.enable_graph_emails = int(self.config_settings[9].strip())
            self.send_graph_every = self.config_settings[10].strip()
            self.send_graphs_to_csv_emails = self.config_settings[11].strip()

            self.email_reports_time_of_day = self.config_settings[12].strip()
            self.email_graph_time_of_day = self.config_settings[13].strip()
            self.server_smtp_tls_enabled = int(self.config_settings[14].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Email Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Email Configuration.")
                self.save_config_to_file()


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
