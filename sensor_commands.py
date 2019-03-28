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

from operations_modules.operations_wifi_file import write_wifi_config_to_file
from operations_modules.trigger_variances import write_triggers_to_file as write_variances_to_file
import operations_modules.operations_file_locations as file_locations
from operations_modules import operations_commands
from operations_modules import operations_html_templates
from operations_modules import operations_logger
from operations_modules import operations_sensors
from operations_modules.operations_config_db import CreateDatabaseVariables
from operations_modules.operations_db import sql_execute_get_data, sql_execute
from operations_modules.operations_config import current_config, installed_sensors
from operations_modules.operations_version import version, old_version
from operations_modules.operations_variables import flask_http_port, flask_http_ip, bash_commands
from operations_modules.operations_config_file import convert_config_to_str, convert_config_lines_to_obj, \
    write_config_to_file
from operations_modules.operations_installed_sensors import convert_installed_sensors_to_str, \
    convert_installed_sensors_lines_to_obj, write_installed_sensors_to_file

if old_version != version:
    operations_logger.primary_logger.info("Upgrade taking place, waiting for service restart ...")
    # Sleep before loading anything due to needed updates
    # The update service started by "record_to_db.py" will automatically restart this app when it's done
    while True:
        sleep(10)

monkey.patch_all()
app = Flask(__name__)

# If installed, start up SenseHAT Joystick program
if installed_sensors.raspberry_pi_sense_hat:
    sense_joy_stick_thread = Thread(target=operations_sensors.rp_sense_hat_sensor_access.start_joy_stick_commands)
    sense_joy_stick_thread.daemon = True
    sense_joy_stick_thread.start()

database_columns_and_tables = CreateDatabaseVariables()


@app.route("/")
def root_http():
    return "KootNet Sensors || Raspberry Pi Sensor"


@app.route("/Ver")
@app.route("/About")
def show_version():
    message = "<p>KootNet Sensors || " + version + "</p>"
    config = operations_commands.get_config_information().split(",")[-1]
    message += "<p>" + config + "</p>"
    return message


@app.route("/TestSensor")
def test_sensor():
    sensor_readings = operations_commands.get_sensor_readings()
    sensor_info_raw = operations_commands.get_system_information().split(",")
    sensor_config_raw = operations_commands.get_config_information().split(",")
    sensor_config = ""
    sensor_info = ""

    info_start = operations_html_templates.sensor_info_start
    config_start = operations_html_templates.sensor_config_start
    readings_start = operations_html_templates.sensor_readings_start

    for config in sensor_config_raw:
        sensor_config += "<th><span style='background-color: #0BB10D;'>" + config + "</span></th>"

    for info in sensor_info_raw:
        sensor_info += "<th><span style='background-color: #0BB10D;'>" + info + "</span></th>"

    message = "<p><span style='color: red'>KootNet Sensors || Sensor Testing Page</span></p>" + \
              info_start + "<tr>" + sensor_info + "</tr></table>"

    message += config_start + "<tr>" + sensor_config + "</tr></table>"

    message += readings_start + "<tr>" + sensor_readings[0] + "</tr>" + "<tr>" + sensor_readings[1] + "</tr></table>"

    message += operations_html_templates.sensor_test_final_end
    return message


@app.route("/CheckOnlineStatus")
def check_online():
    operations_logger.network_logger.debug("Sensor Checked by " + str(request.remote_addr))
    return "OK"


@app.route("/GetSensorReadings")
def get_sensor_readings():
    operations_logger.network_logger.info("* Sent Sensor Readings")
    sensor_readings = operations_commands.get_sensor_readings()
    return_str = str(sensor_readings[0]) + "," + str(sensor_readings[1])
    return return_str


@app.route("/GetSystemData")
def get_system_data():
    operations_logger.network_logger.info("* Sensor Data Sent to " + str(request.remote_addr))
    return operations_commands.get_system_information()


@app.route("/GetConfigurationReport")
def get_configuration_report():
    operations_logger.network_logger.info("* Sensor Data Sent to " + str(request.remote_addr))
    return operations_commands.get_config_information()


@app.route("/GetInstalledSensors")
def get_installed_sensors():
    operations_logger.network_logger.info("* Sent Installed Sensors")
    installed_sensors_str = convert_installed_sensors_to_str(installed_sensors)
    return installed_sensors_str


@app.route("/GetConfiguration")
def get_configuration():
    operations_logger.network_logger.info("* Sent Sensors Configuration")
    installed_config_str = convert_config_to_str(current_config)
    return installed_config_str


@app.route("/GetWifiConfiguration")
def get_wifi_config():
    operations_logger.network_logger.info("* Sent wpa_supplicant")
    return send_file(file_locations.wifi_config_file)


@app.route("/SetWifiConfiguration", methods=["PUT"])
def set_wifi_config():
    try:
        new_wifi_config = request.form['command_data']
        write_wifi_config_to_file(new_wifi_config)
        operations_logger.network_logger.info("* wpa_supplicant Changed - OK")
    except Exception as error:
        operations_logger.network_logger.warning("* wpa_supplicant Change - Failed: " + str(error))
    return "OK"


