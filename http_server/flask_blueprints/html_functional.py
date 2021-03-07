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
from time import sleep
from flask import Blueprint, send_file, render_template, request, send_from_directory
from werkzeug.security import check_password_hash
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from http_server.server_http_generic_functions import get_html_hidden_state, message_and_return
from http_server.server_http_auth import auth

html_functional_routes = Blueprint("html_functional_routes", __name__)
html_extras_dir = file_locations.program_root_dir + "/http_server/extras"
documentation_root_dir = file_locations.program_root_dir + "/extras/documentation"


@html_functional_routes.route("/favicon.ico")
def fav_icon():
    return send_file(file_locations.program_root_dir + "/extras/icon.ico")


@html_functional_routes.route("/SensorUnitHelp.html")
def sensor_unit_help():
    return send_file(documentation_root_dir + "/index.html")


@html_functional_routes.route("/MenuScript.js")
def menu_script():
    return send_file(html_extras_dir + "/menu.js")


@html_functional_routes.route("/MenuStyle.css")
def menu_style_css():
    return send_file(html_extras_dir + "/style.css")


@html_functional_routes.route("/Chart.min.js")
def charts_min_js():
    return send_file(html_extras_dir + "/Chart.bundle.min.js")


@html_functional_routes.route("/jquery.min.js")
def jquery_slim_min_js():
    return send_file(html_extras_dir + "/jquery-3.4.1.min.js")


@html_functional_routes.route("/mui.min.css")
def mui_min_css():
    return send_file(html_extras_dir + "/mui.min-ver-0.9.43.css")


@html_functional_routes.route("/mui.min.js")
def mui_min_js():
    return send_file(html_extras_dir + "/mui.min-ver-0.9.43.js")


@html_functional_routes.route("/mui-colors.min.css")
def mui_colors_min_css():
    return send_file(html_extras_dir + "/mui-colors.min-ver-0.9.43.css")


@html_functional_routes.route("/tinymce.min.js")
def tinymce_min_js():
    return send_file(html_extras_dir + "/tinymce/tinymce.min.js")


@html_functional_routes.route("/jquery.tinymce.min.js")
def jquery_tinymce_min_js():
    return send_file(html_extras_dir + "/tinymce/jquery.tinymce.min.js")


@html_functional_routes.route("/themes/silver/theme.min.js")
def tinymce_theme_min_js():
    return send_file(html_extras_dir + "/tinymce/themes/silver/theme.min.js")


@html_functional_routes.route("/skins/ui/oxide/skin.min.css")
def tinymce_skin_min_css():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/skin.min.css")


@html_functional_routes.route("/skins/ui/oxide/content.min.css")
def tinymce_ui_content_min_css():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/content.min.css")


@html_functional_routes.route("/icons/default/icons.min.js")
def tinymce_icons():
    return send_file(html_extras_dir + "/tinymce/icons/default/icons.min.js")


@html_functional_routes.route("/skins/ui/oxide/content.inline.min.css")
def tinymce_ui_content_inline_min_css():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/content.inline.min.css")


@html_functional_routes.route("/skins/ui/oxide/content.mobile.min.css")
def tinymce_ui_content_mobile_min_css():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/content.mobile.min.css")


@html_functional_routes.route("/skins/ui/oxide/skin.mobile.min.css")
def tinymce_ui_content_mobile_skin():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/skin.mobile.min.css")


@html_functional_routes.route("/skins/ui/oxide/fonts/tinymce-mobile.woff")
def tinymce_ui_content_wolf_font():
    return send_file(html_extras_dir + "/tinymce/skins/ui/oxide-dark/fonts/tinymce-mobile.woff")


@html_functional_routes.route("/skins/content/default/content.min.css")
def tinymce_content_min_css():
    return send_file(html_extras_dir + "/tinymce/skins/content/dark/content.min.css")


@html_functional_routes.route("/plugins/link/plugin.min.js")
def tinymce_plugin_link():
    return send_file(html_extras_dir + "/tinymce/plugins/link/plugin.min.js")


@html_functional_routes.route("/plugins/autolink/plugin.min.js")
def tinymce_plugin_autolink():
    return send_file(html_extras_dir + "/tinymce/plugins/autolink/plugin.min.js")


@html_functional_routes.route("/plugins/lists/plugin.min.js")
def tinymce_plugin_lists():
    return send_file(html_extras_dir + "/tinymce/plugins/lists/plugin.min.js")


@html_functional_routes.route("/plugins/print/plugin.min.js")
def tinymce_plugin_print():
    return send_file(html_extras_dir + "/tinymce/plugins/print/plugin.min.js")


@html_functional_routes.route("/plugins/wordcount/plugin.min.js")
def tinymce_plugin_wordcount():
    return send_file(html_extras_dir + "/tinymce/plugins/wordcount/plugin.min.js")


@html_functional_routes.route("/plugins/code/plugin.min.js")
def tinymce_plugin_code():
    return send_file(html_extras_dir + "/tinymce/plugins/code/plugin.min.js")


