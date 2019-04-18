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
from threading import Thread
from time import sleep
from flask import Flask, request, send_file
from gevent import monkey, pywsgi

from html_files import page_quick
from operations_modules import wifi_file
from operations_modules import trigger_variances
from operations_modules import file_locations
from operations_modules import logger
from operations_modules import sensors
from operations_modules import sqlite_database
from operations_modules import configuration_main
from operations_modules import software_version
from operations_modules import variables
from operations_modules import configuration_files
from operations_modules import installed_sensors

if software_version.old_version != software_version.version:
    logger.primary_logger.info("Upgrade taking place, waiting for service restart ...")
    # Sleep before loading anything due to needed updates
    # The update service started by "record_to_db.py" will automatically restart this app when it's done
    while True:
        sleep(10)

monkey.patch_all()
app = Flask(__name__)

# If installed, start up SenseHAT Joystick program
if configuration_main.installed_sensors.raspberry_pi_sense_hat:
    sense_joy_stick_thread = Thread(target=sensors.rp_sense_hat_sensor_access.start_joy_stick_commands)
    sense_joy_stick_thread.daemon = True
    sense_joy_stick_thread.start()

database_columns_and_tables = variables.CreateDatabaseVariables()


@app.route("/")
@app.route("/Ver")
@app.route("/About")
def root_http():
    logger.network_logger.info("Root web page accessed from " + str(request.remote_addr))
    message = "<p>KootNet Sensors || " + software_version.version + "</p>"
    config = sensors.get_config_information().split(",")[-1]
    message += "<p>" + config + "</p>"
    return message


@app.route("/Quick")
def quick_links():
    logger.network_logger.info("Quick Links accessed from " + str(request.remote_addr))

    return_page = page_quick.get_page_start()
    return_page += page_quick.get_system()
    return_page += page_quick.get_configuration()
    return_page += page_quick.get_page_links()
    return_page += page_quick.get_html_page_end()
    return return_page


@app.route("/TestSensor")
def test_sensor():
    return sensors.get_sensor_readings()


@app.route("/CheckOnlineStatus")
def check_online():
    logger.network_logger.debug("Sensor Checked by " + str(request.remote_addr))
    return "OK"


@app.route("/GetSensorReadings")
def get_sensor_readings():
    logger.network_logger.info("* Sent Sensor Readings")
    sensor_readings = sensors.get_sensor_readings()
    return_str = str(sensor_readings[0]) + "," + str(sensor_readings[1])
    return return_str


@app.route("/GetSystemData")
def get_system_data():
    logger.network_logger.info("* Sensor Data Sent to " + str(request.remote_addr))
    return sensors.get_system_information()


@app.route("/GetConfigurationReport")
def get_configuration_report():
    logger.network_logger.info("* Sensor Data Sent to " + str(request.remote_addr))
    return sensors.get_config_information()


@app.route("/GetInstalledSensors")
def get_installed_sensors():
    logger.network_logger.info("* Sent Installed Sensors")
    installed_sensors_str = installed_sensors.convert_installed_sensors_to_str(configuration_main.installed_sensors)
    return installed_sensors_str


@app.route("/GetConfiguration")
def get_configuration():
    logger.network_logger.info("* Sent Sensors Configuration")
    installed_config_str = configuration_files.convert_config_to_str(configuration_main.current_config)
    return installed_config_str


@app.route("/GetWifiConfiguration")
def get_wifi_config():
    logger.network_logger.info("* Sent wpa_supplicant")
    return send_file(file_locations.wifi_config_file)


@app.route("/SetWifiConfiguration", methods=["PUT"])
def set_wifi_config():
    try:
        new_wifi_config = request.form['command_data']
        wifi_file.write_wifi_config_to_file(new_wifi_config)
        logger.network_logger.info("* wpa_supplicant Changed - OK")
    except Exception as error:
        logger.network_logger.warning("* wpa_supplicant Change - Failed: " + str(error))
    return "OK"


