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
import copy
from time import sleep
from datetime import datetime, timedelta
from operations_modules import logger
from operations_modules.app_generic_classes import CreateMonitoredThread
from operations_modules.email_server import CreateSensorReadingEmailAlert
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import sqlite_database
from sensor_modules import sensor_access

database_variables = app_cached_variables.database_variables


class _CreateHighLowTriggerThreadData:
    def __init__(self):
        config_high_low_triggers = app_config_access.trigger_high_low

        self.system_temperature = {
            "enabled": config_high_low_triggers.cpu_temperature_enabled,
            "get_reading_func": sensor_access.get_cpu_temperature,
            "sleep_duration": config_high_low_triggers.cpu_temperature_wait_seconds,
            "database_column": database_variables.system_temperature,
            "low_trigger": config_high_low_triggers.cpu_temperature_low,
            "high_trigger": config_high_low_triggers.cpu_temperature_high
        }
        self.env_temperature = {
            "enabled": config_high_low_triggers.env_temperature_enabled,
            "get_reading_func": sensor_access.get_environment_temperature,
            "sleep_duration": config_high_low_triggers.env_temperature_wait_seconds,
            "database_column": database_variables.env_temperature,
            "low_trigger": config_high_low_triggers.env_temperature_low,
            "high_trigger": config_high_low_triggers.env_temperature_high
        }
        self.pressure = {
            "enabled": config_high_low_triggers.pressure_enabled,
            "get_reading_func": sensor_access.get_pressure,
            "sleep_duration": config_high_low_triggers.pressure_wait_seconds,
            "database_column": database_variables.pressure,
            "low_trigger": config_high_low_triggers.pressure_low,
            "high_trigger": config_high_low_triggers.pressure_high
        }
        self.humidity = {
            "enabled": config_high_low_triggers.humidity_enabled,
            "get_reading_func": sensor_access.get_humidity,
            "sleep_duration": config_high_low_triggers.humidity_wait_seconds,
            "database_column": database_variables.humidity,
            "low_trigger": config_high_low_triggers.humidity_low,
            "high_trigger": config_high_low_triggers.humidity_high
        }
        self.altitude = {
            "enabled": config_high_low_triggers.altitude_enabled,
            "get_reading_func": sensor_access.get_altitude,
            "sleep_duration": config_high_low_triggers.altitude_wait_seconds,
            "database_column": database_variables.altitude,
            "low_trigger": config_high_low_triggers.altitude_low,
            "high_trigger": config_high_low_triggers.altitude_high
        }
        self.distance = {
            "enabled": config_high_low_triggers.distance_enabled,
            "get_reading_func": sensor_access.get_distance,
            "sleep_duration": config_high_low_triggers.distance_wait_seconds,
            "database_column": database_variables.distance,
            "low_trigger": config_high_low_triggers.distance_low,
            "high_trigger": config_high_low_triggers.distance_high
        }
        self.lumen = {
            "enabled": config_high_low_triggers.lumen_enabled,
            "get_reading_func": sensor_access.get_lumen,
            "sleep_duration": config_high_low_triggers.lumen_wait_seconds,
            "database_column": database_variables.lumen,
            "low_trigger": config_high_low_triggers.lumen_low,
            "high_trigger": config_high_low_triggers.lumen_high
        }

        self.colours = {
            "enabled": config_high_low_triggers.colour_enabled,
            "get_reading_func": sensor_access.get_ems_colors,
            "sleep_duration": config_high_low_triggers.colour_wait_seconds,
            "database_column": [database_variables.red, database_variables.orange, database_variables.yellow,
                                database_variables.green, database_variables.blue, database_variables.violet],
            "low_trigger": [config_high_low_triggers.red_low, config_high_low_triggers.orange_low,
                            config_high_low_triggers.yellow_low,
                            config_high_low_triggers.green_low, config_high_low_triggers.blue_low,
                            config_high_low_triggers.violet_low],
            "high_trigger": [config_high_low_triggers.red_high, config_high_low_triggers.orange_high,
                             config_high_low_triggers.yellow_high,
                             config_high_low_triggers.green_high, config_high_low_triggers.blue_high,
                             config_high_low_triggers.violet_high]
        }
        self.ultra_violet = {
            "enabled": config_high_low_triggers.ultra_violet_enabled,
            "get_reading_func": sensor_access.get_ultra_violet,
            "sleep_duration": config_high_low_triggers.ultra_violet_wait_seconds,
            "database_column": [database_variables.ultra_violet_a,
                                database_variables.ultra_violet_b],
            "low_trigger": [config_high_low_triggers.ultra_violet_a_low,
                            config_high_low_triggers.ultra_violet_b_low],
            "high_trigger": [config_high_low_triggers.ultra_violet_a_high,
                             config_high_low_triggers.ultra_violet_b_high]
        }
        self.gas_resistance = {
            "enabled": config_high_low_triggers.gas_enabled,
            "get_reading_func": sensor_access.get_gas,
            "sleep_duration": config_high_low_triggers.gas_wait_seconds,
            "database_column": [database_variables.gas_resistance_index,
                                database_variables.gas_oxidising,
                                database_variables.gas_reducing,
                                database_variables.gas_nh3],
            "low_trigger": [config_high_low_triggers.gas_resistance_index_low,
                            config_high_low_triggers.gas_oxidising_low,
                            config_high_low_triggers.gas_reducing_low,
                            config_high_low_triggers.gas_nh3_low],
            "high_trigger": [config_high_low_triggers.gas_resistance_index_high,
                             config_high_low_triggers.gas_oxidising_high,
                             config_high_low_triggers.gas_reducing_high,
                             config_high_low_triggers.gas_nh3_high]
        }
        self.particulate_matter = {
            "enabled": config_high_low_triggers.particulate_matter_enabled,
            "get_reading_func": sensor_access.get_particulate_matter,
            "sleep_duration": config_high_low_triggers.particulate_matter_wait_seconds,
            "database_column": [database_variables.particulate_matter_1,
                                database_variables.particulate_matter_2_5,
                                database_variables.particulate_matter_4,
                                database_variables.particulate_matter_10],
            "low_trigger": [config_high_low_triggers.particulate_matter_1_low,
                            config_high_low_triggers.particulate_matter_2_5_low,
                            config_high_low_triggers.particulate_matter_4_low,
                            config_high_low_triggers.particulate_matter_10_low],
            "high_trigger": [config_high_low_triggers.particulate_matter_1_high,
                             config_high_low_triggers.particulate_matter_2_5_high,
                             config_high_low_triggers.particulate_matter_4_high,
                             config_high_low_triggers.particulate_matter_10_high]
        }

        self.accelerometer = {
            "enabled": config_high_low_triggers.accelerometer_enabled,
            "get_reading_func": sensor_access.get_accelerometer_xyz,
            "sleep_duration": config_high_low_triggers.accelerometer_wait_seconds,
            "database_column": [database_variables.acc_x,
                                database_variables.acc_y,
                                database_variables.acc_z],
            "low_trigger": [config_high_low_triggers.accelerometer_x_low,
                            config_high_low_triggers.accelerometer_y_low,
                            config_high_low_triggers.accelerometer_z_low],
            "high_trigger": [config_high_low_triggers.accelerometer_x_high,
                             config_high_low_triggers.accelerometer_y_high,
                             config_high_low_triggers.accelerometer_z_high]
        }
        self.magnetometer = {
            "enabled": config_high_low_triggers.magnetometer_enabled,
            "get_reading_func": sensor_access.get_magnetometer_xyz,
            "sleep_duration": config_high_low_triggers.magnetometer_wait_seconds,
            "database_column": [database_variables.mag_x,
                                database_variables.mag_y,
                                database_variables.mag_z],
            "low_trigger": [config_high_low_triggers.magnetometer_x_low,
                            config_high_low_triggers.magnetometer_y_low,
                            config_high_low_triggers.magnetometer_z_low],
            "high_trigger": [config_high_low_triggers.magnetometer_x_high,
                             config_high_low_triggers.magnetometer_y_high,
                             config_high_low_triggers.magnetometer_z_high]
        }
        self.gyroscope = {
            "enabled": config_high_low_triggers.gyroscope_enabled,
            "get_reading_func": sensor_access.get_gyroscope_xyz,
            "sleep_duration": config_high_low_triggers.gyroscope_wait_seconds,
            "database_column": [database_variables.gyro_x,
                                database_variables.gyro_y,
                                database_variables.gyro_z],
            "low_trigger": [config_high_low_triggers.gyroscope_x_low,
                            config_high_low_triggers.gyroscope_y_low,
                            config_high_low_triggers.gyroscope_z_low],
            "high_trigger": [config_high_low_triggers.gyroscope_x_high,
                             config_high_low_triggers.gyroscope_y_high,
                             config_high_low_triggers.gyroscope_z_high]
        }


