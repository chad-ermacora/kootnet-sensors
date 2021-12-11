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
import time
from threading import Thread
from operations_modules import logger
from operations_modules.app_generic_disk import get_file_content, write_file_to_disk


class CreateGeneralConfiguration:
    """ Base Configuration Template Class """

    def __init__(self, config_file_location, load_from_file=True):
        self.load_from_file = load_from_file
        self.config_file_location = config_file_location
        self.config_file_header = "General Configuration File"
        self.valid_setting_count = 0
        self.config_settings = []
        self.config_settings_names = []

    def _init_config_variables(self):
        """ Sets configuration settings from file, saves default if missing. """

        try:
            if self.check_config_file_exists():
                self.set_config_with_str(get_file_content(self.config_file_location))
        except Exception as error:
            log_msg = "Error setting variables from "
            log_msg2 = "Saving Default Configuration for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location) + " - " + str(error))
            logger.primary_logger.warning(log_msg2 + str(self.config_file_location))
            self.save_config_to_file()

    def check_config_file_exists(self):
        if not os.path.isfile(self.config_file_location):
            logger.primary_logger.info(self.config_file_location + " Not found, saving default")
            self.save_config_to_file()
            return False
        return True

    def save_config_to_file(self):
        """ Saves configuration to file. """
        logger.primary_logger.debug("Saving Configuration to " + str(self.config_file_location))

        write_file_to_disk(self.config_file_location, self.get_config_as_str())

    def get_config_as_str(self):
        """ Returns configuration as a String. """
        logger.primary_logger.debug("Returning Configuration as string for " + str(self.config_file_location))

        new_file_content = self.config_file_header + "\n"
        for setting, setting_name in zip(self.config_settings, self.config_settings_names):
            new_file_content += str(setting) + " = " + str(setting_name) + "\n"
        return new_file_content

    def set_config_with_str(self, config_file_text):
        """ Sets configuration with the provided Text. """

        if config_file_text is not None:
            config_file_text = config_file_text.strip().split("\n")
            config_file_text = config_file_text[1:]  # Remove the header that's not a setting
            if not self.valid_setting_count == len(config_file_text):
                if self.load_from_file:
                    log_msg = "Invalid number of settings found in "
                    logger.primary_logger.warning(log_msg + str(self.config_file_location) + " - Please Check Config")

            self.config_settings = []
            for line in config_file_text:
                try:
                    final_setting = ""
                    line_split = line.split("=")[:-1]
                    if len(line_split) > 1:
                        for section in line_split:
                            final_setting += section + "="
                        final_setting = final_setting[:-1]
                    else:
                        final_setting = line_split[0]
                    setting = final_setting.strip()
                except Exception as error:
                    if self.load_from_file:
                        logger.primary_logger.warning(str(self.config_file_location) + " - " + str(error))
                    setting = "error"
                self.config_settings.append(setting)
        else:
            if self.load_from_file:
                logger.primary_logger.error("Null configuration text provided " + str(self.config_file_location))


class CreateMonitoredThread:
    """
    Creates a thread and checks every 30 seconds to make sure it's still running.
    If the thread stops, it will be restarted up to 5 times by default.
    If it gets restarted more than 5 times, it logs an error message and stops.
    """

    def __init__(self, function, args=None, thread_name="Generic Thread", max_restart_tries=10):
        self.is_running = True
        self.current_state = "Starting"
        self.function = function
        self.args = args
        self.thread_name = thread_name
        self.current_restart_count = 0
        self.max_restart_count = max_restart_tries

        self.shutdown_thread = False

        if self.args is not None:
            self.monitored_thread = Thread(target=self.function, args=self.args)
        else:
            self.monitored_thread = Thread(target=self.function)
        self.monitored_thread.daemon = True

        self.watch_thread = Thread(target=self._thread_and_monitor)
        self.watch_thread.daemon = True
        self.watch_thread.start()

        self.restart_watch_thread = Thread(target=self._restart_count_reset_watch)
        self.restart_watch_thread.daemon = True
        self.restart_watch_thread.start()
        self.current_state = "Running"

    def _restart_count_reset_watch(self):
        """ Resets self.current_restart_count to 0 if it's been longer then 60 seconds since a restart. """

        last_restart_time = time.time()
        last_count = 0
        while True:
            if self.current_restart_count:
                if last_count != self.current_restart_count:
                    last_count = self.current_restart_count
                    last_restart_time = time.time()
                elif time.time() - last_restart_time > 60:
                    self.current_restart_count = 0
            time.sleep(30)

    def _thread_and_monitor(self):
        logger.primary_logger.debug(" -- Starting " + self.thread_name + " Thread")

        self.monitored_thread.start()
        while not self.shutdown_thread:
            if not self.monitored_thread.is_alive():
                logger.primary_logger.info(self.thread_name + " Restarting...")
                self.is_running = False
                self.current_state = "Restarting"
                self.current_restart_count += 1
                if self.current_restart_count < self.max_restart_count:
                    if self.args is None:
                        self.monitored_thread = Thread(target=self.function)
                    else:
                        self.monitored_thread = Thread(target=self.function, args=self.args)
                    self.monitored_thread.daemon = True
                    self.monitored_thread.start()
                    self.is_running = True
                    self.current_state = "Running"
                else:
                    log_msg = self.thread_name + " has restarted " + str(self.current_restart_count)
                    log_msg += " times in less then 1 minutes."
                    logger.primary_logger.critical(log_msg + " No further restart attempts will be made.")
                    self.current_state = "Error"
                    while True:
                        time.sleep(600)
            time.sleep(5)
        self.current_state = "Stopped"
        self.shutdown_thread = False