@app.route("/GetVarianceConfiguration")
def get_variance_config():
    logger.network_logger.info("* Sent Variance Configuration")
    return send_file(file_locations.trigger_variances_file_location)


@app.route("/SetVarianceConfiguration", methods=["PUT"])
def set_variance_config():
    try:
        new_variance_config = request.form['command_data']
        trigger_variances.write_triggers_to_file(new_variance_config)
        logger.network_logger.info("* wpa_supplicant Changed - OK")
    except Exception as error:
        logger.network_logger.warning("* wpa_supplicant Change - Failed: " + str(error))

    sensors.restart_services()
    return "OK"


@app.route("/GetPrimaryLog")
def get_primary_log():
    logger.network_logger.info("* Sent Primary Log")
    log = logger.get_sensor_log(file_locations.primary_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetPrimaryLogHTML")
def get_primary_log_html():
    logger.network_logger.info("* Sent Primary Log in HTML format")
    log = logger.get_sensor_log_html(file_locations.primary_log)
    return log


@app.route("/GetNetworkLog")
def get_network_log():
    logger.network_logger.info("* Sent Network Log")
    log = logger.get_sensor_log(file_locations.network_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetNetworkLogHTML")
def get_network_log_html():
    logger.network_logger.info("* Sent Network Log in HTML format")
    log = logger.get_sensor_log_html(file_locations.network_log)
    return log


@app.route("/GetSensorsLog")
def get_sensors_log():
    logger.network_logger.info("* Sent Sensor Log")
    log = logger.get_sensor_log(file_locations.sensors_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetSensorsLogHTML")
def get_sensors_log_html():
    logger.network_logger.info("* Sent Sensor Log in HTML format")
    log = logger.get_sensor_log_html(file_locations.sensors_log)
    return log


@app.route("/GetDatabaseNotes")
def get_db_notes():
    logger.network_logger.info("* Sent Sensor Notes")
    sql_query = "SELECT " + \
                database_columns_and_tables.other_table_column_notes + \
                " FROM " + \
                database_columns_and_tables.table_other

    sql_data = sqlite_database.sql_execute_get_data(sql_query)

    if len(sql_data) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data:
            new_entry = str(entry)[2:-3]
            new_entry = new_entry.replace(",", "[replaced_comma]")
            return_data_string += new_entry + ","
            count += 1

        return_data_string = return_data_string[:-1]

        return return_data_string
    else:
        return "No Notes"


@app.route("/GetDatabaseNoteDates")
def get_db_note_dates():
    logger.network_logger.info("* Sent Sensor Note Dates")
    sql_query_notes = "SELECT " + \
                      database_columns_and_tables.all_tables_datetime + \
                      " FROM " + \
                      database_columns_and_tables.table_other

    sql_data_notes = sqlite_database.sql_execute_get_data(sql_query_notes)

    if len(sql_data_notes) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data_notes:
            new_entry = str(entry)[2:-7]
            new_entry = new_entry.replace(",", "[replaced_comma]")
            return_data_string += new_entry + ","
            count += 1

        return_data_string = return_data_string[:-1]

        return return_data_string
    else:
        return "No Data"


@app.route("/GetDatabaseNoteUserDates")
def get_db_note_user_dates():
    logger.network_logger.info("* Sent Sensor Note User Set Dates")
    sql_query_user_datetime = "SELECT " + \
                              database_columns_and_tables.other_table_column_user_date_time + \
                              " FROM " + \
                              database_columns_and_tables.table_other

    sql_data_user_datetime = sqlite_database.sql_execute_get_data(sql_query_user_datetime)

    if len(sql_data_user_datetime) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data_user_datetime:
            new_entry = str(entry)[2:-7]
            return_data_string += new_entry + ","
            count += 1

        return_data_string = return_data_string[:-1]

        return return_data_string
    else:
        return "No Data"


@app.route("/DeleteDatabaseNote", methods=["PUT"])
def del_db_note():
    datetime_var = request.form['command_data']
    logger.network_logger.info("* Deleted Note from: " + str(datetime_var))

    sql_query = "DELETE FROM " + \
                str(database_columns_and_tables.table_other) + \
                " WHERE " + \
                str(database_columns_and_tables.all_tables_datetime) + \
                " = '" + datetime_var + "'"
    sqlite_database.sql_execute(sql_query)


@app.route("/DownloadPrimaryLog")
def download_primary_log():
    logger.network_logger.info("* Sent Full Primary Log")
    log_name = sensors.get_ip()[-3:].replace(".", "_") + "PrimaryLog.txt"
    return send_file(file_locations.primary_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadNetworkLog")
def download_network_log():
    logger.network_logger.info("* Sent Full Network Log")
    log_name = sensors.get_ip()[-3:].replace(".", "_") + "NetworkLog.txt"
    return send_file(file_locations.network_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadSensorsLog")
def download_sensors_log():
    logger.network_logger.info("* Sent Full Sensor Log")
    log_name = sensors.get_ip()[-3:].replace(".", "_") + "SensorLog.txt"
    return send_file(file_locations.sensors_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadSQLDatabase")
def download_sensors_sql_database():
    logger.network_logger.info("* Sent Sensor SQL Database")
    sql_filename = sensors.get_ip()[-3:].replace(".", "_") + "SensorRecordingDatabase.sqlite"
    return send_file(file_locations.sensor_database_location, as_attachment=True, attachment_filename=sql_filename)


@app.route("/PutDatabaseNote", methods=["PUT"])
def put_sql_note():
    new_note = request.form['command_data']
    sensors.add_note_to_database(new_note)
    logger.network_logger.info("* Inserted Note into Database")
    return "OK"


@app.route("/UpdateDatabaseNote", methods=["PUT"])
def update_sql_note():
    new_note = request.form['command_data']
    sensors.update_note_in_database(new_note)
    logger.network_logger.info("* Updated Note in Database")
    return "OK"


@app.route("/UpgradeOnline", methods=["PUT"])
def upgrade_http():
    os.system(variables.bash_commands["UpgradeOnline"])
    logger.network_logger.info("* update_programs_online.sh Complete")
    return "OK"


@app.route("/CleanOnline")
def upgrade_clean_http():
    os.system(variables.bash_commands["CleanOnline"])
    logger.network_logger.info("* Started Clean Upgrade - HTTP")
    return "OK"


@app.route("/UpgradeSMB")
def upgrade_smb():
    os.system(variables.bash_commands["UpgradeSMB"])
    logger.network_logger.info("* update_programs_smb.sh Complete")
    return "OK"


@app.route("/CleanSMB")
def upgrade_clean_smb():
    os.system(variables.bash_commands["CleanSMB"])
    logger.network_logger.info("* Started Clean Upgrade - SMB")
    return "OK"


@app.route("/UpgradeSystemOS")
def upgrade_system_os():
    logger.network_logger.info("* Updating Operating System & rebooting")
    os.system(variables.bash_commands["UpgradeSystemOS"])
    return "OK"


@app.route("/inkupg")
def upgrade_rp_controller():
    os.system(variables.bash_commands["inkupg"])
    logger.network_logger.info("* update_programs_e-Ink.sh Complete")
    return "OK"


@app.route("/RebootSystem")
def system_reboot():
    logger.network_logger.info("* Rebooting System")
    os.system(variables.bash_commands["RebootSystem"])


@app.route("/ShutdownSystem")
def system_shutdown():
    logger.network_logger.info("* System Shutdown started by " + str(request.remote_addr))
    os.system(variables.bash_commands["ShutdownSystem"])


@app.route("/RestartServices")
def services_restart():
    logger.network_logger.info("* Service restart started by " + str(request.remote_addr))
    sensors.restart_services()


@app.route("/SetHostName", methods=["PUT"])
def set_hostname():
    try:
        new_host = request.form['command_data']
        os.system("hostnamectl set-hostname " + new_host)
        logger.network_logger.info("* Hostname Changed to " + new_host + " - OK")
    except Exception as error:
        logger.network_logger.warning("* Hostname Change Failed: " + str(error))
    return "OK"


@app.route("/SetDateTime", methods=["PUT"])
def set_date_time():
    new_datetime = request.form['command_data']
    os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
    logger.network_logger.info("* Set System DateTime: " + new_datetime)
    return "OK"


@app.route("/SetConfiguration", methods=["PUT"])
def set_configuration():
    logger.network_logger.info("* Setting Sensor Configuration")

    raw_config = request.form['command_data'].splitlines()
    new_config = configuration_files.convert_config_lines_to_obj(raw_config)
    configuration_files.write_config_to_file(new_config)
    sensors.restart_services()
    return "OK"


@app.route("/SetInstalledSensors", methods=["PUT"])
def set_installed_sensors():
    logger.network_logger.info("* Setting Sensor Installed Sensors")
    raw_installed_sensors = request.form['command_data'].splitlines()
    new_installed_sensors = installed_sensors.convert_installed_sensors_lines_to_obj(raw_installed_sensors)
    installed_sensors.write_installed_sensors_to_file(new_installed_sensors)
    sensors.restart_services()
    return "OK"


@app.route("/GetHostName")
def get_hostname():
    logger.network_logger.debug("* Sent Sensor HostName")
    return str(sensors.get_hostname())


@app.route("/GetSystemUptime")
def get_system_uptime():
    logger.network_logger.debug("* Sent Sensor System Uptime")
    return str(sensors.get_system_uptime())


@app.route("/GetCPUTemperature")
def get_cpu_temperature():
    logger.network_logger.debug("* Sent Sensor CPU Temperature")
    return str(sensors.get_cpu_temperature())


@app.route("/GetEnvTemperature")
def get_env_temperature():
    logger.network_logger.debug("* Sent Sensor Environment Temperature")
    return str(sensors.get_sensor_temperature())


@app.route("/GetTempOffsetEnv")
def get_env_temp_offset():
    logger.network_logger.debug("* Sent Sensor Env Temperature Offset")
    return str(configuration_main.current_config.temperature_offset)


@app.route("/GetPressure")
def get_pressure():
    logger.network_logger.debug("* Sent Sensor Pressure")
    return str(sensors.get_pressure())


@app.route("/GetHumidity")
def get_humidity():
    logger.network_logger.debug("* Sent Sensor Humidity")
    return str(sensors.get_humidity())


@app.route("/GetLumen")
def get_lumen():
    logger.network_logger.debug("* Sent Sensor Lumen")
    return str(sensors.get_lumen())


@app.route("/GetEMS")
def get_ems():
    logger.network_logger.debug("* Sent Sensor Electromagnetic Spectrum")
    return str(sensors.get_ems())


@app.route("/GetAccelerometerXYZ")
def get_acc_xyz():
    logger.network_logger.debug("* Sent Sensor Accelerometer XYZ")
    return str(sensors.get_accelerometer_xyz())


@app.route("/GetMagnetometerXYZ")
def get_mag_xyz():
    logger.network_logger.debug("* Sent Sensor Magnetometer XYZ")
    return str(sensors.get_magnetometer_xyz())


@app.route("/GetGyroscopeXYZ")
def get_gyro_xyz():
    logger.network_logger.debug("* Sent Sensor Gyroscope XYZ")
    return str(sensors.get_gyroscope_xyz())


logger.network_logger.info("** starting up on port " + str(variables.flask_http_port) + " **")
http_server = pywsgi.WSGIServer((variables.flask_http_ip, variables.flask_http_port), app)
http_server.serve_forever()
