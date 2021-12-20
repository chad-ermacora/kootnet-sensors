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
import time
from hashlib import scrypt, md5
from datetime import datetime, timedelta
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from threading import Thread
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_generic_classes import CreateRefinedVersion


def thread_function(function, args=None):
    """ Starts provided function as a thread with optional arguments. """

    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)
    system_thread.daemon = True
    system_thread.start()


def start_and_wait_threads(threads_list):
    """ Starts provided list of threads and waits for them all to complete. """

    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()


def get_list_of_filenames_in_dir(folder_location, sort_list=True):
    """
    Takes a folder argument and returns a list of filenames from it
    Optional: Set sort_list to True or False to return a sorted list, Default = True
    """
    return_filenames_list = []
    try:
        _, _, filenames = next(os.walk(folder_location))
        for f_name in filenames:
            return_filenames_list.append(f_name)
        if sort_list:
            return_filenames_list.sort()
    except Exception as custom_db_error:
        log_msg = " -- Error getting list of filenames in folder " + folder_location + ": "
        logger.primary_logger.warning(log_msg + str(custom_db_error))
    return return_filenames_list


def get_file_size(file_location, round_to=2, return_as_level=1):
    """
     Returns provided file size. By default returns main Database Size.
     Set return_as_level to 0 for bytes, 1 for MB and 2 for GB.
     Set round_to for remainder length (Default 2).
    """
    if os.path.isfile(file_location):
        db_size = os.path.getsize(file_location)
        if db_size != 0:
            if return_as_level == 1:
                db_size = db_size / 1024 / 1024
            elif return_as_level == 2:
                db_size = db_size / 1024 / 1024 / 1024
            db_size = round(db_size, round_to)
        return db_size
    return "0.0"


def get_zip_size(zip_file):
    """ Returns the size of provided Zip file. """

    files_size = 0.0
    try:
        with ZipFile(zip_file, 'r') as zip_file_access:
            for info in zip_file_access.infolist():
                files_size += info.compress_size
    except Exception as error:
        logger.primary_logger.error("Error during get zip size: " + str(error))
    return files_size


def zip_files(file_names_list, files_content_list, save_type="get_bytes_io", file_location="", skip_datetime=False):
    """
    Creates a zip of 1 or more files provided as a list.
    Saves to memory or disk based on save_type & file_location
    """

    try:
        if save_type == "get_bytes_io":
            return_zip_file = BytesIO()
        else:
            return_zip_file = file_location
        date_time = time.localtime(time.time())[:6]

        file_meta_data_list = []
        for name in file_names_list:
            name_data = ZipInfo(name)
            if not skip_datetime:
                name_data.date_time = date_time
            name_data.compress_type = ZIP_DEFLATED
            file_meta_data_list.append(name_data)
        with ZipFile(return_zip_file, "w") as zip_file:
            for file_meta_data, file_content in zip(file_meta_data_list, files_content_list):
                zip_file.writestr(file_meta_data, file_content)
        if save_type == "get_bytes_io":
            return_zip_file.seek(0)
            return return_zip_file
        return "Saved to disk"
    except Exception as error:
        logger.primary_logger.error("Zip Files Failed: " + str(error))
        return "error"


def adjust_datetime(var_datetime, hour_offset, return_datetime_obj=False):
    """ Adjusts the provided datetime as a string by the provided hour offset and returns the result as a string. """
    datetime_format = "%Y-%m-%d %H:%M:%S"
    min_expected_datetime_length = 19
    max_expected_datetime_length = 26
    cleaned_datetime = var_datetime.strip()

    if min_expected_datetime_length <= len(cleaned_datetime) <= max_expected_datetime_length:
        try:
            year = cleaned_datetime[:4]
            month_var = cleaned_datetime[5:7]
            day_var = cleaned_datetime[8:10]
            hour_var = cleaned_datetime[11:13]
            min_var = cleaned_datetime[14:16]
            second_var = cleaned_datetime[17:19]

            original_date_time = year + "-" + month_var + "-" + day_var + " " + \
                                 hour_var + ":" + min_var + ":" + second_var
            adjusted_date = datetime.strptime(original_date_time, datetime_format)
            adjusted_date = adjusted_date + timedelta(hours=hour_offset)
            replacement_date = adjusted_date.strftime(datetime_format)
            if return_datetime_obj:
                return adjusted_date
            return replacement_date
        except Exception as error:
            logger.primary_logger.warning("Date Adjustment Error: " + str(error))
            return var_datetime
    else:
        logger.primary_logger.debug("DateTime Adjustment input is invalid")
        return var_datetime


def create_password_hash(password, salt=None):
    """
    Creates and returns a [password_hash, password_salt] based on provided password.
    Optional: Provide the salt (must be bytes)
    """
    if salt is None:
        salt = os.urandom(16)
    scrypt_n = 16384
    scrypt_r = 8
    scrypt_p = 1
    try:
        start_time = time.time()
        pass_bytes = password.encode("UTF-8")
        password_hash = scrypt(password=pass_bytes, salt=salt, n=scrypt_n, r=scrypt_r, p=scrypt_p)
        end_time = time.time()
        total_processing_time = round(float(end_time - start_time), 6)
        logger.primary_logger.debug("Password Hash took " + str(total_processing_time) + " Seconds to Create")
        return [password_hash, salt]
    except Exception as error:
        logger.primary_logger.error("Creating Password Hash: " + str(error))
    return ["Hash_Error", "Hash_Error"]


def verify_password_to_hash(password_guess, salt=None, valid_password_hash=None):
    """
    Takes plain text password and creates hash to compare to the saved password hash.
    If hashes are equal, return True, else, return False
    Optional: salt and valid_password_hash, if missing, uses app_cached_variables flask variables
    """
    try:
        if valid_password_hash is None or salt is None:
            valid_password_hash = app_cached_variables.http_flask_password_hash
            salt = app_cached_variables.http_flask_password_salt
        password_guess_hash = create_password_hash(password_guess, salt=salt)[0]
        if password_guess_hash == valid_password_hash:
            return True
    except Exception as error:
        logger.primary_logger.error("Verifying Password Hash: " + str(error))
    return False


def get_md5_hash_of_file(file_location):
    try:
        if type(file_location) is str:
            with open(file_location, "rb") as file:
                file_md5 = md5(file.read()).hexdigest()
        else:
            file_md5 = md5(file_location).hexdigest()
        return file_md5
    except Exception as error:
        logger.primary_logger.warning("Error Creating MD5 of " + str(file_location) + ": " + str(error))
    return None


def check_if_version_newer(current_version, new_version_str):
    current_ver = CreateRefinedVersion(current_version)
    latest_ver = CreateRefinedVersion(new_version_str)

    if latest_ver.major_version > current_ver.major_version:
        return True
    elif latest_ver.major_version == current_ver.major_version:
        if latest_ver.feature_version > current_ver.feature_version:
            return True
        elif latest_ver.feature_version == current_ver.feature_version:
            if latest_ver.minor_version > current_ver.minor_version:
                return True
    return False
