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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules import sensor_access
from sensor_recording_modules import recording_interval
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_checkbox_state, message_and_return

html_config_installed_sensors_routes = Blueprint("html_config_installed_sensors_routes", __name__)
running_with_root = app_cached_variables.running_with_root


@html_config_installed_sensors_routes.route("/EditInstalledSensors", methods=["POST"])
@auth.login_required
def html_set_installed_sensors():
    logger.network_logger.debug("** HTML Apply - Installed Sensors - Source " + str(request.remote_addr))
    if request.method == "POST":
        try:
            app_config_access.installed_sensors.update_with_html_request(request)
            app_config_access.installed_sensors.save_config_to_file()
            sensor_access.sensors_direct.__init__()
            recording_interval.available_sensors.__init__()
            return_page = message_and_return("Installed Sensors Set & Re-Initialized", url="/ConfigurationsHTML")
            return return_page
        except Exception as error:
            logger.primary_logger.error("HTML Apply - Installed Sensors - Error: " + str(error))
            return message_and_return("Bad Installed Sensors POST Request", url="/ConfigurationsHTML")


def get_config_installed_sensors_tab():
    try:
        installed_sensors = app_config_access.installed_sensors
        return render_template("edit_configurations/config_installed_sensors.html",
                               PageURL="/ConfigurationsHTML",
                               GnuLinux=get_html_checkbox_state(installed_sensors.linux_system),
                               KootnetDummySensors=get_html_checkbox_state(installed_sensors.kootnet_dummy_sensor),
                               RaspberryPi=get_html_checkbox_state(installed_sensors.raspberry_pi),
                               SenseHAT=get_html_checkbox_state(installed_sensors.raspberry_pi_sense_hat),
                               PimoroniBH1745=get_html_checkbox_state(installed_sensors.pimoroni_bh1745),
                               PimoroniAS7262=get_html_checkbox_state(installed_sensors.pimoroni_as7262),
                               PimoroniMCP9600=get_html_checkbox_state(installed_sensors.pimoroni_mcp9600),
                               PimoroniBMP280=get_html_checkbox_state(installed_sensors.pimoroni_bmp280),
                               PimoroniBME680=get_html_checkbox_state(installed_sensors.pimoroni_bme680),
                               PimoroniEnviroPHAT=get_html_checkbox_state(installed_sensors.pimoroni_enviro),
                               PimoroniEnviroPlus=get_html_checkbox_state(installed_sensors.pimoroni_enviroplus),
                               PimoroniPMS5003=get_html_checkbox_state(installed_sensors.pimoroni_pms5003),
                               PimoroniSGP30=get_html_checkbox_state(installed_sensors.pimoroni_sgp30),
                               PimoroniMSA301=get_html_checkbox_state(installed_sensors.pimoroni_msa301),
                               PimoroniLSM303D=get_html_checkbox_state(installed_sensors.pimoroni_lsm303d),
                               PimoroniICM20948=get_html_checkbox_state(installed_sensors.pimoroni_icm20948),
                               PimoroniVL53L1X=get_html_checkbox_state(installed_sensors.pimoroni_vl53l1x),
                               PimoroniLTR559=get_html_checkbox_state(installed_sensors.pimoroni_ltr_559),
                               PimoroniVEML6075=get_html_checkbox_state(installed_sensors.pimoroni_veml6075),
                               Pimoroni11x7LEDMatrix=get_html_checkbox_state(installed_sensors.pimoroni_matrix_11x7),
                               PimoroniSPILCD10_96=get_html_checkbox_state(installed_sensors.pimoroni_st7735),
                               PimoroniMonoOLED128x128BW=get_html_checkbox_state(installed_sensors.pimoroni_mono_oled_luma),
                               SensirionSPS30=get_html_checkbox_state(installed_sensors.sensirion_sps30),
                               W1ThermSensor=get_html_checkbox_state(installed_sensors.w1_therm_sensor))
    except Exception as error:
        logger.network_logger.error("Error building Installed Sensors configuration page: " + str(error))
        return render_template("edit_configurations/config_load_error.html", TabID="installed-sensors-tab")
