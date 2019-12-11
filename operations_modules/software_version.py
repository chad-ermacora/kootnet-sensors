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
from os import path
from operations_modules import file_locations


def _get_old_version():
    """ Loads the previously written program version and returns it as a string. """
    if path.isfile(file_locations.old_version_file):
        old_version_file = open(file_locations.old_version_file, 'r')
        old_version_content = old_version_file.read()
        old_version_file.close()
        return old_version_content.strip()
    else:
        write_program_version_to_file()
        return "0.0.0"


def write_program_version_to_file():
    """ Writes the current program version to previous program version file. """
    current_version_file = open(file_locations.old_version_file, 'w')
    current_version_file.write(version)
    current_version_file.close()


# Current Version of the program
version = "Alpha.28.86"
old_version = _get_old_version()
