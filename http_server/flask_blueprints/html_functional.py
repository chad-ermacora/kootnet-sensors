from flask import Blueprint, send_file, render_template, request
from werkzeug.security import check_password_hash
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_config_access
from http_server import server_http_generic_functions
from http_server.server_http_auth import auth

html_functional_routes = Blueprint("html_basics", __name__)


@html_functional_routes.route("/favicon.ico")
def fav_icon():
    return send_file(file_locations.html_icon)


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


@html_functional_routes.route('/logout')
def logout():
    return render_template("message_return.html", TextMessage="Logout OK.  Returning to Home.", URL="/"), 401


@auth.verify_password
def verify_password(username, password):
    if username == app_config_access.http_flask_user:
        logger.network_logger.debug("* Login attempt from " + str(request.remote_addr))
        return check_password_hash(app_config_access.http_flask_password, password)
    return False


@auth.error_handler
def auth_error():
    logger.network_logger.debug(" *** First or Failed Login from " + str(request.remote_addr))
    return server_http_generic_functions.message_and_return("Unauthorized Access")
