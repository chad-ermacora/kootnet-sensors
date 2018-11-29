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
from shutil import disk_usage
from time import sleep

import operations_config
import operations_db
import operations_logger
import operations_sensors
import sensor_modules.Linux_OS as Linux_System
import sensor_modules.RaspberryPi_System as RaspberryPi_Sensors

sensor_system = RaspberryPi_Sensors.CreateRPSystem()
sensor_os = Linux_System.CreateLinuxSystem()

bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_programs_e-Ink.sh",
                 "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/update_programs_online.sh",
                 "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/update_programs_smb.sh",
                 "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                 "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "UpgradeSystemOS": "apt-get update && apt-get scripts -y && reboot"}


def get_sensor_readings():
    """ Returns sensor types and readings for interval and trigger sensors in html table format. """

    return_data = ""
    return_types = ""
    interval_data = operations_sensors.get_interval_sensor_readings()
    trigger_data = operations_sensors.get_trigger_sensor_readings()

    str_interval_types = interval_data.sensor_types.split(",")
    str_interval_data = interval_data.sensor_readings.split(",")
    str_trigger_types = trigger_data.sensor_types.split(",")[3:]
    str_trigger_data = trigger_data.sensor_readings.split(",")[3:]

    count = 0
    for interval_type in str_interval_types:
        return_types += "<th><span style='background-color: #00ffff;'>" + interval_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + str_interval_data[count] + "</span></th>"
        count = count + 1

    count = 0
    for trigger_type in str_trigger_types:
        return_types += "<th><span style='background-color: #00ffff;'>" + \
                        trigger_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + str_trigger_data[count] + "</span></th>"
        count = count + 1

    return [return_types, return_data]


def get_system_information():
    """ Returns System Information needed for a Control Center 'System Report'. """
    sensor_config = operations_config.get_installed_config()
    free_disk = disk_usage("/")[2]

    try:
        str_sensor_data = str(sensor_os.get_hostname()) + \
                          "," + str(sensor_os.get_ip()) + \
                          "," + str(sensor_os.get_sys_datetime()) + \
                          "," + str(sensor_os.get_uptime()) + \
                          "," + str(operations_config.version) + \
                          "," + str(round(sensor_system.cpu_temperature(), 2)) + \
                          "," + str(round(free_disk / (2 ** 30), 2)) + \
                          "," + str(sensor_os.get_sql_db_size()) + \
                          "," + str(sensor_config.write_to_db) + \
                          "," + str(sensor_config.enable_custom) + \
                          "," + str(get_last_updated())
    except Exception as error:
        operations_logger.network_logger.error("Sensor reading failed - " + str(error))
        str_sensor_data = "Sensor Unit, Data Retrieval, Failed, 0, 0, 0, 0, 0, 0, 0, 0, 0"

    return str_sensor_data


def get_config_information():
    """ Opens configuration file and returns it as a comma separated string. """
    temp_config = operations_config.get_installed_config()
    installed_sensors = operations_config.get_installed_sensors()

    str_installed_sensors = ""
    if installed_sensors.linux_system:
        str_installed_sensors = str_installed_sensors + installed_sensors.linux_system_name + " || "
    if installed_sensors.raspberry_pi_zero_w:
        str_installed_sensors = str_installed_sensors + installed_sensors.raspberry_pi_zero_w_name + " || "
    if installed_sensors.raspberry_pi_3b_plus:
        str_installed_sensors = str_installed_sensors + installed_sensors.raspberry_pi_3b_plus_name + " || "
    if installed_sensors.raspberry_pi_sense_hat:
        str_installed_sensors = str_installed_sensors + installed_sensors.raspberry_pi_sense_hat_name + " || "
    if installed_sensors.pimoroni_bh1745:
        str_installed_sensors = str_installed_sensors + installed_sensors.pimoroni_bh1745_name + " || "
    if installed_sensors.pimoroni_bme680:
        str_installed_sensors = str_installed_sensors + installed_sensors.pimoroni_bme680_name + " || "
    if installed_sensors.pimoroni_enviro:
        str_installed_sensors = str_installed_sensors + installed_sensors.pimoroni_enviro_name + " || "
    if installed_sensors.pimoroni_lsm303d:
        str_installed_sensors = str_installed_sensors + installed_sensors.pimoroni_lsm303d_name + " || "
    if installed_sensors.pimoroni_vl53l1x:
        str_installed_sensors = str_installed_sensors + installed_sensors.pimoroni_vl53l1x_name + " || "

    str_installed_sensors = str_installed_sensors[:-4]

    try:
        tmp_str_config = str(temp_config.sleep_duration_interval) + \
                         "," + str(temp_config.sleep_duration_trigger) + \
                         "," + str(temp_config.write_to_db) + \
                         "," + str(temp_config.enable_custom) + \
                         "," + str(temp_config.acc_variance) + \
                         "," + str(temp_config.mag_variance) + \
                         "," + str(temp_config.gyro_variance) + \
                         "," + str(str_installed_sensors)

    except Exception as error:
        operations_logger.network_logger.error("Getting sensor config failed - " + str(error))
        tmp_str_config = "0, 0, 0, 0, 0, 0, 0"

    return tmp_str_config