class _SingleTriggerThread:
    def __init__(self, custom_trigger_variables):
        self.current_state = "Disabled"
        self.previous_email_state = "Normal"
        self.sensor_name = str(custom_trigger_variables["database_column"])
        self.low_trigger = custom_trigger_variables["low_trigger"]
        self.high_trigger = custom_trigger_variables["high_trigger"]
        self.last_reported_abnormal_sate = datetime(1920, 1, 1, 1, 1, 1)
        self.email_alert_obj = CreateSensorReadingEmailAlert(self.sensor_name, self.high_trigger, self.low_trigger)

        self.custom_trigger_variables = custom_trigger_variables
        if self.custom_trigger_variables["enabled"]:
            self.current_state = "Starting"
            if self.custom_trigger_variables["get_reading_func"]() is not None:
                while not app_cached_variables.restart_all_trigger_threads:
                    try:
                        sensor_reading = self.custom_trigger_variables["get_reading_func"]()
                        sensor_reading = sensor_reading[self.sensor_name]
                        reading_taken_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        if self.high_trigger > sensor_reading > self.low_trigger:
                            if self.current_state != "Normal":
                                self.current_state = "Normal"
                                self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)

                        elif sensor_reading < self.low_trigger:
                            if self.current_state != "Low":
                                self.current_state = "Low"
                                self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)

                        elif sensor_reading > self.high_trigger:
                            if self.current_state != "High":
                                self.current_state = "High"
                                self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)

                        if app_config_access.trigger_high_low.enable_email_alerts:
                            # The following goes somewhat like this. Only add to email alerts to be sent if
                            # the current state is different from the previous state (High/Normal/Low)
                            # OR
                            # The current state is the same as the previous state BUT not "Normal" AND
                            # the time since the last alert was passed through is more or equal to the time
                            # between sending emails alerts found in the High/Low Triggers configuration.
                            #
                            # After passing the above, it then makes sure the current state is enabled
                            # for email alerts in the High/Low Trigger configuration.
                            # If enabled, an alert is added to the que of alerts to be emailed
                            time_passed = datetime.utcnow() - self.last_reported_abnormal_sate
                            tmp_eeh = app_config_access.trigger_high_low.alerts_resend_emails_every_hours
                            resend_delay = timedelta(hours=tmp_eeh)
                            if self.previous_email_state != self.current_state or \
                                    self.current_state != "Normal" and time_passed >= resend_delay:
                                self.previous_email_state = copy.copy(self.current_state)
                                alerts_normal_enabled = app_config_access.trigger_high_low.alerts_normal_enabled
                                alerts_low_enabled = app_config_access.trigger_high_low.alerts_low_enabled
                                alerts_high_enabled = app_config_access.trigger_high_low.alerts_high_enabled

                                if self.current_state == "Normal" and alerts_normal_enabled:
                                    # This is to make sure emails are not sent when "Returning to normal"
                                    # from a state that's not enabled to send email alerts
                                    if self.previous_email_state == "Low" and alerts_low_enabled or \
                                            self.previous_email_state == "High" and alerts_high_enabled:
                                        self.email_alert_obj.add_trigger_email_entry(sensor_reading, self.current_state)
                                        self.last_reported_abnormal_sate = datetime.utcnow()
                                elif self.current_state == "Low" and alerts_low_enabled or \
                                        self.current_state == "High" and alerts_high_enabled:
                                    self.email_alert_obj.add_trigger_email_entry(sensor_reading, self.current_state)
                                    self.last_reported_abnormal_sate = datetime.utcnow()
                    except Exception as error:
                        log_msg = f"Trigger problem in '{self.sensor_name}' Trigger Thread: {str(error)}"
                        logger.primary_logger.error(log_msg)

                    sleep_fraction_interval = 5
                    if self.custom_trigger_variables["sleep_duration"] < 5:
                        sleep_fraction_interval = self.custom_trigger_variables["sleep_duration"]
                    sleep_total = 0
                    while sleep_total < self.custom_trigger_variables["sleep_duration"] \
                            and not app_cached_variables.restart_all_trigger_threads:
                        sleep(sleep_fraction_interval)
                        sleep_total += sleep_fraction_interval
            else:
                logger.primary_logger.info(f"High/Low Triggers: {self.sensor_name}: Sensor Missing")
                self.current_state = "Sensor Missing"
                while not app_cached_variables.restart_all_trigger_threads:
                    sleep(10)

    def _write_readings_to_sql(self, reading_datetime, reading, trigger_state):
        try:
            sql_data = [str(reading_datetime), app_cached_variables.hostname, str(reading), trigger_state]
            sql_string = "INSERT OR IGNORE INTO TriggerData (" + \
                         database_variables.all_tables_datetime + "," + \
                         database_variables.sensor_name + "," + \
                         self.custom_trigger_variables["database_column"] + "," + \
                         database_variables.trigger_state + \
                         ") VALUES (?,?,?,?)"
            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            logger.primary_logger.error(f"Trigger '{self.sensor_name}' Recording Failure: {str(error)}")


