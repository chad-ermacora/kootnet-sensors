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
import os
from flask import send_file
from zipfile import ZipFile, ZIP_DEFLATED
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_config_access
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import network_wifi
from operations_modules import config_trigger_variances
from operations_modules import app_generic_functions
from operations_modules import os_cli_commands
from operations_modules import app_validation_checks
from operations_modules.add_on_modules.online_services import CreateOnlineServicesConfig
from http_server import server_http_flask_render_templates
from http_server import server_http_flask_post_checks as http_post_checks
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables

text_message_may_take_minutes = "This may take a few minutes ..."


class CreateRouteFunctions:
    def __init__(self, sensor_access):
        self.sensor_access = sensor_access
        self.online_services_config = CreateOnlineServicesConfig(sensor_access)
        self.render_templates = server_http_flask_render_templates.CreateRenderTemplates(sensor_access)

    def index(self):
        return self.render_templates.index_page()

    def logout(self):
        return self.render_templates.logout()

    def auth_error(self, request):
        logger.network_logger.info(" *** First or Failed Login from " + str(request.remote_addr))
        return self.render_templates.message_and_return("Unauthorized Access")

    def html_system_information(self, request):
        logger.network_logger.debug("* Sensor Information accessed from " + str(request.remote_addr))
        return self.render_templates.system_information()

    def html_sensors_readings(self, request):
        logger.network_logger.debug("** Sensor Readings accessed from " + str(request.remote_addr))
        return self.render_templates.sensors_readings()

    def html_system_management(self, request):
        logger.network_logger.debug("** System Commands accessed from " + str(request.remote_addr))
        return self.render_templates.system_management()

    def html_view_https_config_diagnostics(self, request):
        logger.network_logger.debug("** HTTPS Configuration Diagnostics accessed from " + str(request.remote_addr))
        return self.render_templates.view_https_config_diagnostics()

    def html_online_services(self, request):
        logger.network_logger.debug("** Online Services accessed from " + str(request.remote_addr))
        return self.render_templates.sensor_online_services(self.online_services_config)

    def html_edit_online_services(self, request):
        logger.network_logger.debug("** Edit Online Services accessed from " + str(request.remote_addr))
        if request.method == "POST":
            self.online_services_config.update_weather_underground_html(request)
            if app_config_access.wu_thread_running:
                main_message = "Online Services Updated - Restarting Sensor Software"
                message2 = "New Weather Underground settings will take effect after the sensor software restarts"
                app_generic_functions.thread_function(self.sensor_access.restart_services)
            else:
                app_generic_functions.thread_function(self.online_services_config.start_weather_underground)
                main_message = "Online Services Updated"
                message2 = ""
                if request.form.get("enable_weather_underground") is not None:
                    main_message += " - Weather Underground Started"
            return self.render_templates.message_and_return(main_message,
                                                            text_message2=message2,
                                                            url="/OnlineServices")
        else:
            logger.primary_logger.error("HTML Edit Online Services set Error")
            return self.render_templates.message_and_return("Bad Configuration POST Request",
                                                            url="/OnlineServices")

    def html_edit_configurations(self, request):
        logger.network_logger.debug("** HTML Configurations accessed from " + str(request.remote_addr))
        return self.render_templates.edit_configurations()

    def html_get_log_view(self, request):
        logger.network_logger.debug("** HTML Logs accessed from " + str(request.remote_addr))
        return self.render_templates.get_log_view()

    def html_set_config_main(self, request):
        logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
        if request.method == "POST":
            try:
                http_post_checks.check_html_config_main(request)
                app_generic_functions.thread_function(self.sensor_access.restart_services)
                return self.render_templates.message_and_return("Restarting Service, Please Wait ...",
                                                                url="/ConfigurationsHTML")

            except Exception as error:
                logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
                return self.render_templates.message_and_return("Bad Configuration POST Request",
                                                                url="/ConfigurationsHTML")

    def html_set_installed_sensors(self, request):
        logger.network_logger.debug("** HTML Apply - Installed Sensors - Source " + str(request.remote_addr))
        if request.method == "POST":
            try:
                http_post_checks.check_html_installed_sensors(request)
                app_generic_functions.thread_function(self.sensor_access.restart_services)
                return self.render_templates.message_and_return("Restarting Service, Please Wait ...",
                                                                url="/ConfigurationsHTML")
            except Exception as error:
                logger.primary_logger.error("HTML Apply - Installed Sensors - Error: " + str(error))
                return self.render_templates.message_and_return("Bad Installed Sensors POST Request",
                                                                url="/ConfigurationsHTML")

    def html_set_trigger_variances(self, request):
        logger.network_logger.debug("** HTML Apply - Trigger Variances - Source " + str(request.remote_addr))
        if request.method == "POST":
            try:
                http_post_checks.check_html_variance_triggers(request)
                return self.render_templates.message_and_return("Trigger Variances Set",
                                                                url="/ConfigurationsHTML")
            except Exception as error:
                logger.primary_logger.warning("HTML Apply - Trigger Variances - Error: " + str(error))
        return self.render_templates.message_and_return("Bad Trigger Variances POST Request",
                                                        url="/ConfigurationsHTML")

    def html_reset_trigger_variances(self, request):
        logger.network_logger.info("** Trigger Variances Reset - Source " + str(request.remote_addr))
        default_trigger_variances = config_trigger_variances.CreateTriggerVariances()
        app_config_access.trigger_variances = default_trigger_variances
        config_trigger_variances.write_triggers_to_file(default_trigger_variances)
        return self.render_templates.message_and_return("Trigger Variances Reset",
                                                        url="/ConfigurationsHTML")

    def html_set_wifi_config(self, request):
        logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
        if request.method == "POST" and "ssid1" in request.form:

            if app_validation_checks.text_has_no_double_quotes(request.form.get("wifi_key1")):
                pass
            else:
                message = "Do not use double quotes in the Wireless Key Sections."
                return self.render_templates.message_and_return("Invalid Wireless Key",
                                                                text_message2=message,
                                                                url="/ConfigurationsHTML")

            if app_validation_checks.wireless_ssid_is_valid(request.form.get("ssid1")):
                new_wireless_config = http_post_checks.check_html_config_wifi(request)
                if new_wireless_config is not "":
                    return_message = "You must reboot the sensor to take effect."
                    app_generic_functions.update_cached_variables(self.sensor_access)
                    return self.render_templates.message_and_return("WiFi Configuration Updated",
                                                                    text_message2=return_message,
                                                                    url="/ConfigurationsHTML")
            else:
                return_message = "Network Names cannot be blank and can only use " + \
                                 "Alphanumeric Characters, dashes, underscores and spaces."
                return self.render_templates.message_and_return("Unable to Process Wireless Configuration",
                                                                text_message2=return_message,
                                                                url="/ConfigurationsHTML")

        return self.render_templates.message_and_return("Unable to Process WiFi Configuration",
                                                        url="/ConfigurationsHTML")

    def html_set_ipv4_config(self, request):
        logger.network_logger.debug("** HTML Apply - IPv4 Configuration - Source " + str(request.remote_addr))
        message2 = "Network settings have not been changed."
        if request.method == "POST" and app_validation_checks.hostname_is_valid(request.form.get("ip_hostname")):
            if request.form.get("ip_dhcp") is not None:
                message2 = "You must reboot for all settings to take effect."
                dhcpcd_template = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file_template)
                dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", "")
                hostname = request.form.get("ip_hostname")
                os.system("hostnamectl set-hostname " + hostname)
                app_generic_functions.write_file_to_disk(file_locations.dhcpcd_config_file, dhcpcd_template)
                app_generic_functions.update_cached_variables(self.sensor_access)
                return self.render_templates.message_and_return("IPv4 Configuration Updated",
                                                                text_message2=message2,
                                                                url="/ConfigurationsHTML")

            ip_address = request.form.get("ip_address")
            ip_subnet = request.form.get("ip_subnet")
            ip_gateway = request.form.get("ip_gateway")
            ip_dns1 = request.form.get("ip_dns1")
            ip_dns2 = request.form.get("ip_dns2")

            try:
                app_validation_checks.ip_address_is_valid(ip_address)
            except ValueError:
                return self.render_templates.message_and_return("Invalid IP Address",
                                                                text_message2=message2,
                                                                url="/ConfigurationsHTML")
            if not app_validation_checks.subnet_mask_is_valid(ip_subnet):
                return self.render_templates.message_and_return("Invalid Subnet Mask",
                                                                text_message2=message2,
                                                                url="/ConfigurationsHTML")
            if ip_gateway is not "":
                try:
                    app_validation_checks.ip_address_is_valid(ip_gateway)
                except ValueError:
                    return self.render_templates.message_and_return("Invalid Gateway",
                                                                    text_message2=message2,
                                                                    url="/ConfigurationsHTML")
            if ip_dns1 is not "":
                try:
                    app_validation_checks.ip_address_is_valid(ip_dns1)
                except ValueError:
                    return self.render_templates.message_and_return("Invalid Primary DNS Address",
                                                                    text_message2=message2,
                                                                    url="/ConfigurationsHTML")
            if ip_dns2 is not "":
                try:
                    app_validation_checks.ip_address_is_valid(ip_dns2)
                except ValueError:
                    return self.render_templates.message_and_return("Invalid Secondary DNS Address",
                                                                    text_message2=message2,
                                                                    url="/ConfigurationsHTML")

            http_post_checks.check_html_config_ipv4(request)
            app_generic_functions.update_cached_variables(self.sensor_access)
            return self.render_templates.message_and_return("IPv4 Configuration Updated",
                                                            text_message2="You must reboot the sensor to take effect.",
                                                            url="/ConfigurationsHTML")
        else:
            return_message = "Invalid or Missing Hostname.\n\n" + \
                             "Only Alphanumeric Characters, Dashes and Underscores may be used."
            return self.render_templates.message_and_return("Unable to Process IPv4 Configuration",
                                                            text_message2=return_message,
                                                            url="/ConfigurationsHTML")

    @staticmethod
    def check_online(request):
        logger.network_logger.debug("CC Sensor Status Checked by " + str(request.remote_addr))
        return "OK"

    def cc_get_sensor_readings(self, request):
        logger.network_logger.debug("* CC Sensor Readings sent to " + str(request.remote_addr))
        sensor_readings = self.sensor_access.get_sensor_readings()
        return_str = str(sensor_readings[0]) + "," + str(sensor_readings[1])
        return return_str

    def cc_get_system_data(self, request):
        logger.network_logger.debug("* CC Sensor System Data Sent to " + str(request.remote_addr))
        return self.sensor_access.get_system_information()

    def cc_get_configuration_report(self, request):
        logger.network_logger.debug("* CC Sensor Configuration Data Sent to " + str(request.remote_addr))
        return self.sensor_access.get_config_information()

    @staticmethod
    def cc_get_installed_sensors(request):
        logger.network_logger.debug("* CC Installed Sensors Sent to " + str(request.remote_addr))
        installed_sensors_str = app_config_access.installed_sensors.get_installed_sensors_config_as_str()
        return installed_sensors_str

    @staticmethod
    def cc_get_configuration(request):
        logger.network_logger.debug("* CC Primary Sensor Configuration Sent to " + str(request.remote_addr))
        installed_config_str = app_config_access.config_primary.convert_config_to_str(app_config_access.current_config)
        return installed_config_str

    @staticmethod
    def cc_get_wifi_config(request):
        logger.network_logger.debug("* CC Wifi Sent to " + str(request.remote_addr))
        return send_file(file_locations.wifi_config_file)

    @staticmethod
    def cc_set_wifi_config(request):
        logger.network_logger.debug("* CC set Wifi Accessed by " + str(request.remote_addr))
        try:
            new_wifi_config = request.form['command_data']
            network_wifi.write_wifi_config_to_file(new_wifi_config)
            logger.network_logger.info("** Wifi WPA Supplicant Changed by " + str(request.remote_addr))
        except Exception as error:
            logger.network_logger.error("* Failed to change Wifi WPA Supplicant sent from " +
                                        str(request.remote_addr) + " - " +
                                        str(error))
        return "OK"

    @staticmethod
    def cc_get_variance_config(request):
        logger.network_logger.debug("* CC Variance Configuration Sent to " + str(request.remote_addr))
        return send_file(file_locations.trigger_variances_file_location)

    def cc_set_variance_config(self, request):
        logger.network_logger.debug("* CC set Wifi Accessed by " + str(request.remote_addr))
        try:
            new_variance_config = request.form['command_data']
            config_trigger_variances.write_triggers_to_file(new_variance_config)
            logger.network_logger.info("** Variance Configuration Changed by " + str(request.remote_addr))
        except Exception as error:
            logger.network_logger.info("* Failed to change Variance Configuration sent from " +
                                       str(request.remote_addr) + " - " +
                                       str(error))
        self.sensor_access.restart_services()
        return "OK"

    @staticmethod
    def cc_get_primary_log(request):
        logger.network_logger.debug("* CC Primary Log Sent to " + str(request.remote_addr))
        log = logger.get_sensor_log(file_locations.primary_log)
        return log

    @staticmethod
    def cc_get_network_log(request):
        logger.network_logger.debug("* CC Network Log Sent to " + str(request.remote_addr))
        log = logger.get_sensor_log(file_locations.network_log)
        return log

    @staticmethod
    def cc_get_sensors_log(request):
        logger.network_logger.debug("* CC Sensor Log Sent to " + str(request.remote_addr))
        log = logger.get_sensor_log(file_locations.sensors_log)
        return log

    def cc_get_db_notes(self, request):
        logger.network_logger.debug("* CC Sensor Notes Sent to " + str(request.remote_addr))
        return self.sensor_access.get_db_notes()

    def delete_primary_log(self, request):
        logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_primary_log()
        return self.render_templates.message_and_return("Primary Log Deleted", url="/GetLogsHTML")

    def delete_network_log(self, request):
        logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_network_log()
        return self.render_templates.message_and_return("Network Log Deleted", url="/GetLogsHTML")

    def delete_sensors_log(self, request):
        logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
        logger.clear_sensor_log()
        return self.render_templates.message_and_return("Sensors Log Deleted", url="/GetLogsHTML")

    def cc_get_db_note_dates(self, request):
        logger.network_logger.debug("* CC Sensor Note Dates Sent to " + str(request.remote_addr))
        return self.sensor_access.get_db_note_dates()

    def cc_get_db_note_user_dates(self, request):
        logger.network_logger.debug("* CC User Set Sensor Notes Dates Sent to " + str(request.remote_addr))
        return self.sensor_access.get_db_note_user_dates()

    def cc_del_db_note(self, request):
        logger.network_logger.debug("* CC Delete Sensor Note Accessed by " + str(request.remote_addr))
        note_datetime = request.form['command_data']
        logger.network_logger.info("** CC - " + str(request.remote_addr) + " Deleted Note " + str(note_datetime))
        self.sensor_access.delete_db_note(note_datetime)

    def download_zipped_logs(self, request):
        logger.network_logger.debug("* Download Zip of all Logs Accessed by " + str(request.remote_addr))
        log_name = "Logs_" + self.sensor_access.get_ip()[-3:].replace(".", "_") + self.sensor_access.get_hostname() + ".zip"
        try:
            with ZipFile(file_locations.log_zip_file, "w", ZIP_DEFLATED) as zip_file:
                zip_file.write(file_locations.primary_log, os.path.basename(file_locations.primary_log))
                zip_file.write(file_locations.network_log, os.path.basename(file_locations.network_log))
                zip_file.write(file_locations.sensors_log, os.path.basename(file_locations.sensors_log))
            return send_file(file_locations.log_zip_file, as_attachment=True, attachment_filename=log_name)
        except Exception as error:
            logger.primary_logger.error("* Unable to Zip Logs: " + str(error))
            return self.render_templates.message_and_return("Unable to zip logs for Download", url="/GetLogsHTML")

    def download_sensors_sql_database(self, request):
        logger.network_logger.debug("* Download SQL Database Accessed by " + str(request.remote_addr))
        try:
            sql_filename = self.sensor_access.get_ip()[-3:].replace(".", "_") + \
                           self.sensor_access.get_hostname() + \
                           "SensorDatabase.sqlite"
            logger.network_logger.info("* Sensor SQL Database Sent to " + str(request.remote_addr))
            return send_file(file_locations.sensor_database_location, as_attachment=True,
                             attachment_filename=sql_filename)
        except Exception as error:
            logger.primary_logger.error("* Unable to Send Database to " + str(request.remote_addr) + ": " + str(error))
            return self.render_templates.message_and_return("Error sending Database - " + str(error))

    def put_sql_note(self, request):
        new_note = request.form['command_data']
        self.sensor_access.add_note_to_database(new_note)
        logger.network_logger.info("** SQL Note Inserted by " + str(request.remote_addr))
        return "OK"

    def update_sql_note(self, request):
        datetime_entry_note_csv = request.form['command_data']
        self.sensor_access.update_note_in_database(datetime_entry_note_csv)
        logger.network_logger.debug("** Updated Note in Database from " + str(request.remote_addr))
        return "OK"

    def upgrade_http(self, request):
        logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeOnline"])
        return self.render_templates.message_and_return("HTTP Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def upgrade_clean_http(self, request):
        logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["CleanOnline"])
        return self.render_templates.message_and_return("HTTP Clean Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def upgrade_http_dev(self, request):
        logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeOnlineDEV"])
        return self.render_templates.message_and_return("HTTP Developer Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def upgrade_smb(self, request):
        logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeSMB"])
        return self.render_templates.message_and_return("SMB Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def upgrade_clean_smb(self, request):
        logger.network_logger.info("** Clean Upgrade - SMB Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["CleanSMB"])
        return self.render_templates.message_and_return("SMB Clean Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def upgrade_smb_dev(self, request):
        logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeSMBDEV"])
        return self.render_templates.message_and_return("SMB Developer Upgrade Started",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    @staticmethod
    def upgrade_rp_controller(request):
        logger.network_logger.info("* Upgrade - E-Ink Mobile Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["inkupg"])
        return "OK"

    def reinstall_program_requirements(self, request):
        logger.network_logger.info("** Program Dependency Install Initiated by " + str(request.remote_addr))
        message2 = "Once complete, the sensor programs will be restarted. " + text_message_may_take_minutes
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["ReInstallRequirements"])
        return self.render_templates.message_and_return("Dependency Install Started",
                                                        text_message2=message2,
                                                        url="/SensorInformation")

    def upgrade_system_os(self, request):
        logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
        message = "Upgrade is already running.  "
        message2 = "The sensor will reboot when done. This will take awhile.  " + \
                   "You may continue to use the sensor during the upgrade process.  " + \
                   "There will be a loss of connectivity when the sensor reboots for up to 5 minutes."
        if app_config_access.linux_os_upgrade_ready:
            message = "Operating System Upgrade Started"
            app_config_access.linux_os_upgrade_ready = False
            app_generic_functions.thread_function(self.sensor_access.upgrade_linux_os)
        else:
            logger.network_logger.warning("* Operating System Upgrade Already Running")
        return self.render_templates.message_and_return(message, text_message2=message2, url="/SensorInformation")

    def system_reboot(self, request):
        logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["RebootSystem"])
        return self.render_templates.message_and_return("Sensor Rebooting",
                                                        text_message2=text_message_may_take_minutes,
                                                        url="/SensorInformation")

    def system_shutdown(self, request):
        logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
        message2 = "You will be unable to access it until some one turns it back on."
        app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["ShutdownSystem"])
        return self.render_templates.message_and_return("Sensor Shutting Down", text_message2=message2, url="/")

    def services_restart(self, request):
        logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(self.sensor_access.restart_services)
        return self.render_templates.message_and_return("Restarting Sensor Service",
                                                        text_message2="This should only take 5 to 30 seconds.",
                                                        url="/SensorInformation")

    def cc_set_hostname(self, request):
        logger.network_logger.debug("** CC Set Hostname Initiated by " + str(request.remote_addr))
        try:
            new_host = request.form['command_data']
            os.system("hostnamectl set-hostname " + new_host)
            message = "Hostname Changed to " + new_host
            app_generic_functions.update_cached_variables(self.sensor_access)
        except Exception as error:
            logger.network_logger.error(
                "** Hostname Change Failed from " + str(request.remote_addr) + " - " + str(error))
            message = "Failed to change Hostname"
        return self.render_templates.message_and_return(message, url="/SensorInformation")

    @staticmethod
    def cc_set_date_time(request):
        logger.network_logger.debug("** CC Set DateTime Initiated by " + str(request.remote_addr))
        try:
            new_datetime = request.form['command_data']
            os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
            logger.network_logger.info(
                "** CC System DateTime Set by " + str(request.remote_addr) + " to " + new_datetime)
        except Exception as error:
            logger.network_logger.error(
                "** DateTime Change Failed from " + str(request.remote_addr) + ": " + str(error))

    def cc_set_configuration(self, request):
        logger.network_logger.info("** CC Sensor Configuration set by " + str(request.remote_addr))
        raw_config = request.form['command_data'].splitlines()
        new_config = config_primary.convert_config_lines_to_obj(raw_config)
        config_primary.write_config_to_file(new_config)
        self.sensor_access.restart_services()

    def cc_set_installed_sensors(self, request):
        logger.network_logger.info("** CC Installed Sensors set by " + str(request.remote_addr))
        raw_installed_sensors = request.form['command_data'].splitlines()
        new_installed_sensors = config_installed_sensors.convert_installed_sensors_lines_to_obj(raw_installed_sensors)
        config_installed_sensors.write_installed_sensors_to_file(new_installed_sensors)
        self.sensor_access.restart_services()

    def cc_get_hostname(self, request):
        logger.network_logger.debug("* CC Sensor's HostName sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_hostname())

    def get_system_uptime(self, request):
        logger.network_logger.debug("* Sensor's Uptime sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_uptime_minutes())

    def get_cpu_temperature(self, request):
        logger.network_logger.debug("* Sensor's CPU Temperature sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_cpu_temperature())

    def get_env_temperature(self, request):
        logger.network_logger.debug("* Environment Temperature sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_sensor_temperature())

    @staticmethod
    def get_env_temp_offset(request):
        logger.network_logger.debug("* Environment Temperature Offset sent to " + str(request.remote_addr))
        return str(app_config_access.current_config.temperature_offset)

    def get_pressure(self, request):
        logger.network_logger.debug("* Pressure sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_pressure())

    def get_altitude(self, request):
        logger.network_logger.debug("* Altitude sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_altitude())

    def get_humidity(self, request):
        logger.network_logger.debug("* Humidity sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_humidity())

    def get_distance(self, request):
        logger.network_logger.debug("* Distance sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_distance())

    def get_all_gas(self, request):
        logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
        gas_return = [self.sensor_access.get_gas_resistance_index(),
                      self.sensor_access.get_gas_oxidised(),
                      self.sensor_access.get_gas_reduced(),
                      self.sensor_access.get_gas_nh3()]
        return str(gas_return)

    def get_gas_resistance_index(self, request):
        logger.network_logger.debug("* GAS Resistance Index sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_gas_resistance_index())

    def get_gas_oxidised(self, request):
        logger.network_logger.debug("* GAS Oxidised sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_gas_oxidised())

    def get_gas_reduced(self, request):
        logger.network_logger.debug("* GAS Reduced sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_gas_reduced())

    def get_gas_nh3(self, request):
        logger.network_logger.debug("* GAS NH3 sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_gas_nh3())

    def get_all_particulate_matter(self, request):
        logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
        return_pm = [self.sensor_access.get_particulate_matter_1(),
                     self.sensor_access.get_particulate_matter_2_5(),
                     self.sensor_access.get_particulate_matter_10()]

        return str(return_pm)

    def get_particulate_matter_1(self, request):
        logger.network_logger.debug("* Particulate Matter 1 sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_particulate_matter_1())

    def get_particulate_matter_2_5(self, request):
        logger.network_logger.debug("* Particulate Matter 2.5 sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_particulate_matter_2_5())

    def get_particulate_matter_10(self, request):
        logger.network_logger.debug("* Particulate Matter 10 sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_particulate_matter_10())

    def get_lumen(self, request):
        logger.network_logger.debug("* Lumen sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_lumen())

    def get_visible_ems(self, request):
        logger.network_logger.debug("* Visible Electromagnetic Spectrum sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_ems())

    def get_all_ultra_violet(self, request):
        logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
        return_ultra_violet = [self.sensor_access.get_ultra_violet_a(), self.sensor_access.get_ultra_violet_b()]
        return str(return_ultra_violet)

    def get_ultra_violet_a(self, request):
        logger.network_logger.debug("* Ultra Violet A sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_ultra_violet_a())

    def get_ultra_violet_b(self, request):
        logger.network_logger.debug("* Ultra Violet B sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_ultra_violet_b())

    def get_acc_xyz(self, request):
        logger.network_logger.debug("* Accelerometer XYZ sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_accelerometer_xyz())

    def get_mag_xyz(self, request):
        logger.network_logger.debug("* Magnetometer XYZ sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_magnetometer_xyz())

    def get_gyro_xyz(self, request):
        logger.network_logger.debug("* Gyroscope XYZ sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_gyroscope_xyz())

    def cc_get_interval_readings(self, request):
        logger.network_logger.debug("* Interval Sensor Readings sent to " + str(request.remote_addr))
        return str(self.sensor_access.get_interval_sensor_readings())

    def html_plotly_graph(self, request):
        logger.network_logger.debug("* Plotly Graph viewed by " + str(request.remote_addr))
        generating_message = "Generating Plotly Graph. This may take awhile."
        generating_message2 = "Once the graph is complete, you will automatically be returned to the Graphing page."

        if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
            logger.primary_logger.debug("Plotly Graph is currently being generated, please wait...")
            return self.render_templates.message_and_return(generating_message,
                                                            text_message2=generating_message2,
                                                            url="/PlotlyGraph")
        return self.render_templates.plotly_graph_main()

    def html_create_plotly_graph(self, request):
        generating_message = "Generating Plotly Graph. This may take awhile."
        generating_message2 = "Once the graph is complete, you will automatically be returned to the Graphing page."

        if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
            logger.primary_logger.debug("Plotly Graph is currently being generated, please wait...")
            return self.render_templates.message_and_return(generating_message,
                                                            text_message2=generating_message2,
                                                            url="/PlotlyGraph")

        if request.method == "POST" and "SQLRecordingType" in request.form:
            logger.network_logger.info("* Plotly Graph Initiated by " + str(request.remote_addr))
            try:
                new_graph_data = server_plotly_graph_variables.CreateGraphData()
                new_graph_data.graph_table = request.form.get("SQLRecordingType")

                if request.form.get("PlotlyRenderType") == "OpenGL":
                    new_graph_data.enable_plotly_webgl = True
                else:
                    new_graph_data.enable_plotly_webgl = False

                # The format the received datetime should look like "2019-01-01 00:00:00"
                new_graph_data.graph_start = request.form.get("graph_datetime_start").replace("T", " ") + ":00"
                new_graph_data.graph_end = request.form.get("graph_datetime_end").replace("T", " ") + ":00"
                new_graph_data.datetime_offset = request.form.get("HourOffset")
                new_graph_data.sql_queries_skip = int(request.form.get("SkipSQL").strip())
                new_graph_data.graph_columns = server_plotly_graph.check_form_columns(request.form)

                if len(new_graph_data.graph_columns) < 4:
                    return self.render_templates.message_and_return("Please Select at least One Sensor",
                                                                    url="/PlotlyGraph")
                else:
                    app_generic_functions.thread_function(server_plotly_graph.create_plotly_graph,
                                                          args=new_graph_data)
            except Exception as error:
                logger.primary_logger.warning("Plotly Graph: " + str(error))

            return self.render_templates.message_and_return(generating_message,
                                                            text_message2=generating_message2,
                                                            url="/PlotlyGraph")
        return self.render_templates.plotly_graph_main()

    def html_view_interval_graph_plotly(self, request):
        logger.network_logger.info("* Interval Plotly Graph Viewed from " + str(request.remote_addr))
        if os.path.isfile(file_locations.save_plotly_html_to + file_locations.interval_plotly_html_filename):
            return send_file(file_locations.save_plotly_html_to + file_locations.interval_plotly_html_filename)
        else:
            return self.render_templates.message_and_return("No Interval Plotly Graph Generated - Click to Close Tab",
                                                            special_command="JavaScript:window.close()",
                                                            url="")

    def html_view_triggers_graph_plotly(self, request):
        logger.network_logger.info("* Triggers Plotly Graph Viewed from " + str(request.remote_addr))
        if os.path.isfile(file_locations.save_plotly_html_to + file_locations.triggers_plotly_html_filename):
            return send_file(file_locations.save_plotly_html_to + file_locations.triggers_plotly_html_filename)
        else:
            return self.render_templates.message_and_return("No Triggers Plotly Graph Generated - Click to Close Tab",
                                                            special_command="JavaScript:window.close()",
                                                            url="")

    def display_text(self, request):
        max_length_text_message = 250
        if app_config_access.current_config.enable_display and app_config_access.installed_sensors.has_display:
            logger.network_logger.info("* Show Message on Display Initiated by " + str(request.remote_addr))
            text_message = request.form['command_data']
            if len(text_message) > max_length_text_message:
                logger.network_logger.warning("Message sent to Display is longer then " + str(max_length_text_message) +
                                              ". Truncating to " + str(max_length_text_message) + " Character")
                text_message = text_message[:max_length_text_message]
            self.sensor_access.display_message(text_message)
        else:
            logger.network_logger.warning("* Unable to Display Text: Sensor Display disabled or not installed")

    def view_help_file(self, request):
        logger.network_logger.debug("* Sensor Help Viewed from " + str(request.remote_addr))
        return self.render_templates.help_file()
