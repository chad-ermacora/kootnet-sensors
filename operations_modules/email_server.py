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
from operations_modules.app_validation_checks import email_is_valid
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.remote_management import rm_cached_variables
from http_server.flask_blueprints.atpro.remote_management.rm_reports import generate_html_reports_combo
from http_server.flask_blueprints.atpro.atpro_graphing import generate_plotly_graph
from http_server import server_plotly_graph_variables


def send_test_email(to_email):
    message = get_new_email_message("Kootnet Sensor Test Email")
    body_text = "This is a test email from a Kootnet Sensor. " + \
                "\nThis Email was sent at " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC0, Sensor Time." + \
                "\n\nKootnet Sensor Information\nSensorName: " + app_cached_variables.hostname + \
                "\nIP: " + app_cached_variables.ip + \
                "\nKootnet Sensors Version: " + software_version.version
    message.attach(MIMEText(body_text, "plain"))
    send_email(to_email, message)


def send_report_emails(email_address_list):
    generate_html_reports_combo(app_config_access.email_reports_config.get_raw_ip_addresses_as_list())
    while rm_cached_variables.creating_combo_report:
        sleep(5)

    message = get_new_email_message("Kootnet Sensor Report - " + app_cached_variables.hostname)
    message.attach(MIMEText(_get_default_email_body_text("HTML Report"), "plain"))
    date_time = datetime.utcnow().strftime("Y%Y-M%m-D%d-h%H-m%M")
    filename = app_cached_variables.hostname + "_" + date_time + "_KS_Report"
    zipped_report = zip_files([filename + ".html"], [rm_cached_variables.html_combo_report])
    payload = MIMEBase("application", "zip")
    payload.set_payload(zipped_report.read())
    encoders.encode_base64(payload)
    payload.add_header("Content-Disposition", "attachment", filename=filename + ".zip")
    message.attach(payload)

    for email_address in email_address_list:
        send_email(email_address, message)


def send_db_graph_emails(email_address_list):
    generate_plotly_graph(None, graph_config=app_config_access.email_db_graph_config)
    sleep(5)
    while server_plotly_graph_variables.graph_creation_in_progress:
        sleep(5)

    date_time = datetime.utcnow().strftime("Y%Y-M%m-D%d-h%H-m%M")
    filename = app_cached_variables.hostname + "_" + date_time + "_KS_Graph"
    message = get_new_email_message("Kootnet Sensor Graph - " + app_cached_variables.hostname)
    message.attach(MIMEText(_get_default_email_body_text("Plotly Graph"), "plain"))

    try:
        zipped_graph = zip_files(
            [filename + ".html"],
            [get_file_content(app_config_access.email_db_graph_config.plotly_graph_saved_location, open_type="rb")]
        )
        payload = MIMEBase("application", "zip")
        payload.set_payload(zipped_graph.read())
        encoders.encode_base64(payload)
        payload.add_header("Content-Disposition", "attachment", filename=filename + ".zip")
        message.attach(payload)
    except Exception as error:
        logger.network_logger.error("Graph Email did not send: " + str(error))
        payload = MIMEText("\n\nError Generating Zip of Plotly Graph\n\n", "plain")
        message.attach(payload)

    for email_address in email_address_list:
        send_email(email_address, message)


def get_new_email_message(email_subject):
    message = MIMEMultipart()
    message["Subject"] = email_subject
    message["From"] = app_config_access.email_config.server_sending_email
    message["Date"] = utils.formatdate()
    message["Message-ID"] = utils.make_msgid()
    return message


def send_email(receiver_email, message):
    smtp_server = app_config_access.email_config.server_smtp_address
    port = app_config_access.email_config.server_smtp_port
    sender_email = app_config_access.email_config.server_sending_email
    login = app_config_access.email_config.server_smtp_user
    password = app_config_access.email_config.server_smtp_password

    try:
        receiver_email = receiver_email.strip()
        if not email_is_valid(receiver_email):
            logger.network_logger.warning("Invalid Email found in Email list: " + str(receiver_email))
        else:
            message["To"] = receiver_email
            if app_config_access.email_config.server_smtp_ssl_enabled:
                smtp_connection = smtplib.SMTP_SSL(smtp_server, port)
            elif app_config_access.email_config.server_smtp_tls_enabled:
                smtp_connection = smtplib.SMTP(smtp_server, port)
                smtp_connection.starttls()
            else:
                smtp_connection = smtplib.SMTP(smtp_server, port)
            smtp_connection.ehlo()
            smtp_connection.login(login, password)
            smtp_connection.sendmail(sender_email, receiver_email, message.as_string())
            smtp_connection.close()
            logger.network_logger.info("Email Sent OK - '" + str(message["Subject"]) + "'")
    except (gaierror, ConnectionRefusedError):
        logger.network_logger.error("Failed to connect to the server. Bad connection settings?")
    except smtplib.SMTPServerDisconnected:
        logger.network_logger.error("Failed to connect to the server. Wrong user/password?")
    except smtplib.SMTPException as error:
        logger.network_logger.error("SMTP error occurred: " + str(error))
    except Exception as error:
        logger.network_logger.error("SMTP Unknown error: " + str(error))


def _get_default_email_body_text(attachment_name):
    email_message = "Your " + attachment_name + " should be in a zip file attached to this email." + \
                    "\nThis Email was sent at " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + \
                    " UTC0, Sensor Time." + \
                    "\n\nKootnet Sensor Information\nSensorName: " + app_cached_variables.hostname + \
                    "\nIP: " + app_cached_variables.ip + \
                    "\nKootnet Sensors Version: " + software_version.version
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
        send_report_emails(app_config_access.email_config.send_report_to_csv_emails.split(","))

    while not app_cached_variables.restart_report_email_thread:
        send_report_every = app_config_access.email_config.send_report_every
        email_reports_time_of_day = app_config_access.email_config.email_reports_time_of_day
        main_sleep = _get_email_send_sleep_time(send_report_every, email_reports_time_of_day)
        sleep_total = 0
        while sleep_total < main_sleep and not app_cached_variables.restart_report_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_report_email_thread:
            send_report_emails(app_config_access.email_config.send_report_to_csv_emails.split(","))
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
        send_db_graph_emails(app_config_access.email_config.send_graphs_to_csv_emails.split(","))

    while not app_cached_variables.restart_graph_email_thread:
        sleep_total = 0
        send_graph_every = app_config_access.email_config.send_graph_every
        email_graph_time_of_day = app_config_access.email_config.email_graph_time_of_day
        main_sleep = _get_email_send_sleep_time(send_graph_every, email_graph_time_of_day)
        while sleep_total < main_sleep and not app_cached_variables.restart_graph_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_graph_email_thread:
            send_db_graph_emails(app_config_access.email_config.send_graphs_to_csv_emails.split(","))
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
