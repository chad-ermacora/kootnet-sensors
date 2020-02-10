from flask import Blueprint, send_file, render_template, request
from werkzeug.security import check_password_hash
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from http_server import server_http_generic_functions
from http_server.server_http_auth import auth

html_functional_routes = Blueprint("html_basics", __name__)


@html_functional_routes.route("/favicon.ico")
def fav_icon():
    return send_file(file_locations.html_icon)


@html_functional_routes.route("/SensorUnitHelp.html")
def sensor_unit_help():
    return send_file(file_locations.sensor_html_help)


@html_functional_routes.route("/MenuScript.js")
def menu_script():
    return send_file(file_locations.menu_script)


@html_functional_routes.route("/MenuStyle.css")
def menu_style_css():
    return send_file(file_locations.menu_css_style)


@html_functional_routes.route("/jquery.min.js")
def jquery_slim_min_js():
    return send_file(file_locations.j_query_js)


@html_functional_routes.route("/mui.min.css")
def mui_min_css():
    return send_file(file_locations.mui_min_css)


@html_functional_routes.route("/mui.min.js")
def mui_min_js():
    return send_file(file_locations.mui_min_js)


@html_functional_routes.route("/mui-colors.min.css")
def mui_colors_min_css():
    return send_file(file_locations.mui_colors_min_css)


@html_functional_routes.route("/tinymce.min.js")
def tinymce_min_js():
    return send_file(file_locations.tinymce_min_js)


@html_functional_routes.route("/jquery.tinymce.min.js")
def jquery_tinymce_min_js():
    return send_file(file_locations.tinymce_jquery_min_js)


@html_functional_routes.route("/themes/silver/theme.min.js")
def tinymce_theme_min_js():
    return send_file(file_locations.tinymce_theme_min_js)


@html_functional_routes.route("/skins/ui/oxide/skin.min.css")
def tinymce_skin_min_css():
    return send_file(file_locations.tinymce_skin_min_css)


@html_functional_routes.route("/skins/ui/oxide/content.min.css")
def tinymce_ui_content_min_css():
    return send_file(file_locations.tinymce_ui_content_min_css)


@html_functional_routes.route("/skins/content/default/content.min.css")
def tinymce_content_min_css():
    return send_file(file_locations.tinymce_content_min_css)


@html_functional_routes.route("/plugins/link/plugin.min.js")
def tinymce_plugin_link():
    return send_file(file_locations.tinymce_plugin_link)


@html_functional_routes.route("/plugins/autolink/plugin.min.js")
def tinymce_plugin_autolink():
    return send_file(file_locations.tinymce_plugin_autolink)


@html_functional_routes.route("/plugins/lists/plugin.min.js")
def tinymce_plugin_lists():
    return send_file(file_locations.tinymce_plugin_lists)


@html_functional_routes.route("/plugins/print/plugin.min.js")
def tinymce_plugin_print():
    return send_file(file_locations.tinymce_plugin_print)


@html_functional_routes.route("/plugins/wordcount/plugin.min.js")
def tinymce_plugin_wordcount():
    return send_file(file_locations.tinymce_plugin_wordcount)


@html_functional_routes.route("/plugins/code/plugin.min.js")
def tinymce_plugin_code():
    return send_file(file_locations.tinymce_plugin_code)


@html_functional_routes.route("/plugins/insertdatetime/plugin.min.js")
def tinymce_plugin_insertdatetime():
    return send_file(file_locations.tinymce_plugin_insertdatetime)


@html_functional_routes.route("/plugins/fullscreen/plugin.min.js")
def tinymce_plugin_fullscreen():
    return send_file(file_locations.tinymce_plugin_fullscreen)


@html_functional_routes.route("/plugins/spellchecker/plugin.min.js")
def tinymce_plugin_spellchecker():
    return send_file(file_locations.tinymce_plugin_spellchecker)


@html_functional_routes.route("/plugins/help/plugin.min.js")
def tinymce_plugin_help():
    return send_file(file_locations.tinymce_plugin_help)


@html_functional_routes.route('/logout')
def logout():
    return render_template("message_return.html", TextMessage="Logout OK.  Returning to Home.", URL="/"), 401


@auth.verify_password
def verify_password(username, password):
    if username == app_cached_variables.http_flask_user:
        logger.network_logger.debug("* Login attempt from " + str(request.remote_addr))
        return check_password_hash(app_cached_variables.http_flask_password, password)
    return False


@auth.error_handler
def auth_error():
    logger.network_logger.debug(" *** First or Failed Login from " + str(request.remote_addr))
    return server_http_generic_functions.message_and_return("Unauthorized Access")
