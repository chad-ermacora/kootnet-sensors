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
from operations_modules import file_locations
from operations_modules.software_version import version
from operations_modules.app_generic_classes import CreateRefinedVersion
from operations_modules.app_generic_functions import get_md5_hash_of_file
from operations_modules.app_generic_disk import get_file_content, write_file_to_disk

original_source_dir = file_locations.program_root_dir + "/"
user_home_dir = "/home/" + file_locations.get_user() + "/"
debian_installer_dir = user_home_dir + "kootnet_sensors_installers/"
debian_build_dir = debian_installer_dir + "KootnetSensors/"

current_version = CreateRefinedVersion(version)

upgrade_filename_version = "kootnet_version.txt"
upgrade_filename_md5 = "KootnetSensors-deb-MD5.txt"
upgrade_filename_full_installer = "KootnetSensors.deb"
upgrade_filename_update_installer = "KootnetSensors_online.deb"

options_menu = f"""Kootnet Sensors [[ version ]] - Debian Installer Creation Tool
Output folder: {debian_installer_dir}\n
1. Start Build
2. Change Minor Version Number
3. Change Feature Version Number
4. Change Major Version Number
5. Change Default Configuration Settings
6. Install Required OS APT Packages
12. Exit
"""

configurations_menu = """Change Configuration Defaults\n
1. Main Configuration
2. URLs Configuration
3. Automatic Upgrades Configuration
4. Installed Sensors Configuration
5. Sensor Offsets Configuration
6. Display Configuration
7. Sensor Checkins Configuration
8. Interval SQL Recording Configuration
9. High/Low Variance SQL Recording Configuration
10. Trigger Variance SQL Recording Configuration
11. Email Configuration
12. MQTT Publisher Configuration
13. MQTT Subscriber Configuration
14. MQTT Broker Configuration
15. Open Sense Map Configuration
16. Weather Underground Configuration
17. Sensor Community Configuration
"""


def start_deb_build_cli_menu():
    global current_version
    _check_build_directories()

    running = True
    while running:
        new_options_menu = options_menu.replace("[[ version ]]", current_version.get_version_string())
        os.system("clear")
        print(new_options_menu)
        selection = input("Enter Number: ")

        try:
            selection = int(selection)
            os.system("clear")
            if selection == 1:
                start_debian_package_build()
            elif selection == 2:
                print(f"Current Minor Version: {current_version.minor_version}")
                new_version = input("Enter Minor Version: ")
                if new_version == "back":
                    pass
                elif new_version.isnumeric():
                    current_version.minor_version = new_version
                    _change_program_version(current_version)
                else:
                    print("Only Numbers can be used")
            elif selection == 3:
                print(f"Current Feature Version: {current_version.feature_version}")
                new_version = input("Enter Feature Version: ")
                if new_version == "back":
                    pass
                elif new_version.isnumeric():
                    current_version.feature_version = new_version
                    _change_program_version(current_version)
                else:
                    print("Only Numbers can be used")
            elif selection == 4:
                print(f"Current Major Version: {current_version.major_version}")
                new_version = input("Enter Major Version: ")
                if new_version == "back":
                    pass
                elif new_version.isnumeric():
                    current_version.major_version = new_version
                    _change_program_version(current_version)
                else:
                    print("Only Numbers can be used")
            elif selection == 5:
                print(configurations_menu)
                _edit_default_configs()
            elif selection == 6:
                os.system("sudo apt-get -y install zip")
            elif selection == 11:
                _copy_to_smb()
            elif selection == 12:
                running = False
            else:
                os.system("clear")
                print("Invalid Selection: " + str(selection))
        except ValueError:
            os.system("clear")
            print("Invalid Selection: " + str(selection))
        except Exception as error:
            os.system("clear")
            print("Invalid Selection: " + str(selection) + " - " + str(error))
        if running:
            input("\nPress enter to continue")


def start_debian_package_build():
    try:
        print("Creating Debian Package Base folders ...")
        _create_debian_build_dir()
        print("Copying Source Code to Debian Package Folder ...")
        _zip_original_code()
        _unzip_original_code()
        print("Starting to Build Debian Packages ...")
        _build_package()
        print("Creating Upgrade Version File & Appending to MD5s File ...")
        _create_version_file()
        _create_md5_file()
        _set_file_permissions()
        print("\nDebian Installer Creations Complete")
    except Exception as error:
        print("Error Building Debian Packages: " + str(error))


