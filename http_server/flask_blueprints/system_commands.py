import os
import time
from datetime import datetime
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from operations_modules import os_cli_commands
from operations_modules.sqlite_database import validate_sqlite_database, check_database_structure
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return
from sensor_modules import sensor_access


html_system_commands_routes = Blueprint("html_system_commands_routes", __name__)
sensor_network_commands = app_cached_variables.CreateNetworkGetCommands()
message_few_min = "This may take a few minutes ..."


@html_system_commands_routes.route("/CheckOnlineStatus")
def check_online():
    logger.network_logger.debug("Sensor Status Checked by " + str(request.remote_addr))
    return "OK"


@html_system_commands_routes.route("/GetHostName")
def get_hostname():
    logger.network_logger.debug("* Sensor's HostName sent to " + str(request.remote_addr))
    return app_cached_variables.hostname


@html_system_commands_routes.route("/GetSystemDateTime")
def get_system_date_time():
    logger.network_logger.debug("* Sensor's Date & Time sent to " + str(request.remote_addr))
    return str(sensor_access.get_system_datetime())


@html_system_commands_routes.route("/GetSystemUptime")
def get_system_uptime():
    logger.network_logger.debug("* Sensor's Uptime sent to " + str(request.remote_addr))
    return str(sensor_access.get_uptime_str())


@html_system_commands_routes.route("/GetOSVersion")
def get_operating_system_version():
    logger.network_logger.debug("* Sensor's Operating System Version sent to " + str(request.remote_addr))
    return str(sensor_access.get_operating_system_name())


@html_system_commands_routes.route("/GetSensorVersion")
def get_sensor_program_version():
    logger.network_logger.debug("* Sensor's Version sent to " + str(request.remote_addr))
    return str(app_config_access.software_version.version)


@html_system_commands_routes.route("/GetSQLDBSize")
def get_sql_db_size():
    logger.network_logger.debug("* Sensor's Database Size sent to " + str(request.remote_addr))
    return str(sensor_access.get_db_size())


@html_system_commands_routes.route("/UploadSQLDatabase", methods=["GET", "POST"])
@auth.login_required
def put_sql_db():
    logger.network_logger.info("* Sensor's Database Replaced by " + str(request.remote_addr))
    return_message_ok = "The previous database was archived and replaced with the uploaded Database."
    return_message_fail = "Invalid SQLite3 Database File."
    return_backup_fail = "Upload cancelled due to failed database backup."

    temp_db_location = file_locations.sensor_data_dir + "/upload_test.sqlite"
    new_database = request.files["command_data"]
    if new_database is not None:
        new_database.save(temp_db_location)
        if validate_sqlite_database(database_location=temp_db_location):
            check_database_structure(database_location=temp_db_location)
            if _move_database():
                os.system("mv -f " + temp_db_location + " " + file_locations.sensor_database)
                return message_and_return("Sensor Database Uploaded OK", text_message2=return_message_ok, url="/")
            else:
                return message_and_return("Sensor Database Backup Failed", text_message2=return_backup_fail, url="/")
    return message_and_return("Sensor Database Uploaded Failed", text_message2=return_message_fail, url="/")


def _move_database():
    sql_filename = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + "SensorDatabase.sqlite"
    zip_filename = str(datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")) + "SensorDatabase.zip"
    try:
        zip_content = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.sensor_data_dir + "/" + zip_filename)
        logger.network_logger.info("* Sensor's Database backed up as " + file_locations.sensor_data_dir + zip_filename)
        os.system("rm " + file_locations.sensor_database)
        return True
    except Exception as error:
        logger.network_logger.error("Unable to backup database as zip - " + str(error))
    return False


@html_system_commands_routes.route("/GetZippedSQLDatabaseSize")
def get_zipped_sql_database_size():
    logger.network_logger.debug("* Zipped SQL Database Size Sent to " + str(request.remote_addr))
    try:
        database_name = app_cached_variables.hostname + "SensorDatabase.sqlite"
        start_time = time.time()
        sql_database = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
        zip_file = app_generic_functions.zip_files([database_name], [sql_database])
        sql_database_size = round(app_generic_functions.get_zip_size(zip_file) / 1000000, 2)
        end_time = time.time()
        run_time = str(round(end_time - start_time, 2)) + " Seconds"
        log_message = "Database Zip Creation and Size Retrieval Took: " + run_time
        logger.network_logger.debug(log_message)
        return str(sql_database_size)
    except Exception as error:
        log_message = "* Unable to Send Database Size to " + str(request.remote_addr) + ": " + str(error)
        logger.primary_logger.error(log_message)
        return "Error"


@html_system_commands_routes.route("/GetRAMUsed")
def get_ram_usage_percent():
    logger.network_logger.debug("* Sensor's RAM % used sent to " + str(request.remote_addr))
    return str(sensor_access.get_memory_usage_percent())


