from flask import Blueprint, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return, get_sensor_control_report
from http_server.server_http_sensor_control import get_clean_address_list
from http_server.flask_blueprints.sensor_control_files.sensor_control_functions import \
    check_sensor_status_sensor_control, \
    create_all_databases_zipped, create_multiple_sensor_logs_zipped, put_all_reports_zipped_to_cache, \
    downloads_sensor_control, get_html_reports_combo, sensor_control_management, get_sum_db_sizes, \
    CreateSensorHTTPCommand

html_sensor_control_routes = Blueprint("html_sensor_control_routes", __name__)


@html_sensor_control_routes.route("/SensorControlManage", methods=["GET", "POST"])
def html_sensor_control_management():
    logger.network_logger.debug("* HTML Sensor Control accessed by " + str(request.remote_addr))
    if request.method == "POST":
        sc_action = request.form.get("selected_action")
        sc_download_type = request.form.get("selected_send_type")
        app_config_access.sensor_control_config.set_from_html_post(request)
        ip_list = get_clean_address_list(request)

        if len(ip_list) > 0:
            if sc_action == app_config_access.sensor_control_config.radio_check_status:
                return check_sensor_status_sensor_control(ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_report_combo:
                return get_html_reports_combo(ip_list, skip_rewrite_link=True)
            elif sc_action == app_config_access.sensor_control_config.radio_report_system:
                system_report = app_config_access.sensor_control_config.radio_report_system
                return get_sensor_control_report(ip_list, report_type=system_report)
            elif sc_action == app_config_access.sensor_control_config.radio_report_config:
                config_report = app_config_access.sensor_control_config.radio_report_config
                return get_sensor_control_report(ip_list, report_type=config_report)
            elif sc_action == app_config_access.sensor_control_config.radio_report_test_sensors:
                sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors
                return get_sensor_control_report(ip_list, report_type=sensors_report)
            elif sc_action == app_config_access.sensor_control_config.radio_download_reports:
                app_config_access.creating_the_reports_zip = True
                logger.network_logger.info("Sensor Control - Reports Zip Generation Started")
                app_generic_functions.clear_zip_names()
                app_generic_functions.thread_function(put_all_reports_zipped_to_cache, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_databases:
                download_sql_databases = app_config_access.sensor_control_config.radio_download_databases
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    return downloads_sensor_control(ip_list, download_type=download_sql_databases)
                else:
                    app_config_access.creating_databases_zip = True
                    logger.network_logger.info("Sensor Control - Databases Zip Generation Started")
                    app_generic_functions.thread_function(create_all_databases_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_download_logs:
                app_generic_functions.clear_zip_names()
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    download_logs = app_config_access.sensor_control_config.radio_download_logs
                    return downloads_sensor_control(ip_list, download_type=download_logs)
                elif sc_download_type == app_config_access.sensor_control_config.radio_send_type_relayed:
                    app_config_access.creating_logs_zip = True
                    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Started")
                    app_generic_functions.thread_function(create_multiple_sensor_logs_zipped, args=ip_list)
            elif sc_action == app_config_access.sensor_control_config.radio_create_the_big_zip:
                create_the_big_zip = app_config_access.sensor_control_config.radio_create_the_big_zip
                logger.network_logger.info("Sensor Control - The Big Zip Generation Started")
                databases_size = get_sum_db_sizes(ip_list)
                if app_generic_functions.save_to_memory_ok(databases_size):
                    app_generic_functions.clear_zip_names()
                    app_cached_variables.sc_big_zip_in_memory = True
                else:
                    app_cached_variables.sc_big_zip_in_memory = False
                app_config_access.creating_the_big_zip = True
                app_generic_functions.thread_function(create_the_big_zip, args=ip_list)
    return sensor_control_management()


@html_sensor_control_routes.route("/MultiSCSaveSettings", methods=["POST"])
@auth.login_required
def html_sensor_control_save_settings():
    logger.network_logger.debug("* HTML Sensor Control Settings saved by " + str(request.remote_addr))
    try:
        app_config_access.sensor_control_config.set_from_html_post(request)
        app_config_access.sensor_control_config.write_current_config_to_file()
    except Exception as error:
        logger.network_logger.error("Unable to process HTML Sensor Control Settings: " + str(error))
    return sensor_control_management()


@html_sensor_control_routes.route("/DownloadSCDatabasesZip")
def download_sc_databases_zip():
    logger.network_logger.debug("* Download Zip of Multiple Sensor DBs Accessed by " + str(request.remote_addr))
    if not app_config_access.creating_databases_zip:
        if app_cached_variables.sc_databases_zip_name != "":
            try:
                if app_cached_variables.sc_databases_zip_in_memory:
                    zip_file = app_cached_variables.sc_in_memory_zip
                else:
                    zip_file = file_locations.html_sensor_control_databases_zip

                zip_filename = app_cached_variables.sc_databases_zip_name
                app_cached_variables.sc_databases_zip_name = ""
                app_cached_variables.sc_databases_zip_in_memory = False
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
            except Exception as error:
                logger.network_logger.error("Send Databases Zip Error: " + str(error))
                app_cached_variables.sc_databases_zip_name = ""
                app_cached_variables.sc_databases_zip_in_memory = False
                return message_and_return("Problem loading Zip", url="/SensorControlManage")
    else:
        return message_and_return("Zipped Databases Creation in Progress", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCReportsZip")
def download_sc_reports_zip():
    logger.network_logger.debug("* Download SC Reports Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_the_reports_zip:
            if app_cached_variables.sc_reports_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_reports_zip_name
                app_cached_variables.sc_reports_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return message_and_return("Zipped Reports Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Reports Zip Error: " + str(error))

    app_cached_variables.sc_reports_zip_name = ""
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCLogsZip")
def download_sc_logs_zip():
    logger.network_logger.debug("* Download SC Logs Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_logs_zip:
            if app_cached_variables.sc_logs_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_logs_zip_name
                app_cached_variables.sc_logs_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return message_and_return("Zipped Multiple Sensors Logs Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send SC Logs Zip Error: " + str(error))

    app_cached_variables.sc_logs_zip_name = ""
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/DownloadSCBigZip")
def download_sc_big_zip():
    logger.network_logger.debug("* Download 'The Big Zip' Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_the_big_zip:
            if app_cached_variables.sc_big_zip_name != "":
                if app_cached_variables.sc_big_zip_in_memory:
                    zip_file = app_cached_variables.sc_in_memory_zip
                else:
                    zip_file = file_locations.html_sensor_control_big_zip

                zip_filename = app_cached_variables.sc_big_zip_name
                app_cached_variables.sc_big_zip_name = ""
                app_cached_variables.sc_big_zip_in_memory = False
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return message_and_return("Big Zip Creation in Progress", url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Big Zip Error: " + str(error))
    app_cached_variables.sc_big_zip_in_memory = False
    return message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_sensor_control_routes.route("/SensorControlEditConfigMain", methods=["POST"])
def sc_edit_config_primary():
    logger.network_logger.debug("* Sensor Control Set 'Primary Config' Accessed by " + str(request.remote_addr))
    ip_list = get_clean_address_list(request)
    if len(ip_list) > 0:
        pass
    msg2 = "Primary configuration sent to sensors"
    return message_and_return("Sensor Control - Configurations", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/SensorControlEditInstalledSensors", methods=["POST"])
def sc_edit_config_installed_sensors():
    msg = "* Sensor Control Set 'Installed Sensors Config' Accessed by "
    logger.network_logger.debug(msg + str(request.remote_addr))
    ip_list = get_clean_address_list(request)
    if len(ip_list) > 0:
        pass
    msg2 = "Installed Sensors configuration sent to sensors"
    return message_and_return("Sensor Control - Configurations", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/SensorControlEditConfigWifi", methods=["POST"])
def sc_edit_config_wifi():
    logger.network_logger.debug("* Sensor Control Set 'Wifi Config' Accessed by " + str(request.remote_addr))
    ip_list = get_clean_address_list(request)
    if len(ip_list) > 0:
        pass
    msg2 = "Wireless configuration sent to sensors"
    return message_and_return("Sensor Control - Configurations", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/SensorControlEditTriggerVariances", methods=["POST"])
def sc_edit_config_triggers():
    msg = "* Sensor Control Set 'Trigger Variances Config' Accessed by "
    logger.network_logger.debug(msg + str(request.remote_addr))
    ip_list = get_clean_address_list(request)
    if len(ip_list) > 0:
        pass
    msg2 = "Trigger configuration sent to sensors"
    return message_and_return("Sensor Control - Configurations", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/SCActiveOnlineServices", methods=["POST"])
def sc_active_online_services():
    logger.network_logger.debug("* Sensor Control 'Active Online Services' Accessed by " + str(request.remote_addr))
    ip_list = get_clean_address_list(request)
    if len(ip_list) > 0:
        service_state = 0
        if request.form.get("enable_online_service") is not None:
            service_state = 1

        for ip in ip_list:
            c_data = {"service": request.form.get("online_service_selected_action"), "service_state": service_state}
            sensor_http_command_instance = CreateSensorHTTPCommand(ip, "SetActiveOnlineServices", command_data=c_data)
            sensor_http_command_instance.send_http_online_service_set()
    msg2 = "Online Service setting sent to sensors"
    return message_and_return("Sensor Control - Online Service", url="/SensorControlManage", text_message2=msg2)


@html_sensor_control_routes.route("/SetActiveOnlineServices", methods=["POST"])
@auth.login_required
def set_active_online_services():
    logger.network_logger.debug("* Set 'Active Online Services' Accessed by " + str(request.remote_addr))

    active_state = 0
    if str(request.form.get("service_state")) == "1":
        active_state = 1

    if request.form.get("service") == "weather_underground":
        app_config_access.weather_underground_config.weather_underground_enabled = active_state
        app_config_access.weather_underground_config.write_config_to_file()
    elif request.form.get("service") == "luftdaten":
        app_config_access.luftdaten_config.luftdaten_enabled = active_state
        app_config_access.luftdaten_config.write_config_to_file()
    elif request.form.get("service") == "open_sense_map":
        app_config_access.open_sense_map_config.open_sense_map_enabled = active_state
        app_config_access.open_sense_map_config.write_config_to_file()
