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
from datetime import datetime, timedelta
from time import sleep
from threading import Thread
import smtplib
from email import utils, encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from socket import gaierror
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import software_version
from operations_modules.app_generic_classes import CreateMonitoredThread
from operations_modules.app_generic_functions import zip_files
from operations_modules.app_generic_disk import get_file_content
from operations_modules.app_validation_checks import get_validate_csv_emails
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables
from http_server.flask_blueprints.atpro.remote_management.rm_reports import generate_html_reports_combo
from http_server.flask_blueprints.atpro.atpro_graphing import generate_plotly_graph
from http_server import server_plotly_graph_variables

get_clean_db_col_name = app_cached_variables.database_variables.get_clean_db_col_name


class CreateSensorReadingEmailAlert:
    def __init__(self, sensor_name, high_trigger, low_trigger):
        """
        Creates a thread to send email alerts when readings are added using add_trigger_email_entry()
        Email frequency is limited based on settings in the High/Low trigger configuration.
        When an email is sent, it sends all readings in self.alerts_to_send_list then empties the list.
        :param sensor_name: Database column name of the sensor reading
        :param high_trigger: Value at which the sensor reading is considered "High"
        :param low_trigger: Value at which the sensor reading is considered "Low"
        """
        self.sensor_name = sensor_name
        self.high_trigger = high_trigger
        self.low_trigger = low_trigger

        self.email_alert_last_sent = datetime(1920, 1, 1, 1, 1, 1)
        self.alerts_to_send_list = []
        email_alert_thread = Thread(target=self._start_email_alert_send_thread_worker)
        email_alert_thread.daemon = True
        email_alert_thread.start()

    def add_trigger_email_entry(self, reading_value, reading_state):
        """
        Takes reading_value and reading_state and adds a dictionary of them, along with the datetime, to the
        self.alerts_to_send_list variable to be emailed at a later time based on email frequency setting.
        :param reading_value: The current sensor reading that triggered an alert
        :param reading_state: The current sensor state that was triggered (High/Normal/Low)
        :return: Nothing
        """
        self.alerts_to_send_list.append({"reading_value": reading_value,
                                         "reading_state": reading_state,
                                         "datetime": datetime.utcnow()})

    def _start_email_alert_send_thread_worker(self):
        """
        Every 30 seconds, checks to see if there are any alert emails ready to be sent, if so, it checks to make sure
        enough time has passed since last sending an email, based on the email frequency found in
        the High/Low trigger configuration. If this passes, it sends the alerts.
        :return: Nothing
        """
        while True:
            try:
                if len(self.alerts_to_send_list):
                    time_since_last_email_sent = datetime.utcnow() - self.email_alert_last_sent
                    _send_delay_in_hours = app_config_access.trigger_high_low.alerts_resend_emails_every_hours
                    send_delay_in_hours = timedelta(hours=_send_delay_in_hours)
                    if time_since_last_email_sent >= send_delay_in_hours:
                        self.email_alert_last_sent = datetime.utcnow()
                        self._send_email_alert()
                sleep(30)
            except Exception as error:
                logger.primary_logger.error(f"Email Alert - {self.sensor_name}: " + str(error))

    def _send_email_alert(self):
        """
        Sends an email containing all the sensor's alerts since the last time it sent an email of alerts.
        Clears all email alerts after creating the email.
        :return: Nothing
        """
        email_subject = self._get_email_subject_text()
        email_body_html = self._get_email_body_html()
        self.alerts_to_send_list = []
        csv_emails = app_config_access.trigger_high_low.alerts_csv_emails
        email_alert_thread = Thread(target=send_emails, args=(csv_emails, email_subject, email_body_html))
        email_alert_thread.daemon = True
        email_alert_thread.start()

    def _get_email_subject_text(self):
        """
        Returns email subject line in plain text based on system's hostname and the sensor's name.
        :return: Subject line for trigger emails in plain text
        """
        return f"{app_cached_variables.hostname} Trigger(s) - {get_clean_db_col_name(self.sensor_name)}"

    def _get_email_body_html(self):
        """
        Creates and returns the email's main body text in HTML based on the alerts in self.alerts_to_send_list
        :return: Email body in HTML
        """
        total_alerts = str(len(self.alerts_to_send_list))
        return_text = f"The {get_clean_db_col_name(self.sensor_name)} Sensor " + \
                      f"has been triggered {total_alerts} time(s) on " + \
                      f"{app_cached_variables.hostname}<br>" + \
                      f"High Trigger: <b>{str(self.high_trigger)}</b><br>" + \
                      f"Low Trigger: <b>{str(self.low_trigger)}</b><br><br>"

        if len(self.alerts_to_send_list) > 200:
            return_text += f"{total_alerts} trigger entries found<br>Showing the last 200<br><br>"
            self.alerts_to_send_list = self.alerts_to_send_list[:-200]

        for alert_entry in self.alerts_to_send_list:
            utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
            entry_datetime = alert_entry["datetime"] + timedelta(hours=utc0_hour_offset)
            state = alert_entry["reading_state"]
            reading = alert_entry["reading_value"]
            return_text += f"DateTime: <b>{str(entry_datetime)[:-7]} UTC{str(utc0_hour_offset)}</b><br>" + \
                           f"Trigger: <b>{state}</b><br>" + \
                           f"Reading: <b>{reading}</b><br><br>"
        return return_text


