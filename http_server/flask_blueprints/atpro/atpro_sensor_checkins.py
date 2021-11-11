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
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_size, adjust_datetime, get_file_content, thread_function
from operations_modules.sqlite_database import sql_execute_get_data, write_to_sql_database, get_clean_sql_table_name, \
    get_sql_element, get_sqlite_tables_in_list, get_one_db_entry
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index
from http_server.flask_blueprints.sensor_checkin_server import check_sensor_checkin_columns

html_atpro_sensor_check_ins_routes = Blueprint("html_atpro_sensor_check_ins_routes", __name__)
db_loc = file_locations.sensor_checkin_database
db_v = app_cached_variables.database_variables

checkin_temp_location = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/page_templates/"
checkin_temp_location += "sensor_checkins/sensor-checkin-table-entry-template.html"
checkin_table_entry_template = get_file_content(checkin_temp_location).strip()
generating_checkin_table_html = "<h3><strong><a style='color: red;'>Generating list, please wait ...</a></strong></h3>"
checkin_table_failed = "<h3><strong><a style='color: red;'>Sensor Checkins List Generation Failed</a></strong></h3>"


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-view")
@auth.login_required
def html_atpro_sensor_checkin_main_view():
    sensor_count = len(get_sqlite_tables_in_list(db_loc))
    sensor_ids_and_date_list = _get_sensor_id_and_last_checkin_date_as_list()

    sensor_statistics = ""
    current_date_time = datetime.utcnow()

    sensor_contact_count = 0
    count_contact_days = app_config_access.checkin_config.count_contact_days
    for count, sensor_id_and_date in enumerate(sensor_ids_and_date_list):
        cleaned_id = sensor_id_and_date[0]
        checkin_date = sensor_id_and_date[1]
        if (current_date_time - checkin_date) < timedelta(days=count_contact_days):
            sensor_contact_count += 1
        if count < app_config_access.checkin_config.main_page_max_sensors:
            sensor_statistics += _get_sensor_info_string(cleaned_id)

    try:
        past_checkin_percent = round(((sensor_contact_count / sensor_count) * 100), 2)
    except ZeroDivisionError:
        logger.primary_logger.debug("No Sensors found for Sensor Checkin View")
        past_checkin_percent = 0.0
    except Exception as error:
        logger.primary_logger.warning("Unknown Sensor Checkin View Error: " + str(error))
        past_checkin_percent = 0.0

    if os.path.isfile(db_loc):
        db_size_mb = get_file_size(db_loc, round_to=3)
    else:
        db_size_mb = 0.0

    enabled_text = "<span style='color: red;'>Disabled</span>"
    if app_config_access.checkin_config.enable_checkin_recording:
        enabled_text = "<span style='color: green;'>Enabled</span>"
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-main-view.html",
                           MaxSensorCount=app_config_access.checkin_config.main_page_max_sensors,
                           SensorsInDatabase=str(sensor_count),
                           CheckinDBSize=db_size_mb,
                           ContactInPastDays=app_config_access.checkin_config.count_contact_days,
                           TotalSensorsContactDays=sensor_contact_count,
                           PercentOfTotalDays=past_checkin_percent,
                           DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days,
                           CheckinEnabledText=enabled_text,
                           CheckinSensorStatistics=sensor_statistics)


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-delete-old-sensors", methods=["POST"])
@auth.login_required
def delete_sensors_older_then():
    try:
        app_config_access.checkin_config.update_with_html_request(request, skip_all_but_delete_setting=True)
        delete_sensors_older_days = app_config_access.checkin_config.delete_sensors_older_days
        datetime_sensor_ids_list = _get_sensor_id_and_last_checkin_date_as_list()
        current_date_time = datetime.utcnow() + timedelta(hours=app_config_access.primary_config.utc0_hour_offset)
        for date_and_sensor_id in datetime_sensor_ids_list:
            clean_last_checkin_date = date_and_sensor_id[1]
            if (current_date_time - clean_last_checkin_date).days >= delete_sensors_older_days:
                _delete_sensor_id(date_and_sensor_id[0])
        write_to_sql_database("VACUUM;", None, sql_database_location=db_loc)
    except Exception as error:
        logger.primary_logger.warning("Error trying to delete old sensors from the Check-Ins database: " + str(error))
    return get_html_atpro_index(run_script="SelectNav('sensor-checkin-view');")