class CreateNetworkSystemCommands:
    """ Create an object instance holding available network "System" commands (Mostly Upgrades). """

    def __init__(self):
        self.upgrade_system_os = "UpgradeSystemOS"
        self.upgrade_pip_modules = "UpdatePipModules"

        self.upgrade_http = "UpgradeOnline"
        self.upgrade_http_dev = "UpgradeOnlineDev"
        self.upgrade_http_clean = "UpgradeOnlineClean"
        self.upgrade_http_clean_dev = "UpgradeOnlineCleanDEV"

        self.upgrade_smb = "UpgradeSMB"
        self.upgrade_smb_dev = "UpgradeSMBDev"
        self.upgrade_smb_clean = "UpgradeSMBClean"
        self.upgrade_smb_clean_dev = "UpgradeSMBCleanDEV"

        self.restart_services = "RestartServices"
        self.restart_system = "RebootSystem"
        self.shutdown_system = "ShutdownSystem"


class CreateNetworkSetCommands:
    """ Create a object instance holding available network "Set" commands (AKA set configurations on remote sensor). """

    def __init__(self):
        self.set_primary_configuration = "SetPrimaryConfiguration"
        self.set_installed_sensors = "SetInstalledSensors"

        self.set_interval_configuration = "SetIntervalConfiguration"
        self.set_high_low_trigger_config = "SetHighLowTriggerConfiguration"
        self.set_variance_configuration = "SetVarianceConfiguration"

        self.set_display_config = "SetDisplayConfiguration"
        self.set_email_configuration = "SetEmailConfiguration"
        self.set_wifi_configuration = "SetWifiConfiguration"

        self.set_weather_underground_configuration = "SetWeatherUndergroundConfiguration"
        self.set_luftdaten_configuration = "SetLuftdatenConfiguration"
        self.set_open_sense_map_configuration = "SetOpenSenseMapConfiguration"