def send_test_email(to_email):
    """
    Sends a simple test email to the provided email address.
    :param to_email: Email to send a test email to
    :return: Nothing
    """
    body_text = "This is a test email from a Kootnet Sensor. " + \
                "<br>This Email was sent at " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC0, Sensor Time." + \
                "<br><br>Kootnet Sensor Information<br>SensorName: " + app_cached_variables.hostname + \
                "<br>IP: " + app_cached_variables.ip + \
                "<br>Kootnet Sensors Version: " + software_version.version
    send_emails(to_email, "Kootnet Sensor Test Email", body_text)


def send_report_emails(csv_emails):
    """
    If csv_emails is not empty, generate a combination report and send it to the provided emails.
    :param csv_emails: Text containing CSV email addresses
    :return: Nothing
    """
    if len(csv_emails):
        generate_html_reports_combo(app_config_access.email_reports_config.get_raw_ip_addresses_as_list())
        # Sleep for 5 seconds to ensure the "creating_combo_report" variable has been set
        sleep(5)

        while rm_cached_variables.creating_combo_report:
            sleep(5)

        date_time = datetime.utcnow().strftime("Y%Y-M%m-D%d-h%H-m%M")
        filename = app_cached_variables.hostname + "_" + date_time + "_KS_Report"
        subj = f"Kootnet Sensor Report - {app_cached_variables.hostname}"
        msg = _get_default_attachment_email_body_text(f"{filename}.zip")
        zipped_report = zip_files([filename + ".html"], [rm_cached_variables.html_combo_report])

        send_emails(csv_emails, subj, msg, attachment_name=f"{filename}.zip", attachment=zipped_report.read())


def send_db_graph_emails(csv_emails):
    """
    If csv_emails is not empty, generate a Plotly graph and send it to the provided emails.
    :param csv_emails: Text containing CSV email addresses
    :return: Nothing
    """
    if len(csv_emails):
        generate_plotly_graph(None, graph_config=app_config_access.email_db_graph_config)
        # Sleep for 5 seconds to ensure the "graph_creation_in_progress" variable has been set
        sleep(5)

        while server_plotly_graph_variables.graph_creation_in_progress:
            sleep(5)

        date_time = datetime.utcnow().strftime("Y%Y-M%m-D%d-h%H-m%M")
        subj = f"Kootnet Sensor Graph - {app_cached_variables.hostname}"
        filename = f"{app_cached_variables.hostname}_{date_time}_KS_Graph"
        msg = _get_default_attachment_email_body_text(f"{filename}.zip")
        plotly_graph_saved_location = app_config_access.email_db_graph_config.plotly_graph_saved_location
        file_content = get_file_content(plotly_graph_saved_location, open_type="rb")
        zipped_graph = zip_files([filename + ".html"], [file_content])

        send_emails(csv_emails, subj, msg, attachment_name=f"{filename}.zip", attachment=zipped_graph.read())


def _get_default_attachment_email_body_text(attachment_name):
    """
    Returns the HTML code used in the body of an email when the email is all about the attachment.
    :param attachment_name: Name of the attached file in text
    :return: Email body (in HTML) for sending attachments
    """
    email_message = f"{attachment_name} is attached to this email.<br>This Email was sent at " + \
                    f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC0, Sensor Time." + \
                    f"<br><br>Kootnet Sensor Information<br>SensorName: {app_cached_variables.hostname}" + \
                    f"<br>IP: {app_cached_variables.ip}" + \
                    f"<br>Kootnet Sensors Version: {software_version.version}"
    return email_message


