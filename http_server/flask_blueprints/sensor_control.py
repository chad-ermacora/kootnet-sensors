import time
from threading import Thread
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from http_server.server_http_auth import auth
from http_server import server_http_generic_functions
from http_server import server_http_sensor_control

html_sensor_control_routes = Blueprint("html_sensor_control_routes", __name__)
sensor_network_commands = server_http_sensor_control.CreateNetworkGetCommands()


@html_sensor_control_routes.route("/SensorControlManage", methods=["GET", "POST"])
def html_sensor_control_management():
    logger.network_logger.debug("* HTML Sensor Control accessed by " + str(request.remote_addr))
    g_s_c = server_http_generic_functions.get_sensor_control_report

    if request.method == "POST":
        sc_action = request.form.get("selected_action")
        sc_download_type = request.form.get("selected_send_type")
        app_config_access.sensor_control_config.set_from_html_post(request)
        ip_list = server_http_sensor_control.get_clean_address_list(request)

        if len(ip_list) > 0:
            check_status = app_config_access.sensor_control_config.radio_check_status
            system_report = app_config_access.sensor_control_config.radio_report_system
            config_report = app_config_access.sensor_control_config.radio_report_config
            sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors
            create_zipped_reports = app_config_access.sensor_control_config.radio_download_reports
            download_sql_databases = app_config_access.sensor_control_config.radio_download_databases
            download_logs = app_config_access.sensor_control_config.radio_download_logs
            create_the_big_zip = app_config_access.sensor_control_config.radio_create_the_big_zip

            if sc_action == check_status:
                return check_sensor_status_sensor_control(ip_list)
            elif sc_action == system_report:
                return g_s_c(ip_list, report_type=system_report)
            elif sc_action == config_report:
                return g_s_c(ip_list, report_type=config_report)
            elif sc_action == sensors_report:
                return g_s_c(ip_list, report_type=sensors_report)
            elif sc_action == create_zipped_reports:
                app_config_access.creating_the_reports_zip = True
                logger.network_logger.info("Sensor Control - Reports Zip Generation Started")
                app_generic_functions.clear_zip_names()
                app_generic_functions.thread_function(_put_all_reports_zipped_to_cache, args=ip_list)
            elif sc_action == download_sql_databases:
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    return downloads_sensor_control(ip_list, download_type=download_sql_databases)
                else:
                    app_config_access.creating_databases_zip = True
                    logger.network_logger.info("Sensor Control - Databases Zip Generation Started")
                    app_generic_functions.thread_function(_create_all_databases_zipped, args=ip_list)
            elif sc_action == download_logs:
                app_generic_functions.clear_zip_names()
                if sc_download_type == app_config_access.sensor_control_config.radio_send_type_direct:
                    return downloads_sensor_control(ip_list, download_type=download_logs)
                elif sc_download_type == app_config_access.sensor_control_config.radio_send_type_relayed:
                    app_config_access.creating_logs_zip = True
                    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Started")
                    app_generic_functions.thread_function(_create_multiple_sensor_logs_zipped, args=ip_list)
            elif sc_action == create_the_big_zip:
                logger.network_logger.info("Sensor Control - The Big Zip Generation Started")
                databases_size = _get_sum_db_sizes(ip_list)
                if app_generic_functions.save_to_memory_ok(databases_size):
                    app_generic_functions.clear_zip_names()
                    app_cached_variables.sc_big_zip_in_memory = True
                else:
                    app_cached_variables.sc_big_zip_in_memory = False
                app_config_access.creating_the_big_zip = True
                app_generic_functions.thread_function(_create_the_big_zip, args=ip_list)
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


def check_sensor_status_sensor_control(address_list):
    text_ip_and_response = ""

    threads = []
    for address in address_list:
        threads.append(Thread(target=_get_remote_sensor_check_and_delay, args=[address, True]))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    address_responses = []
    while not app_cached_variables.data_queue.empty():
        address_responses.append(app_cached_variables.data_queue.get())
        app_cached_variables.data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        if response["status"] == "OK":
            response_time = response["response_time"]
            background_colour = app_generic_functions.get_response_bg_colour(response_time)

            text_ip_and_response += "        <tr><th><span style='background-color: #f2f2f2;'>" + \
                                    response["address"] + "</span></th>\n" + \
                                    "        <th><span style='background-color: " + background_colour + ";'>" + \
                                    response_time + " Seconds</span></th>\n" + \
                                    "        <th><span style='background-color: #f2f2f2;'>" + \
                                    response["sensor_hostname"] + "</span></th></tr>\n"

    return render_template("sensor_control_online_status.html", SensorResponse=text_ip_and_response.strip())