def _create_debian_build_dir():
    if os.path.isdir(debian_build_dir):
        os.system("rm -f -r " + debian_build_dir)
    os.system(f"cp -f -r {original_source_dir}extras/deb_package_files/ {debian_installer_dir}")
    os.system(f"mv -f {debian_installer_dir}deb_package_files {debian_installer_dir}KootnetSensors")


def _zip_original_code():
    old_source_folder_name = original_source_dir[:-1].split("/")[-1]
    pre_original_source_dir = "/"
    for directory in original_source_dir[:-1].split("/")[:-1]:
        pre_original_source_dir += directory + "/"
    command_zip_source = f"cd {pre_original_source_dir} && zip -FSr '{debian_installer_dir}KootNetSensors.zip' " \
                         f"./{old_source_folder_name} -x '*/\.*' '*/\__pycache*'"
    os.system(command_zip_source)


def _unzip_original_code():
    old_source_folder_name = original_source_dir[:-1].split("/")[-1]

    command_unzip_source = f"unzip -q '{debian_installer_dir}KootNetSensors.zip' -d '{debian_build_dir}opt/'"
    os.system(command_unzip_source)
    if not os.path.isdir(f"{debian_build_dir}opt/kootnet-sensors"):
        os.system(f"mv -f {debian_build_dir}opt/{old_source_folder_name} {debian_build_dir}opt/kootnet-sensors")


def _create_version_file():
    with open(debian_installer_dir + upgrade_filename_version, "w") as version_file:
        version_file.write(current_version.get_version_string())


def _create_md5_file():
    file_content = ""
    if os.path.isfile(debian_installer_dir + upgrade_filename_md5):
        with open(debian_installer_dir + upgrade_filename_md5, "r") as md5_file:
            file_content = md5_file.read()
    with open(debian_installer_dir + upgrade_filename_md5, "w") as md5_file:
        md5_file.write(_get_md5_formatted() + _remove_this_version_from_md5(file_content))


def _remove_this_version_from_md5(md5_content):
    md5_locations = []
    return_content = ""
    for index, line in enumerate(md5_content.split("\n")):
        line = line.strip()
        if line == current_version.get_version_string() + " KootnetSensors.deb":
            md5_locations.append(index)

    new_md5_locations = []
    for index_loc in md5_locations:
        new_md5_locations.append(index_loc)
        new_md5_locations.append(index_loc + 1)
        new_md5_locations.append(index_loc + 2)
        new_md5_locations.append(index_loc + 3)
        new_md5_locations.append(index_loc + 4)
        new_md5_locations.append(index_loc + 5)

    for index, line in enumerate(md5_content.split("\n")):
        line = line.strip()
        if index not in new_md5_locations:
            return_content += "\n" + line
    return return_content.strip()


def _get_md5_formatted():
    full_installer_md5 = get_md5_hash_of_file(debian_installer_dir + upgrade_filename_full_installer)
    upgrade_installer_md5 = get_md5_hash_of_file(debian_installer_dir + upgrade_filename_update_installer)

    return f"""\n
{current_version.get_version_string()} KootnetSensors.deb
MD5: {full_installer_md5}
---
{current_version.get_version_string()} KootnetSensors_online.deb
MD5: {upgrade_installer_md5}
------------------\n"""


def _build_package():
    if os.path.dirname(debian_installer_dir + "KootnetSensors_online/"):
        os.system("rm -f -r " + debian_installer_dir + "KootnetSensors_online/")
    if os.path.isdir(f"{debian_installer_dir}KootnetSensors"):
        os.system(f"dpkg-deb --build {debian_installer_dir}KootnetSensors")
        os.system(f" rm -rf {debian_build_dir}opt/kootnet-sensors/extras/python_modules/")
        os.system(f"mv '{debian_installer_dir}/KootnetSensors' '{debian_installer_dir}/KootnetSensors_online'")
        os.system(f"dpkg-deb --build {debian_installer_dir}KootnetSensors_online")


