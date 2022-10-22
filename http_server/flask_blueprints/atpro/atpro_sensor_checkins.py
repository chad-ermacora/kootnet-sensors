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
from time import sleep
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_size, adjust_datetime, thread_function
from operations_modules.app_generic_disk import get_file_content
from operations_modules.sqlite_database import sql_execute_get_data, write_to_sql_database, get_clean_sql_table_name, \
    get_sql_element, get_sqlite_tables_in_list, get_one_db_entry
from configuration_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from http_server.flask_blueprints.sensor_checkin_server import check_sensor_checkin_columns

html_atpro_sensor_check_ins_routes = Blueprint("html_atpro_sensor_check_ins_routes", __name__)
db_loc = file_locations.sensor_checkin_database
db_v = app_cached_variables.database_variables

# Checkin Cached Table Variables
checkins_sensors_html_list_last_updated = "Please Refresh Information || Datetime is displayed in "
checkins_db_sensors_count = 0
checkins_db_sensors_count_from_past_days = 0
checkins_sensors_html_table_list = """
<div class="col-12 col-m-12 col-sm-12">
    <div class="card">
        <div class="card-content">
            <h2><i class="fa fa-exclamation-triangle"></i> Press the 'Refresh Table Information' button to view checkins</h2>
        </div>
    </div>
</div>
"""
html_info_temp_loc = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/page_templates/"
html_info_temp_loc += "sensor_checkins/sensor-checkin-info-template.html"
sensor_info_html_template = get_file_content(html_info_temp_loc)

# Sensor Check-in View Variables
checkins_update_in_progress = False
checkin_search_sensor_id = ""
checkin_search_sensor_installed_sensors = ""
checkin_sensor_info = ""
checkin_search_primary_log = ""
checkin_search_network_log = ""
checkin_search_sensors_log = ""
checkin_lookup_entry_dates = []
checkin_lookup_date_selected = ""


def _update_checkin_lookup_variables():
    global checkin_search_sensor_id
    global checkin_lookup_entry_dates
    global checkin_lookup_date_selected

    checkin_lookup_entry_dates = []

    if _check_sensor_id_exists(checkin_search_sensor_id):
        sql_query = "SELECT " + db_v.all_tables_datetime + " FROM '" + checkin_search_sensor_id + "' WHERE " \
                    + db_v.all_tables_datetime + " != '' ORDER BY " + db_v.all_tables_datetime + " DESC;"
        date_tuples = sql_execute_get_data(sql_query, sql_database_location=file_locations.sensor_checkin_database)
        return_dates = []
        checkin_lookup_date_selected = get_sql_element(date_tuples[0])
        for date_entry in date_tuples:
            date_entry = get_sql_element(date_entry)
            return_dates.append([str(date_entry), _get_date_entry_text_label(date_entry)])
        checkin_lookup_entry_dates = return_dates


def _get_date_entry_text_label(date_entry):
    column_names = [
        db_v.sensor_name, db_v.kootnet_sensors_version, db_v.ip, db_v.sensor_uptime,
        db_v.sensor_check_in_installed_sensors, db_v.sensor_check_in_primary_log, db_v.sensor_check_in_network_log,
        db_v.sensor_check_in_sensors_log
    ]
    label_texts = [" SN", " V", " IP", " UT", " IS", " PL", " NL", " SL"]

    return_label_text = ""
    for column_name, label_text in zip(column_names, label_texts):
        sql_query = "SELECT " + column_name + " FROM '" + checkin_search_sensor_id + "' WHERE " \
                    + db_v.all_tables_datetime + " == '" + date_entry + "';"
        sql_return_data = sql_execute_get_data(sql_query, sql_database_location=file_locations.sensor_checkin_database)
        sql_return_data = str(get_sql_element(sql_return_data)).strip()
        if sql_return_data != "" and sql_return_data != "None":
            return_label_text += label_text
    return return_label_text