@html_functional_routes.route("/plugins/insertdatetime/plugin.min.js")
def tinymce_plugin_insertdatetime():
    return send_file(html_extras_dir + "/tinymce/plugins/insertdatetime/plugin.min.js")


@html_functional_routes.route("/plugins/fullscreen/plugin.min.js")
def tinymce_plugin_fullscreen():
    return send_file(html_extras_dir + "/tinymce/plugins/fullscreen/plugin.min.js")


@html_functional_routes.route("/plugins/spellchecker/plugin.min.js")
def tinymce_plugin_spellchecker():
    return send_file(html_extras_dir + "/tinymce/plugins/spellchecker/plugin.min.js")


@html_functional_routes.route("/plugins/help/plugin.min.js")
def tinymce_plugin_help():
    return send_file(html_extras_dir + "/tinymce/plugins/help/plugin.min.js")


# Help file requirements
@html_functional_routes.route("/KootnetSensorHardware.jpg")
def kootnet_sensor_hardware_picture():
    return send_file(file_locations.program_root_dir + "/extras/SensorHardware.jpg")


@html_functional_routes.route("/bootstrap.min.js")
def bootstrap_javascript():
    return send_file(documentation_root_dir + "/js/bootstrap.min.js")


@html_functional_routes.route("/retina.js")
def retina_javascript():
    return send_file(documentation_root_dir + "/js/retina.js")


@html_functional_routes.route("/wow.js")
def wow_javascript():
    return send_file(documentation_root_dir + "/js/wow.js")


@html_functional_routes.route("/jquery.prettyPhoto.js")
def jquery_pretty_photo_javascript():
    return send_file(documentation_root_dir + "/js/jquery.prettyPhoto.js")


@html_functional_routes.route("/doc_custom.js")
def doc_custom_javascript():
    return send_file(documentation_root_dir + "/js/custom.js")


@html_functional_routes.route("/doc_main.js")
def doc_main_javascript():
    return send_file(documentation_root_dir + "/js/main.js")


@html_functional_routes.route("/shCore.js")
def sh_core_javascript():
    return send_file(documentation_root_dir + "/js/syntax-highlighter/scripts/shCore.js")


@html_functional_routes.route("/shBrushBash.js")
def brush_bash_javascript():
    return send_file(documentation_root_dir + "/js/syntax-highlighter/scripts/shBrushBash.js")


@html_functional_routes.route("/font-awesome.min.css")
def font_awesome_css():
    return send_file(documentation_root_dir + "/fonts/font-awesome-4.3.0/css/font-awesome.min.css")


@html_functional_routes.route("/stroke.css")
def stroke_css():
    return send_file(documentation_root_dir + "/css/stroke.css")


@html_functional_routes.route("/bootstrap.css")
def bootstrap_css():
    return send_file(documentation_root_dir + "/css/bootstrap.css")


@html_functional_routes.route("/animate.css")
def animate_css():
    return send_file(documentation_root_dir + "/css/animate.css")


@html_functional_routes.route("/prettyPhoto.css")
def pretty_photo_css():
    return send_file(documentation_root_dir + "/css/prettyPhoto.css")


@html_functional_routes.route("/doc_style.css")
def doc_style_css():
    return send_file(documentation_root_dir + "/css/style.css")


@html_functional_routes.route("/shCore.css")
def sh_core_css():
    return send_file(documentation_root_dir + "/js/syntax-highlighter/styles/shCore.css")


@html_functional_routes.route("/shThemeRDark.css")
def sh_theme_dark_css():
    return send_file(documentation_root_dir + "/js/syntax-highlighter/styles/shThemeRDark.css")


@html_functional_routes.route("/doc_custom.css")
def doc_custom_css():
    return send_file(documentation_root_dir + "/css/custom.css")


# New way to get HTTP extras sent for most above things (Does not work for current interface)
@html_functional_routes.route('/extras/<path:filename>')
def html_extras_folder_static_files(filename):
    extras_folder = file_locations.program_root_dir + "/http_server/extras/"
    return send_from_directory(extras_folder, filename)


# Start -- HTML JS/assets/fonts/css for 'ATPro admin' interface
@html_functional_routes.route('/atpro/<path:filename>')
def atpro_root_static_files(filename):
    atpro_folder = file_locations.program_root_dir + "/http_server/templates/ATPro_admin/"
    return send_from_directory(atpro_folder, filename)
# End -- HTML assets for 'ATPro admin' interface


@html_functional_routes.route('/logout')
def logout():
    return render_template(
        "message_return.html",
        PageURL="/",
        RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
        RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
        TextMessage="Logout OK.  Returning to Home."), 401


@auth.verify_password
def verify_password(username, password):
    if username == app_cached_variables.http_flask_user and \
            check_password_hash(app_cached_variables.http_flask_password, password):
        logger.network_logger.debug("* Login to Web Portal Successful from " + str(request.remote_addr))
        return True
    logger.network_logger.debug("* Login to Web Portal Failed from " + str(request.remote_addr))
    # Sleep on failure to help prevent brute force attempts
    sleep(1)
    return False


@auth.error_handler
def auth_error():
    return message_and_return("Unauthorized Access")
