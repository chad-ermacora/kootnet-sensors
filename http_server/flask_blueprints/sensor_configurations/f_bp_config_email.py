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
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_hidden_state, get_html_checkbox_state, \
    message_and_return, get_html_selected_state
from operations_modules.email_server import send_test_email, send_report_email, send_quick_graph_email

html_email_routes = Blueprint("html_email_routes", __name__)
email_config = app_config_access.email_config


@html_email_routes.route("/EmailConfigurationsHTML")
@auth.login_required
def html_get_config_email_page():
    logger.network_logger.debug("** Sensor Email Configuration accessed from " + str(request.remote_addr))

    quick_graph_checked = "checked"
    plotly_graph_checked = ""
    if email_config.graph_type:
        plotly_graph_checked = "checked"
        quick_graph_checked = ""

    report_send_selected_options = _get_send_option_selection(email_config.send_report_every)
    graph_send_selected_options = _get_send_option_selection(email_config.send_graph_every)
    return render_template("edit_configurations/config_email.html",
                           PageURL="/EmailConfigurationsHTML",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           CheckedEmailComboReport=get_html_checkbox_state(email_config.enable_combo_report_emails),
                           EmailReportsSelectedDaily=report_send_selected_options[0],
                           EmailReportsSelectedWeekly=report_send_selected_options[1],
                           EmailReportsSelectedMonthly=report_send_selected_options[2],
                           EmailReportsSelectedYearly=report_send_selected_options[3],
                           EmailReportAtHourMin=email_config.email_reports_time_of_day,
                           EmailReportsToCSVAddresses=email_config.send_report_to_csv_emails,
                           CheckedEmailGraphs=get_html_checkbox_state(email_config.enable_graph_emails),
                           EmailGraphSelectedDaily=graph_send_selected_options[0],
                           EmailGraphSelectedWeekly=graph_send_selected_options[1],
                           EmailGraphSelectedMonthly=graph_send_selected_options[2],
                           EmailGraphSelectedYearly=graph_send_selected_options[3],
                           EmailGraphAtHourMin=email_config.email_graph_time_of_day,
                           EmailGraphsToCSVAddresses=email_config.send_graphs_to_csv_emails,
                           QuickGraphChecked=quick_graph_checked,
                           PlotlyGraphChecked=plotly_graph_checked,
                           GraphsPastHours=email_config.graph_past_hours,
                           SensorUptimeChecked=get_html_checkbox_state(email_config.sensor_uptime),
                           CPUTemperatureChecked=get_html_checkbox_state(email_config.system_temperature),
                           EnvTemperatureChecked=get_html_checkbox_state(email_config.env_temperature),
                           PressureChecked=get_html_checkbox_state(email_config.pressure),
                           AltitudeChecked=get_html_checkbox_state(email_config.altitude),
                           HumidityChecked=get_html_checkbox_state(email_config.humidity),
                           DistanceChecked=get_html_checkbox_state(email_config.distance),
                           GasChecked=get_html_checkbox_state(email_config.gas),
                           PMChecked=get_html_checkbox_state(email_config.particulate_matter),
                           LumenChecked=get_html_checkbox_state(email_config.lumen),
                           ColoursChecked=get_html_checkbox_state(email_config.color),
                           UltraVioletChecked=get_html_checkbox_state(email_config.ultra_violet),
                           AccChecked=get_html_checkbox_state(email_config.accelerometer),
                           MagChecked=get_html_checkbox_state(email_config.magnetometer),
                           GyroChecked=get_html_checkbox_state(email_config.gyroscope),
                           ServerSendingEmail=email_config.server_sending_email,
                           ServerSMTPAddress=email_config.server_smtp_address,
                           CheckedEmailSSL=get_html_checkbox_state(email_config.server_smtp_ssl_enabled),
                           ServerSMTPPort=email_config.server_smtp_port,
                           ServerSMTPUser=email_config.server_smtp_user)


def _get_send_option_selection(selected_send_every):
    send_options = [
        email_config.send_option_daily, email_config.send_option_weekly,
        email_config.send_option_monthly, email_config.send_option_yearly
    ]

    selected_values = []
    for send_type in send_options:
        if selected_send_every == send_type:
            selected_values.append("selected")
        else:
            selected_values.append("")
    return selected_values


@html_email_routes.route("/SendTestEmail", methods=["POST"])
@auth.login_required
def html_send_test_email():
    logger.network_logger.debug("** HTML Test Email Sent - Source: " + str(request.remote_addr))
    if email_is_valid(request.form.get("test_email_address")):
        email_address = request.form.get("test_email_address")
        thread_function(send_test_email, args=email_address)
        return message_and_return("Test email is being sent", url="/EmailConfigurationsHTML")
    return message_and_return("Please Specify a valid email address to send to", url="/EmailConfigurationsHTML")


@html_email_routes.route("/SendReportsEmail", methods=["POST"])
@auth.login_required
def html_send_reports_email():
    logger.network_logger.debug("** HTML Reports Email Sent - Source: " + str(request.remote_addr))
    if email_is_valid(request.form.get("test_email_address")):
        email_address = request.form.get("test_email_address")
        thread_function(send_report_email, args=email_address)
        return message_and_return("Reports email is being sent", url="/EmailConfigurationsHTML")
    return message_and_return("Please Specify a valid email address to send to", url="/EmailConfigurationsHTML")


@html_email_routes.route("/SendGraphEmail", methods=["POST"])
@auth.login_required
def html_send_graph_email():
    logger.network_logger.debug("** HTML Graph Email Sent - Source: " + str(request.remote_addr))
    if email_is_valid(request.form.get("test_email_address")):
        email_address = request.form.get("test_email_address")
        thread_function(send_quick_graph_email, args=email_address)
        return message_and_return("Graph email is being sent", url="/EmailConfigurationsHTML")
    return message_and_return("Please Specify a valid email address to send to", url="/EmailConfigurationsHTML")


@html_email_routes.route("/UpdateReportsEmailSettings", methods=["POST"])
@auth.login_required
def html_update_reports_email_settings():
    logger.network_logger.debug("** HTML Reports Email settings updated - Source: " + str(request.remote_addr))
    email_config.update_with_html_request_reports(request)
    email_config.update_configuration_settings_list()
    email_config.save_config_to_file()
    app_cached_variables.restart_report_email_thread = True
    return html_get_config_email_page()


@html_email_routes.route("/UpdateGraphEmailSettings", methods=["POST"])
@auth.login_required
def html_update_graph_email_settings():
    logger.network_logger.debug("** HTML Graph Email settings updated - Source: " + str(request.remote_addr))
    email_config.update_with_html_request_graph(request)
    email_config.update_configuration_settings_list()
    email_config.save_config_to_file()
    app_cached_variables.restart_graph_email_thread = True
    return html_get_config_email_page()


@html_email_routes.route("/UpdateServerEmailSettings", methods=["POST"])
@auth.login_required
def html_update_server_email_settings():
    logger.network_logger.debug("** HTML Server Email settings updated - Source: " + str(request.remote_addr))
    email_config.update_with_html_request_server(request)
    email_config.update_configuration_settings_list()
    email_config.save_config_to_file()
    return html_get_config_email_page()