def _change_program_version(new_version):
    ks_version_file = get_file_content(original_source_dir + "operations_modules/software_version.py")
    control_version_file_content = get_file_content(original_source_dir + "extras/deb_package_files/DEBIAN/control")

    new_ks_version_file = ""
    for line in ks_version_file.split("\n"):
        if line.split("=")[0].strip() == "version":
            new_ks_version_file += f'version = "{new_version.get_version_string()}"\n'
        else:
            new_ks_version_file += f"{line}\n"
    new_ks_version_file = new_ks_version_file.strip() + "\n"
    write_file_to_disk(original_source_dir + "operations_modules/software_version.py", new_ks_version_file)

    new_control_version = ""
    for line in control_version_file_content.split("\n"):
        if line.split(":")[0].strip() == "Version":
            nv = f"Version: {new_version.major_version}.{new_version.feature_version}-{new_version.minor_version}\n"
            new_control_version += nv
        else:
            new_control_version += f"{line}\n"
    new_control_version = new_control_version.strip() + "\n"
    write_file_to_disk(original_source_dir + "extras/deb_package_files/DEBIAN/control", new_control_version)


def _edit_default_configs():
    config_selection = input("Enter Number: ")
    try:
        config_selection = int(config_selection)
        os.system("clear")
        if config_selection == 1:
            os.system(f"nano {original_source_dir}configuration_modules/config_primary.py")
        elif config_selection == 2:
            os.system(f"nano {original_source_dir}configuration_modules/config_urls.py")
        elif config_selection == 3:
            os.system(f"nano {original_source_dir}configuration_modules/config_upgrades.py")
        elif config_selection == 4:
            os.system(f"nano {original_source_dir}configuration_modules/config_installed_sensors.py")
        elif config_selection == 5:
            os.system(f"nano {original_source_dir}configuration_modules/config_sensor_offsets.py")
        elif config_selection == 6:
            os.system(f"nano {original_source_dir}configuration_modules/config_display.py")
        elif config_selection == 7:
            os.system(f"nano {original_source_dir}configuration_modules/config_check_ins.py")
        elif config_selection == 8:
            os.system(f"nano {original_source_dir}configuration_modules/config_interval_recording.py")
        elif config_selection == 9:
            os.system(f"nano {original_source_dir}configuration_modules/config_trigger_high_low.py")
        elif config_selection == 10:
            os.system(f"nano {original_source_dir}configuration_modules/config_trigger_variances.py")
        elif config_selection == 11:
            os.system(f"nano {original_source_dir}configuration_modules/config_email.py")
        elif config_selection == 12:
            os.system(f"nano {original_source_dir}configuration_modules/config_mqtt_publisher.py")
        elif config_selection == 13:
            os.system(f"nano {original_source_dir}configuration_modules/config_mqtt_subscriber.py")
        elif config_selection == 14:
            os.system(f"nano {original_source_dir}configuration_modules/config_mqtt_broker.py")
        elif config_selection == 15:
            os.system(f"nano {original_source_dir}configuration_modules/config_open_sense_map.py")
        elif config_selection == 16:
            os.system(f"nano {original_source_dir}configuration_modules/config_weather_underground.py")
        elif config_selection == 17:
            os.system(f"nano {original_source_dir}configuration_modules/config_luftdaten.py")
        else:
            os.system("clear")
            print("Invalid Selection: " + str(config_selection))
    except ValueError:
        os.system("clear")
        print("Invalid Selection: " + str(config_selection))
    except Exception as error:
        os.system("clear")
        print("Invalid Selection: " + str(config_selection) + " - " + str(error))


def _copy_to_smb():
    print("Transferring Upgrade Files to Dev's SMB Share ...")
    new_location = debian_installer_dir + "KootNetSMB/"
    md5_versions_file = debian_installer_dir + upgrade_filename_md5
    upgrade_installer_files = [
        debian_installer_dir + upgrade_filename_version,
        debian_installer_dir + upgrade_filename_full_installer,
        debian_installer_dir + upgrade_filename_update_installer
    ]
    os.system(f"cp -f {md5_versions_file} '{new_location}'")
    for file_loc in upgrade_installer_files:
        os.system(f"cp -f {file_loc} '{new_location}dev/'")


def _set_file_permissions():
    """ Sets upgrade files permissions to be accessible by all. """
    os.chmod(debian_installer_dir + upgrade_filename_version, 0o666)
    os.chmod(debian_installer_dir + upgrade_filename_md5, 0o666)
    os.chmod(debian_installer_dir + upgrade_filename_full_installer, 0o777)
    os.chmod(debian_installer_dir + upgrade_filename_update_installer, 0o777)


def _check_build_directories():
    directories_list = [
        debian_installer_dir
    ]
    for directory in directories_list:
        if not os.path.isdir(directory):
            os.mkdir(directory)


if __name__ == '__main__':
    start_deb_build_cli_menu()