checkin_temp_location = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/page_templates/"
checkin_temp_location += "sensor_checkins/sensor-checkin-table-entry-template.html"
checkin_table_entry_template = get_file_content(checkin_temp_location).strip()
updating_checkin_info_html_msg = """
<div class="col-12 col-m-12 col-sm-12">
    <div class="card">
        <div class="card-content">
            <h2 id="blink_shadow"><i class="fas fa-info-circle"></i> Updating Information, Please Wait ...</h2>
        </div>
    </div>
</div>
"""
checkin_table_failed = "<h3><strong><a style='color: red;'>Sensor Checkins List Generation Failed</a></strong></h3>"


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-view")
@auth.login_required
def html_atpro_sensor_checkin_main_view():
    global checkins_db_sensors_count
    global checkins_sensors_html_list_last_updated
    global checkins_db_sensors_count_from_past_days
    global checkins_sensors_html_table_list

    sensor_count = len(get_sqlite_tables_in_list(db_loc))
    checkins_db_sensors_count = sensor_count
    if os.path.isfile(db_loc):
        db_size_mb = get_file_size(db_loc, round_to=3)
    else:
        db_size_mb = 0.0

    enabled_text = "<span style='color: red;'>Disabled</span>"
    if app_config_access.checkin_config.enable_checkin_recording:
        enabled_text = "<span style='color: green;'>Enabled</span>"

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    checkin_info_last_updated = checkins_sensors_html_list_last_updated
    checkins_sensors_html_list_last_updated = adjust_datetime(checkin_info_last_updated, utc0_hour_offset)
    run_script = ""
    if checkins_sensors_html_table_list == updating_checkin_info_html_msg:
        run_script = "CreatingSensorCheckinsTable();"
    checkin_table_last_update = str(checkins_sensors_html_list_last_updated) + " UTC" + str(utc0_hour_offset)
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-main-view.html",
                           SensorsInDatabase=str(sensor_count),
                           CheckinDBSize=db_size_mb,
                           DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days,
                           CheckinEnabledText=enabled_text,
                           CheckinsLastTableUpdateDatetime=checkin_table_last_update,
                           ContactInPastDays=str(app_config_access.checkin_config.count_contact_days),
                           TotalSensorsContactDays=str(checkins_db_sensors_count_from_past_days),
                           HTMLSensorsTableCode=checkins_sensors_html_table_list,
                           RunScript=run_script)


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-data")
@auth.login_required
def clear_check_ins_counts():
    thread_function(_thread_clear_check_ins_counts)
    return_msg = "Clearing all but the last Sensor Checkin from all sensors, check Logs for more info"
    return get_message_page("Redundant Sensor Checkins Clean-up Started", return_msg, page_url="sensor-checkin-view")


def _thread_clear_check_ins_counts():
    logger.network_logger.info("Checkin Database 'Clear Old Checkin Data' Started")
    global checkin_lookup_entry_dates

    for sensor_id in get_sqlite_tables_in_list(db_loc):
        _clear_old_sensor_checkin_data(sensor_id)
    write_to_sql_database("VACUUM;", None, sql_database_location=db_loc)
    if len(checkin_lookup_entry_dates) > 0:
        _update_checkin_lookup_variables()
    logger.network_logger.info("Checkin Database 'Clear Old Checkin Data' Finished")


def _clear_old_sensor_checkin_data(sensor_id):
    global checkin_lookup_entry_dates

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
        if len(checkin_lookup_entry_dates) > 0:
            _update_checkin_lookup_variables()
    except Exception as error:
        logger.primary_logger.error("Sensor Check-ins - Clearing Sensor '" + sensor_id + "' Data: " + str(error))


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-delete-old-sensors", methods=["POST"])
@auth.login_required
def delete_sensors_older_then():
    delete_sensors_older_days = 365000  # 1000 years
    if request.form.get("delete_sensors_older_days") is not None:
        delete_sensors_older_days = float(request.form.get("delete_sensors_older_days"))
    thread_function(_thread_delete_sensors_older_then, args=delete_sensors_older_days)
    return get_message_page("Old Sensor Clean-up Started", "Check Logs for more info", page_url="sensor-checkin-view")


def _thread_delete_sensors_older_then(delete_sensors_older_days):
    logger.network_logger.info("Checkin Database Clean-up Started")
    try:
        datetime_sensor_ids_list = _get_sensor_id_and_last_checkin_date_as_list()
        current_date_time = datetime.utcnow() + timedelta(hours=app_config_access.primary_config.utc0_hour_offset)
        for date_and_sensor_id in datetime_sensor_ids_list:
            clean_last_checkin_date = date_and_sensor_id[1]
            if (current_date_time - clean_last_checkin_date).days >= delete_sensors_older_days:
                _delete_sensor_id(date_and_sensor_id[0])
        write_to_sql_database("VACUUM;", None, sql_database_location=db_loc)
        logger.network_logger.info("Checkin Database Clean-up Finished")
    except Exception as error:
        logger.primary_logger.warning("Error trying to delete old sensors from the Check-Ins database: " + str(error))


