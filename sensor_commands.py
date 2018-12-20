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

from flask import Flask, request
from gevent import monkey, pywsgi

from operations_modules import operations_commands
from operations_modules import operations_config
from operations_modules import operations_html_templates
from operations_modules import operations_logger
from operations_modules import operations_sensors

if operations_config.get_old_version() != operations_config.version:
    operations_logger.primary_logger.info("Upgrade taking place, waiting for service restart ...")
    # Sleep before loading anything due to needed updates
    # The update service started by "record_to_db.py" will automatically restart this app when it's done
    while True:
        sleep(10)

monkey.patch_all()
app = Flask(__name__)

installed_sensors = operations_config.get_installed_sensors()

# If installed, start up SenseHAT Joystick program
if installed_sensors.raspberry_pi_sense_hat:
    sense_joy_stick_thread = Thread(target=operations_sensors.rp_sense_hat_sensor_access.start_joy_stick_commands)
    sense_joy_stick_thread.daemon = True
    sense_joy_stick_thread.start()


@app.route("/")
def root_http():
    return "KootNet Sensors || Raspberry Pi Sensor"


@app.route("/Ver")
def show_version():
    message = "<p>KootNet Sensors || " + operations_config.version + "</p>"
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
    return str(operations_commands.get_sensor_readings())


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
    current_installed_sensors = operations_config.get_installed_sensors()
    installed_sensors_str = operations_config.installed_sensors_convert_to_file(current_installed_sensors)
    return installed_sensors_str


@app.route("/GetConfiguration")
def get_configuration():
    operations_logger.network_logger.info("* Sent Sensors Configuration")
    current_installed_config = operations_config.get_installed_config()
    installed_config_str = operations_config.config_convert_to_file(current_installed_config)
    return installed_config_str


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


@app.route("/DownloadPrimaryLog")
def download_primary_log():
    operations_logger.network_logger.info("* Sent Full Primary Log")
    log = operations_commands.get_sensor_log(operations_logger.primary_log)
    return log


@app.route("/DownloadNetworkLog")
def download_network_log():
    operations_logger.network_logger.info("* Sent Full Network Log")
    log = operations_commands.get_sensor_log(operations_logger.network_log)
    return log


@app.route("/DownloadSensorsLog")
def download_sensors_log():
    operations_logger.network_logger.info("* Sent Full Sensor Log")
    log = operations_commands.get_sensor_log(operations_logger.sensors_log)
    return log


@app.route("/DownloadSQLDatabase")
def download_sensors_sql_database():
    operations_logger.network_logger.info("* Sent Sensor SQL Database")
    local_db = open(operations_config.sensor_database_location, "rb")
    sensor_database = local_db.read()
    local_db.close()
    return sensor_database


@app.route("/PutDatabaseNote", methods=["PUT"])
def put_sql_note():
    new_note = request.form['command_data']
    operations_commands.add_note_to_database(new_note)
    operations_logger.network_logger.info("* Inserted Note into Database")
    return "OK"


@app.route("/UpgradeOnline", methods=["PUT"])
def upgrade_http():
    os.system(operations_commands.bash_commands["UpgradeOnline"])
    operations_logger.network_logger.info("* update_programs_online.sh Complete")
    return "OK"


@app.route("/CleanOnline")
def upgrade_clean_http():
    os.system(operations_commands.bash_commands["CleanOnline"])
    operations_logger.network_logger.info("* Started Clean Upgrade - HTTP")
    return "OK"


@app.route("/UpgradeSMB")
def upgrade_smb():
    os.system(operations_commands.bash_commands["UpgradeSMB"])
    operations_logger.network_logger.info("* update_programs_smb.sh Complete")
    return "OK"


@app.route("/CleanSMB")
def upgrade_clean_smb():
    os.system(operations_commands.bash_commands["CleanSMB"])
    operations_logger.network_logger.info("* Started Clean Upgrade - SMB")
    return "OK"


@app.route("/UpgradeSystemOS")
def upgrade_system_os():
    operations_logger.network_logger.info("* Updating Operating System & rebooting")
    os.system(operations_commands.bash_commands["UpgradeSystemOS"])
    return "OK"


@app.route("/inkupg")
def upgrade_rp_controller():
    os.system(operations_commands.bash_commands["inkupg"])
    operations_logger.network_logger.info("* update_programs_e-Ink.sh Complete")
    return "OK"


@app.route("/RebootSystem")
def system_reboot():
    operations_logger.network_logger.info("* Rebooting System")
    os.system(operations_commands.bash_commands["RebootSystem"])


@app.route("/ShutdownSystem")
def system_shutdown():
    operations_logger.network_logger.info("* System Shutdown started by " + str(request.remote_addr))
    os.system(operations_commands.bash_commands["ShutdownSystem"])


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
        operations_logger.network_logger.info("* Hostname Change Failed: " + str(error))
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
    new_config = operations_config.config_convert_from_file(raw_config)
    operations_config.write_config_to_file(new_config)
    operations_commands.restart_services()
    return "OK"


@app.route("/SetInstalledSensors", methods=["PUT"])
def set_installed_sensors():
    operations_logger.network_logger.info("* Setting Sensor Installed Sensors")
    raw_installed_sensors = request.form['command_data'].splitlines()
    new_installed_sensors = operations_config.installed_sensors_convert_from_file(raw_installed_sensors)
    operations_config.write_installed_sensors_to_file(new_installed_sensors)
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
    return str(operations_sensors.get_sensor_temperature_offset())


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


operations_logger.network_logger.info("** starting up on port " + str(operations_config.flask_http_port) + " **")
http_server = pywsgi.WSGIServer((operations_config.flask_http_ip, operations_config.flask_http_port), app)
http_server.serve_forever()