@app.route("/GetVarianceConfiguration")
def get_variance_config():
    operations_logger.network_logger.info("* Sent Variance Configuration")
    return send_file(file_locations.trigger_variances_file_location)


@app.route("/SetVarianceConfiguration", methods=["PUT"])
def set_variance_config():
    try:
        new_variance_config = request.form['command_data']
        write_variances_to_file(new_variance_config)
        operations_logger.network_logger.info("* wpa_supplicant Changed - OK")
    except Exception as error:
        operations_logger.network_logger.warning("* wpa_supplicant Change - Failed: " + str(error))

    operations_commands.restart_services()
    return "OK"


@app.route("/GetPrimaryLog")
def get_primary_log():
    operations_logger.network_logger.info("* Sent Primary Log")
    log = operations_commands.get_sensor_log(operations_logger.primary_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetNetworkLog")
def get_network_log():
    operations_logger.network_logger.info("* Sent Network Log")
    log = operations_commands.get_sensor_log(operations_logger.network_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetSensorsLog")
def get_sensors_log():
    operations_logger.network_logger.info("* Sent Sensor Log")
    log = operations_commands.get_sensor_log(operations_logger.sensors_log)
    if len(log) > 1150:
        log = log[-1150:]
    return log


@app.route("/GetDatabaseNotes")
def get_db_notes():
    operations_logger.network_logger.info("* Sent Sensor Notes")
    sql_query = "SELECT " + \
                database_columns_and_tables.other_table_column_notes + \
                " FROM " + \
                database_columns_and_tables.table_other

    sql_data = sql_execute_get_data(sql_query)

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
        return "No Data,No Data"


@app.route("/GetDatabaseNoteDates")
def get_db_note_dates():
    operations_logger.network_logger.info("* Sent Sensor Note Dates")
    sql_query = "SELECT " + \
                database_columns_and_tables.all_tables_datetime + \
                " FROM " + \
                database_columns_and_tables.table_other

    sql_data = sql_execute_get_data(sql_query)

    if len(sql_data) > 0:
        return_data_string = ""

        count = 0
        for entry in sql_data:
            new_entry = str(entry)[2:-7]
            new_entry = new_entry.replace(",", "[replaced_comma]")
            return_data_string += new_entry + ","
            count += 1

        return_data_string = return_data_string[:-1]

        return return_data_string
    else:
        return "No Data,No Data"


@app.route("/DownloadPrimaryLog")
def download_primary_log():
    operations_logger.network_logger.info("* Sent Full Primary Log")
    log_name = operations_sensors.get_ip()[-3:].replace(".", "_") + "PrimaryLog.txt"
    return send_file(operations_logger.primary_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadNetworkLog")
def download_network_log():
    operations_logger.network_logger.info("* Sent Full Network Log")
    log_name = operations_sensors.get_ip()[-3:].replace(".", "_") + "NetworkLog.txt"
    return send_file(operations_logger.network_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadSensorsLog")
def download_sensors_log():
    operations_logger.network_logger.info("* Sent Full Sensor Log")
    log_name = operations_sensors.get_ip()[-3:].replace(".", "_") + "SensorLog.txt"
    return send_file(operations_logger.sensors_log, as_attachment=True, attachment_filename=log_name)


@app.route("/DownloadSQLDatabase")
def download_sensors_sql_database():
    operations_logger.network_logger.info("* Sent Sensor SQL Database")
    sql_filename = operations_sensors.get_ip()[-3:].replace(".", "_") + "SensorRecordingDatabase.sqlite"
    return send_file(file_locations.sensor_database_location, as_attachment=True, attachment_filename=sql_filename)


@app.route("/PutDatabaseNote", methods=["PUT"])
def put_sql_note():
    new_note = request.form['command_data']
    operations_commands.add_note_to_database(new_note)
    operations_logger.network_logger.info("* Inserted Note into Database")
    return "OK"


@app.route("/UpgradeOnline", methods=["PUT"])
def upgrade_http():
    os.system(bash_commands["UpgradeOnline"])
    operations_logger.network_logger.info("* update_programs_online.sh Complete")
    return "OK"


@app.route("/CleanOnline")
def upgrade_clean_http():
    os.system(bash_commands["CleanOnline"])
    operations_logger.network_logger.info("* Started Clean Upgrade - HTTP")
    return "OK"


@app.route("/UpgradeSMB")
def upgrade_smb():
    os.system(bash_commands["UpgradeSMB"])
    operations_logger.network_logger.info("* update_programs_smb.sh Complete")
    return "OK"


@app.route("/CleanSMB")
def upgrade_clean_smb():
    os.system(bash_commands["CleanSMB"])
    operations_logger.network_logger.info("* Started Clean Upgrade - SMB")
    return "OK"


@app.route("/UpgradeSystemOS")
def upgrade_system_os():
    operations_logger.network_logger.info("* Updating Operating System & rebooting")
    os.system(bash_commands["UpgradeSystemOS"])
    return "OK"


@app.route("/inkupg")
def upgrade_rp_controller():
    os.system(bash_commands["inkupg"])
    operations_logger.network_logger.info("* update_programs_e-Ink.sh Complete")
    return "OK"


@app.route("/RebootSystem")
def system_reboot():
    operations_logger.network_logger.info("* Rebooting System")
    os.system(bash_commands["RebootSystem"])


@app.route("/ShutdownSystem")
def system_shutdown():
    operations_logger.network_logger.info("* System Shutdown started by " + str(request.remote_addr))
    os.system(bash_commands["ShutdownSystem"])


@app.route("/RestartServices")
def services_restart():
    operations_logger.network_logger.info("* Service restart started by " + str(request.remote_addr))
    operations_commands.restart_services()


@app.route("/SetHostName", methods=["PUT"])
def set_hostname():
    try:
        new_host = request.form['command_data']
        os.system("hostnamectl set-hostname " + new_host)
        operations_logger.network_logger.info("* Hostname Changed to " + new_host + " - OK")
    except Exception as error:
        operations_logger.network_logger.warning("* Hostname Change Failed: " + str(error))
    return "OK"


@app.route("/SetDateTime", methods=["PUT"])
def set_date_time():
    new_datetime = request.form['command_data']
    os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
    operations_logger.network_logger.info("* Set System DateTime: " + new_datetime)
    return "OK"


@app.route("/SetConfiguration", methods=["PUT"])
def set_configuration():
    operations_logger.network_logger.info("* Setting Sensor Configuration")

    raw_config = request.form['command_data'].splitlines()
    new_config = convert_config_lines_to_obj(raw_config)
    write_config_to_file(new_config)
    operations_commands.restart_services()
    return "OK"


@app.route("/SetInstalledSensors", methods=["PUT"])
def set_installed_sensors():
    operations_logger.network_logger.info("* Setting Sensor Installed Sensors")
    raw_installed_sensors = request.form['command_data'].splitlines()
    new_installed_sensors = convert_installed_sensors_lines_to_obj(raw_installed_sensors)
    write_installed_sensors_to_file(new_installed_sensors)
    operations_commands.restart_services()
    return "OK"


@app.route("/GetHostName")
def get_hostname():
    operations_logger.network_logger.debug("* Sent Sensor HostName")
    return str(operations_sensors.get_hostname())


@app.route("/GetSystemUptime")
def get_system_uptime():
    operations_logger.network_logger.debug("* Sent Sensor System Uptime")
    return str(operations_sensors.get_system_uptime())


@app.route("/GetCPUTemperature")
def get_cpu_temperature():
    operations_logger.network_logger.debug("* Sent Sensor CPU Temperature")
    return str(operations_sensors.get_cpu_temperature())


@app.route("/GetEnvTemperature")
def get_env_temperature():
    operations_logger.network_logger.debug("* Sent Sensor Environment Temperature")
    return str(operations_sensors.get_sensor_temperature())


@app.route("/GetTempOffsetEnv")
def get_env_temp_offset():
    operations_logger.network_logger.debug("* Sent Sensor Env Temperature Offset")
    return str(current_config.temperature_offset)


@app.route("/GetPressure")
def get_pressure():
    operations_logger.network_logger.debug("* Sent Sensor Pressure")
    return str(operations_sensors.get_pressure())


@app.route("/GetHumidity")
def get_humidity():
    operations_logger.network_logger.debug("* Sent Sensor Humidity")
    return str(operations_sensors.get_humidity())


@app.route("/GetLumen")
def get_lumen():
    operations_logger.network_logger.debug("* Sent Sensor Lumen")
    return str(operations_sensors.get_lumen())


@app.route("/GetEMS")
def get_ems():
    operations_logger.network_logger.debug("* Sent Sensor Electromagnetic Spectrum")
    return str(operations_sensors.get_ems())


@app.route("/GetAccelerometerXYZ")
def get_acc_xyz():
    operations_logger.network_logger.debug("* Sent Sensor Accelerometer XYZ")
    return str(operations_sensors.get_accelerometer_xyz())


@app.route("/GetMagnetometerXYZ")
def get_mag_xyz():
    operations_logger.network_logger.debug("* Sent Sensor Magnetometer XYZ")
    return str(operations_sensors.get_magnetometer_xyz())


@app.route("/GetGyroscopeXYZ")
def get_gyro_xyz():
    operations_logger.network_logger.debug("* Sent Sensor Gyroscope XYZ")
    return str(operations_sensors.get_gyroscope_xyz())


operations_logger.network_logger.info("** starting up on port " + str(flask_http_port) + " **")
http_server = pywsgi.WSGIServer((flask_http_ip, flask_http_port), app)
http_server.serve_forever()