@html_atpro_sensor_check_ins_routes.route("/atpro/checkin-sensors-list")
@auth.login_required
def html_atpro_checkin_sensors_list():
    run_script = ""
    if app_cached_variables.checkins_sensors_html_table_list == generating_checkin_table_html:
        run_script = "CreatingSensorCheckinsTable();"
    return render_template(
        "ATPro_admin/page_templates/sensor_checkins/checkin-sensors-list.html",
        DateTimeOffset=str(app_config_access.primary_config.utc0_hour_offset),
        SQLSensorsInDB=str(app_cached_variables.checkins_db_sensors_count),
        CheckinsLastTableUpdateDatetime=str(app_cached_variables.checkins_sensors_html_list_last_updated),
        HTMLSensorsTableCode=app_cached_variables.checkins_sensors_html_table_list,
        RunScript=run_script)


@html_atpro_sensor_check_ins_routes.route("/atpro/generate-checkin-sensors-list")
@auth.login_required
def html_atpro_sensor_checkins_generate_sensors_html_list():
    thread_function(_generate_sensors_checkins_html_list)
    return html_atpro_checkin_sensors_list()


def _generate_sensors_checkins_html_list():
    app_cached_variables.checkins_sensors_html_table_list = generating_checkin_table_html
    try:
        checkin_sensors = get_sqlite_tables_in_list(db_loc)
        app_cached_variables.checkins_db_sensors_count = len(checkin_sensors)

        sensors_html_list = []
        for sensor_id in checkin_sensors:
            sensors_html_list.append(_get_sensor_html_table_code(sensor_id))

        sensors_html_list.sort(key=lambda x: x[1], reverse=True)
        html_sensor_table_code = ""
        for sensor in sensors_html_list:
            html_sensor_table_code += sensor[0]
        app_cached_variables.checkins_sensors_html_table_list = html_sensor_table_code
        dt_format = "%Y-%m-%d %H:%M:%S"
        app_cached_variables.checkins_sensors_html_list_last_updated = datetime.utcnow().strftime(dt_format)
    except Exception as error:
        logger.network_logger.warning("Failed to Generate Sensor Checkins HTML List: " + str(error))
        app_cached_variables.checkins_sensors_html_table_list = checkin_table_failed
        app_cached_variables.checkins_sensors_html_list_last_updated = "NA"