class _MultiTriggerThread:
    def __init__(self, custom_trigger_variables):
        self.current_states = []
        self.previous_email_states = []
        self.email_alert_obj_list = []

        self.sensor_name = ""
        for text_char in custom_trigger_variables["database_column"][0]:
            if not text_char.isdigit():
                self.sensor_name += text_char
        self.sensor_name = self.sensor_name.replace("_", " ").strip()

        if custom_trigger_variables["enabled"]:
            self.last_reported_abnormal_sate = datetime(1920, 1, 1, 1, 1, 1)
            self.db_col_list = copy.copy(custom_trigger_variables["database_column"])
            self.trig_low_list = custom_trigger_variables["low_trigger"]
            self.trig_high_list = custom_trigger_variables["high_trigger"]
            sensor_readings = custom_trigger_variables["get_reading_func"]()
            if sensor_readings is not None:
                index = 0
                for sensor_name in custom_trigger_variables["database_column"]:
                    if sensor_name in sensor_readings and sensor_readings[sensor_name] is not None:
                        trig_low = self.trig_low_list[index]
                        trig_high = self.trig_high_list[index]
                        email_alert_obj = CreateSensorReadingEmailAlert(sensor_name, trig_high, trig_low)
                        self.email_alert_obj_list.append(email_alert_obj)
                        self.current_states.append("Starting")
                        self.previous_email_states.append("Normal")
                        index += 1
                    else:
                        self.trig_low_list.pop(index)
                        self.trig_high_list.pop(index)
                        self.db_col_list.pop(index)

                while not app_cached_variables.restart_all_trigger_threads:
                    alerts_normal_enabled = app_config_access.trigger_high_low.alerts_normal_enabled
                    alerts_low_enabled = app_config_access.trigger_high_low.alerts_low_enabled
                    alerts_high_enabled = app_config_access.trigger_high_low.alerts_high_enabled
                    try:
                        sensor_readings = custom_trigger_variables["get_reading_func"]()
                        reading_taken_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        # The following checks to make sure the sensors reading(s) provided is not None, which would
                        # indicate a hardware malfunction, then checks for each possible reading from that type
                        # of sensor as well as checks to see if the individual readings are not None, since some
                        # sensors don't have all the sensors of its type. If the reading is valid, test it against
                        # the high/low triggers, otherwise, skip that sensor reading.
                        if sensor_readings is not None:
                            for index, sensor_name in enumerate(self.db_col_list):
                                if sensor_name in sensor_readings and sensor_readings[sensor_name] is not None:
                                    reading = sensor_readings[sensor_name]
                                    trig_low = self.trig_low_list[index]
                                    trig_high = self.trig_high_list[index]
                                    if trig_low < reading < trig_high:
                                        if self.current_states[index] != "Normal":
                                            self.current_states[index] = "Normal"
                                            self._write_readings_to_sql(reading_taken_at, reading,
                                                                        self.current_states[index], sensor_name)
                                    elif trig_low > reading:
                                        if self.current_states[index] != "Low":
                                            self.current_states[index] = "Low"
                                            self._write_readings_to_sql(reading_taken_at, reading,
                                                                        self.current_states[index], sensor_name)
                                    elif trig_high < reading:
                                        if self.current_states[index] != "High":
                                            self.current_states[index] = "High"
                                            self._write_readings_to_sql(
                                                reading_taken_at, reading, self.current_states[index], sensor_name
                                            )
                                    if app_config_access.trigger_high_low.enable_email_alerts:
                                        # The following goes somewhat like this. Only add to email alerts to be sent if
                                        # the current state is different from the previous state (High/Normal/Low)
                                        # OR
                                        # The current state is the same as the previous state BUT not "Normal" AND
                                        # the time since the last alert was passed through is more or equal to the time
                                        # between sending emails alerts found in the High/Low Triggers configuration.
                                        #
                                        # After passing the above, it then makes sure the current state is enabled
                                        # for email alerts in the High/Low Trigger configuration.
                                        # If enabled, an alert is added to the que of alerts to be emailed
                                        time_passed = datetime.utcnow() - self.last_reported_abnormal_sate
                                        tmp_eeh = app_config_access.trigger_high_low.alerts_resend_emails_every_hours
                                        resend_delay = timedelta(hours=tmp_eeh)
                                        if self.previous_email_states[index] != self.current_states[index] or \
                                                self.current_states[index] != "Normal" and time_passed >= resend_delay:

                                            self.previous_email_states[index] = copy.copy(self.current_states[index])
                                            if self.current_states[index] == "Normal" and alerts_normal_enabled or \
                                                    self.current_states[index] == "Low" and alerts_low_enabled or \
                                                    self.current_states[index] == "High" and alerts_high_enabled:
                                                self.email_alert_obj_list[index].add_trigger_email_entry(
                                                    reading, self.current_states[index]
                                                )
                                                self.last_reported_abnormal_sate = datetime.utcnow()
                    except Exception as error:
                        log_msg = f"Trigger problem in '{self.sensor_name}' Trigger Thread: {str(error)}"
                        logger.primary_logger.error(log_msg)

                    sleep_fraction_interval = 5
                    if custom_trigger_variables["sleep_duration"] < 5:
                        sleep_fraction_interval = custom_trigger_variables["sleep_duration"]
                    sleep_total = 0
                    while sleep_total < custom_trigger_variables["sleep_duration"] \
                            and not app_cached_variables.restart_all_trigger_threads:
                        sleep(sleep_fraction_interval)
                        sleep_total += sleep_fraction_interval
            else:
                logger.primary_logger.info(f"High/Low Triggers - {self.sensor_name}: Sensor Missing")
                while not app_cached_variables.restart_all_trigger_threads:
                    sleep(10)

    @staticmethod
    def _write_readings_to_sql(reading_datetime, reading, trigger_state, database_column):
        try:
            sql_data = [str(reading_datetime), app_cached_variables.hostname, str(reading), trigger_state]
            sql_string = "INSERT OR IGNORE INTO TriggerData (" + \
                         database_variables.all_tables_datetime + "," + \
                         database_variables.sensor_name + "," + \
                         database_column + "," + \
                         database_variables.trigger_state + \
                         ") VALUES (?,?,?,?)"
            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            logger.primary_logger.error(f"Trigger '{str(database_column)}' Recording Failure: {str(error)}")


