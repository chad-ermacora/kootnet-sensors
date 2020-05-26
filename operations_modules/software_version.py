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


class CreateRefinedVersion:
    """ Takes the provided program version as text and creates a data class object. """
    def __init__(self, version_text=""):
        self.bad_version_load = True
        self.major_version = 0
        self.feature_version = 0
        self.minor_version = 0
        self.load_from_string(version_text)

    def load_from_string(self, version_text):
        try:
            version_split = str(version_text).split(".")
            if len(version_split) > 2:
                self.major_version = version_split[0]
                self.feature_version = int(version_split[1])
                self.minor_version = int(version_split[2])
                self.bad_version_load = False
        except Exception as error:
            print("version load error: " + str(error))

    def get_version_string(self):
        return str(self.major_version) + "." + str(self.feature_version) + "." + str(self.minor_version)


def _get_old_version():
    """ Loads the previously written program version and returns it as a string. """
    if path.isfile(file_locations.old_version_file):
        with open(file_locations.old_version_file, 'r') as old_version_file:
            old_version_content = old_version_file.read()
            return old_version_content.strip()
    else:
        write_program_version_to_file()
        return "New_Install.99.999"


def write_program_version_to_file():
    """ Writes the current program version to previous program version file. """
    with open(file_locations.old_version_file, 'w') as current_version_file:
        current_version_file.write(version)


# Current Version of the program
version = "Beta.30.112"
old_version = _get_old_version()
