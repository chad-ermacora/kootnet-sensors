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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function
from operations_modules.app_validation_checks import email_is_valid
from operations_modules.email_server import send_test_email, send_report_email, send_db_graph_email
from configuration_modules import app_config_access
from http_server.server_http_generic_functions import get_html_checkbox_state, get_html_selected_state
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page

html_atpro_settings_email_routes = Blueprint("html_atpro_settings_email_routes", __name__)
email_config = app_config_access.email_config


@html_atpro_settings_email_routes.route("/atpro/settings-email-reports", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_email_reports():
    if request.method == "POST":
        email_config.update_with_html_request_reports(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        app_cached_variables.restart_report_email_thread = True
        return get_message_page("Email Reports Settings Updated", page_url="sensor-settings")

    report_send_selected_options = _get_send_option_selection(email_config.send_report_every)
    return render_template(
        "ATPro_admin/page_templates/settings/settings-email-reports.html",
        CheckedEmailComboReport=get_html_checkbox_state(email_config.enable_combo_report_emails),
        EmailReportsSelectedDaily=report_send_selected_options[0],
        EmailReportsSelectedWeekly=report_send_selected_options[1],
        EmailReportsSelectedMonthly=report_send_selected_options[2],
        EmailReportsSelectedYearly=report_send_selected_options[3],
        EmailReportAtHourMin=email_config.email_reports_time_of_day,
        EmailReportsToCSVAddresses=email_config.send_report_to_csv_emails
    )


def _get_send_option_selection(selected_send_every):
    send_options = [
        app_config_access.email_config.send_option_daily, app_config_access.email_config.send_option_weekly,
        app_config_access.email_config.send_option_monthly, app_config_access.email_config.send_option_yearly
    ]

    selected_values = []
    for send_type in send_options:
        if selected_send_every == send_type:
            selected_values.append("selected")
        else:
            selected_values.append("")
    return selected_values


@html_atpro_settings_email_routes.route("/atpro/settings-email-graphs", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_email_graphs():
    if request.method == "POST":
        email_config.update_with_html_request_graph(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        app_cached_variables.restart_graph_email_thread = True
        return get_message_page("Email Graph Settings Updated", page_url="sensor-settings")
    graph_send_selected_options = _get_send_option_selection(email_config.send_graph_every)
    return render_template("ATPro_admin/page_templates/settings/settings-email-graphs.html",
                           CheckedEmailGraphs=get_html_checkbox_state(email_config.enable_graph_emails),
                           EmailGraphSelectedDaily=graph_send_selected_options[0],
                           EmailGraphSelectedWeekly=graph_send_selected_options[1],
                           EmailGraphSelectedMonthly=graph_send_selected_options[2],
                           EmailGraphSelectedYearly=graph_send_selected_options[3],
                           EmailGraphAtHourMin=email_config.email_graph_time_of_day,
                           EmailGraphsToCSVAddresses=email_config.send_graphs_to_csv_emails)


@html_atpro_settings_email_routes.route("/atpro/settings-email-settings", methods=["GET", "POST"])
@auth.login_required
def html_atpro_sensor_settings_email_smtp():
    if request.method == "POST":
        email_config.update_with_html_request_server(request)
        email_config.update_configuration_settings_list()
        email_config.save_config_to_file()
        return get_message_page("Email SMTP Settings Updated", page_url="sensor-settings")
    checked_cs_none = ""
    if not email_config.server_smtp_tls_enabled and not email_config.server_smtp_ssl_enabled:
        checked_cs_none = get_html_selected_state(True)
    return render_template("ATPro_admin/page_templates/settings/settings-email-smtp.html",
                           ServerSendingEmail=email_config.server_sending_email,
                           ServerSMTPAddress=email_config.server_smtp_address,
                           CheckedCS_None=checked_cs_none,
                           CheckedCS_SSL=get_html_selected_state(email_config.server_smtp_ssl_enabled),
                           CheckedCS_TLS=get_html_selected_state(email_config.server_smtp_tls_enabled),
                           ServerSMTPPort=email_config.server_smtp_port,
                           ServerSMTPUser=email_config.server_smtp_user)


@html_atpro_settings_email_routes.route("/atpro/test-email", methods=["POST"])
@auth.login_required
def html_atpro_send_reports_email():
    logger.network_logger.debug("** HTML Reports Email Sent - Source: " + str(request.remote_addr))
    button_pressed = request.form.get("test_email_button")
    email_address = request.form.get("test_email_address")

    msg = "Check the Network logs for more information"
    if email_is_valid(email_address):
        if button_pressed == "reports":
            thread_function(send_report_email, args=email_address)
            return get_message_page("Reports email is being sent", msg, page_url="sensor-settings")
        elif button_pressed == "graphs":
            thread_function(send_db_graph_email, args=email_address)
            return get_message_page("Graph email is being sent", msg, page_url="sensor-settings")
        elif button_pressed == "settings":
            thread_function(send_test_email, args=email_address)
            return get_message_page("Test email is being sent", msg, page_url="sensor-settings")
    return get_message_page("Please Specify a valid email address to send to", page_url="sensor-settings")
