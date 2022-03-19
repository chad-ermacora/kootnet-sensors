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
from datetime import datetime
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.sqlite_database import sql_execute_get_data
from operations_modules.app_generic_functions import thread_function
from configuration_modules import app_config_access
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index

html_atpro_sensor_insights_routes = Blueprint("html_atpro_sensor_insights_routes", __name__)
db_v = app_cached_variables.database_variables
generating_insights = False

html_sensor_insights_row = """
    <div class='col-3 col-m-6 col-sm-12'>
        <div class="card">
            <div class="card-content">
                <h2 style="color: red;">{{ SensorName }}</h2>
                <p>
                    <span class="readings-header">Highest Readings</span><br><br>
                    {{ AddHighestReadings }}
                    <br><br>
                    <span class="readings-header">Lowest Readings</span><br><br>
                    {{ AddLowestReadings }}
                </p>
            </div>
        </div>
    </div>
"""

html_sensor_insight_high_entry = """{{ SensorReadingHigh }} {{ UnitType }}<br>{{ SensorDateTimeHigh }}"""
html_sensor_insight_low_entry = """{{ SensorReadingLow }} {{ UnitType }}<br>{{ SensorDateTimeLow }}"""

html_sensor_insights = """
<div class="col-12 col-m-12 col-sm-12">
    <div class="card" style="width: 100vw;">
        <div class="card-content">
            <h2>
                <i class="fa fa-exclamation-triangle"></i> Press the 'Refresh Insights' button to view Sensor Insights
            </h2>
        </div>
    </div>
</div>
<script>SetInsightGenDateTime('NA');</script>
"""

html_sensor_insights_updating = """
<div class="col-12 col-m-12 col-sm-12">
    <div class="card" style="width: 100vw;">
        <div class="card-content">
            <h2 style="text-align: center;">
                <i class="fas fa-info-circle"></i> Updating Information, Please Wait ...
            </h2>
        </div>
    </div>
</div>
<script>
    document.getElementById("insights-refresh-btn").disabled = true;
    SetInsightGenDateTime('Generation in Progress');
    window.setTimeout(RefreshInsightsPageTimed, 5000);
</script>
"""

html_sensor_insights_error = """
<div class="col-12 col-m-12 col-sm-12">
    <div class="card">
        <div class="card-content">
            <h2><i class="fas fa-info-circle"></i> Generation Failed, Please Try Again Later ...</h2>
        </div>
    </div>
</div>
<script>
    document.getElementById('insights-refresh-btn').disabled = false;
    SetInsightGenDateTime('NA');
</script>
"""


@html_atpro_sensor_insights_routes.route("/atpro/sensor-insights", methods=["GET", "POST"])
def html_atpro_sensors_insights():
    global html_sensor_insights
    if request.method == "POST":
        app_config_access.sensor_insights.update_with_html_request(request)
        app_config_access.sensor_insights.save_config_to_file()
        return get_html_atpro_index(run_script="SelectNav('sensor-readings-base');")
    return html_sensor_insights


@html_atpro_sensor_insights_routes.route("/atpro/generate-Sensor-Insights")
def html_atpro_generate_sensor_insights():
    thread_function(_generate_sensor_insights)
    return "Generating"


def _generate_sensor_insights():
    global html_sensor_insights
    global generating_insights

    if not generating_insights:
        generating_insights = True

        html_sensor_insights = html_sensor_insights_updating
        try:
            db_columns = [
                db_v.sensor_uptime, db_v.system_temperature, db_v.env_temperature, db_v.pressure, db_v.altitude,
                db_v.humidity,
                db_v.dew_point, db_v.distance, db_v.gas_resistance_index, db_v.gas_reducing, db_v.gas_oxidising,
                db_v.gas_nh3,
                db_v.particulate_matter_1, db_v.particulate_matter_2_5, db_v.particulate_matter_4,
                db_v.particulate_matter_10,
                db_v.lumen, db_v.red, db_v.orange, db_v.yellow, db_v.green, db_v.blue, db_v.violet,
                db_v.ultra_violet_index,
                db_v.ultra_violet_a, db_v.ultra_violet_b, db_v.acc_x, db_v.acc_y, db_v.acc_z, db_v.mag_x, db_v.mag_y,
                db_v.mag_z, db_v.gyro_x, db_v.gyro_y, db_v.gyro_z, db_v.latitude, db_v.longitude,
                db_v.gps_num_satellites,
                db_v.gps_speed_over_ground

            ]
            special_reading_units = [
                " Minutes", " °C", " °C", " hPa", " Meters", " %RH", " °C", " ???", " kΩ", " kΩ", " kΩ", " kΩ",
                " µg/m³", " µg/m³", " µg/m³", " µg/m³", " lm", " lm", " lm", " lm", " lm", " lm", " lm", " lm?", " lm?",
                " lm?",
                " g", " g", " g", " μT", " μT", " μT", " °/s", " °/s", " °/s", " Latitude", " Longitude",
                " # of Satellites",
                " km/hr?"

            ]
            sensor_count = 0
            html_final_code = "<script>document.getElementById('insights-refresh-btn').disabled = false;</script>"
            for column_name, s_unit in zip(db_columns, special_reading_units):
                new_sensor_html_code = _create_sensor_insights_html(column_name, s_unit)
                html_final_code += new_sensor_html_code + "\n"
                if new_sensor_html_code.strip() != "":
                    sensor_count += 1
            if sensor_count < 4:
                new_code = "<div class='col-" + str(int(12 / sensor_count)) + " col-m-" + str(
                    sensor_count * 2) + " col-sm-12'>"
                html_final_code = html_final_code.replace("<div class='col-3 col-m-6 col-sm-12'>", new_code)
            html_final_code += "<script>SetInsightGenDateTime('" + \
                               datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + \
                               " UTC0');</script>"
            html_sensor_insights = html_final_code
        except Exception as error:
            logger.network_logger.error("Sensor Insights Generation: " + str(error))
            html_sensor_insights = html_sensor_insights_error
        generating_insights = False