def start_trigger_high_low_recording_server():
    if app_config_access.trigger_high_low.enable_high_low_trigger_recording:
        # Sleep to allow cached variables like sensor IP & hostname to populate
        sleep(10)
        logger.primary_logger.info(" -- High/Low Trigger Recording Started")

        tmp_tv = _CreateHighLowTriggerThreadData()
        if app_config_access.trigger_high_low.cpu_temperature_enabled:
            app_cached_variables.trigger_high_low_cpu_temp = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.system_temperature],
                thread_name="High/Low Trigger CPU Temperature"
            )

        if app_config_access.trigger_high_low.env_temperature_enabled:
            app_cached_variables.trigger_high_low_env_temp = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.env_temperature],
                thread_name="High/Low Trigger Env Temperature"
            )

        if app_config_access.trigger_high_low.pressure_enabled:
            app_cached_variables.trigger_high_low_pressure = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.pressure],
                thread_name="High/Low Trigger Pressure"
            )

        if app_config_access.trigger_high_low.humidity_enabled:
            app_cached_variables.trigger_high_low_humidity = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.humidity],
                thread_name="High/Low Trigger Humidity"
            )

        if app_config_access.trigger_high_low.altitude_enabled:
            app_cached_variables.trigger_high_low_altitude = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.altitude],
                thread_name="High/Low Trigger Altitude"
            )

        if app_config_access.trigger_high_low.distance_enabled:
            app_cached_variables.trigger_high_low_distance = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.distance],
                thread_name="High/Low Trigger Distance"
            )

        if app_config_access.trigger_high_low.lumen_enabled:
            app_cached_variables.trigger_high_low_lumen = CreateMonitoredThread(
                _SingleTriggerThread,
                args=[tmp_tv.lumen],
                thread_name="High/Low Trigger Lumen"
            )

        if app_config_access.trigger_high_low.colour_enabled:
            app_cached_variables.trigger_high_low_visible_colours = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.colours],
                thread_name="High/Low Trigger Colours"
            )

        if app_config_access.trigger_high_low.ultra_violet_enabled:
            app_cached_variables.trigger_high_low_ultra_violet = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.ultra_violet],
                thread_name="High/Low Trigger Ultra Violet"
            )

        if app_config_access.trigger_high_low.gas_enabled:
            app_cached_variables.trigger_high_low_gas = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.gas_resistance],
                thread_name="High/Low Trigger Gas"
            )

        if app_config_access.trigger_high_low.particulate_matter_enabled:
            app_cached_variables.trigger_high_low_particulate_matter = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.particulate_matter],
                thread_name="High/Low Trigger Particulate Matter"
            )

        if app_config_access.trigger_high_low.accelerometer_enabled:
            app_cached_variables.trigger_high_low_accelerometer = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.accelerometer],
                thread_name="High/Low Trigger Accelerometer"
            )

        if app_config_access.trigger_high_low.magnetometer_enabled:
            app_cached_variables.trigger_high_low_magnetometer = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.magnetometer],
                thread_name="High/Low Trigger Magnetometer"
            )

        if app_config_access.trigger_high_low.gyroscope_enabled:
            app_cached_variables.trigger_high_low_gyroscope = CreateMonitoredThread(
                _MultiTriggerThread,
                args=[tmp_tv.gyroscope],
                thread_name="High/Low Trigger Gyroscope"
            )
    else:
        logger.primary_logger.debug("High/Low Trigger Recording Disabled in Configuration")