def _create_all_databases_zipped(ip_list):
    try:
        get_db_command = sensor_network_commands.sensor_sql_database
        database_sum_sizes = _get_sum_db_sizes(ip_list)
        write_to_memory = app_generic_functions.save_to_memory_ok(database_sum_sizes)

        _queue_name_and_file_list(ip_list, command=get_db_command)

        data_list = app_generic_functions.get_data_queue_items()
        database_names = []
        sensors_database = []
        for sensor_data in data_list:
            db_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".zip"
            database_names.append(db_name)
            sensors_database.append(sensor_data[2])

        if write_to_memory:
            app_generic_functions.clear_zip_names()
            app_cached_variables.sc_databases_zip_in_memory = True
            app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(database_names,
                                                                                    sensors_database)
        else:
            app_cached_variables.sc_databases_zip_in_memory = False
            app_generic_functions.zip_files(database_names,
                                            sensors_database,
                                            save_type="save_to_disk",
                                            file_location=file_locations.html_sensor_control_databases_zip)
        app_cached_variables.sc_databases_zip_name = "Multiple_Databases_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Databases Zip Generation Error: " + str(error))
        app_cached_variables.sc_databases_zip_name = ""
    app_config_access.creating_databases_zip = False
    logger.network_logger.info("Sensor Control - Databases Zip Generation Complete")


def _create_multiple_sensor_logs_zipped(ip_list):
    try:
        get_db_command = sensor_network_commands.download_zipped_logs
        _queue_name_and_file_list(ip_list, command=get_db_command)

        data_list = app_generic_functions.get_data_queue_items()
        database_names = []
        sensors_database = []
        for sensor_data in data_list:
            db_name = sensor_data[0].split(".")[-1] + "_" + sensor_data[1] + ".zip"
            database_names.append(db_name)
            sensors_database.append(sensor_data[2])

        app_generic_functions.clear_zip_names()
        app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(database_names, sensors_database)
        app_cached_variables.sc_logs_zip_name = "Multiple_Logs_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Logs Zip Generation Error: " + str(error))
        app_cached_variables.sc_logs_zip_name = ""
    app_config_access.creating_logs_zip = False
    logger.network_logger.info("Sensor Control - Multi Sensors Logs Zip Generation Complete")


def _get_remote_sensor_check_and_delay(address, add_hostname=False):
    task_start_time = time.time()
    sensor_status = app_generic_functions.get_http_sensor_reading(address)
    task_end_time = round(time.time() - task_start_time, 3)
    sensor_hostname = ""
    if add_hostname:
        sensor_hostname = app_generic_functions.get_http_sensor_reading(address, command="GetHostName").strip()
    app_cached_variables.data_queue.put({"address": address,
                                         "status": str(sensor_status),
                                         "response_time": str(task_end_time),
                                         "sensor_hostname": str(sensor_hostname)})


def _put_all_reports_zipped_to_cache(ip_list):
    try:
        hostname = app_cached_variables.hostname
        html_reports = _get_all_html_reports(ip_list)
        html_report_names = ["ReportSystem.html", "ReportConfiguration.html", "ReportSensorsTests.html"]
        app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(html_report_names, html_reports)
        app_cached_variables.sc_reports_zip_name = "Reports_from_" + hostname + "_" + str(time.time())[:-8] + ".zip"
    except Exception as error:
        logger.network_logger.error("Sensor Control - Reports Zip Generation Error: " + str(error))
    app_config_access.creating_the_reports_zip = False
    logger.network_logger.info("Sensor Control - Reports Zip Generation Complete")