@html_atpro_sensor_check_ins_routes.route("/atpro/generate-checkin-sensors-list")
@auth.login_required
def html_atpro_sensor_checkins_generate_sensors_html_list():
    global checkins_sensors_html_table_list

    if checkins_sensors_html_table_list != updating_checkin_info_html_msg:
        checkins_sensors_html_table_list = updating_checkin_info_html_msg
        thread_function(_generate_sensors_checkins_html_list)
    # This just initiates generation and does not return a page to "View"
    return "OK"


def _generate_sensors_checkins_html_list():
    global checkins_db_sensors_count
    global checkins_sensors_html_list_last_updated
    global checkins_db_sensors_count_from_past_days
    global checkins_sensors_html_table_list

    try:
        sensor_ids_and_date_list = _get_sensor_id_and_last_checkin_date_as_list()
        checkins_db_sensors_count = len(sensor_ids_and_date_list)
        current_date_time = datetime.utcnow()

        sensor_contact_count = 0
        sensors_html_list = []
        for sensor_id_and_date in sensor_ids_and_date_list:
            sensors_html_list.append(_get_sensor_html_table_code(sensor_id_and_date[0]))
            checkin_date = sensor_id_and_date[1]
            if (current_date_time - checkin_date) < timedelta(days=app_config_access.checkin_config.count_contact_days):
                sensor_contact_count += 1
        checkins_db_sensors_count_from_past_days = sensor_contact_count

        sensors_html_list.sort(key=lambda x: x[1], reverse=True)
        html_sensor_table_code = ""
        for sensor in sensors_html_list:
            html_sensor_table_code += sensor[0]
        checkins_sensors_html_table_list = html_sensor_table_code
        dt_format = "%Y-%m-%d %H:%M:%S"
        checkins_sensors_html_list_last_updated = datetime.utcnow().strftime(dt_format)
    except Exception as error:
        logger.network_logger.warning("Failed to Generate Sensor Checkins HTML List: " + str(error))
        checkins_sensors_html_table_list = checkin_table_failed
        checkins_sensors_html_list_last_updated = "NA"


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
    global checkin_search_sensor_id
    global checkins_update_in_progress
    global checkin_sensor_info
    global checkin_search_primary_log
    global checkin_search_network_log
    global checkin_search_sensors_log

    buttons_state = ""
    sensor_info_hidden = ""
    if checkins_update_in_progress or checkin_search_sensor_id == "":
        buttons_state = "disabled"
        sensor_info_hidden = "hidden"
    searching_script = ""
    if checkins_update_in_progress:
        searching_script = "PageRefresh();"
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-search.html",
                           CheckinSelectionNames=_get_drop_down_items(),
                           HiddenSensorInfo=sensor_info_hidden,
                           SearchSensorInfo=checkin_sensor_info,
                           SearchSensorDeleteDisabled=buttons_state,
                           SearchSensorClearDisabled=buttons_state,
                           PrimaryLogs=checkin_search_primary_log.replace("\n", "<br>"),
                           NetworkLogs=checkin_search_network_log.replace("\n", "<br>"),
                           SensorsLogs=checkin_search_sensors_log.replace("\n", "<br>"),
                           SearchingScript=searching_script)


