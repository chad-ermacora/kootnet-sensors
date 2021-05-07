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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_file_size
from operations_modules.sqlite_database import get_sql_element, get_sqlite_tables_in_list, get_clean_sql_table_name, \
    sql_execute_get_data
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index

html_atpro_mqtt_subscriber_routes = Blueprint("html_atpro_mqtt_subscriber_routes", __name__)


@html_atpro_mqtt_subscriber_routes.route("/atpro/mqtt-subscriber-view-data-stream")
@auth.login_required
def html_atpro_mqtt_subscriber_data_stream_view():
    mqtt_subscriber_log = file_locations.mqtt_subscriber_log
    max_entries = app_config_access.mqtt_subscriber_config.mqtt_page_view_max_entries
    mqtt_subscriber_log_content = logger.get_sensor_log(mqtt_subscriber_log, max_lines=max_entries).strip()
    if mqtt_subscriber_log_content == "":
        mqtt_subscriber_log_content = _mqtt_sub_entry_to_html("")
    else:
        new_return = ""
        for line in mqtt_subscriber_log_content.split("\n"):
            new_return += _mqtt_sub_entry_to_html(line)
        mqtt_subscriber_log_content = new_return
    return render_template(
        "ATPro_admin/page_templates/mqtt-subscriber-data-view.html",
        MQTTSubDatabaseSize=get_file_size(file_locations.mqtt_subscriber_database),
        MQTTSubscriberServerAddress=app_config_access.mqtt_subscriber_config.broker_address,
        MQTTShowing=max_entries,
        MQTTTotoalEntries=logger.get_number_of_log_entries(mqtt_subscriber_log),
        SQLMQTTSensorsInDB=str(len(get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database))),
        MQTTEnabledColor=_get_html_color(app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber),
        MQTTSubscriberEnabledText=_get_html_text(app_config_access.mqtt_subscriber_config.enable_mqtt_subscriber),
        MQTTSQLEnabledColor=_get_html_color(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        MQTTSQLSubscriberEnabledText=_get_html_text(app_config_access.mqtt_subscriber_config.enable_mqtt_sql_recording),
        SubscriberTopicsContent=mqtt_subscriber_log_content
    )


def _get_html_color(setting):
    if setting:
        return "lightgreen"
    return "red"


def _get_html_text(setting):
    if setting:
        return "Enabled"
    return "Disabled"


def _mqtt_sub_entry_to_html(sub_entry):
    sensor_id = ""
    sensor_time = ""
    sensor_data = ""
    try:
        split_entry_space = sub_entry.split(" ")
        if len(split_entry_space) >= 5:
            sensor_time = split_entry_space[0] + " " + split_entry_space[1]
            sensor_id = split_entry_space[3]
            entry_dic = eval(str(sub_entry.split("=")[1].strip()))
            if type(entry_dic) is dict:
                sensor_data = ""
                for index, data in entry_dic.items():
                    unit_measurement_type = " " + sensor_access.get_reading_unit(index)
                    if index == "DateTime":
                        pass
                    else:
                        index = index.replace("_", " ")
                        sensor_data += "<div class='col-6 col-m-6 col-sm-6'><div class='counter bg-primary'>"
                        sensor_data += "<span class='sensor-info'>" + index + "</span><br>"
                        sensor_data += str(data) + unit_measurement_type + "<br></div></div>"
            else:
                sensor_id = "NA"
                sensor_time = "NA"
                sensor_data = "<div class='col-6 col-m-6 col-sm-6'><div class='counter bg-primary'>"
                sensor_data += str(sub_entry)
                sensor_data += "</div></div>"
    except Exception as error:
        logger.network_logger.debug("** HTML MQTT Subscriber convert for view: " + str(error))
        sensor_id = "NA"
        sensor_time = "NA"
        sensor_data = str(sub_entry)
    return render_template("ATPro_admin/page_templates/mqtt-subscriber-data-entry-template.html",
                           SensorID=sensor_id,
                           DateTimeContact=sensor_time,
                           MQTTData=sensor_data)


@html_atpro_mqtt_subscriber_routes.route("/atpro/mqtt-subscriber-clear-log")
@auth.login_required
def html_atpro_clear_mqtt_subscriber_log():
    logger.network_logger.debug("** HTML Clear - MQTT Subscriber Log - Source: " + str(request.remote_addr))
    logger.clear_mqtt_subscriber_log()
    return get_html_atpro_index(run_script="SelectNav('mqtt-subscriber-view-data-stream');")


@html_atpro_mqtt_subscriber_routes.route("/atpro/mqtt-subscriber-sensors-list")
@auth.login_required
def html_atpro_mqtt_subscriber_sensors_list():
    mqtt_subscriber_sensors = get_sqlite_tables_in_list(file_locations.mqtt_subscriber_database)
    sensors_count = len(mqtt_subscriber_sensors)

    sensors_html_list = []
    for sensor_id in mqtt_subscriber_sensors:
        sensor_id = get_sql_element(sensor_id)
        sensors_html_list.append(_get_sensor_html_table_code(sensor_id))

    sensors_html_list.sort(key=lambda x: x[1], reverse=True)
    html_sensor_table_code = ""
    for sensor in sensors_html_list:
        html_sensor_table_code += sensor[0]
    return render_template(
        "ATPro_admin/page_templates/mqtt-subscriber-sensors-list.html",
        SQLMQTTSensorsInDB=str(sensors_count),
        HTMLSensorsTableCode=html_sensor_table_code)


def _get_sensor_html_table_code(sensor_id):
    dv_v = app_cached_variables.database_variables
    sensor_id = get_clean_sql_table_name(sensor_id)
    html_sensor_code = """<tr>
        <td>{{ SensorID }}</td>
        <td>{{ SensorHostName }}</td>
        <td>{{ IPAddress }}</td>
        <td>{{ LastContact }}</td>
    </tr>
    """.replace("{{ SensorID }}", sensor_id)

    columns_list = [dv_v.sensor_name, dv_v.ip, dv_v.all_tables_datetime]
    replacement_variables = ["{{ SensorHostName }}", "{{ IPAddress }}", "{{ LastContact }}"]
    sql_get_code = "SELECT {{ ColumnName }} FROM '" + sensor_id + "' WHERE {{ ColumnName }} != '' ORDER BY " \
                          + app_cached_variables.database_variables.all_tables_datetime + " DESC LIMIT 1;"

    results_list = []
    for column, replacement_var in zip(columns_list, replacement_variables):
        replacement_data = sql_execute_get_data(sql_get_code.replace("{{ ColumnName }}", column),
                                                sql_database_location=file_locations.mqtt_subscriber_database)
        replacement_data = get_sql_element(replacement_data)
        results_list.append(replacement_data)
        try:
            html_sensor_code = html_sensor_code.replace(replacement_var, replacement_data)
        except Exception as error:
            logger.network_logger.warning("MQTT Subscriber Sensors List Creation: " + str(error))
    return [html_sensor_code, results_list[-1]]