def downloads_sensor_control(address_list, download_type="sensors_download_databases"):
    network_commands = server_http_sensor_control.CreateNetworkGetCommands()
    download_command = network_commands.sensor_sql_database
    download_type_message = "the SQLite3 Database"
    if download_type == app_config_access.sensor_control_config.radio_download_logs:
        download_command = network_commands.download_zipped_logs
        download_type_message = "Full Logs"
    sensor_download_url = "window.open('https://{{ IPAddress }}:10065/" + download_command + "');"
    sensor_download_sql_list = ""
    text_ip_and_response = ""

    threads = []
    for address in address_list:
        if address != "Invalid":
            threads.append(Thread(target=_get_remote_sensor_check_and_delay, args=[address]))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    address_responses = []
    while not app_cached_variables.data_queue.empty():
        address_responses.append(app_cached_variables.data_queue.get())
        app_cached_variables.data_queue.task_done()

    address_responses = sorted(address_responses, key=lambda i: i['address'])
    for response in address_responses:
        if response["status"] == "OK":
            response_time = response["response_time"]
            background_colour = app_generic_functions.get_response_bg_colour(response_time)
            new_download = sensor_download_url.replace("{{ IPAddress }}", response["address"])
            sensor_download_sql_list += new_download + "\n            "
            text_ip_and_response += "        <tr><th><span style='background-color: #f2f2f2;'>" + \
                                    response["address"] + "</span></th>\n" + \
                                    "        <th><span style='background-color: " + background_colour + ";'>" + \
                                    response_time + " Seconds</span></th></tr>\n"

    return render_template("sensor_control_downloads.html",
                           DownloadTypeMessage=download_type_message,
                           DownloadURLs=sensor_download_sql_list.strip(),
                           SensorResponse=text_ip_and_response.strip())


def _get_all_html_reports(ip_list):
    try:
        g_s_c = server_http_generic_functions.get_sensor_control_report
        system_report = app_config_access.sensor_control_config.radio_report_system
        config_report = app_config_access.sensor_control_config.radio_report_config
        sensors_report = app_config_access.sensor_control_config.radio_report_test_sensors

        html_system_report = g_s_c(ip_list, report_type=system_report)
        html_config_report = g_s_c(ip_list, report_type=config_report)
        html_sensors_test_report = g_s_c(ip_list, report_type=sensors_report)

        html_system_report = _replace_text_in_report(html_system_report)
        html_config_report = _replace_text_in_report(html_config_report)
        html_sensors_test_report = _replace_text_in_report(html_sensors_test_report)
    except Exception as error:
        logger.primary_logger.error("Sensor Control - Unable to Generate Reports for Download: " + str(error))
        html_system_report = "error"
        html_config_report = "error"
        html_sensors_test_report = "error"
    return [html_system_report, html_config_report, html_sensors_test_report]


def _replace_text_in_report(report):
    old_text_list = ["Back to Sensor Control",
                     "/SensorControlManage"]
    new_text_list = ["Program Home Page",
                     "https://github.com/chad-ermacora/sensor-rp"]

    for old_text, new_text in zip(old_text_list, new_text_list):
        report = report.replace(old_text, new_text)
    return report


def _create_the_big_zip(ip_list):
    network_commands = server_http_sensor_control.CreateNetworkGetCommands()
    app_cached_variables.sc_big_zip_name = "TheBigZip_" + app_cached_variables.hostname + "_" + \
                                           str(time.time())[:-8] + ".zip"

    if len(ip_list) > 0:
        try:
            return_names = ["ReportSystem.html", "ReportConfiguration.html", "ReportSensorsTests.html"]
            return_files = _get_all_html_reports(ip_list)

            _queue_name_and_file_list(ip_list, network_commands.download_zipped_everything)
            ip_name_and_data = app_generic_functions.get_data_queue_items()

            for sensor in ip_name_and_data:
                current_file_name = sensor[0].split(".")[-1] + "_" + sensor[1] + ".zip"
                return_names.append(current_file_name)
                return_files.append(sensor[2])

            get_zipped_sql_size = network_commands.sensor_zipped_sql_database_size
            zipped_database_sizes_list = []
            for ip in ip_list:
                database_size = app_generic_functions.get_http_sensor_reading(ip, command=get_zipped_sql_size)
                try:
                    int_size = int(database_size)
                    zipped_database_sizes_list.append(int_size)
                except Exception as error:
                    logger.network_logger.warning("Sensor Control - Failed getting Database size for " + str(ip))
                    logger.network_logger.debug("SC Database Size Error: " + str(error))

            total_databases_size = 0
            for size in zipped_database_sizes_list:
                total_databases_size += size

            if app_generic_functions.save_to_memory_ok(total_databases_size):
                app_cached_variables.sc_in_memory_zip = app_generic_functions.zip_files(return_names, return_files)
            else:
                zip_location = file_locations.html_sensor_control_big_zip
                app_generic_functions.zip_files(return_names, return_files, save_type="to_disk",
                                                file_location=zip_location)

            logger.network_logger.info("Sensor Control - The Big Zip Generation Completed")
            app_config_access.creating_the_big_zip = False
        except Exception as error:
            logger.primary_logger.error("Sensor Control - Big Zip Error: " + str(error))
            app_config_access.creating_the_big_zip = False
            app_cached_variables.sc_big_zip_name = ""


