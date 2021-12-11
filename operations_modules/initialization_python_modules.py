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
from operations_modules.app_generic_disk import get_file_content


def load_pip_module_on_demand(module_name, module_import_str, from_list=None):
    """
    Returns pip import, if missing, installs it, then returns import
    :param module_name: Python module name used to install with pip
    :param module_import_str: Python module name used to import into python
    :param from_list: Optional: A list of what to import from the Python module
    :return: Python module import
    """
    try:
        if from_list is not None:
            return __import__(module_import_str, fromlist=from_list)
        return __import__(module_import_str)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            if from_list is not None:
                return __import__(module_import_str, fromlist=from_list)
            return __import__(module_import_str)
        except Exception as error:
            logger.primary_logger.error("Unable to install Python Module '" + module_name + "': " + str(error))
    return None


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
    if app_cached_variables.running_with_root and running_on_pi():
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


def running_on_pi():
    try:
        pi_version = str(subprocess.check_output("cat /proc/device-tree/model", shell=True).decode())
        if str(pi_version)[:12] == "Raspberry Pi":
            return True
    except Exception as error:
        logger.primary_logger.debug("Unable to verify Pi hardware: " + str(error))
    return False


def _install_pip_module(module_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    except Exception as error:
        logger.primary_logger.error("Unable to install Python Module '" + module_name + "': " + str(error))
