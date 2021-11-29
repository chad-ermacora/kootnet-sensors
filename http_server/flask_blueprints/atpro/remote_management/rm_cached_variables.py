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
from operations_modules import logger
from operations_modules import file_locations


# Copied from app_generic_functions to prevent circular importing
def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns it's content. """
    logger.primary_logger.debug("Loading File: " + str(load_file))

    if os.path.isfile(load_file):
        try:
            with open(load_file, open_type) as loaded_file:
                file_content = loaded_file.read()
        except Exception as error:
            file_content = ""
            logger.primary_logger.error("Unable to load " + load_file + " - " + str(error))
        return file_content
    else:
        logger.primary_logger.debug(load_file + " not found")
    return ""


# Login used for remote sensors (Used in Sensor Remote Management)
# ToDo: Use Remote Management configuration user/pass instead? Save hashes and allow auth with hash directly?
http_login = ""
http_password = ""

html_report_css = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/style.css"
html_report_js = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/index.js"
html_report_pure_css = file_locations.program_root_dir + "/http_server/extras/pure-min.css"
html_pure_css_menu = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/pure-horizontal-menu.css"
html_report_all_start = file_locations.atpro_reports_folder + "report-all-start.html"
html_report_all_end = file_locations.atpro_reports_folder + "report-all-end.html"
html_report_template = file_locations.atpro_reports_folder + "report-template.html"
html_report_sensor_error_template = file_locations.atpro_reports_folder + "report-sensor-error-template.html"

# Cached Reports
default_report = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="robots" content="noindex">
        <title>Kootnet Sensors</title>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
    </head>
    <body style='background-color: black;'>
        <h2 style='text-decoration: underline; color: red;'>Report Not Found</h3>
        <p style='color: white;'>No report found, please generated the report first</p>
    </body>
</html>
"""
html_combo_report = default_report
html_system_report = default_report
html_config_report = default_report
html_readings_report = default_report
html_latency_report = default_report

html_pure_css = get_file_content(html_report_pure_css).strip()
html_pure_css_menu = get_file_content(html_pure_css_menu).strip()
html_report_css = get_file_content(html_report_css).strip()
html_report_js = get_file_content(html_report_js).strip()

html_report_combo = get_file_content(file_locations.html_combo_report).strip()
html_report_combo = html_report_combo.replace("{{ ReportCSSStyles }}", html_report_css)
html_report_combo = html_report_combo.replace("{{ PureCSS }}", html_pure_css)
html_report_combo = html_report_combo.replace("{{ PureCSSHorizontalMenu }}", html_pure_css_menu)

html_report_start = get_file_content(html_report_all_start).strip()
html_report_start = html_report_start.replace("{{ ReportCSSStyles }}", html_report_css)
html_report_end = get_file_content(html_report_all_end).strip()
html_report_end = html_report_end.replace("{{ ReportJavaScript }}", html_report_js)

html_report_template = get_file_content(html_report_template).strip()
report_sensor_error_template = get_file_content(html_report_sensor_error_template).strip()

# Variables to make sure Remote Management is only creating a single copy at any given time
creating_combo_reports_zip = False
creating_the_big_zip = False
creating_databases_zip = False
creating_logs_zip = False

creating_combo_report = False
creating_system_report = False
creating_config_report = False
creating_readings_report = False
creating_latency_report = False

# Sensor Control (Remote Management) Download placeholders
sc_reports_zip_name = ""
sc_logs_zip_name = ""
sc_databases_zip_name = ""
sc_big_zip_name = ""
sc_databases_zip_in_memory = False
sc_big_zip_in_memory = False
sc_in_memory_zip = b''
