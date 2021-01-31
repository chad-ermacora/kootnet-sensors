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
from dateutil.relativedelta import relativedelta
from time import sleep
import smtplib
import ssl
from email import utils, encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from socket import gaierror
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import software_version
from operations_modules.app_generic_functions import zip_files, CreateMonitoredThread
from operations_modules.app_validation_checks import email_is_valid
from configuration_modules import app_config_access
from http_server.flask_blueprints.sensor_control_files.sensor_control_functions import generate_html_reports_combo
from http_server.flask_blueprints.graphing_quick import get_html_live_graphing_page

email_config = app_config_access.email_config


def send_test_email(to_email):
    message = get_new_email_message(to_email, "Kootnet Sensor Test Email")
    body_text = "This is a test email from a Kootnet Sensor. " + \
                "\nThis Email was sent at " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC0, Sensor Time." + \
                "\n\nKootnet Sensor Information\nSensorName: " + app_cached_variables.hostname + \
                "\nIP: " + app_cached_variables.ip + \
                "\nKootnet Sensors Version: " + software_version.version
    message.attach(MIMEText(body_text, "plain"))
    send_email(to_email, message)


def send_report_email(to_email, report_generated=False):
    message = get_new_email_message(to_email, "Kootnet Sensor Report - " + app_cached_variables.hostname)
    message.attach(MIMEText(_get_default_email_body_text("HTML Report"), "plain"))

    if not report_generated:
        ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
        generate_html_reports_combo(ip_list)

    html_filename = app_cached_variables.hostname + "_KootnetSensorReport.html"
    zip_filename = app_cached_variables.hostname + "_KSReport.zip"
    zipped_report = zip_files([html_filename], [app_cached_variables.html_combo_report])
    payload = MIMEBase("application", "zip")
    payload.set_payload(zipped_report.read())
    encoders.encode_base64(payload)
    payload.add_header("Content-Disposition", "attachment", filename=zip_filename)
    message.attach(payload)
    send_email(to_email, message)


def send_quick_graph_email(to_email, graph=None):
    _set_graphs_to_include()
    message = get_new_email_message(to_email, "Kootnet Sensor Graph - " + app_cached_variables.hostname)
    message.attach(MIMEText(_get_default_email_body_text("Quick Graph"), "plain"))
    if graph is None:
        quick_graph = get_html_live_graphing_page(email_graph=True)
        quick_graph = _update_quick_graph_for_email(quick_graph)
    else:
        quick_graph = graph

    html_filename = app_cached_variables.hostname + "_KootnetSensorGraph.html"
    zip_filename = app_cached_variables.hostname + "_KSGraph.zip"
    zipped_graph = zip_files([html_filename], [quick_graph])
    payload = MIMEBase("application", "zip")
    payload.set_payload(zipped_graph.read())
    encoders.encode_base64(payload)
    payload.add_header("Content-Disposition", "attachment", filename=zip_filename)
    message.attach(payload)
    send_email(to_email, message)


def _set_graphs_to_include():
    app_cached_variables.quick_graph_uptime = email_config.sensor_uptime
    app_cached_variables.quick_graph_cpu_temp = email_config.system_temperature
    app_cached_variables.quick_graph_env_temp = email_config.env_temperature
    app_cached_variables.quick_graph_pressure = email_config.pressure
    app_cached_variables.quick_graph_altitude = email_config.altitude
    app_cached_variables.quick_graph_humidity = email_config.humidity
    app_cached_variables.quick_graph_distance = email_config.distance
    app_cached_variables.quick_graph_gas = email_config.gas
    app_cached_variables.quick_graph_particulate_matter = email_config.particulate_matter
    app_cached_variables.quick_graph_lumen = email_config.lumen
    app_cached_variables.quick_graph_colours = email_config.color
    app_cached_variables.quick_graph_ultra_violet = email_config.ultra_violet
    app_cached_variables.quick_graph_acc = email_config.accelerometer
    app_cached_variables.quick_graph_mag = email_config.magnetometer
    app_cached_variables.quick_graph_gyro = email_config.gyroscope


def _update_quick_graph_for_email(quick_graph):
    old_chart = """<script src="/Chart.min.js"></script>"""
    new_chart = """<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.bundle.js" integrity="sha512-G8JE1Xbr0egZE5gNGyUm1fF764iHVfRXshIoUWCTPAbKkkItp/6qal5YAHXrxEu4HNfPTQs6HOu3D5vCGS1j3w==" crossorigin="anonymous"></script>"""
    old_mui_min_css = """<link href="/mui.min.css" rel="stylesheet" type="text/css"/>"""
    new_mui_min_css = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mui/3.7.1/css/mui.min.css" integrity="sha512-uclHupzhjfJ5Zbsweb6eEK3HyTUpSfiWq/+ORo20uQLZg3yI5Jg4iCZYOD5Q1Q5Ftm4FG9kCzwT82bVcNgFMRw==" crossorigin="anonymous" />"""
    old_mui_colors_min_css = """<link href="/mui-colors.min.css" rel="stylesheet" type="text/css"/>"""
    new_mui_colors_min_css = """<link href="//cdn.muicss.com/mui-0.10.3/extra/mui-colors.min.css" rel="stylesheet" type="text/css" />"""

    quick_graph = quick_graph.replace(">Refresh", " disabled>Refresh")
    quick_graph = quick_graph.replace(old_chart, new_chart)
    quick_graph = quick_graph.replace(old_mui_min_css, new_mui_min_css)
    quick_graph = quick_graph.replace(old_mui_colors_min_css, new_mui_colors_min_css)
    return quick_graph