def get_sensor_log(log_file):
    """ Opens provided log file location and returns its content. """
    log_content = open(log_file, "r")
    log = log_content.read()
    log_content.close()
    return log


def get_last_updated():
    """ Returns when the sensor programs were last updated and how. """
    try:
        last_updated_file = open(operations_config.last_updated_file_location, "r")
        tmp_last_updated = last_updated_file.readlines()
        last_updated_file.close()
        last_updated = str(tmp_last_updated[0]) + str(tmp_last_updated[1])
    except Exception as error:
        operations_logger.network_logger.error("Unable to Load Last Updated File: " + str(error))
        last_updated = "N/A"

    return last_updated


def set_sensor_config(config_data):
    """ Applies the provided configuration file and restarts the SQL recording service. """
    split_list_config = config_data.split(",")
    new_config = operations_config.CreateConfig()
    sensor_enable = "systemctl enable SensorRecording"
    sensor_start = "systemctl start SensorRecording"
    sensor_disable = "systemctl disable SensorRecording"
    sensor_stop = "systemctl stop SensorRecording"

    try:
        new_config.write_to_db = int(split_list_config[0])
        if new_config.write_to_db:
            os.system(sensor_enable + " && " + sensor_start)
        else:
            os.system(sensor_disable + " && " + sensor_stop)

    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Record Sensors to SQL Database' - " + str(error1))

    try:
        new_config.sleep_duration_interval = int(split_list_config[1])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Duration between Interval Readings' - " + str(error1))

    try:
        new_config.sleep_duration_trigger = float(split_list_config[2])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Duration between Trigger Readings' - " + str(error1))

    try:
        new_config.enable_custom = int(split_list_config[3])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Enable Custom Settings' - " + str(error1))

    try:
        new_config.acc_variance = float(split_list_config[4])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Accelerometer Variance' - " + str(error1))

    try:
        new_config.mag_variance = float(split_list_config[5])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Magnetometer Variance' - " + str(error1))

    try:
        new_config.gyro_variance = float(split_list_config[6])
    except Exception as error1:
        operations_logger.network_logger.error("Bad config 'Gyroscope Variance' - " + str(error1))

    operations_config.write_config_to_file(new_config)
    os.system("systemctl restart SensorRecording")


def restart_services():
    """ Reloads systemd service files & restarts all sensor program services. """
    os.system("systemctl daemon-reload && "
              "systemctl restart SensorRecording")
    # Sleep to make sure logs are created before setting permissions
    # Needed for remote log viewing on first run
    sleep(5)
    os.system("bash /opt/kootnet-sensors/scripts/set_permissions.sh")
    os.system("systemctl restart SensorCommands")


def add_note_to_database(datetime_note):
    sql_data = operations_db.CreateOtherDataEntry()
    datetime_note = datetime_note.strip()
    datetime_note = datetime_note.replace("'", '"')
    custom_datetime = "'" + datetime_note[:23] + "'"
    note = "'" + datetime_note[23:] + "'"

    sql_data.sensor_types = "DateTime, Notes"
    sql_data.sensor_readings = custom_datetime + ", " + note

    sql_execute = (sql_data.sql_query_start + sql_data.sensor_types +
                   sql_data.sql_query_values_start + sql_data.sensor_readings +
                   sql_data.sql_query_values_end)

    operations_db.write_to_sql_database(sql_execute)