def _get_drop_down_items():
    global checkin_lookup_date_selected
    global checkins_update_in_progress

    dropdown_selection = ""
    if not checkins_update_in_progress:
        custom_drop_downs_html_text = "<option value='{{ CheckinDateEntry }}' {{ Selected }}>{{ CheckinDateEntryName }}</option>"
        for file_name in checkin_lookup_entry_dates:
            new_entry = custom_drop_downs_html_text.replace("{{ CheckinDateEntry }}", file_name[0])
            if file_name[0] == checkin_lookup_date_selected:
                new_entry = new_entry.replace("{{ Selected }}", "selected")
            else:
                new_entry = new_entry.replace("{{ Selected }}", "")
            dropdown_selection += new_entry.replace("{{ CheckinDateEntryName }}", file_name[0] + file_name[1]) + "\n"
    return dropdown_selection


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-checkins")
@auth.login_required
def search_sensor_clear_old_check_ins():
    if checkin_search_sensor_id != "":
        _clear_old_sensor_checkin_data(checkin_search_sensor_id)
        _update_search_sensor_check_ins(checkin_search_sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-search-delete-sensor")
@auth.login_required
def search_sensor_delete_senor_id():
    global checkin_search_sensor_id

    if checkin_search_sensor_id != "":
        write_to_sql_database("DROP TABLE '" + checkin_search_sensor_id + "';", None, sql_database_location=db_loc)
        _update_search_sensor_check_ins(checkin_search_sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-id-search", methods=["POST"])
@auth.login_required
def search_sensor_check_ins():
    global checkins_update_in_progress

    if request.form.get("sensor_id") is not None:
        sensor_id = str(request.form.get("sensor_id")).strip()
        new_date_entry = str(request.form.get("checkin_selection")).strip()
        if sensor_id == "DateSearch":
            _threaded_checkin_lookup([sensor_id, new_date_entry])
        else:
            checkins_update_in_progress = True
            thread_function(_threaded_checkin_lookup, args=[sensor_id, new_date_entry])
    return view_search_sensor_check_ins()


def _threaded_checkin_lookup(sensor_id_and_date):
    global checkins_update_in_progress
    global checkin_search_sensor_id
    global checkin_sensor_info
    global checkin_search_sensor_installed_sensors
    global checkin_search_primary_log
    global checkin_search_network_log
    global checkin_search_sensors_log
    global checkin_lookup_entry_dates
    global checkin_lookup_date_selected
    try:
        if sensor_id_and_date[0] != "":
            if sensor_id_and_date[0] == "DateSearch":
                try:
                    datetime.strptime(sensor_id_and_date[1], "%Y-%m-%d %H:%M:%S")
                    checkin_lookup_date_selected = sensor_id_and_date[1]
                    _update_search_sensor_check_ins(checkin_search_sensor_id)
                except Exception as error:
                    print(str(error))
                    checkin_lookup_date_selected = ""
            else:
                checkin_search_sensor_id = ""
                checkin_sensor_info = "Sensor ID Not Found\n\n"
                checkin_search_sensor_installed_sensors = ""
                checkin_search_primary_log = ""
                checkin_search_network_log = ""
                checkin_search_sensors_log = ""
                checkin_lookup_entry_dates = []
                checkin_lookup_date_selected = ""

                sensor_id = get_clean_sql_table_name(sensor_id_and_date[0])
                _update_search_sensor_check_ins(sensor_id)
                _update_checkin_lookup_variables()
    except Exception as error:
        logger.network_logger.error("Checkins Search Failed: " + str(error))
    checkins_update_in_progress = False


def _update_search_sensor_check_ins(sensor_id):
    global checkin_search_sensor_id
    global checkin_lookup_date_selected

    if _check_sensor_id_exists(sensor_id):
        if checkin_lookup_date_selected == "":
            checkin_search_sensor_id = sensor_id
        _update_sensor_info_string()
        _search_checkin_get_logs(checkin_search_sensor_id)


def _search_checkin_get_logs(sensor_id):
    global checkin_search_primary_log
    global checkin_search_network_log
    global checkin_search_sensors_log

    checkin_search_primary_log = "Log Not Found"
    checkin_search_network_log = "Log Not Found"
    checkin_search_sensors_log = "Log Not Found"

    primary_logs = get_last_rec_db_entry_wrapper(sensor_id, db_v.sensor_check_in_primary_log)
    network_logs = get_last_rec_db_entry_wrapper(sensor_id, db_v.sensor_check_in_network_log)
    sensors_logs = get_last_rec_db_entry_wrapper(sensor_id, db_v.sensor_check_in_sensors_log)

    if len(primary_logs) > 0:
        checkin_search_primary_log = str(primary_logs)
    if len(network_logs) > 0:
        checkin_search_network_log = str(network_logs)
    if len(sensors_logs) > 0:
        checkin_search_sensors_log = str(sensors_logs)


def _update_sensor_info_string():
    global sensor_info_html_template
    global checkin_search_sensor_id
    global checkin_lookup_date_selected
    global checkin_sensor_info
    ks_version_col = db_v.kootnet_sensors_version

    utc0_hour_offset = app_config_access.primary_config.utc0_hour_offset
    db_last_datetime_entry = get_one_db_entry_wrapper(checkin_search_sensor_id, db_v.all_tables_datetime)
    get_sensor_checkin_count_per_id_sql = "SELECT count('" + db_v.all_tables_datetime + "') FROM '" + \
                                          checkin_search_sensor_id + "';"

    sensor_name = get_one_db_entry_wrapper(checkin_search_sensor_id, db_v.sensor_name,
                                           specific_date=checkin_lookup_date_selected)
    sensor_ip = get_one_db_entry_wrapper(checkin_search_sensor_id, db_v.ip,
                                         specific_date=checkin_lookup_date_selected)
    last_checkin_datetime = adjust_datetime(db_last_datetime_entry, utc0_hour_offset)
    checkin_count = sql_execute_get_data(get_sensor_checkin_count_per_id_sql, sql_database_location=db_loc)
    software_version = get_one_db_entry_wrapper(checkin_search_sensor_id, ks_version_col,
                                                specific_date=checkin_lookup_date_selected)
    sensor_uptime = get_one_db_entry_wrapper(checkin_search_sensor_id, db_v.sensor_uptime,
                                             specific_date=checkin_lookup_date_selected)
    installed_sensors = get_last_rec_db_entry_wrapper(checkin_search_sensor_id, db_v.sensor_check_in_installed_sensors)

    replacement_identifiers = [
        "{{ SensorID }}", "{{ SensorName }}", "{{ SensorIP }}", "{{ LastCheckinDate }}",
        "{{ TotalCheckins }}", "{{ SoftwareVersion }}", "{{ SensorUptime }}", "{{ InstalledSensors }}"
    ]
    replacement_variables = [
        checkin_search_sensor_id, sensor_name, sensor_ip, last_checkin_datetime,
        get_sql_element(checkin_count), software_version, sensor_uptime, installed_sensors
    ]
    return_html = sensor_info_html_template
    for replace_id, replace_value in zip(replacement_identifiers, replacement_variables):
        return_html = return_html.replace(replace_id, str(replace_value))
    checkin_sensor_info = return_html


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
        while app_cached_variables.sql_db_locked:
            sleep(1)
        database_connection = sqlite3.connect(db_loc, isolation_level=None)
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


def get_one_db_entry_wrapper(table_name, column_name, specific_date=None, order="DESC"):
    if specific_date is not None and len(checkin_lookup_entry_dates) > 0:
        if specific_date == "":
            specific_date = checkin_lookup_entry_dates[0][0]
        sql_query = "SELECT " + column_name + " FROM '" + table_name + "' WHERE " \
                    + db_v.all_tables_datetime + " == '" + specific_date + "'" + " LIMIT 1;"
        return_entry = get_sql_element(sql_execute_get_data(sql_query, sql_database_location=db_loc))
        return return_entry
    return get_one_db_entry(table_name=table_name, column_name=column_name, order=order, database=db_loc)


def get_last_rec_db_entry_wrapper(table_name, column_name):
    global checkin_lookup_entry_dates
    global checkin_lookup_date_selected

    if len(checkin_lookup_entry_dates) > 0:
        if checkin_lookup_date_selected == "":
            checkin_lookup_date_selected = checkin_lookup_entry_dates[-1][0]
        sql_query = "SELECT rowid FROM '" + table_name + "' WHERE " + \
                    db_v.all_tables_datetime + " == '" + checkin_lookup_date_selected + "'"
        row_id = str(get_sql_element(sql_execute_get_data(sql_query, sql_database_location=db_loc)))
        sql_query = "SELECT " + column_name + " FROM '" + table_name + "' WHERE " + column_name + \
                    " IS NOT NULL AND " + column_name + " != '' AND rowid BETWEEN 0 AND " + row_id + \
                    " ORDER BY rowid DESC LIMIT 1;"
        return_value = str(get_sql_element(sql_execute_get_data(sql_query, sql_database_location=db_loc)))
        return return_value
    return get_one_db_entry_wrapper(table_name, column_name)