def _queue_name_and_file_list(ip_list, command):
    thread_list = []
    for address in ip_list:
        if address != "Invalid":
            thread_list.append(Thread(target=_worker_queue_list_ip_name_file, args=[address, command]))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


def _worker_queue_list_ip_name_file(address, command):
    try:
        sensor_name = app_generic_functions.get_http_sensor_reading(address, command="GetHostName")
        sensor_data = app_generic_functions.get_http_sensor_file(address, command)
        app_cached_variables.data_queue.put([address, sensor_name, sensor_data])
    except Exception as error:
        logger.network_logger.error("Sensor Control - Get Remote File Failed: " + str(error))


def sensor_control_management():
    radio_checked_online_status = ""
    radio_checked_systems_report = ""
    radio_checked_config_report = ""
    radio_checked_sensors_test_report = ""
    radio_checked_download_reports = ""
    radio_checked_download_database = ""
    radio_checked_download_logs = ""
    radio_checked_download_big_zip = ""

    radio_checked_send_relayed = ""
    radio_checked_send_direct = ""

    disabled_download_relayed = ""
    disabled_download_direct = ""
    selected_action = app_config_access.sensor_control_config.selected_action
    if selected_action == app_config_access.sensor_control_config.radio_check_status:
        radio_checked_online_status = "checked"
        disabled_download_relayed = "disabled"
        disabled_download_direct = "disabled"
    elif selected_action == app_config_access.sensor_control_config.radio_report_system:
        radio_checked_systems_report = "checked"
        disabled_download_relayed = "disabled"
        disabled_download_direct = "disabled"
    elif selected_action == app_config_access.sensor_control_config.radio_report_config:
        radio_checked_config_report = "checked"
        disabled_download_relayed = "disabled"
        disabled_download_direct = "disabled"
    elif selected_action == app_config_access.sensor_control_config.radio_report_test_sensors:
        radio_checked_sensors_test_report = "checked"
        disabled_download_relayed = "disabled"
        disabled_download_direct = "disabled"
    elif selected_action == app_config_access.sensor_control_config.radio_download_reports:
        radio_checked_download_reports = "checked"
        radio_checked_send_relayed = "checked"
        disabled_download_direct = "disabled"
    elif selected_action == app_config_access.sensor_control_config.radio_download_databases:
        radio_checked_download_database = "checked"
    elif selected_action == app_config_access.sensor_control_config.radio_download_logs:
        radio_checked_download_logs = "checked"
    elif selected_action == app_config_access.sensor_control_config.radio_create_the_big_zip:
        radio_checked_download_big_zip = "checked"
        radio_checked_send_relayed = "checked"
        disabled_download_direct = "disabled"

    if radio_checked_send_relayed == "" and radio_checked_send_direct == "":
        radio_checked_send_relayed = "checked"

    download_big_zip = "disabled"
    if not app_config_access.creating_the_big_zip and app_cached_variables.sc_big_zip_name != "":
        download_big_zip = ""

    download_reports_zip = "disabled"
    if not app_config_access.creating_the_reports_zip and app_cached_variables.sc_reports_zip_name != "":
        download_reports_zip = ""

    download_databases_zip = "disabled"
    if not app_config_access.creating_databases_zip and app_cached_variables.sc_databases_zip_name != "":
        download_databases_zip = ""

    download_logs_zip = "disabled"
    if not app_config_access.creating_logs_zip and app_cached_variables.sc_logs_zip_name != "":
        download_logs_zip = ""

    extra_message = ""
    disabled_reports_zip = ""
    disabled_big_zip = ""
    disable_run_action_button = ""
    if app_config_access.creating_the_big_zip:
        extra_message = "Creating Big Zip"
        disable_run_action_button = "disabled"
    elif app_config_access.creating_the_reports_zip:
        extra_message = "Creating Reports Zip"
        disable_run_action_button = "disabled"
    elif app_config_access.creating_databases_zip:
        extra_message = "Creating Databases Zip"
        disable_run_action_button = "disabled"
    elif app_config_access.creating_logs_zip:
        extra_message = "Creating Logs Zip"
        disable_run_action_button = "disabled"

    return render_template("sensor_control.html",
                           ExtraTextMessage=extra_message,
                           DownloadReportsZipDisabled=download_reports_zip,
                           DownloadDatabasesDisabled=download_databases_zip,
                           DownloadLogsDisabled=download_logs_zip,
                           DownloadBigZipDisabled=download_big_zip,
                           RunActionDisabled=disable_run_action_button,
                           CheckedOnlineStatus=radio_checked_online_status,
                           CheckedSystemReports=radio_checked_systems_report,
                           CheckedConfigReports=radio_checked_config_report,
                           CheckedSensorsTestReports=radio_checked_sensors_test_report,
                           CheckedRelayedDownload=radio_checked_send_relayed,
                           CheckedDirectDownload=radio_checked_send_direct,
                           CheckedDownloadReports=radio_checked_download_reports,
                           CheckedDownloadDatabases=radio_checked_download_database,
                           CheckedDownloadLogs=radio_checked_download_logs,
                           CheckedDownloadBig=radio_checked_download_big_zip,
                           DownloadBigDisabled=disabled_big_zip,
                           DisabledDownloadReports=disabled_reports_zip,
                           DisabledRelayedDownload=disabled_download_relayed,
                           DisabledDirectDownload=disabled_download_direct,
                           SensorIP1=app_config_access.sensor_control_config.sensor_ip_dns1,
                           SensorIP2=app_config_access.sensor_control_config.sensor_ip_dns2,
                           SensorIP3=app_config_access.sensor_control_config.sensor_ip_dns3,
                           SensorIP4=app_config_access.sensor_control_config.sensor_ip_dns4,
                           SensorIP5=app_config_access.sensor_control_config.sensor_ip_dns5,
                           SensorIP6=app_config_access.sensor_control_config.sensor_ip_dns6,
                           SensorIP7=app_config_access.sensor_control_config.sensor_ip_dns7,
                           SensorIP8=app_config_access.sensor_control_config.sensor_ip_dns8,
                           SensorIP9=app_config_access.sensor_control_config.sensor_ip_dns9,
                           SensorIP10=app_config_access.sensor_control_config.sensor_ip_dns10,
                           SensorIP11=app_config_access.sensor_control_config.sensor_ip_dns11,
                           SensorIP12=app_config_access.sensor_control_config.sensor_ip_dns12,
                           SensorIP13=app_config_access.sensor_control_config.sensor_ip_dns13,
                           SensorIP14=app_config_access.sensor_control_config.sensor_ip_dns14,
                           SensorIP15=app_config_access.sensor_control_config.sensor_ip_dns15,
                           SensorIP16=app_config_access.sensor_control_config.sensor_ip_dns16,
                           SensorIP17=app_config_access.sensor_control_config.sensor_ip_dns17,
                           SensorIP18=app_config_access.sensor_control_config.sensor_ip_dns18,
                           SensorIP19=app_config_access.sensor_control_config.sensor_ip_dns19,
                           SensorIP20=app_config_access.sensor_control_config.sensor_ip_dns20)