def start_report_email_server():
    text_name = "Report Email Server"
    function = _report_email_server
    app_cached_variables.report_email_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.email_config.enable_combo_report_emails:
        logger.primary_logger.debug("Report Emails Disabled in Configuration")
        app_cached_variables.report_email_thread.current_state = "Disabled"


def _report_email_server():
    sleep(10)
    app_cached_variables.report_email_thread.current_state = "Disabled"
    while not app_config_access.email_config.enable_combo_report_emails:
        sleep(5)
    app_cached_variables.report_email_thread.current_state = "Running"
    app_cached_variables.restart_report_email_thread = False

    if app_config_access.email_config.send_on_start:
        send_report_emails(app_config_access.email_config.send_report_to_csv_emails)

    while not app_cached_variables.restart_report_email_thread:
        send_report_every = app_config_access.email_config.send_report_every
        email_reports_time_of_day = app_config_access.email_config.email_reports_time_of_day
        main_sleep = _get_email_send_sleep_time(send_report_every, email_reports_time_of_day)
        sleep_total = 0
        while sleep_total < main_sleep and not app_cached_variables.restart_report_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_report_email_thread:
            send_report_emails(app_config_access.email_config.send_report_to_csv_emails)
            logger.network_logger.debug("Report Emails Sent")


def start_graph_email_server():
    text_name = "Graph Email Server"
    function = _graph_email_server
    app_cached_variables.graph_email_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.email_config.enable_graph_emails:
        logger.primary_logger.debug("Graph Emails Disabled in Configuration")
        app_cached_variables.graph_email_thread.current_state = "Disabled"


def _graph_email_server():
    sleep(10)
    app_cached_variables.graph_email_thread.current_state = "Disabled"
    while not app_config_access.email_config.enable_graph_emails:
        sleep(5)
    app_cached_variables.graph_email_thread.current_state = "Running"
    app_cached_variables.restart_graph_email_thread = False

    if app_config_access.email_config.send_on_start:
        send_db_graph_emails(app_config_access.email_config.send_graphs_to_csv_emails)

    while not app_cached_variables.restart_graph_email_thread:
        sleep_total = 0
        send_graph_every = app_config_access.email_config.send_graph_every
        email_graph_time_of_day = app_config_access.email_config.email_graph_time_of_day
        main_sleep = _get_email_send_sleep_time(send_graph_every, email_graph_time_of_day)
        while sleep_total < main_sleep and not app_cached_variables.restart_graph_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_graph_email_thread:
            send_db_graph_emails(app_config_access.email_config.send_graphs_to_csv_emails)
        logger.network_logger.debug("Graph Emails Sent")


def _get_email_send_sleep_time(send_every, sleep_time_of_day):
    sleep_seconds = 604800
    hour = int(sleep_time_of_day[0:2])
    minute = int(sleep_time_of_day[3:5])

    if send_every == app_config_access.email_config.send_option_daily:
        sleep_seconds = _get_email_sleep_seconds(day=1, hour=hour, minutes=minute)
    elif send_every == app_config_access.email_config.send_option_weekly:
        sleep_seconds = _get_email_sleep_seconds(day=7, hour=hour, minutes=minute)
    elif send_every == app_config_access.email_config.send_option_monthly:
        sleep_seconds = _get_email_sleep_seconds(month=1, hour=hour, minutes=minute)
    elif send_every == app_config_access.email_config.send_option_yearly:
        sleep_seconds = _get_email_sleep_seconds(year=1, hour=hour, minutes=minute)
    return sleep_seconds


def _get_email_sleep_seconds(year=0, month=0, day=0, hour=8, minutes=0):
    """ Returns seconds between now and the years/months/days from now at the provided hour/minute """
    try:
        total_add_time = timedelta()
        if year:
            total_add_time += timedelta(weeks=52 * year)
        if month:
            total_add_time += timedelta(weeks=4 * month)
        if day:
            total_add_time += timedelta(days=day)

        utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
        adjusted_utc_now = datetime.utcnow() + timedelta(hours=utc0_hour_offset)
        adjusted_utc0_total_time = adjusted_utc_now + total_add_time

        if adjusted_utc0_total_time.hour == hour:
            if adjusted_utc0_total_time.minute < minutes:
                adjusted_utc0_total_time = adjusted_utc0_total_time - timedelta(days=1)
        elif adjusted_utc0_total_time.hour < hour:
            adjusted_utc0_total_time = adjusted_utc0_total_time - timedelta(days=1)

        temp_time_str = adjusted_utc0_total_time.strftime("%Y-%m-%d_" + str(hour) + ":" + str(minutes))
        next_datetime = datetime.strptime(temp_time_str, "%Y-%m-%d_%H:%M") - adjusted_utc_now
        return int(next_datetime.total_seconds())
    except Exception as error:
        logger.primary_logger.warning("Getting email sleep time in seconds error: " + str(error))
    return 604800  # 1 week


