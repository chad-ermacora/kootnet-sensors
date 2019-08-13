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
from zipfile import ZipFile, ZIP_DEFLATED
from threading import Thread
from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from gevent import pywsgi
from operations_modules import wifi_file
from operations_modules import trigger_variances
from operations_modules import file_locations
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import app_variables
from operations_modules import configuration_files
from http_server import server_http_flask_render_templates
from http_server import server_http_post_checks as http_post_checks
from http_server import server_http_auth
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables


class CreateSensorHTTP:
    def __init__(self, sensor_access):
        self.app = Flask(__name__)
        self.auth = HTTPBasicAuth()
        http_auth = server_http_auth.CreateHTTPAuth()
        http_auth.set_http_auth_from_file()
        render_templates = server_http_flask_render_templates.CreateRenderTemplates(sensor_access)

        @self.app.route("/")
        @self.app.route("/index")
        @self.app.route("/index.html")
        def index():
            return render_templates.index_page()

        @self.app.route("/MenuScript.js")
        def menu_script():
            return send_file(file_locations.menu_script)

        @self.app.route("/GraphScript.js")
        def graph_script():
            return send_file(file_locations.graph_script)

        @self.app.route("/MenuStyle.css")
        def menu_style_css():
            return send_file(file_locations.menu_css_style)

        @self.app.route("/jquery.min.js")
        def jquery_slim_min_js():
            return send_file(file_locations.j_query_js)

        @self.app.route("/mui.min.css")
        def mui_min_css():
            return send_file(file_locations.mui_min_css)

        @self.app.route("/mui.min.js")
        def mui_min_js():
            return send_file(file_locations.mui_min_js)

        @self.app.route("/mui-colors.min.css")
        def mui_colors_min_css():
            return send_file(file_locations.mui_colors_min_css)

        @self.auth.verify_password
        def verify_password(username, password):
            if username == http_auth.http_flask_user:
                logger.network_logger.debug("* Login attempt from " + str(request.remote_addr))
                return check_password_hash(http_auth.http_flask_password, password)
            return False

        @self.auth.error_handler
        def auth_error():
            logger.network_logger.info(" *** First or Failed Login from " + str(request.remote_addr))
            return render_templates.message_and_return("Unauthorized Access")

        @self.app.route('/logout')
        def logout():
            return render_templates.logout()

        @self.app.route("/About")
        @self.app.route("/SensorInformation")
        def html_system_information():
            logger.network_logger.debug("* Sensor Information accessed from " + str(request.remote_addr))
            return render_templates.system_information()

        @self.app.route("/TestSensor")
        @self.app.route("/SensorReadings")
        def html_sensors_readings():
            return render_templates.sensors_readings()

        @self.app.route("/Quick")
        @self.app.route("/SystemCommands")
        def html_system_management():
            logger.network_logger.debug("** System Commands accessed from " + str(request.remote_addr))
            return render_templates.system_management()

        @self.app.route("/ConfigurationsHTML")
        @self.auth.login_required
        def html_edit_configurations():
            logger.network_logger.debug("** HTML Configurations accessed from " + str(request.remote_addr))
            return render_templates.edit_configurations()

        @self.app.route("/EditConfigMain", methods=["POST"])
        @self.auth.login_required
        def html_set_config_main():
            logger.network_logger.debug("** HTML Apply - Main Configuration - Source: " + str(request.remote_addr))
            if request.method == "POST" and "interval_delay_seconds" in request.form:
                try:
                    http_post_checks.check_html_config_main(request)
                    configuration_files.write_config_to_file(configuration_main.current_config)
                    thread_function(sensor_access.restart_services)
                    return render_templates.message_and_return("Restarting Service, Please Wait ...",
                                                               url="/ConfigurationsHTML")

                except Exception as error:
                    logger.primary_logger.error("HTML Main Configuration set Error: " + str(error))
                    return render_templates.message_and_return("Bad Configuration POST Request",
                                                               url="/ConfigurationsHTML")

        @self.app.route("/EditInstalledSensors", methods=["POST"])
        @self.auth.login_required
        def html_set_installed_sensors():
            logger.network_logger.debug("** HTML Apply - Installed Sensors - Source " + str(request.remote_addr))
            if request.method == "POST":
                try:
                    http_post_checks.check_html_installed_sensors(request)
                    installed_sensors = configuration_main.installed_sensors.get_installed_sensors_config_as_str()
                    configuration_files.write_installed_sensors_to_file(installed_sensors)
                    thread_function(sensor_access.restart_services)
                    return render_templates.message_and_return("Restarting Service, Please Wait ...",
                                                               url="/ConfigurationsHTML")
                except Exception as error:
                    logger.primary_logger.error("HTML Apply - Installed Sensors - Error: " + str(error))
                    return render_templates.message_and_return("Bad Installed Sensors POST Request",
                                                               url="/ConfigurationsHTML")

        @self.app.route("/EditConfigWifi", methods=["POST"])
        @self.auth.login_required
        def html_set_wifi_config():
            logger.network_logger.debug("** HTML Apply - WiFi Configuration - Source " + str(request.remote_addr))
            if request.method == "POST" and "configuration" in request.form:
                try:
                    new_config = request.form.get("configuration").strip()
                    wifi_file.write_wifi_config_to_file(new_config)
                except Exception as error:
                    logger.primary_logger.error("HTML Apply - WiFi Configuration - Error: " + str(error))

        @self.app.route("/EditTriggerVariances", methods=["POST"])
        @self.auth.login_required
        def html_set_trigger_variances():
            logger.network_logger.debug("** HTML Apply - Trigger Variances - Source " + str(request.remote_addr))
            if request.method == "POST" and "configuration" in request.form:
                try:
                    new_config = request.form.get("configuration").strip()
                    trigger_variances.write_triggers_to_file(new_config)
                    thread_function(sensor_access.restart_services)
                    return render_templates.message_and_return("Restarting Service, Please Wait ...",
                                                               url="/EditInstalledSensors")
                except Exception as error:
                    logger.primary_logger.warning("HTML Apply - Trigger Variances - Error: " + str(error))

        @self.app.route("/CheckOnlineStatus")
        def check_online():
            logger.network_logger.debug("Sensor Checked by " + str(request.remote_addr))
            return "OK"

        @self.app.route("/GetSensorReadings")
        def cc_get_sensor_readings():
            logger.network_logger.debug("* Sensor Readings sent to " + str(request.remote_addr))
            sensor_readings = sensor_access.get_sensor_readings()
            return_str = str(sensor_readings[0]) + "," + str(sensor_readings[1])
            return return_str

        @self.app.route("/GetSystemData")
        def cc_get_system_data():
            logger.network_logger.debug("* Sensor System Data Sent to " + str(request.remote_addr))
            return sensor_access.get_system_information()

        @self.app.route("/GetConfigurationReport")
        def cc_get_configuration_report():
            logger.network_logger.debug("* Sensor Configuration Data Sent to " + str(request.remote_addr))
            return sensor_access.get_config_information()

        @self.app.route("/GetInstalledSensors")
        def cc_get_installed_sensors():
            logger.network_logger.debug("* Installed Sensors Sent to " + str(request.remote_addr))
            installed_sensors_str = configuration_main.installed_sensors.get_installed_sensors_config_as_str()
            return installed_sensors_str

        @self.app.route("/GetConfiguration")
        def cc_get_configuration():
            logger.network_logger.debug("* Primary Sensor Configuration Sent to " + str(request.remote_addr))
            installed_config_str = configuration_files.convert_config_to_str(configuration_main.current_config)
            return installed_config_str

        @self.app.route("/GetWifiConfiguration")
        @self.auth.login_required
        def cc_get_wifi_config():
            logger.network_logger.debug("* Wifi WPA Supplicant Sent to " + str(request.remote_addr))
            return send_file(file_locations.wifi_config_file)

        @self.app.route("/SetWifiConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_wifi_config():
            try:
                new_wifi_config = request.form['command_data']
                wifi_file.write_wifi_config_to_file(new_wifi_config)
                logger.network_logger.info("** Wifi WPA Supplicant Changed by " + str(request.remote_addr))
            except Exception as error:
                logger.network_logger.info("* Failed to change Wifi WPA Supplicant sent from " +
                                           str(request.remote_addr) + " - " +
                                           str(error))
            return "OK"

        @self.app.route("/GetVarianceConfiguration")
        def cc_get_variance_config():
            logger.network_logger.debug("* Variance Configuration Sent to " + str(request.remote_addr))
            return send_file(file_locations.trigger_variances_file_location)

        @self.app.route("/SetVarianceConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_variance_config():
            try:
                new_variance_config = request.form['command_data']
                trigger_variances.write_triggers_to_file(new_variance_config)
                logger.network_logger.info("** Variance Configuration Changed by " + str(request.remote_addr))
            except Exception as error:
                logger.network_logger.info("* Failed to change Variance Configuration sent from " +
                                           str(request.remote_addr) + " - " +
                                           str(error))
            sensor_access.restart_services()
            return "OK"

        @self.app.route("/GetPrimaryLog")
        def cc_get_primary_log():
            logger.network_logger.debug("* Primary Log Sent to " + str(request.remote_addr))
            log = logger.get_sensor_log(file_locations.primary_log)
            return log

        @self.app.route("/GetNetworkLog")
        def cc_get_network_log():
            logger.network_logger.debug("* Network Log Sent to " + str(request.remote_addr))
            log = logger.get_sensor_log(file_locations.network_log)
            return log

        @self.app.route("/GetSensorsLog")
        def cc_get_sensors_log():
            logger.network_logger.debug("* Sensor Log Sent to " + str(request.remote_addr))
            log = logger.get_sensor_log(file_locations.sensors_log)
            return log

        @self.app.route("/GetLogsHTML")
        def html_get_log_view():
            return render_templates.get_log_view()

        @self.app.route("/GetDatabaseNotes")
        def cc_get_db_notes():
            logger.network_logger.debug("* Sensor Notes Sent to " + str(request.remote_addr))
            return sensor_access.get_db_notes()

        @self.app.route("/DeletePrimaryLog")
        @self.auth.login_required
        def delete_primary_log():
            logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
            logger.clear_primary_log()
            return render_templates.message_and_return("Primary Log Deleted", url="/GetLogsHTML")

        @self.app.route("/DeleteNetworkLog")
        @self.auth.login_required
        def delete_network_log():
            logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
            logger.clear_network_log()
            return render_templates.message_and_return("Network Log Deleted", url="/GetLogsHTML")

        @self.app.route("/DeleteSensorsLog")
        @self.auth.login_required
        def delete_sensors_log():
            logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
            logger.clear_sensor_log()
            return render_templates.message_and_return("Sensors Log Deleted", url="/GetLogsHTML")

        @self.app.route("/GetDatabaseNoteDates")
        def cc_get_db_note_dates():
            logger.network_logger.debug("* Sensor Note Dates Sent to " + str(request.remote_addr))
            return sensor_access.get_db_note_dates()

        @self.app.route("/GetDatabaseNoteUserDates")
        def cc_get_db_note_user_dates():
            logger.network_logger.debug("* User Set Sensor Notes Dates Sent to " + str(request.remote_addr))
            return sensor_access.get_db_note_user_dates()

        @self.app.route("/DeleteDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def cc_del_db_note():
            note_datetime = request.form['command_data']
            logger.network_logger.info("** " + str(request.remote_addr) +
                                       " Deleted Note " +
                                       str(note_datetime))
            sensor_access.delete_db_note(note_datetime)

        @self.app.route("/DownloadZippedLogs")
        def download_zipped_logs():
            logger.network_logger.debug("* Zip of all Logs Sent to " + str(request.remote_addr))
            log_name = "Logs_" + sensor_access.get_ip()[-3:].replace(".", "_") + sensor_access.get_hostname() + ".zip"
            try:
                with ZipFile(file_locations.log_zip_file, "w", ZIP_DEFLATED) as zip_file:
                    zip_file.write(file_locations.primary_log, os.path.basename(file_locations.primary_log))
                    zip_file.write(file_locations.network_log, os.path.basename(file_locations.network_log))
                    zip_file.write(file_locations.sensors_log, os.path.basename(file_locations.sensors_log))
                return send_file(file_locations.log_zip_file, as_attachment=True, attachment_filename=log_name)
            except Exception as error:
                logger.primary_logger.error("* Unable to Zip Logs: " + str(error))

        @self.app.route("/DownloadSQLDatabase")
        def download_sensors_sql_database():
            logger.network_logger.info("* Sensor SQL Database Sent to " + str(request.remote_addr))
            sql_filename = sensor_access.get_ip()[-3:].replace(".", "_") + \
                           sensor_access.get_hostname() + \
                           "SensorDatabase.sqlite"
            return send_file(file_locations.sensor_database_location, as_attachment=True,
                             attachment_filename=sql_filename)

        @self.app.route("/PutDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def put_sql_note():
            new_note = request.form['command_data']
            sensor_access.add_note_to_database(new_note)
            logger.network_logger.debug("** SQL Note Inserted by " + str(request.remote_addr))
            return "OK"

        @self.app.route("/UpdateDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def update_sql_note():
            datetime_entry_note_csv = request.form['command_data']
            sensor_access.update_note_in_database(datetime_entry_note_csv)
            logger.network_logger.debug("** Updated Note in Database from " + str(request.remote_addr))
            return "OK"

        @self.app.route("/UpgradeOnline")
        @self.auth.login_required
        def upgrade_http():
            logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["UpgradeOnline"])
            return render_templates.message_and_return("HTTP Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/CleanOnline")
        @self.auth.login_required
        def upgrade_clean_http():
            logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["CleanOnline"])
            return render_templates.message_and_return("HTTP Clean Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/UpgradeOnlineDev")
        @self.auth.login_required
        def upgrade_http_dev():
            logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["UpgradeOnlineDEV"])
            return render_templates.message_and_return("HTTP Developer Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/UpgradeSMB")
        @self.auth.login_required
        def upgrade_smb():
            logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["UpgradeSMB"])
            return render_templates.message_and_return("SMB Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/CleanSMB")
        @self.auth.login_required
        def upgrade_clean_smb():
            logger.network_logger.info("** Clean Upgrade - SMB Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["CleanSMB"])
            return render_templates.message_and_return("SMB Clean Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/UpgradeSMBDev")
        @self.auth.login_required
        def upgrade_smb_dev():
            logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["UpgradeSMBDEV"])
            return render_templates.message_and_return("SMB Developer Upgrade Started",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/inkupg")
        @self.auth.login_required
        def upgrade_rp_controller():
            logger.network_logger.info("* Upgrade - E-Ink Mobile Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["inkupg"])
            return "OK"

        @self.app.route("/ReInstallRequirements")
        @self.auth.login_required
        def reinstall_program_requirements():
            logger.network_logger.info("** Program Dependency Install Initiated by " + str(request.remote_addr))
            message2 = "Once complete, the sensor programs will be restarted. " + app_variables.text_message_may_take_minutes
            thread_function(os.system, args=app_variables.bash_commands["ReInstallRequirements"])
            return render_templates.message_and_return("Dependency Install Started",
                                                       text_message2=message2,
                                                       url="/SensorInformation")

        @self.app.route("/UpgradeSystemOS")
        @self.auth.login_required
        def upgrade_system_os():
            logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
            message = "Upgrade is already running.  "
            message2 = "The sensor will reboot when done. This will take awhile.  " + \
                       "You may continue to use the sensor during the upgrade process.  " + \
                       "There will be a loss of connectivity when the sensor reboots for up to 5 minutes."
            if configuration_main.linux_os_upgrade_ready:
                message = "Operating System Upgrade Started"
                configuration_main.linux_os_upgrade_ready = False
                thread_function(sensor_access.upgrade_linux_os)
            else:
                logger.network_logger.warning("* Operating System Upgrade Already Running")
            return render_templates.message_and_return(message,
                                                       text_message2=message2,
                                                       url="/SensorInformation")

        @self.app.route("/RebootSystem")
        @self.auth.login_required
        def system_reboot():
            logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
            thread_function(os.system, args=app_variables.bash_commands["RebootSystem"])
            return render_templates.message_and_return("Sensor Rebooting",
                                                       text_message2=app_variables.text_message_may_take_minutes,
                                                       url="/SensorInformation")

        @self.app.route("/ShutdownSystem")
        @self.auth.login_required
        def system_shutdown():
            logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
            message2 = "You will be unable to access it until some one turns it back on."
            thread_function(os.system, args=app_variables.bash_commands["ShutdownSystem"])
            return render_templates.message_and_return("Sensor Shutting Down",
                                                       text_message2=message2,
                                                       url="/SystemCommands")

        @self.app.route("/RestartServices")
        def services_restart():
            logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
            thread_function(sensor_access.restart_services)
            return render_templates.message_and_return("Restarting Sensor Service",
                                                       text_message2="This should only take 5 to 30 seconds.",
                                                       url="/SensorInformation")

        @self.app.route("/SetHostName", methods=["PUT"])
        @self.auth.login_required
        def set_hostname():
            try:
                new_host = request.form['command_data']
                os.system("hostnamectl set-hostname " + new_host)
                logger.network_logger.info("** Hostname Change Initiated by " + str(request.remote_addr))
                message = "Hostname Changed to " + new_host
                configuration_main.cache_hostname = new_host
            except Exception as error:
                logger.network_logger.info("** Hostname Change Failed from " +
                                           str(request.remote_addr) + " - " + str(error))
                message = "Failed to change Hostname"
            return render_templates.message_and_return(message, url="/SensorInformation")

        @self.app.route("/SetDateTime", methods=["PUT"])
        @self.auth.login_required
        def set_date_time():
            new_datetime = request.form['command_data']
            os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
            logger.network_logger.info("** Set System DateTime Initiated by " +
                                       str(request.remote_addr) +
                                       " to " + new_datetime)

        @self.app.route("/SetConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_configuration():
            logger.network_logger.info("** Sensor Configuration set by " + str(request.remote_addr))
            raw_config = request.form['command_data'].splitlines()
            new_config = configuration_files.convert_config_lines_to_obj(raw_config)
            configuration_files.write_config_to_file(new_config)
            sensor_access.restart_services()

        @self.app.route("/SetInstalledSensors", methods=["PUT"])
        @self.auth.login_required
        def cc_set_installed_sensors():
            logger.network_logger.info("** Installed Sensors set by " + str(request.remote_addr))
            raw_installed_sensors = request.form['command_data'].splitlines()
            new_installed_sensors = configuration_files.convert_installed_sensors_lines_to_obj(raw_installed_sensors)
            configuration_files.write_installed_sensors_to_file(new_installed_sensors)
            sensor_access.restart_services()

        @self.app.route("/GetHostName")
        def get_hostname():
            logger.network_logger.debug("* Sensor's HostName sent to " + str(request.remote_addr))
            return str(sensor_access.get_hostname())

        @self.app.route("/GetSystemUptime")
        def get_system_uptime():
            logger.network_logger.debug("* Sensor's Uptime sent to " + str(request.remote_addr))
            return str(sensor_access.get_system_uptime())

        @self.app.route("/GetCPUTemperature")
        def get_cpu_temperature():
            logger.network_logger.debug("* Sensor's CPU Temperature sent to " + str(request.remote_addr))
            return str(sensor_access.get_cpu_temperature())

        @self.app.route("/GetEnvTemperature")
        def get_env_temperature():
            logger.network_logger.debug("* Environment Temperature sent to " + str(request.remote_addr))
            return str(sensor_access.get_sensor_temperature())

        @self.app.route("/GetTempOffsetEnv")
        def get_env_temp_offset():
            logger.network_logger.debug("* Environment Temperature Offset sent to " + str(request.remote_addr))
            return str(configuration_main.current_config.temperature_offset)

        @self.app.route("/GetPressure")
        def get_pressure():
            logger.network_logger.debug("* Pressure sent to " + str(request.remote_addr))
            return str(sensor_access.get_pressure())

        @self.app.route("/GetAltitude")
        def get_altitude():
            logger.network_logger.debug("* Altitude sent to " + str(request.remote_addr))
            return str(sensor_access.get_altitude())

        @self.app.route("/GetHumidity")
        def get_humidity():
            logger.network_logger.debug("* Humidity sent to " + str(request.remote_addr))
            return str(sensor_access.get_humidity())

        @self.app.route("/GetDistance")
        def get_distance():
            logger.network_logger.debug("* Distance sent to " + str(request.remote_addr))
            return str(sensor_access.get_distance())

        @self.app.route("/GetAllGas")
        def get_all_gas():
            logger.network_logger.debug("* GAS Sensors sent to " + str(request.remote_addr))
            gas_return = [sensor_access.get_gas_resistance_index(),
                          sensor_access.get_gas_oxidised(),
                          sensor_access.get_gas_reduced(),
                          sensor_access.get_gas_nh3()]
            return str(gas_return)

        @self.app.route("/GetGasResistanceIndex")
        def get_gas_resistance_index():
            logger.network_logger.debug("* GAS Resistance Index sent to " + str(request.remote_addr))
            return str(sensor_access.get_gas_resistance_index())

        @self.app.route("/GetGasOxidised")
        def get_gas_oxidised():
            logger.network_logger.debug("* GAS Oxidised sent to " + str(request.remote_addr))
            return str(sensor_access.get_gas_oxidised())

        @self.app.route("/GetGasReduced")
        def get_gas_reduced():
            logger.network_logger.debug("* GAS Reduced sent to " + str(request.remote_addr))
            return str(sensor_access.get_gas_reduced())

        @self.app.route("/GetGasNH3")
        def get_gas_nh3():
            logger.network_logger.debug("* GAS NH3 sent to " + str(request.remote_addr))
            return str(sensor_access.get_gas_nh3())

        @self.app.route("/GetAllParticulateMatter")
        def get_all_particulate_matter():
            logger.network_logger.debug("* Particulate Matter Sensors sent to " + str(request.remote_addr))
            return_pm = [sensor_access.get_particulate_matter_1(),
                         sensor_access.get_particulate_matter_2_5(),
                         sensor_access.get_particulate_matter_10()]

            return str(return_pm)

        @self.app.route("/GetParticulateMatter1")
        def get_particulate_matter_1():
            logger.network_logger.debug("* Particulate Matter 1 sent to " + str(request.remote_addr))
            return str(sensor_access.get_particulate_matter_1())

        @self.app.route("/GetParticulateMatter2_5")
        def get_particulate_matter_2_5():
            logger.network_logger.debug("* Particulate Matter 2.5 sent to " + str(request.remote_addr))
            return str(sensor_access.get_particulate_matter_2_5())

        @self.app.route("/GetParticulateMatter10")
        def get_particulate_matter_10():
            logger.network_logger.debug("* Particulate Matter 10 sent to " + str(request.remote_addr))
            return str(sensor_access.get_particulate_matter_10())

        @self.app.route("/GetLumen")
        def get_lumen():
            logger.network_logger.debug("* Lumen sent to " + str(request.remote_addr))
            return str(sensor_access.get_lumen())

        @self.app.route("/GetEMS")
        def get_ems():
            logger.network_logger.debug("* Electromagnetic Spectrum sent to " + str(request.remote_addr))
            return str(sensor_access.get_ems())

        @self.app.route("/GetAllUltraViolet")
        def get_all_ultra_violet():
            logger.network_logger.debug("* Ultra Violet Sensors sent to " + str(request.remote_addr))
            return_ultra_violet = [sensor_access.get_ultra_violet_a(), sensor_access.get_ultra_violet_b()]
            return str(return_ultra_violet)

        @self.app.route("/GetUltraVioletA")
        def get_ultra_violet_a():
            logger.network_logger.debug("* Ultra Violet A sent to " + str(request.remote_addr))
            return str(sensor_access.get_ultra_violet_a())

        @self.app.route("/GetUltraVioletB")
        def get_ultra_violet_b():
            logger.network_logger.debug("* Ultra Violet B sent to " + str(request.remote_addr))
            return str(sensor_access.get_ultra_violet_b())

        @self.app.route("/GetAccelerometerXYZ")
        def get_acc_xyz():
            logger.network_logger.debug("* Accelerometer XYZ sent to " + str(request.remote_addr))
            return str(sensor_access.get_accelerometer_xyz())

        @self.app.route("/GetMagnetometerXYZ")
        def get_mag_xyz():
            logger.network_logger.debug("* Magnetometer XYZ sent to " + str(request.remote_addr))
            return str(sensor_access.get_magnetometer_xyz())

        @self.app.route("/GetGyroscopeXYZ")
        def get_gyro_xyz():
            logger.network_logger.debug("* Gyroscope XYZ sent to " + str(request.remote_addr))
            return str(sensor_access.get_gyroscope_xyz())

        @self.app.route("/GetIntervalSensorReadings")
        def cc_get_interval_readings():
            logger.network_logger.debug("* Interval Sensor Readings sent to " + str(request.remote_addr))
            return str(sensor_access.get_interval_sensor_readings())

        @self.app.route("/PlotlyGraph", methods=["GET", "POST"])
        # @self.auth.login_required
        def html_graph_plotly():
            generating_message = "Generating Plotly Graph. This may take awhile."
            generating_message2 = "Once the graph is complete, you will automatically be returned to the Graphing page."

            if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
                logger.primary_logger.debug("Plotly Graph is currently being generated, please wait...")
                return render_templates.message_and_return(generating_message,
                                                           text_message2=generating_message2,
                                                           url="/PlotlyGraph")
            else:
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
                            return render_templates.message_and_return("Please Select at least One Sensor",
                                                                       url="/PlotlyGraph")
                        else:
                            thread_function(server_plotly_graph.create_plotly_graph, args=new_graph_data)
                    except Exception as error:
                        logger.primary_logger.warning("Plotly Graph: " + str(error))

                    return render_templates.message_and_return(generating_message,
                                                               text_message2=generating_message2,
                                                               url="/PlotlyGraph")
                else:
                    return render_templates.plotly_graph_main()

        @self.app.route("/ViewIntervalPlotlyGraph")
        def html_view_interval_graph_plotly():
            logger.network_logger.info("* Interval Plotly Graph Viewed from " + str(request.remote_addr))
            if os.path.isfile(file_locations.save_plotly_html_to + file_locations.interval_plotly_html_filename):
                return send_file(file_locations.save_plotly_html_to + file_locations.interval_plotly_html_filename)
            else:
                return render_templates.message_and_return("No Interval Plotly Graph Generated - Click to Close Tab",
                                                           special_command="JavaScript:window.close()",
                                                           url="")

        @self.app.route("/ViewTriggerPlotlyGraph")
        def html_view_triggers_graph_plotly():
            logger.network_logger.info("* Triggers Plotly Graph Viewed from " + str(request.remote_addr))
            if os.path.isfile(file_locations.save_plotly_html_to + file_locations.triggers_plotly_html_filename):
                return send_file(file_locations.save_plotly_html_to + file_locations.triggers_plotly_html_filename)
            else:
                return render_templates.message_and_return("No Triggers Plotly Graph Generated - Click to Close Tab",
                                                           special_command="JavaScript:window.close()",
                                                           url="")

        @self.app.route("/DisplayText", methods=["PUT"])
        @self.auth.login_required
        def display_text():
            if configuration_main.current_config.enable_display and configuration_main.installed_sensors.has_display:
                logger.network_logger.info("* Show Message on Display Initiated by " + str(request.remote_addr))
                text_message = request.form['command_data']
                sensor_access.display_message(text_message)
            else:
                message = "Unable to Display Text: Sensor Display disabled or not installed"
                logger.network_logger.warning("* " + message)

        def thread_function(function, args=None):
            if args:
                system_thread = Thread(target=function, args=[args])
                system_thread.daemon = True
                system_thread.start()
            else:
                system_thread = Thread(target=function)
                system_thread.daemon = True
                system_thread.start()

        logger.network_logger.info("** starting up on port " + str(app_variables.flask_http_port) + " **")
        http_server = pywsgi.WSGIServer((app_variables.flask_http_ip, app_variables.flask_http_port), self.app)
        logger.primary_logger.info("HTTP Server Started")
        http_server.serve_forever()