class CreateNetworkGetCommands:
    """ Create a object instance holding available network "Get" commands (AKA get data from remote sensor). """

    def __init__(self):
        self.check_online_status = "CheckOnlineStatus"
        self.check_portal_login = "TestLogin"

        self.sensor_name = "GetHostName"
        self.sensor_id = "GetSensorID"

        self.os_version = "GetOSVersion"
        self.program_version = "GetSensorVersion"
        self.program_last_updated = "GetProgramLastUpdated"

        self.rm_system_report = "atpro/rm-get-system-entry"
        self.rm_config_report = "atpro/rm-get-config-entry"
        self.rm_readings_report = "atpro/rm-get-readings-entry"
        self.rm_latency_report = "atpro/rm-get-latency-entry"

        self.system_uptime = "GetSystemUptime"
        self.system_uptime_minutes = "GetSystemUptimeMinutes"
        self.system_date_time = "GetSystemDateTime"
        self.system_ram_used = "GetRAMUsed"
        self.system_ram_free = "GetRAMFree"
        self.system_ram_total = "GetRAMTotal"
        self.system_ram_size_type = "GetRAMTotalSizeType"
        self.system_disk_space_free = "GetFreeDiskSpace"

        self.sensor_sql_all_databases_zip = "DownloadALLSQLDatabases"
        self.sensor_sql_database = "DownloadSQLDatabase"
        self.sensor_sql_database_raw = "DownloadSQLDatabaseRAW"
        self.sensor_sql_database_size = "GetSQLDBSize"
        self.sensor_zipped_sql_database_size = "GetZippedSQLDatabaseSize"

        self.primary_configuration_file = "GetPrimaryConfiguration"
        self.installed_sensors_file = "GetInstalledSensors"
        self.interval_configuration_file = "GetIntervalConfiguration"
        self.high_low_trigger_configuration_file = "GetHighLowTriggerConfiguration"
        self.variance_config_file = "GetVarianceConfiguration"
        self.display_configuration_file = "GetDisplayConfiguration"
        self.email_configuration_file = "GetEmailConfiguration"
        self.email_reports_configuration_file = "GetEmailReportsConfiguration"
        self.email_db_graphs_configuration_file = "GetEmailDatabaseGraphsConfiguration"
        self.wifi_config_file = "GetWifiConfiguration"
        self.weather_underground_config_file = "GetWeatherUndergroundConfiguration"
        self.luftdaten_config_file = "GetOnlineServicesLuftdaten"
        self.open_sense_map_config_file = "GetOnlineServicesOpenSenseMap"

        self.download_zipped_logs = "DownloadZippedLogs"

        self.download_zipped_everything = "DownloadZippedEverything"

        self.sensor_readings = "GetAllSensorReadings"
        self.sensors_latency = "GetSensorsLatency"

        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.altitude = "GetAltitude"
        self.humidity = "GetHumidity"
        self.distance = "GetDistance"
        self.dew_point = "GetDewPoint"

        self.all_gas = "GetAllGas"
        self.gas_resistance_index = "GetGasResistanceIndex"
        self.gas_oxidising = "GetGasOxidising"
        self.gas_reducing = "GetGasReducing"
        self.gas_nh3 = "GetGasNH3"

        self.all_particulate_matter = "GetAllParticulateMatter"
        self.particulate_matter_1 = "GetParticulateMatter1"
        self.particulate_matter_2_5 = "GetParticulateMatter2_5"
        self.particulate_matter_4 = "GetParticulateMatter4"
        self.particulate_matter_10 = "GetParticulateMatter10"

        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMSColors"
        self.red = "GetRed"
        self.orange = "GetOrange"
        self.yellow = "GetYellow"
        self.green = "GetGreen"
        self.blue = "GetBlue"
        self.violet = "GetViolet"

        self.all_ultra_violet = "GetAllUltraViolet"
        self.ultra_violet_index = "GetUltraVioletIndex"
        self.ultra_violet_a = "GetUltraVioletA"
        self.ultra_violet_b = "GetUltraVioletB"

        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.acc_x = "GetAccX"
        self.acc_y = "GetAccY"
        self.acc_z = "GetAccZ"

        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.mag_x = "GetMagX"
        self.mag_y = "GetMagY"
        self.mag_z = "GetMagZ"

        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.gyro_x = "GetGyroX"
        self.gyro_y = "GetGyroY"
        self.gyro_z = "GetGyroZ"

        self.no_http_auth_required_commands_list = [
            self.check_online_status, self.sensor_name, self.sensor_id, self.os_version, self.program_version,
            self.program_last_updated, self.rm_system_report, self.rm_readings_report, self.rm_latency_report,
            self.system_uptime, self.system_date_time, self.system_ram_used, self.system_ram_free,
            self.system_ram_total, self.system_ram_size_type, self.system_disk_space_free, self.installed_sensors_file,
            self.interval_configuration_file, self.high_low_trigger_configuration_file, self.variance_config_file,
            self.display_configuration_file, self.luftdaten_config_file, self.sensor_readings, self.sensors_latency,
            self.cpu_temp, self.environmental_temp, self.env_temp_offset, self.pressure, self.altitude, self.humidity,
            self.distance, self.all_gas, self.all_particulate_matter, self.lumen, self.electromagnetic_spectrum,
            self.all_ultra_violet, self.accelerometer_xyz, self.magnetometer_xyz, self.gyroscope_xyz,
            self.gas_resistance_index, self.gas_oxidising, self.gas_reducing, self.gas_nh3, self.particulate_matter_1,
            self.particulate_matter_2_5, self.particulate_matter_4, self.particulate_matter_10, self.red, self.orange,
            self.yellow, self.green, self.blue, self.violet, self.ultra_violet_index, self.ultra_violet_a,
            self.ultra_violet_b, self.acc_x, self.acc_y, self.acc_z, self.mag_x, self.mag_y, self.mag_z, self.gyro_x,
            self.gyro_y, self.gyro_z, self.system_uptime_minutes, "SensorCheckin", "remote-sensor-checkin"
        ] + CreateLiveGraphWrapperNetworkGetCommands().no_http_auth_required_commands_list


