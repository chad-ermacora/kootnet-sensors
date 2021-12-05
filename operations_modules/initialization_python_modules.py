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
import sys
import subprocess
import pkg_resources
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables


def check_and_install_required_python_modules():
    """
    Checks
    :return:
    """
    requirements_location = file_locations.program_root_dir + "/requirements.txt"
    hw_requirements_location = file_locations.program_root_dir + "/requirements_hw_sensors.txt"
    installed_python_module_list = []
    for py_module in pkg_resources.working_set:
        installed_python_module_list.append(py_module.key)

    module_lists = [requirements_location]
    if app_cached_variables.running_with_root and _running_on_pi():
        module_lists.append(hw_requirements_location)
    required_modules_list = _add_pip_modules_to_list(module_lists)
    for requirement in required_modules_list:
        if requirement.lower() not in installed_python_module_list:
            logger.primary_logger.info("Installing Missing Python Module " + requirement)
            _install_pip_module(requirement)


def _add_pip_modules_to_list(requirements_locations_list):
    modules_list = []
    for requirements_location in requirements_locations_list:
        if os.path.isfile(requirements_location):
            requirements_text = get_file_content(requirements_location).strip()
            for requirement in requirements_text.split("\n"):
                requirement = requirement.strip()
                if requirement[0] != "#":
                    modules_list.append(requirement)
    return modules_list


def _running_on_pi():
    pi_version = str(subprocess.check_output("cat /proc/device-tree/model", shell=True).decode())
    if str(pi_version)[:12] == "Raspberry Pi":
        return True
    return False


def _install_pip_module(module_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    except Exception as error:
        logger.primary_logger.error("Unable to install Python Module '" + module_name + "': " + str(error))


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns its content. """
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
