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
from time import sleep

try:
    # noinspection PyUnresolvedReferences
    from flask import Flask, request, send_file
    # noinspection PyUnresolvedReferences
    from flask_compress import Compress
    # noinspection PyUnresolvedReferences
    from flask_httpauth import HTTPBasicAuth
    # noinspection PyUnresolvedReferences
    from werkzeug.security import check_password_hash
    # noinspection PyUnresolvedReferences
    from gevent import pywsgi
    # noinspection PyUnresolvedReferences
    from operations_modules import file_locations
    # noinspection PyUnresolvedReferences
    from operations_modules import app_generic_functions
    # noinspection PyUnresolvedReferences
    from http_server import server_http_route_functions
    # noinspection PyUnresolvedReferences
    from http_server import server_http_auth
    import_errors = False
except ImportError as import_error:
    logger.primary_logger.critical("**** Missing Dependencies: " + str(import_error))
    import_errors = True


flask_http_ip = ""
flask_http_port = 10065


class CreateSensorHTTP:
    def __init__(self, sensor_access):
        if import_errors:
            logger.network_logger.critical("**** Unable to load HTTP Server, missing Python Modules")
            while True:
                sleep(600)
        self.app = Flask(__name__)
        Compress(self.app)
        self.auth = HTTPBasicAuth()
        http_auth = server_http_auth.CreateHTTPAuth()
        http_auth.set_http_auth_from_file()
        route_functions = server_http_route_functions.CreateRouteFunctions(sensor_access)
        if route_functions.weather_underground_config.weather_underground_enabled:
            app_generic_functions.thread_function(route_functions.weather_underground_config.start_weather_underground)

        if route_functions.luftdaten_config.luftdaten_enabled:
            app_generic_functions.thread_function(route_functions.luftdaten_config.start_luftdaten)

        app_generic_functions.update_cached_variables(sensor_access)
        app_generic_functions.thread_function(_delayed_cache_update, args=sensor_access)

        @self.app.route("/MenuScript.js")
        def menu_script():
            return send_file(file_locations.menu_script)

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
            return route_functions.auth_error(request)

        @self.app.route("/")
        @self.app.route("/index")
        @self.app.route("/index.html")
        def index():
            return route_functions.index()

        @self.app.route("/DownloadSQLDatabase")
        def download_sensors_sql_database():
            return route_functions.download_sensors_sql_database(request)

        @self.app.route('/logout')
        def logout():
            return route_functions.logout()

        @self.app.route("/MultiManageSensors", methods=["GET", "POST"])
        def html_multi_sensor_management():
            return route_functions.html_multi_sensor_management(request)

        @self.app.route("/MultiSCSaveSettings", methods=["POST"])
        @self.auth.login_required
        def html_multi_sensor_control_save_settings():
            return route_functions.html_multi_sensor_control_save_settings(request)

        @self.app.route("/About")
        @self.app.route("/SensorInformation")
        def html_system_information():
            return route_functions.html_system_information(request)

        @self.app.route("/TestSensor")
        @self.app.route("/SensorReadings")
        def html_sensors_readings():
            return route_functions.html_sensors_readings(request)

        @self.app.route("/PlotlyGraph")
        def html_plotly_graph():
            return route_functions.html_plotly_graph(request)

        @self.app.route("/CreatePlotlyGraph", methods=["POST"])
        @self.auth.login_required
        def html_create_plotly_graph():
            return route_functions.html_create_plotly_graph(request)

        @self.app.route("/ViewIntervalPlotlyGraph")
        def html_view_interval_graph_plotly():
            return route_functions.html_view_interval_graph_plotly(request)

        @self.app.route("/ViewTriggerPlotlyGraph")
        def html_view_triggers_graph_plotly():
            return route_functions.html_view_triggers_graph_plotly(request)

        @self.app.route("/OnlineServices")
        def html_online_services():
            return route_functions.html_online_services(request)

        @self.app.route("/EditOnlineServicesWeatherUnderground", methods=["POST"])
        @self.auth.login_required
        def html_edit_online_services_wu():
            return route_functions.html_edit_online_services_wu(request)

        @self.app.route("/EditOnlineServicesLuftdaten", methods=["POST"])
        @self.auth.login_required
        def html_edit_online_services_luftdaten():
            return route_functions.html_edit_online_services_luftdaten(request)

        @self.app.route("/Quick")
        @self.app.route("/SystemCommands")
        def html_system_management():
            return route_functions.html_system_management(request)

        @self.app.route("/ConfigurationsHTML")
        @self.auth.login_required
        def html_edit_configurations():
            return route_functions.html_edit_configurations(request)

        @self.app.route("/EditConfigMain", methods=["POST"])
        @self.auth.login_required
        def html_set_config_main():
            return route_functions.html_set_config_main(request)

        @self.app.route("/EditInstalledSensors", methods=["POST"])
        @self.auth.login_required
        def html_set_installed_sensors():
            return route_functions.html_set_installed_sensors(request)

        @self.app.route("/EditConfigIPv4", methods=["POST"])
        @self.auth.login_required
        def html_set_ipv4_config():
            return route_functions.html_set_ipv4_config(request)

        @self.app.route("/EditConfigWifi", methods=["POST"])
        @self.auth.login_required
        def html_set_wifi_config():
            return route_functions.html_set_wifi_config(request)

        @self.app.route("/EditTriggerVariances", methods=["POST"])
        @self.auth.login_required
        def html_set_trigger_variances():
            return route_functions.html_set_trigger_variances(request)

        @self.app.route("/ResetTriggerVariances")
        @self.auth.login_required
        def html_reset_trigger_variances():
            return route_functions.html_reset_trigger_variances(request)

        @self.app.route("/GetLogsHTML")
        def html_get_log_view():
            return route_functions.html_get_log_view(request)

        @self.app.route("/DownloadZippedLogs")
        def download_zipped_logs():
            return route_functions.download_zipped_logs(request)

        @self.app.route("/DeletePrimaryLog")
        @self.auth.login_required
        def delete_primary_log():
            return route_functions.delete_primary_log(request)

        @self.app.route("/DeleteNetworkLog")
        @self.auth.login_required
        def delete_network_log():
            return route_functions.delete_network_log(request)

        @self.app.route("/DeleteSensorsLog")
        @self.auth.login_required
        def delete_sensors_log():
            return route_functions.delete_sensors_log(request)

        @self.app.route("/UpgradeOnline")
        @self.auth.login_required
        def upgrade_http():
            return route_functions.upgrade_http(request)

        @self.app.route("/CleanOnline")
        @self.auth.login_required
        def upgrade_clean_http():
            return route_functions.upgrade_clean_http(request)

        @self.app.route("/UpgradeOnlineDev")
        @self.auth.login_required
        def upgrade_http_dev():
            return route_functions.upgrade_http_dev(request)

        @self.app.route("/UpgradeSMB")
        @self.auth.login_required
        def upgrade_smb():
            return route_functions.upgrade_smb(request)

        @self.app.route("/CleanSMB")
        @self.auth.login_required
        def upgrade_clean_smb():
            return route_functions.upgrade_clean_smb(request)

        @self.app.route("/UpgradeSMBDev")
        @self.auth.login_required
        def upgrade_smb_dev():
            return route_functions.upgrade_smb_dev(request)

        @self.app.route("/inkupg")
        @self.auth.login_required
        def upgrade_rp_controller():
            return route_functions.upgrade_rp_controller(request)

        @self.app.route("/RestartServices")
        def services_restart():
            return route_functions.services_restart(request)

        @self.app.route("/RebootSystem")
        @self.auth.login_required
        def system_reboot():
            return route_functions.system_reboot(request)

        @self.app.route("/ShutdownSystem")
        @self.auth.login_required
        def system_shutdown():
            return route_functions.system_shutdown(request)

        @self.app.route("/UpgradeSystemOS")
        @self.auth.login_required
        def upgrade_system_os():
            return route_functions.upgrade_system_os(request)

        @self.app.route("/ReInstallRequirements")
        @self.auth.login_required
        def reinstall_program_requirements():
            return route_functions.reinstall_program_requirements(request)

        @self.app.route("/HTMLRawConfigurations")
        @self.auth.login_required
        def view_https_config_diagnostics():
            return route_functions.html_view_https_config_diagnostics(request)

        @self.app.route("/SensorHelp")
        def view_help_file():
            return route_functions.view_help_file(request)

        @self.app.route("/CheckOnlineStatus")
        def check_online():
            return route_functions.check_online(request)

        @self.app.route("/GetIntervalSensorReadings")
        def cc_get_interval_readings():
            return route_functions.cc_get_interval_readings(request)

        @self.app.route("/GetSensorReadings")
        def cc_get_sensor_readings():
            return route_functions.cc_get_sensor_readings(request)

        @self.app.route("/GetSystemData")
        def cc_get_system_data():
            return route_functions.cc_get_system_data(request)

        @self.app.route("/GetConfigurationReport")
        def cc_get_configuration_report():
            return route_functions.cc_get_configuration_report(request)

        @self.app.route("/GetInstalledSensors")
        def cc_get_installed_sensors():
            return route_functions.cc_get_installed_sensors(request)

        @self.app.route("/GetConfiguration")
        def cc_get_configuration():
            return route_functions.cc_get_configuration(request)

        @self.app.route("/GetWifiConfiguration")
        @self.auth.login_required
        def cc_get_wifi_config():
            return route_functions.cc_get_wifi_config(request)

        @self.app.route("/SetWifiConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_wifi_config():
            return route_functions.cc_set_wifi_config(request)

        @self.app.route("/GetVarianceConfiguration")
        def cc_get_variance_config():
            return route_functions.cc_get_variance_config(request)

        @self.app.route("/SetVarianceConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_variance_config():
            return route_functions.cc_set_variance_config(request)

        @self.app.route("/GetPrimaryLog")
        def cc_get_primary_log():
            return route_functions.cc_get_primary_log(request)

        @self.app.route("/GetNetworkLog")
        def cc_get_network_log():
            return route_functions.cc_get_network_log(request)

        @self.app.route("/GetSensorsLog")
        def cc_get_sensors_log():
            return route_functions.cc_get_sensors_log(request)

        @self.app.route("/GetDatabaseNotes")
        def cc_get_db_notes():
            return route_functions.cc_get_db_notes(request)

        @self.app.route("/GetDatabaseNoteDates")
        def cc_get_db_note_dates():
            return route_functions.cc_get_db_note_dates(request)

        @self.app.route("/GetDatabaseNoteUserDates")
        def cc_get_db_note_user_dates():
            return route_functions.cc_get_db_note_user_dates(request)

        @self.app.route("/DeleteDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def cc_del_db_note():
            route_functions.cc_del_db_note(request)

        @self.app.route("/PutDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def cc_put_sql_note():
            return route_functions.put_sql_note(request)

        @self.app.route("/UpdateDatabaseNote", methods=["PUT"])
        @self.auth.login_required
        def cc_update_sql_note():
            return route_functions.update_sql_note(request)

        @self.app.route("/SetHostName", methods=["PUT"])
        @self.auth.login_required
        def cc_set_hostname():
            return route_functions.cc_set_hostname(request)

        @self.app.route("/SetDateTime", methods=["PUT"])
        @self.auth.login_required
        def cc_set_date_time():
            return route_functions.cc_set_date_time(request)

        @self.app.route("/SetConfiguration", methods=["PUT"])
        @self.auth.login_required
        def cc_set_configuration():
            route_functions.cc_set_configuration(request)

        @self.app.route("/SetInstalledSensors", methods=["PUT"])
        @self.auth.login_required
        def cc_set_installed_sensors():
            route_functions.cc_set_installed_sensors(request)

        @self.app.route("/GetHostName")
        def get_hostname():
            return route_functions.cc_get_hostname(request)

        @self.app.route("/GetSystemUptime")
        def get_system_uptime():
            return route_functions.get_system_uptime(request)

        @self.app.route("/GetCPUTemperature")
        def get_cpu_temperature():
            return route_functions.get_cpu_temperature(request)

        @self.app.route("/GetEnvTemperature")
        def get_env_temperature():
            return route_functions.get_env_temperature(request)

        @self.app.route("/GetTempOffsetEnv")
        def get_env_temp_offset():
            return route_functions.get_env_temp_offset(request)

        @self.app.route("/GetPressure")
        def get_pressure():
            return route_functions.get_pressure(request)

        @self.app.route("/GetAltitude")
        def get_altitude():
            return route_functions.get_altitude(request)

        @self.app.route("/GetHumidity")
        def get_humidity():
            return route_functions.get_humidity(request)

        @self.app.route("/GetDistance")
        def get_distance():
            return route_functions.get_distance(request)

        @self.app.route("/GetAllGas")
        def get_all_gas():
            return route_functions.get_all_gas(request)

        @self.app.route("/GetGasResistanceIndex")
        def get_gas_resistance_index():
            return route_functions.get_gas_resistance_index(request)

        @self.app.route("/GetGasOxidised")
        def get_gas_oxidised():
            return route_functions.get_gas_oxidised(request)

        @self.app.route("/GetGasReduced")
        def get_gas_reduced():
            return route_functions.get_gas_reduced(request)

        @self.app.route("/GetGasNH3")
        def get_gas_nh3():
            return route_functions.get_gas_nh3(request)

        @self.app.route("/GetAllParticulateMatter")
        def get_all_particulate_matter():
            return route_functions.get_all_particulate_matter(request)

        @self.app.route("/GetParticulateMatter1")
        def get_particulate_matter_1():
            return route_functions.get_particulate_matter_1(request)

        @self.app.route("/GetParticulateMatter2_5")
        def get_particulate_matter_2_5():
            return route_functions.get_particulate_matter_2_5(request)

        @self.app.route("/GetParticulateMatter10")
        def get_particulate_matter_10():
            return route_functions.get_particulate_matter_10(request)

        @self.app.route("/GetLumen")
        def get_lumen():
            return route_functions.get_lumen(request)

        @self.app.route("/GetEMS")
        def get_visible_ems():
            return route_functions.get_visible_ems(request)

        @self.app.route("/GetAllUltraViolet")
        def get_all_ultra_violet():
            return route_functions.get_all_ultra_violet(request)

        @self.app.route("/GetUltraVioletA")
        def get_ultra_violet_a():
            return route_functions.get_ultra_violet_a(request)

        @self.app.route("/GetUltraVioletB")
        def get_ultra_violet_b():
            return route_functions.get_ultra_violet_b(request)

        @self.app.route("/GetAccelerometerXYZ")
        def get_acc_xyz():
            return route_functions.get_acc_xyz(request)

        @self.app.route("/GetMagnetometerXYZ")
        def get_mag_xyz():
            return route_functions.get_mag_xyz(request)

        @self.app.route("/GetGyroscopeXYZ")
        def get_gyro_xyz():
            return route_functions.get_gyro_xyz(request)

        @self.app.route("/DisplayText", methods=["PUT"])
        def display_text():
            route_functions.display_text(request)

        logger.network_logger.info("** starting up on port " + str(flask_http_port) + " **")
        http_server = pywsgi.WSGIServer((flask_http_ip, flask_http_port),
                                        self.app,
                                        keyfile=file_locations.http_ssl_key,
                                        certfile=file_locations.http_ssl_crt)
        logger.primary_logger.info("HTTPS Server Started")
        http_server.serve_forever()


def _delayed_cache_update(sensor_access):
    sleep(5)
    app_generic_functions.update_cached_variables(sensor_access)