class CreateLiveGraphWrapperNetworkGetCommands:
    """ Create a object instance holding Wrapper versions of available network "Get" commands """

    def __init__(self):
        self.sensor_name = "LGWGetHostName"
        self.sensor_id = "LGWGetSensorID"

        self.os_version = "LGWGetOSVersion"
        self.program_version = "LGWGetSensorVersion"
        self.program_last_updated = "LGWGetProgramLastUpdated"

        self.system_uptime = "LGWGetSystemUptime"
        self.system_uptime_minutes = "LGWGetSystemUptimeMinutes"
        self.system_date_time = "LGWGetSystemDateTime"
        self.system_ram_used = "LGWGetRAMUsed"
        self.system_ram_free = "LGWGetRAMFree"
        self.system_ram_total = "LGWGetRAMTotal"
        self.system_ram_size_type = "LGWGetRAMTotalSizeType"
        self.system_disk_space_free = "LGWGetFreeDiskSpace"

        self.cpu_temp = "LGWGetCPUTemperature"
        self.environmental_temp = "LGWGetEnvTemperature"
        self.env_temp_offset = "LGWGetTempOffsetEnv"
        self.pressure = "LGWGetPressure"
        self.altitude = "LGWGetAltitude"
        self.humidity = "LGWGetHumidity"
        self.distance = "LGWGetDistance"
        self.dew_point = "LGWGetDewPoint"

        self.all_gas = "LGWGetAllGas"
        self.gas_resistance_index = "LGWGetGasResistanceIndex"
        self.gas_oxidising = "LGWGetGasOxidising"
        self.gas_reducing = "LGWGetGasReducing"
        self.gas_nh3 = "LGWGetGasNH3"

        self.all_particulate_matter = "LGWGetAllParticulateMatter"
        self.particulate_matter_1 = "LGWGetParticulateMatter1"
        self.particulate_matter_2_5 = "LGWGetParticulateMatter2_5"
        self.particulate_matter_4 = "LGWGetParticulateMatter4"
        self.particulate_matter_10 = "LGWGetParticulateMatter10"

        self.lumen = "LGWGetLumen"
        self.electromagnetic_spectrum = "LGWGetEMSColors"
        self.red = "LGWGetRed"
        self.orange = "LGWGetOrange"
        self.yellow = "LGWGetYellow"
        self.green = "LGWGetGreen"
        self.blue = "LGWGetBlue"
        self.violet = "LGWGetViolet"

        self.all_ultra_violet = "LGWGetAllUltraViolet"
        self.ultra_violet_index = "LGWGetUltraVioletIndex"
        self.ultra_violet_a = "LGWGetUltraVioletA"
        self.ultra_violet_b = "LGWGetUltraVioletB"

        self.accelerometer_xyz = "LGWGetAccelerometerXYZ"
        self.acc_x = "LGWGetAccX"
        self.acc_y = "LGWGetAccY"
        self.acc_z = "LGWGetAccZ"

        self.magnetometer_xyz = "LGWGetMagnetometerXYZ"
        self.mag_x = "LGWGetMagX"
        self.mag_y = "LGWGetMagY"
        self.mag_z = "LGWGetMagZ"

        self.gyroscope_xyz = "LGWGetGyroscopeXYZ"
        self.gyro_x = "LGWGetGyroX"
        self.gyro_y = "LGWGetGyroY"
        self.gyro_z = "LGWGetGyroZ"

        self.no_http_auth_required_commands_list = [
            self.sensor_name, self.sensor_id, self.os_version, self.program_version, self.program_last_updated,
            self.system_uptime, self.system_uptime_minutes, self.system_date_time, self.system_ram_used,
            self.system_ram_free, self.system_ram_total, self.system_ram_size_type, self.system_disk_space_free,
            self.cpu_temp, self.environmental_temp, self.env_temp_offset, self.pressure, self.altitude, self.humidity,
            self.distance, self.dew_point, self.all_gas, self.gas_resistance_index, self.gas_oxidising,
            self.gas_reducing, self.gas_nh3, self.all_particulate_matter, self.particulate_matter_1,
            self.particulate_matter_2_5, self.particulate_matter_4, self.particulate_matter_10, self.lumen,
            self.electromagnetic_spectrum, self.red, self.orange, self.yellow, self.green, self.blue, self.violet,
            self.all_ultra_violet, self.ultra_violet_index, self.ultra_violet_a, self.ultra_violet_b,
            self.accelerometer_xyz, self.acc_x, self.acc_y, self.acc_z, self.magnetometer_xyz, self.mag_x, self.mag_y,
            self.mag_z, self.gyroscope_xyz, self.gyro_x, self.gyro_y, self.gyro_z
        ]