def _get_sensor_html_table_code(sensor_id):
    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    sensor_name = get_one_db_entry_wrapper(sensor_id, db_v.sensor_name)
    sensor_ip = get_one_db_entry_wrapper(sensor_id, db_v.ip)
    sw_version = get_one_db_entry_wrapper(sensor_id, db_v.kootnet_sensors_version)
    first_contact = get_one_db_entry_wrapper(sensor_id, db_v.all_tables_datetime, order="ASC")
    raw_datetime = get_one_db_entry_wrapper(sensor_id, db_v.all_tables_datetime)
    last_contact = adjust_datetime(raw_datetime, utc0_hour_offset)

    html_code = checkin_table_entry_template.replace("{{ SensorID }}", sensor_id)
    html_code = html_code.replace("{{ SensorHostName }}", sensor_name)
    html_code = html_code.replace("{{ IPAddress }}", sensor_ip)
    html_code = html_code.replace("{{ SoftwareVersion }}", sw_version)
    html_code = html_code.replace("{{ FirstContact }}", first_contact)
    html_code = html_code.replace("{{ LastContact }}", last_contact)
    return [html_code, last_contact]


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-search")
@auth.login_required
def view_search_sensor_check_ins():
    buttons_state = ""
    if app_cached_variables.checkin_search_sensor_id == "":
        buttons_state = "disabled"
    old_text = "col-6 col-m-12 col-sm-12"
    new_text = "col-12 col-m-12 col-sm-12"
    sensor_search_info = app_cached_variables.checkin_sensor_info.replace(old_text, new_text)
    sensor_search_info = sensor_search_info.replace(' class="counter bg-success"', "")
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-search.html",
                           SearchSensorInfo=sensor_search_info,
                           SearchSensorDeleteDisabled=buttons_state,
                           SearchSensorClearDisabled=buttons_state,
                           PrimaryLogs=app_cached_variables.checkin_search_primary_log.replace("\n", "<br>"),
                           NetworkLogs=app_cached_variables.checkin_search_network_log.replace("\n", "<br>"),
                           SensorsLogs=app_cached_variables.checkin_search_sensors_log.replace("\n", "<br>"))


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-checkins")
@auth.login_required
def search_sensor_clear_old_check_ins():
    if app_cached_variables.checkin_search_sensor_id != "":
        _clear_old_sensor_checkin_data(app_cached_variables.checkin_search_sensor_id)
        _update_search_sensor_check_ins(app_cached_variables.checkin_search_sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-search-delete-sensor")
@auth.login_required
def search_sensor_delete_senor_id():
    sensor_id = app_cached_variables.checkin_search_sensor_id
    if sensor_id != "":
        write_to_sql_database("DROP TABLE '" + sensor_id + "';", None, sql_database_location=db_loc)
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-id-search", methods=["POST"])
@auth.login_required
def search_sensor_check_ins():
    if request.form.get("sensor_id") is not None:
        sensor_id = get_clean_sql_table_name(str(request.form.get("sensor_id")))
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


def _update_search_sensor_check_ins(sensor_id):
    if _check_sensor_id_exists(sensor_id):
        app_cached_variables.checkin_search_sensor_id = sensor_id
        new_sensor_info_string = _get_sensor_info_string(app_cached_variables.checkin_search_sensor_id)
        app_cached_variables.checkin_sensor_info = new_sensor_info_string
        _search_checkin_get_logs(app_cached_variables.checkin_search_sensor_id)
    else:
        app_cached_variables.checkin_search_sensor_id = ""
        app_cached_variables.checkin_sensor_info = "Sensor ID Not Found\n\n"
        app_cached_variables.checkin_search_sensor_installed_sensors = ""
        app_cached_variables.checkin_search_primary_log = ""
        app_cached_variables.checkin_search_network_log = ""
        app_cached_variables.checkin_search_sensors_log = ""


def _search_checkin_get_logs(sensor_id):
    app_cached_variables.checkin_search_primary_log = "Log Not Found"
    app_cached_variables.checkin_search_network_log = "Log Not Found"
    app_cached_variables.checkin_search_sensors_log = "Log Not Found"

    primary_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_primary_log)
    network_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_network_log)
    sensors_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_sensors_log)

    if len(primary_logs) > 0:
        app_cached_variables.checkin_search_primary_log = str(primary_logs)
    if len(network_logs) > 0:
        app_cached_variables.checkin_search_network_log = str(network_logs)
    if len(sensors_logs) > 0:
        app_cached_variables.checkin_search_sensors_log = str(sensors_logs)


def _get_sensor_info_string(sensor_id):
    get_sensor_checkin_count_per_id_sql = "SELECT count('" + db_v.all_tables_datetime + "') FROM '" + sensor_id + "';"
    checkin_count = sql_execute_get_data(get_sensor_checkin_count_per_id_sql, sql_database_location=db_loc)

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    db_datetime_entry = get_one_db_entry_wrapper(sensor_id, db_v.all_tables_datetime)
    adjusted_datetime = adjust_datetime(db_datetime_entry, utc0_hour_offset)
    installed_sensors = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_installed_sensors)
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-info-template.html",
                           SensorID=sensor_id,
                           SensorName=get_one_db_entry_wrapper(sensor_id, db_v.sensor_name),
                           SensorIP=get_one_db_entry_wrapper(sensor_id, db_v.ip),
                           LastCheckinDate=adjusted_datetime,
                           TotalCheckins=get_sql_element(checkin_count),
                           SoftwareVersion=get_one_db_entry_wrapper(sensor_id, db_v.kootnet_sensors_version),
                           SensorUptime=get_one_db_entry_wrapper(sensor_id, db_v.sensor_uptime),
                           InstalledSensors=installed_sensors)


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-data")
@auth.login_required
def clear_check_ins_counts():
    for sensor_id in get_sqlite_tables_in_list(db_loc):
        _clear_old_sensor_checkin_data(sensor_id)
    write_to_sql_database("VACUUM;", None, sql_database_location=db_loc)
    return get_html_atpro_index(run_script="SelectNav('sensor-checkin-view');")