@html_system_commands_routes.route("/GetRAMTotal")
def get_ram_total():
    logger.network_logger.debug("* Sensor's Total RAM amount sent to " + str(request.remote_addr))
    return str(app_cached_variables.total_ram_memory)


@html_system_commands_routes.route("/GetRAMTotalSizeType")
def get_ram_total_size_type():
    logger.network_logger.debug("* Sensor's Total RAM amount size type sent to " + str(request.remote_addr))
    return app_cached_variables.total_ram_memory_size_type


@html_system_commands_routes.route("/GetUsedDiskSpace")
def get_disk_usage_percent():
    logger.network_logger.debug("* Sensor's Used Disk Space as GBs sent to " + str(request.remote_addr))
    return str(sensor_access.get_disk_usage_gb())


@html_system_commands_routes.route("/GetProgramLastUpdated")
def get_sensor_program_last_updated():
    logger.network_logger.debug("* Sensor's Program Last Updated sent to " + str(request.remote_addr))
    return sensor_access.get_last_updated()


@html_system_commands_routes.route("/UpgradeOnline")
@auth.login_required
def upgrade_http():
    logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeOnline"])
    return message_and_return("HTTP Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeOnlineClean")
@auth.login_required
def upgrade_clean_http():
    logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeOnlineClean"])
    return message_and_return("HTTP Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeOnlineDev")
@auth.login_required
def upgrade_http_dev():
    logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeOnlineDEV"])
    return message_and_return("HTTP Developer Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeSMB")
@auth.login_required
def upgrade_smb():
    logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeSMB"])
    return message_and_return("SMB Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeSMBClean")
@auth.login_required
def upgrade_clean_smb():
    logger.network_logger.info("** Clean Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeSMBClean"])
    return message_and_return("SMB Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeSMBDev")
@auth.login_required
def upgrade_smb_dev():
    logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["UpgradeSMBDEV"])
    return message_and_return("SMB Developer Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/inkupg")
@auth.login_required
def upgrade_rp_controller():
    logger.network_logger.info("* Upgrade - E-Ink Mobile Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["inkupg"])
    return "OK"


@html_system_commands_routes.route("/RestartServices")
def services_restart():
    message = "This should only take 5 to 30 seconds."
    logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(sensor_access.restart_services)
    return message_and_return("Restarting Sensor Service", text_message2=message, url="/SensorInformation")


@html_system_commands_routes.route("/RebootSystem")
@auth.login_required
def system_reboot():
    logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["RebootSystem"])
    return message_and_return("Sensor Rebooting", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/ShutdownSystem")
@auth.login_required
def system_shutdown():
    logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
    message2 = "You will be unable to access it until some one turns it back on."
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["ShutdownSystem"])
    return message_and_return("Sensor Shutting Down", text_message2=message2, url="/")


@html_system_commands_routes.route("/UpgradeSystemOS")
@auth.login_required
def upgrade_system_os():
    logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
    message = "Upgrade is already running.  "
    message2 = "The sensor will reboot when done. This will take awhile.  " + \
               "You may continue to use the sensor during the upgrade process.  " + \
               "There will be a loss of connectivity when the sensor reboots for up to 5 minutes."
    if app_cached_variables.linux_os_upgrade_ready:
        message = "Operating System Upgrade Started"
        app_cached_variables.linux_os_upgrade_ready = False
        app_generic_functions.thread_function(sensor_access.upgrade_linux_os)
    else:
        logger.network_logger.warning("* Operating System Upgrade Already Running")
    return message_and_return(message, text_message2=message2, url="/SensorInformation")


@html_system_commands_routes.route("/ReInstallRequirements")
@auth.login_required
def reinstall_program_requirements():
    logger.network_logger.info("** Program Dependency Install Initiated by " + str(request.remote_addr))
    message2 = "Once complete, the sensor programs will be restarted. " + message_few_min
    app_generic_functions.thread_function(os.system, args=os_cli_commands.bash_commands["ReInstallRequirements"])
    return message_and_return("Dependency Install Started", text_message2=message2, url="/SensorInformation")


@html_system_commands_routes.route("/DisplayText", methods=["PUT"])
def display_text():
    max_length_text_message = 250
    if app_config_access.current_config.enable_display and app_config_access.installed_sensors.has_display:
        logger.network_logger.info("* Show Message on Display Initiated by " + str(request.remote_addr))
        text_message = request.form['command_data']
        if len(text_message) > max_length_text_message:
            logger.network_logger.warning("Message sent to Display is longer then " + str(max_length_text_message) +
                                          ". Truncating to " + str(max_length_text_message) + " Character")
            text_message = text_message[:max_length_text_message]
        sensor_access.display_message(text_message)
    else:
        logger.network_logger.warning("* Unable to Display Text: Sensor Display disabled or not installed")
    return "OK"