class CreateDatabaseVariables:
    """ Creates a object instance holding SQLite3 database table and row names. """

    def __init__(self):
        self.table_interval = "IntervalData"
        self.table_trigger = "TriggerData"
        self.table_other = "OtherData"
        self.table_ks_info = "SensorInformation"
        self.table_db_info = "KootnetSensorsDatabaseInfo"

        self.db_info_database_type_main = "Main"
        self.db_info_database_type_mqtt = "MQTT"
        self.db_info_database_type_sensor_checkins = "SensorCheckins"

        self.db_info_database_type_column = "DatabaseType"

        self.other_table_column_user_date_time = "UserDateTime"
        self.other_table_column_notes = "Notes"

        self.ks_info_configuration_backups = "ConfigurationsZIP"
        self.ks_info_configuration_backups_md5 = "ConfigurationsZIP_MD5"
        self.ks_info_logs = "LogsZIP"

        self.sensor_check_in_installed_sensors = "InstalledSensors"
        self.sensor_check_in_primary_log = "PrimaryLog"
        self.sensor_check_in_network_log = "NetworkLog"
        self.sensor_check_in_sensors_log = "SensorsLog"

        self.trigger_state = "TriggerState"

        self.all_tables_datetime = "DateTime"
        self.kootnet_sensors_version = "KootnetVersion"
        self.sensor_name = "SensorName"
        self.ip = "IP"
        self.sensor_uptime = "SensorUpTime"

        self.system_temperature = "SystemTemp"
        self.env_temperature = "EnvironmentTemp"
        self.env_temperature_offset = "EnvTempOffset"
        self.pressure = "Pressure"
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.dew_point = "Dew_Point"
        self.distance = "Distance"

        self.gas_all_dic = "All_Gas_As_Dictionary"
        self.gas_resistance_index = "Gas_Resistance_Index"
        self.gas_oxidising = "Gas_Oxidising"
        self.gas_reducing = "Gas_Reducing"
        self.gas_nh3 = "Gas_NH3"

        self.particulate_matter_all_dic = "All_Particulate_Matter_As_Dictionary"
        self.particulate_matter_1 = "Particulate_Matter_1"
        self.particulate_matter_2_5 = "Particulate_Matter_2_5"
        self.particulate_matter_4 = "Particulate_Matter_4"
        self.particulate_matter_10 = "Particulate_Matter_10"

        self.lumen = "Lumen"

        self.colour_all_dic = "All_Colours_As_Dictionary"
        self.red = "Red"
        self.orange = "Orange"
        self.yellow = "Yellow"
        self.green = "Green"
        self.blue = "Blue"
        self.violet = "Violet"

        self.ultra_violet_all_dic = "All_Ultra_Violet_As_Dictionary"
        self.ultra_violet_index = "Ultra_Violet_Index"
        self.ultra_violet_a = "Ultra_Violet_A"
        self.ultra_violet_b = "Ultra_Violet_B"

        self.acc_all_dic = "All_Acceleration_As_Dictionary"
        self.acc_x = "Acc_X"
        self.acc_y = "Acc_Y"
        self.acc_z = "Acc_Z"

        self.mag_all_dic = "All_Magnetometer_As_Dictionary"
        self.mag_x = "Mag_X"
        self.mag_y = "Mag_Y"
        self.mag_z = "Mag_Z"

        self.gyro_all_dic = "All_Gyroscope_As_Dictionary"
        self.gyro_x = "Gyro_X"
        self.gyro_y = "Gyro_Y"
        self.gyro_z = "Gyro_Z"

        self.gps_all_dic = "All_GPS_As_Dictionary"
        self.latitude = "Latitude"
        self.longitude = "Longitude"
        self.gps_timestamp = "GPS_Timestamp"
        self.gps_num_satellites = "GPS_Number_Of_Satellites"
        self.gps_quality = "GPS_Quality"
        self.gps_mode_fix_type = "GPS_Mode_Fix_Type"
        self.gps_speed_over_ground = "GPS_Speed_Over_Ground"

        self.gps_pdop = "GPS_PDOP"
        self.gps_hdop = "GPS_HDOP"
        self.gps_vdop = "GPS_VDOP"

    def get_sensor_columns_list(self):
        """ Returns SQL Table columns used for Interval recording as a list. """
        sensor_sql_columns = [self.all_tables_datetime,
                              self.sensor_name,
                              self.ip,
                              self.sensor_uptime,
                              self.system_temperature,
                              self.env_temperature,
                              self.env_temperature_offset,
                              self.pressure,
                              self.altitude,
                              self.humidity,
                              self.dew_point,
                              self.distance,
                              self.gas_resistance_index,
                              self.gas_oxidising,
                              self.gas_reducing,
                              self.gas_nh3,
                              self.particulate_matter_1,
                              self.particulate_matter_2_5,
                              self.particulate_matter_4,
                              self.particulate_matter_10,
                              self.lumen,
                              self.red,
                              self.orange,
                              self.yellow,
                              self.green,
                              self.blue,
                              self.violet,
                              self.ultra_violet_index,
                              self.ultra_violet_a,
                              self.ultra_violet_b,
                              self.acc_x,
                              self.acc_y,
                              self.acc_z,
                              self.mag_x,
                              self.mag_y,
                              self.mag_z,
                              self.gyro_x,
                              self.gyro_y,
                              self.gyro_z,
                              self.latitude,
                              self.longitude,
                              self.gps_timestamp,
                              self.gps_num_satellites,
                              self.gps_quality,
                              self.gps_mode_fix_type,
                              self.gps_speed_over_ground,
                              self.gps_pdop,
                              self.gps_hdop,
                              self.gps_vdop]
        return sensor_sql_columns

    def get_other_columns_list(self):
        """ Returns "Other" SQL Table columns as a list. """
        other_sql_columns = [self.other_table_column_user_date_time,
                             self.other_table_column_notes]
        return other_sql_columns