def _get_sum_db_sizes(ip_list):
    done_get = False
    get_error_count = 0
    get_database_size_command = sensor_network_commands.sensor_zipped_sql_database_size
    databases_size = 0
    for ip in ip_list:
        while not done_get and get_error_count < 3:
            try:
                db_size = int(app_generic_functions.get_http_sensor_reading(ip, command=get_database_size_command))
                databases_size += db_size
                done_get = True
            except Exception as error:
                logger.network_logger.error("Sensor Control - Error adding sensor DB Size for " + ip +
                                            " Try #" + str(get_error_count))
                logger.network_logger.debug("Sensor Control DB Sizes Error: " + str(error))
                get_error_count += 1
        done_get = False
        get_error_count = 0
    return databases_size


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
                return server_http_generic_functions.message_and_return("Problem loading Zip",
                                                                        url="/SensorControlManage")
    else:
        return server_http_generic_functions.message_and_return("Zipped Databases Creation in Progress",
                                                                url="/SensorControlManage")


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
            return server_http_generic_functions.message_and_return("Zipped Reports Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Reports Zip Error: " + str(error))

    app_cached_variables.sc_reports_zip_name = ""
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")


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
            return server_http_generic_functions.message_and_return("Zipped Multiple Sensors Logs Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send SC Logs Zip Error: " + str(error))

    app_cached_variables.sc_logs_zip_name = ""
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")


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
            return server_http_generic_functions.message_and_return("Big Zip Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Big Zip Error: " + str(error))
    app_cached_variables.sc_big_zip_in_memory = False
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")