def get_new_email_message(to_email, email_subject):
    message = MIMEMultipart()
    message["Subject"] = email_subject
    message["From"] = app_config_access.email_config.server_sending_email
    message["To"] = to_email
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
        if app_config_access.email_config.server_smtp_ssl_enabled:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(login, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
        else:
            with smtplib.SMTP(smtp_server, port) as server:
                server.login(login, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
    except (gaierror, ConnectionRefusedError):
        logger.network_logger.error("Failed to connect to the server. Bad connection settings?")
    except smtplib.SMTPServerDisconnected:
        logger.network_logger.error("Failed to connect to the server. Wrong user/password?")
    except smtplib.SMTPException as error:
        logger.network_logger.error("SMTP error occurred: " + str(error))
    else:
        logger.network_logger.debug("Email Sent OK")


def _get_default_email_body_text(attachment_name):
    email_message = "Your " + attachment_name + " should be in a zip file attached to this email." + \
                    "\nThis Email was sent at " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC0, Sensor Time." + \
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
        for email in app_config_access.email_config.send_report_to_csv_emails.split(","):
            email = email.strip()
            if email_is_valid(email):
                send_report_email(email)
                sleep(5)
            else:
                logger.network_logger.warning("Invalid Email found in Report Emails")
    while not app_cached_variables.restart_report_email_thread:
        main_sleep = _get_email_send_sleep_time(email_config.send_report_every, email_config.email_reports_time_of_day)
        sleep_total = 0
        while sleep_total < main_sleep and not app_cached_variables.restart_report_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_report_email_thread:
            try:
                ip_list = app_config_access.sensor_control_config.get_clean_ip_addresses_as_list()
                generate_html_reports_combo(ip_list)
                for email in app_config_access.email_config.send_report_to_csv_emails.split(","):
                    email = email.strip()
                    if email_is_valid(email):
                        send_report_email(email, report_generated=True)
                        sleep(5)
                    else:
                        logger.network_logger.warning("Invalid Email found in Report Emails")
            except Exception as error:
                logger.network_logger.error("Problem sending Report emails: " + str(error))
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
        for email in app_config_access.email_config.send_graphs_to_csv_emails.split(","):
            email = email.strip()
            if email_is_valid(email):
                send_quick_graph_email(email)
                sleep(5)
            else:
                logger.network_logger.warning("Invalid Email found in Graph Emails")

    while not app_cached_variables.restart_graph_email_thread:
        sleep_total = 0
        main_sleep = _get_email_send_sleep_time(email_config.send_graph_every, email_config.email_graph_time_of_day)
        while sleep_total < main_sleep and not app_cached_variables.restart_graph_email_thread:
            sleep(5)
            sleep_total += 5
        if not app_cached_variables.restart_graph_email_thread:
            try:
                quick_graph = get_html_live_graphing_page(email_graph=True)
                quick_graph = _update_quick_graph_for_email(quick_graph)
                for email in app_config_access.email_config.send_graphs_to_csv_emails.split(","):
                    email = email.strip()
                    if email_is_valid(email):
                        send_quick_graph_email(email, graph=quick_graph)
                        sleep(5)
                    else:
                        logger.network_logger.warning("Invalid Email found in Graph Emails")
            except Exception as error:
                logger.network_logger.error("Problem sending Graph emails: " + str(error))
        logger.network_logger.debug("Graph Emails Sent")


def _get_email_send_sleep_time(send_every, sleep_time_of_day):
    sleep_seconds = 604800
    hour = int(sleep_time_of_day[0:2])
    minute = int(sleep_time_of_day[3:5])

    if send_every == email_config.send_option_daily:
        sleep_seconds = _get_email_sleep_seconds(day=1, hour=hour, minute=minute)
    elif send_every == email_config.send_option_weekly:
        sleep_seconds = _get_email_sleep_seconds(day=7, hour=hour, minute=minute)
    elif send_every == email_config.send_option_monthly:
        sleep_seconds = _get_email_sleep_seconds(month=1, hour=hour, minute=minute)
    elif send_every == email_config.send_option_yearly:
        sleep_seconds = _get_email_sleep_seconds(year=1, hour=hour, minute=minute)
    return sleep_seconds


def _get_email_sleep_seconds(year=0, month=0, day=0, hour=8, minute=0):
    """ Returns seconds between now and the years/months/days from now at the provided hour/minute """
    try:
        adjusted_utc_now = datetime.utcnow() + relativedelta(hours=app_config_access.primary_config.utc0_hour_offset)
        next_datetime = adjusted_utc_now + relativedelta(years=year, months=month, days=day, hour=hour, minute=minute)

        if not year and not month and day == 1:
            if adjusted_utc_now.hour <= hour:
                if adjusted_utc_now.hour < hour:
                    hours_in_seconds = ((hour - adjusted_utc_now.hour) * 60 * 60)
                    minutes_in_seconds = ((minute - adjusted_utc_now.minute) * 60)
                    return_total_seconds = hours_in_seconds + minutes_in_seconds
                    return return_total_seconds
                elif adjusted_utc_now.minute < minute:
                    return_total_seconds = ((minute - adjusted_utc_now.minute) * 60)
                    return return_total_seconds
        return_total_seconds = (next_datetime - adjusted_utc_now).total_seconds()
        return return_total_seconds
    except Exception as error:
        logger.primary_logger.warning("Getting email sleep time in seconds error: " + str(error))
    return 604800  # 1 week