def _create_sensor_insights_html(column_name, unit_name):
    final_html_code = html_sensor_insights_row
    try:
        low_entries = _get_html_min_entries(column_name, unit_name)
        high_entries = _get_html_max_entries(column_name, unit_name)
        final_html_code = final_html_code.replace("{{ SensorName }}", column_name.replace("_", " "))
        final_html_code = final_html_code.replace("{{ AddHighestReadings }}", high_entries)
        final_html_code = final_html_code.replace("{{ AddLowestReadings }}", low_entries)
    except Exception as error:
        logger.network_logger.warning("Sensor Database Insights Generation: " + str(error))
    return final_html_code


def _get_html_min_entries(column_name, unit_name):
    replacement_names = ["{{ SensorDateTimeLow }}", "{{ SensorReadingLow }}", "{{ UnitType }}"]
    column_min_and_datetime_values = _get_min_max_sql_entries(column_name, "ASC")
    html_return_min_readings = ""
    try:
        for date_value_pair in column_min_and_datetime_values:
            if date_value_pair[0] is not None and date_value_pair[1] is not None:
                values_list = [date_value_pair[0], date_value_pair[1], unit_name]
                sensor_entry = html_sensor_insight_low_entry
                for replace_text, new_value in zip(replacement_names, values_list):
                    sensor_entry = sensor_entry.replace(replace_text, str(new_value))
                html_return_min_readings += sensor_entry + "<br><br>"
    except Exception as error:
        logger.network_logger.error("Sensor Insights MIN Generation: " + str(error))
    return html_return_min_readings


def _get_html_max_entries(column_name, unit_name):
    replacement_names = ["{{ SensorDateTimeHigh }}", "{{ SensorReadingHigh }}", "{{ UnitType }}"]
    column_max_and_datetime_values = _get_min_max_sql_entries(column_name)
    html_return_max_readings = ""
    try:
        for date_value_pair in column_max_and_datetime_values:
            if date_value_pair[0] is not None and date_value_pair[1] is not None:
                values_list = [date_value_pair[0], date_value_pair[1], unit_name]
                sensor_entry = html_sensor_insight_high_entry
                for replace_text, new_value in zip(replacement_names, values_list):
                    sensor_entry = sensor_entry.replace(replace_text, str(new_value))
                html_return_max_readings += sensor_entry + "<br><br>"
    except Exception as error:
        logger.network_logger.error("Sensor Insights MAX Generation: " + str(error))
    return html_return_max_readings


def _get_min_max_sql_entries(column_name, order="DESC", return_limit=None):
    if return_limit is None:
        return_limit = app_config_access.sensor_insights.insights_per_sensor

    where_query_text = " WHERE NOT " + column_name + " IS NULL AND NOT " + db_v.all_tables_datetime + " IS NULL"
    if app_config_access.sensor_insights.ignore_null_types:
        where_query_text += " AND NOT " + column_name + " IS 0 AND NOT " + column_name + " IS 0.0"
        where_query_text += " AND NOT " + column_name + " IS ''"
    if not app_config_access.sensor_insights.use_all_recorded_data:
        where_query_text += " AND " + db_v.all_tables_datetime + " BETWEEN date('" + \
                            app_config_access.sensor_insights.start_date_range + "') AND date('" + \
                            app_config_access.sensor_insights.end_date_range + "')"

    query_multi = "SELECT " + db_v.all_tables_datetime + ", " + column_name + \
                  " FROM " + db_v.table_interval + where_query_text + \
                  " ORDER BY CAST(" + column_name + " AS REAL) " + order + \
                  " LIMIT " + str(return_limit) + ";"
    return sql_execute_get_data(query_multi, file_locations.sensor_database)
