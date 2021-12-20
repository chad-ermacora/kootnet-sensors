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


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and return it's content. """
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


def write_file_to_disk(file_location, file_content, open_type="w"):
    """ Writes provided file and content to local disk. """
    logger.primary_logger.debug("Writing content to " + str(file_location))

    try:
        with open(file_location, open_type) as write_file:
            write_file.write(file_content)
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))