def _clear_old_sensor_checkin_data(sensor_id):
    last_checkin_date = get_one_db_entry_wrapper(sensor_id, db_v.all_tables_datetime)
    sensor_name = get_one_db_entry_wrapper(sensor_id, db_v.sensor_name)
    sensor_ip = get_one_db_entry_wrapper(sensor_id, db_v.ip)
    program_version = get_one_db_entry_wrapper(sensor_id, db_v.kootnet_sensors_version)
    installed_sensors = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_installed_sensors)
    sensor_uptime = get_one_db_entry_wrapper(sensor_id, db_v.sensor_uptime)

    primary_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_primary_log)
    network_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_network_log)
    sensors_logs = get_one_db_entry_wrapper(sensor_id, db_v.sensor_check_in_sensors_log)

    try:
        write_to_sql_database("DELETE FROM '" + sensor_id + "';", None, sql_database_location=db_loc)

        check_sensor_checkin_columns(sensor_id)
        sql_ex_string = "INSERT OR IGNORE INTO '" + sensor_id + "' (" + \
                        db_v.all_tables_datetime + "," + \
                        db_v.sensor_name + "," + \
                        db_v.ip + "," + \
                        db_v.kootnet_sensors_version + "," + \
                        db_v.sensor_check_in_installed_sensors + "," + \
                        db_v.sensor_uptime + "," + \
                        db_v.sensor_check_in_primary_log + "," + \
                        db_v.sensor_check_in_network_log + "," + \
                        db_v.sensor_check_in_sensors_log + ")" + \
                        " VALUES (?,?,?,?,?,?,?,?,?);"

        sql_data = [last_checkin_date, sensor_name, sensor_ip, program_version, installed_sensors,
                    sensor_uptime, primary_logs, network_logs, sensors_logs]
        write_to_sql_database(sql_ex_string, sql_data, sql_database_location=db_loc)
    except Exception as error:
        logger.network_logger.error("Sensor Check-ins - Clearing Sensor '" + sensor_id + "' Data: " + str(error))


def _get_sensor_id_and_last_checkin_date_as_list(sort_by_date_time=True):
    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    sensor_id_list = get_sqlite_tables_in_list(db_loc)

    return_sensor_ids_list = []
    for sensor_id in sensor_id_list:
        last_checkin_datetime = get_one_db_entry_wrapper(sensor_id, db_v.all_tables_datetime)
        last_checkin_datetime = _get_converted_datetime(adjust_datetime(last_checkin_datetime, utc0_hour_offset))
        return_sensor_ids_list.append([sensor_id, last_checkin_datetime])
    if sort_by_date_time:
        return_sensor_ids_list.sort(key=lambda x: x[1], reverse=True)
    return return_sensor_ids_list


def _get_converted_datetime(date_time_string, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        date_time_object = datetime.strptime(date_time_string[:19], date_format)
        return date_time_object
    except Exception as error:
        logger.network_logger.debug("Checkins View - Unable to convert Date & Time from string: " + str(error))
    return datetime.strptime("1901-01-01 01:01:01", date_format)


def _delete_sensor_id(sensor_id):
    """ Deletes provided Text Sensor ID from the Check-In database """
    write_to_sql_database("DROP TABLE '" + sensor_id + "';", None, sql_database_location=db_loc)


def _check_sensor_id_exists(sensor_id):
    sql_query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + sensor_id + "'"
    try:
        database_connection = sqlite3.connect(db_loc)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_query)
        if sqlite_database.fetchone()[0]:
            database_connection.close()
            return True
        else:
            database_connection.close()
            return False
    except Exception as error:
        logger.primary_logger.error("Unable to access CheckIns Database: " + str(error))


def get_one_db_entry_wrapper(table_name, column_name, order="DESC"):
    return get_one_db_entry(table_name=table_name, column_name=column_name, order=order, database=db_loc)