def send_emails(csv_email_addresses, subject, body_text, attachment_name="", attachment=None):
    """
    Takes text containing CSV emails of where to send the email along with the email subject line and email body HTML.
    Sends the email to all valid email addresses.
    Optional: Attach file to the email.
    :param csv_email_addresses: CSV emails text
    :param subject: Email subject line in text
    :param body_text: Email body in HTML
    :param attachment_name: Optional: The name of the attached file in text
    :param attachment: Optional: A file to attach to the email - Requires attachment_name to be provided
    :return: Nothing
    """
    if app_config_access.email_config.check_if_smtp_configured():
        smtp_server = app_config_access.email_config.server_smtp_address
        port = app_config_access.email_config.server_smtp_port
        sender_email = app_config_access.email_config.server_sending_email
        login = app_config_access.email_config.server_smtp_user
        password = app_config_access.email_config.server_smtp_password

        validated_email_address_list = get_validate_csv_emails(csv_email_addresses).split(",")
        if len(validated_email_address_list) > 0:
            for receiver_email in validated_email_address_list:
                try:
                    new_email = MIMEMultipart()
                    new_email["Subject"] = subject
                    new_email["From"] = app_config_access.email_config.server_sending_email
                    new_email["To"] = receiver_email
                    new_email["Date"] = utils.formatdate()
                    new_email["Message-ID"] = utils.make_msgid()
                    new_email.attach(MIMEText(body_text, "html"))
                    if attachment is not None and attachment_name != "":
                        _attach_file_to_email(new_email, attachment_name, attachment)

                    if app_config_access.email_config.server_smtp_ssl_enabled:
                        smtp_connection = smtplib.SMTP_SSL(smtp_server, port)
                    elif app_config_access.email_config.server_smtp_tls_enabled:
                        smtp_connection = smtplib.SMTP(smtp_server, port)
                        smtp_connection.starttls()
                    else:
                        smtp_connection = smtplib.SMTP(smtp_server, port)
                    smtp_connection.ehlo()
                    smtp_connection.login(login, password)
                    smtp_connection.sendmail(sender_email, receiver_email, new_email.as_string())
                    smtp_connection.close()
                    logger.network_logger.info("Email Sent OK - '" + str(new_email["Subject"]) + "'")
                except (gaierror, ConnectionRefusedError):
                    logger.network_logger.error("Failed to connect to the server. Bad connection settings?")
                except smtplib.SMTPServerDisconnected:
                    logger.network_logger.error("Failed to connect to the server. Wrong user/password?")
                except smtplib.SMTPException as error:
                    logger.network_logger.error("SMTP error occurred: " + str(error))
                except Exception as error:
                    logger.network_logger.error("SMTP Unknown error: " + str(error))
    else:
        logger.network_logger.warning("Email not sent - SMTP Not Configured")


def _attach_file_to_email(email_message, attachment_file_name, attachment_file):
    """
    Attaches a file to a MIMEMultipart() object.
    :param email_message: MIMEMultipart() object
    :param attachment_file_name: The attachment's filename in text
    :param attachment_file: The contents of the attachment
    :return: Nothing
    """
    try:
        attachment_type = attachment_file_name.split(".")[-1]
        if attachment_type == "zip":
            payload = MIMEBase("application", "zip")
            payload.set_payload(attachment_file)
            encoders.encode_base64(payload)
        elif attachment_type == "html":
            payload = MIMEText(attachment_file, "html")
        else:
            payload = MIMEText(attachment_file, "text")

        payload.add_header("Content-Disposition", "attachment", filename=attachment_file_name)
        email_message.attach(payload)
    except Exception as error:
        logger.network_logger.error("Unable to add attachment to email: " + str(error))
        payload = MIMEText("<br><br>Error Adding file to Email<br><br>", "html")
        email_message.attach(payload)
