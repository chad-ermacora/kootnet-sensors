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
import sqlite3

import operations_config
import operations_logger
import operations_upgrades
from operations_commands import restart_services

create_important_files = [operations_config.last_updated_file_location,
                          operations_config.old_version_file_location]


class CreateChecksUpgradesData:
    def __init__(self):
        self.old_config = operations_config.get_installed_config()
        self.upgraded_config = operations_config.CreateConfig()
        self.old_installed_sensors = operations_config.get_installed_sensors()
        self.upgraded_installed_sensors = operations_config.CreateInstalledSensors()

        self.old_version = get_old_version()


def get_old_version():
    old_version_file = open(operations_config.old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version


def _write_current_version_to_file():
    operations_logger.primary_logger.debug("Current version file updating")
    current_version_file = open(operations_config.old_version_file_location, 'w')
    current_version_file.write(operations_config.version)
    current_version_file.close()


def check_missing_files():
    for file in create_important_files:
        if os.path.isfile(file):
            pass
        else:
            operations_logger.primary_logger.warning("Added missing file: " + file)
            os.system("touch " + file)

    os.system("bash /opt/kootnet-sensors/scripts/set_permissions.sh")


def check_database_structure():
    """ Checks and if necessary creates or updates both SQL tables and columns. """
    try:
        db_connection = sqlite3.connect(operations_config.sensor_database_location)
        db_cursor = db_connection.cursor()

        # Create or update Interval table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='IntervalData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'IntervalData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'IntervalData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SensorName',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SensorName' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SensorName' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='IP',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'IP' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'IP' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SensorUpTime',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SensorUpTime' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SensorUpTime' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SystemTemp',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SystemTemp' -  Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SystemTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='EnvironmentTemp',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'EnvironmentTemp' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'EnvironmentTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='EnvTempOffset',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'EnvTempOffset' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'EnvTempOffset' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Pressure',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Pressure' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Pressure' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Humidity',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Humidity' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Humidity' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Lumen',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Lumen' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Lumen' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Red',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Red' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Red' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Green',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Green' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Green' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Blue',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Blue' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Blue' - " + str(error))

        # Create or update Trigger table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='TriggerData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'TriggerData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'TriggerData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='SensorName',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'SensorName' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'SensorName' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='IP',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'IP' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'IP' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_Z' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_Z' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Z' - " + str(error))

        # Create or update OtherData table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='OtherData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'OtherData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'OtherData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='OtherData',
                                                                               cn='Notes',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Notes' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Notes' - " + str(error))

        db_connection.commit()
        db_connection.close()
    except Exception as error:
        operations_logger.primary_logger.error("DB Connection Failed: " + str(error))


def run_upgrade_checks():
    operations_logger.primary_logger.debug("Checking required packages")
    upgrade_data_obj = CreateChecksUpgradesData()
    try:
        old_version_split = upgrade_data_obj.old_version.split(".")
        major_version = old_version_split[0]
        feature_version = old_version_split[1]
        minor_version = old_version_split[2]
    except Exception as error:
        operations_logger.primary_logger.warning("Missing version file: " +
                                                 operations_config.old_version_file_location +
                                                 " - Configuration files reset to defaults")
        operations_logger.primary_logger.debug(str(error))

        major_version = ""
        feature_version = ""
        minor_version = ""
        upgrade_data_obj.old_version = operations_config.version

    if major_version == "Alpha":
        if feature_version == "22":
            if int(minor_version) < 9:
                operations_upgrades.update_ver_a_22_8(upgrade_data_obj)
                operations_logger.primary_logger.info("Upgraded: " + upgrade_data_obj.old_version)
                upgrade_data_obj.old_version = "Alpha.22.9"
            if 21 > int(minor_version) > 8:
                operations_upgrades.update_ver_a_22_20(upgrade_data_obj)
                operations_logger.primary_logger.info("Upgraded: " + upgrade_data_obj.old_version)
                upgrade_data_obj.old_version = "Alpha.22.21"
            else:
                operations_logger.primary_logger.info("Upgrade detected || No configuration changes || Old: " +
                                                      upgrade_data_obj.old_version +
                                                      " New: " +
                                                      operations_config.version)
                upgrade_data_obj.old_version = operations_config.version
                upgrade_data_obj.upgraded_config = upgrade_data_obj.old_config
                upgrade_data_obj.upgraded_installed_sensors = upgrade_data_obj.old_installed_sensors

    operations_config.write_config_to_file(upgrade_data_obj.upgraded_config)
    operations_config.write_installed_sensors_to_file(upgrade_data_obj.upgraded_installed_sensors)
    _write_current_version_to_file()
    restart_services()