class CreateLatencyVariables:
    def __init__(self):
        self.cpu_temperature = "CPU Temperature"
        self.environment_temperature = "Environmental Temperature"
        self.pressure = "Pressure"
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.distance = "Distance"
        self.gas = "GAS"
        self.particulate_matter = "Particulate Matter"
        self.lumen = "Lumen"
        self.colours = "Colours"
        self.ultra_violet = "Ultra Violet"
        self.accelerometer_xyz = "Accelerometer XYZ"
        self.magnetometer_xyz = "Magnetometer XYZ"
        self.gyroscope_xyz = "Gyroscope XYZ"
        self.gps = "GPS"

    def get_all_latency_as_list(self):
        return [self.cpu_temperature, self.environment_temperature, self.pressure, self.altitude,
                self.humidity, self.distance, self.gas, self.particulate_matter, self.lumen,
                self.colours, self.ultra_violet, self.accelerometer_xyz, self.magnetometer_xyz, self.gyroscope_xyz,
                self.gps]


class CreateRefinedVersion:
    """ Takes the provided program version as text and creates a data class object. """
    def __init__(self, version_text=""):
        self.major_version = 0
        self.feature_version = 0
        self.minor_version = 0
        self.load_from_string(version_text)

    def load_from_string(self, version_text):
        try:
            if len(version_text) < 15:
                version_split = str(version_text).strip().split(".")
                if len(version_split) == 3:
                    self.major_version = self._convert_to_int(version_split[0])
                    self.feature_version = self._convert_to_int(version_split[1])
                    self.minor_version = self._convert_to_int(version_split[2])
                else:
                    logger.primary_logger.debug("Software Version - Invalid version text")
        except Exception as error:
            logger.primary_logger.debug("Software Version - Error converting text to version: " + str(error))

    def get_version_string(self):
        return str(self.major_version) + "." + str(self.feature_version) + "." + str(self.minor_version)

    @staticmethod
    def _convert_to_int(text_number):
        try:
            return int(text_number)
        except Exception as error:
            logger.primary_logger.debug("Software Version - Refined Conversion Error: " + str(error))
            return 0


class CreateEmptyThreadClass:
    def __init__(self):
        self.current_state = "Disabled"
