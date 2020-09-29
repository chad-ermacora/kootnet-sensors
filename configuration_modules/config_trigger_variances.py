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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateTriggerVariancesConfiguration(CreateGeneralConfiguration):
    """ Creates the Trigger Variances Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        trigger_variances_config = file_locations.trigger_variances_config
        CreateGeneralConfiguration.__init__(self, trigger_variances_config, load_from_file=load_from_file)
        self.config_file_header = "0 = Disabled and 1 = Enabled"
        self.valid_setting_count = 61
        self.config_settings_names = [
            "Enable Trigger Variances", "Enable CPU Temperature", "CPU Temperature variance",
            "Seconds between CPU Temperature readings", "Enable Environmental Temperature",
            "Environmental Temperature variance", "Seconds between Env Temperature readings",
            "Enable Pressure", "Pressure variance", "Seconds between Pressure readings",
            "Enable Altitude", "Altitude variance", "Seconds between Altitude readings",
            "Enable Humidity", "Humidity variance", "Seconds between Humidity readings", "Enable Distance",
            "Distance variance", "Seconds between Distance readings", "Enable Gas", "Gas Resistance Index variance",
            "Gas Oxidising variance", "Gas Reducing variance", "Gas NH3 variance", "Seconds between Gas readings",
            "Enable Particulate Matter (PM)", "Particulate Matter 1 (PM1) variance",
            "Particulate Matter 2.5 (PM2.5) variance", "Particulate Matter 10 (PM10) variance",
            "Seconds between PM readings", "Enable Lumen", "Lumen variance", "Seconds between Lumen readings",
            "Enable Colour", "Red variance", "Orange variance", "Yellow variance", "Green variance", "Blue variance",
            "Violet variance", "Seconds between Colour readings", "Enable Ultra Violet",
            "Ultra Violet Index variance", "Ultra Violet A variance", "Ultra Violet B variance",
            "Seconds between Ultra Violet readings", "Enable Accelerometer", "Accelerometer X variance",
            "Accelerometer Y variance", "Accelerometer Z variance", "Seconds between Accelerometer readings",
            "Enable Magnetometer", "Magnetometer X variance", "Magnetometer Y variance", "Magnetometer Z variance",
            "Seconds between Magnetometer readings", "Enable Gyroscope", "Gyroscope X variance",
            "Gyroscope Y variance", "Gyroscope Z variance", "Seconds between Gyroscope readings"
        ]

        self.enable_trigger_variance = 0
        self.cpu_temperature_enabled = 0
        self.env_temperature_enabled = 0
        self.pressure_enabled = 0
        self.humidity_enabled = 0
        self.altitude_enabled = 0
        self.distance_enabled = 0
        self.lumen_enabled = 0
        self.colour_enabled = 0
        self.ultra_violet_enabled = 0
        self.gas_enabled = 0
        self.particulate_matter_enabled = 0
        self.accelerometer_enabled = 0
        self.magnetometer_enabled = 0
        self.gyroscope_enabled = 0

        self.cpu_temperature_variance = 5.0
        self.cpu_temperature_wait_seconds = 60.0

        self.env_temperature_variance = 5.0
        self.env_temperature_wait_seconds = 60.0

        self.pressure_variance = 10
        self.pressure_wait_seconds = 60.0

        self.humidity_variance = 5.0
        self.humidity_wait_seconds = 60.0

        self.altitude_variance = 10
        self.altitude_wait_seconds = 60.0

        self.distance_variance = 5.0
        self.distance_wait_seconds = 2.0

        self.lumen_variance = 100.0
        self.lumen_wait_seconds = 10.0

        self.red_variance = 15.0
        self.orange_variance = 15.0
        self.yellow_variance = 15.0
        self.green_variance = 15.0
        self.blue_variance = 15.0
        self.violet_variance = 15.0
        self.colour_wait_seconds = 60.0

        self.ultra_violet_index_variance = 5.0
        self.ultra_violet_a_variance = 10.0
        self.ultra_violet_b_variance = 10.0
        self.ultra_violet_wait_seconds = 60.0

        self.gas_resistance_index_variance = 100.0
        self.gas_oxidising_variance = 100.0
        self.gas_reducing_variance = 100.0
        self.gas_nh3_variance = 100.0
        self.gas_wait_seconds = 60.0

        self.particulate_matter_1_variance = 4.0
        self.particulate_matter_2_5_variance = 4.0
        self.particulate_matter_4_variance = 4.0
        self.particulate_matter_10_variance = 4.0
        self.particulate_matter_wait_seconds = 60.0

        self.accelerometer_x_variance = 0.1
        self.accelerometer_y_variance = 0.1
        self.accelerometer_z_variance = 0.1
        self.accelerometer_wait_seconds = 0.3

        self.magnetometer_x_variance = 25.0
        self.magnetometer_y_variance = 25.0
        self.magnetometer_z_variance = 25.0
        self.magnetometer_wait_seconds = 0.3

        self.gyroscope_x_variance = 25.0
        self.gyroscope_y_variance = 25.0
        self.gyroscope_z_variance = 25.0
        self.gyroscope_wait_seconds = 0.3

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    # noinspection PyAttributeOutsideInit
    def update_with_html_request(self, html_request):
        """ Updates the Trigger Variance configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Variance Triggers Update Check")

        self.enable_trigger_variance = 0
        self.cpu_temperature_enabled = 0
        self.env_temperature_enabled = 0
        self.pressure_enabled = 0
        self.humidity_enabled = 0
        self.altitude_enabled = 0
        self.distance_enabled = 0
        self.lumen_enabled = 0
        self.colour_enabled = 0
        self.ultra_violet_enabled = 0
        self.gas_enabled = 0
        self.particulate_matter_enabled = 0
        self.accelerometer_enabled = 0
        self.magnetometer_enabled = 0
        self.gyroscope_enabled = 0

        if html_request.form.get("enable_trigger_recording") is not None:
            self.enable_trigger_variance = 1

        if html_request.form.get("checkbox_cpu_temperature") is not None:
            self.cpu_temperature_enabled = 1
        if html_request.form.get("trigger_cpu_temperature") is not None:
            self.cpu_temperature_variance = float(html_request.form.get("trigger_cpu_temperature"))
        if html_request.form.get("seconds_cpu_temperature") is not None:
            self.cpu_temperature_wait_seconds = float(html_request.form.get("seconds_cpu_temperature"))

        if html_request.form.get("env_temperature") is not None:
            self.env_temperature_enabled = 1
        if html_request.form.get("trigger_env_temperature") is not None:
            self.env_temperature_variance = float(html_request.form.get("trigger_env_temperature"))
        if html_request.form.get("seconds_env_temperature") is not None:
            self.env_temperature_wait_seconds = float(html_request.form.get("seconds_env_temperature"))

        if html_request.form.get("pressure") is not None:
            self.pressure_enabled = 1
        if html_request.form.get("trigger_pressure") is not None:
            self.pressure_variance = float(html_request.form.get("trigger_pressure"))
        if html_request.form.get("seconds_pressure") is not None:
            self.pressure_wait_seconds = float(html_request.form.get("seconds_pressure"))

        if html_request.form.get("humidity") is not None:
            self.humidity_enabled = 1
        if html_request.form.get("trigger_humidity") is not None:
            self.humidity_variance = float(html_request.form.get("trigger_humidity"))
        if html_request.form.get("seconds_humidity") is not None:
            self.humidity_wait_seconds = float(html_request.form.get("seconds_humidity"))

        if html_request.form.get("altitude") is not None:
            self.altitude_enabled = 1
        if html_request.form.get("trigger_altitude") is not None:
            self.altitude_variance = float(html_request.form.get("trigger_altitude"))
        if html_request.form.get("seconds_altitude") is not None:
            self.altitude_wait_seconds = float(html_request.form.get("seconds_altitude"))

        if html_request.form.get("distance") is not None:
            self.distance_enabled = 1
        if html_request.form.get("trigger_distance") is not None:
            self.distance_variance = float(html_request.form.get("trigger_distance"))
        if html_request.form.get("seconds_distance") is not None:
            self.distance_wait_seconds = float(html_request.form.get("seconds_distance"))

        if html_request.form.get("lumen") is not None:
            self.lumen_enabled = 1
        if html_request.form.get("trigger_lumen") is not None:
            self.lumen_variance = float(html_request.form.get("trigger_lumen"))
        if html_request.form.get("seconds_lumen") is not None:
            self.lumen_wait_seconds = float(html_request.form.get("seconds_lumen"))

        if html_request.form.get("colour") is not None:
            self.colour_enabled = 1
        if html_request.form.get("red") is not None:
            self.red_variance = float(html_request.form.get("red"))
        if html_request.form.get("orange") is not None:
            self.orange_variance = float(html_request.form.get("orange"))
        if html_request.form.get("yellow") is not None:
            self.yellow_variance = float(html_request.form.get("yellow"))
        if html_request.form.get("green") is not None:
            self.green_variance = float(html_request.form.get("green"))
        if html_request.form.get("blue") is not None:
            self.blue_variance = float(html_request.form.get("blue"))
        if html_request.form.get("violet") is not None:
            self.violet_variance = float(html_request.form.get("violet"))
        if html_request.form.get("seconds_colour") is not None:
            self.colour_wait_seconds = float(html_request.form.get("seconds_colour"))

        if html_request.form.get("ultra_violet") is not None:
            self.ultra_violet_enabled = 1
        if html_request.form.get("ultra_violet_a") is not None:
            self.ultra_violet_a_variance = float(html_request.form.get("ultra_violet_a"))
        if html_request.form.get("ultra_violet_b") is not None:
            self.ultra_violet_b_variance = float(html_request.form.get("ultra_violet_b"))
        if html_request.form.get("seconds_ultra_violet") is not None:
            self.ultra_violet_wait_seconds = float(html_request.form.get("seconds_ultra_violet"))

        if html_request.form.get("gas") is not None:
            self.gas_enabled = 1
        if html_request.form.get("trigger_gas_index") is not None:
            self.gas_resistance_index_variance = float(html_request.form.get("trigger_gas_index"))
        if html_request.form.get("trigger_gas_oxidising") is not None:
            self.gas_oxidising_variance = float(html_request.form.get("trigger_gas_oxidising"))
        if html_request.form.get("trigger_gas_reducing") is not None:
            self.gas_reducing_variance = float(html_request.form.get("trigger_gas_reducing"))
        if html_request.form.get("trigger_gas_nh3") is not None:
            self.gas_nh3_variance = float(html_request.form.get("trigger_gas_nh3"))
        if html_request.form.get("seconds_gas") is not None:
            self.gas_wait_seconds = float(html_request.form.get("seconds_gas"))

        if html_request.form.get("particulate_matter") is not None:
            self.particulate_matter_enabled = 1
        if html_request.form.get("trigger_pm1") is not None:
            self.particulate_matter_1_variance = float(html_request.form.get("trigger_pm1"))
        if html_request.form.get("trigger_pm2_5") is not None:
            self.particulate_matter_2_5_variance = float(html_request.form.get("trigger_pm2_5"))
        if html_request.form.get("trigger_pm4") is not None:
            self.particulate_matter_4_variance = float(html_request.form.get("trigger_pm4"))
        if html_request.form.get("trigger_pm10") is not None:
            self.particulate_matter_10_variance = float(html_request.form.get("trigger_pm10"))
        if html_request.form.get("seconds_pm") is not None:
            self.particulate_matter_wait_seconds = float(html_request.form.get("seconds_pm"))

        if html_request.form.get("accelerometer") is not None:
            self.accelerometer_enabled = 1
        if html_request.form.get("accelerometer_x") is not None:
            self.accelerometer_x_variance = float(html_request.form.get("accelerometer_x"))
        if html_request.form.get("accelerometer_y") is not None:
            self.accelerometer_y_variance = float(html_request.form.get("accelerometer_y"))
        if html_request.form.get("accelerometer_z") is not None:
            self.accelerometer_z_variance = float(html_request.form.get("accelerometer_z"))
        if html_request.form.get("seconds_accelerometer") is not None:
            self.accelerometer_wait_seconds = float(html_request.form.get("seconds_accelerometer"))

        if html_request.form.get("magnetometer") is not None:
            self.magnetometer_enabled = 1
        if html_request.form.get("magnetometer_x") is not None:
            self.magnetometer_x_variance = float(html_request.form.get("magnetometer_x"))
        if html_request.form.get("magnetometer_y") is not None:
            self.magnetometer_y_variance = float(html_request.form.get("magnetometer_y"))
        if html_request.form.get("magnetometer_z") is not None:
            self.magnetometer_z_variance = float(html_request.form.get("magnetometer_z"))
        if html_request.form.get("seconds_magnetometer") is not None:
            self.magnetometer_wait_seconds = float(html_request.form.get("seconds_magnetometer"))

        if html_request.form.get("gyroscope") is not None:
            self.gyroscope_enabled = 1
        if html_request.form.get("gyroscope_x") is not None:
            self.gyroscope_x_variance = float(html_request.form.get("gyroscope_x"))
        if html_request.form.get("gyroscope_y") is not None:
            self.gyroscope_y_variance = float(html_request.form.get("gyroscope_y"))
        if html_request.form.get("gyroscope_z") is not None:
            self.gyroscope_z_variance = float(html_request.form.get("gyroscope_z"))
        if html_request.form.get("seconds_gyroscope") is not None:
            self.gyroscope_wait_seconds = float(html_request.form.get("seconds_gyroscope"))
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [
            str(self.enable_trigger_variance), str(self.cpu_temperature_enabled), str(self.cpu_temperature_variance),
            str(self.cpu_temperature_wait_seconds), str(self.env_temperature_enabled),
            str(self.env_temperature_variance), str(self.env_temperature_wait_seconds), str(self.pressure_enabled),
            str(self.pressure_variance), str(self.pressure_wait_seconds), str(self.altitude_enabled),
            str(self.altitude_variance), str(self.altitude_wait_seconds), str(self.humidity_enabled),
            str(self.humidity_variance), str(self.humidity_wait_seconds), str(self.distance_enabled),
            str(self.distance_variance), str(self.distance_wait_seconds), str(self.gas_enabled),
            str(self.gas_resistance_index_variance), str(self.gas_oxidising_variance), str(self.gas_reducing_variance),
            str(self.gas_nh3_variance), str(self.gas_wait_seconds), str(self.particulate_matter_enabled),
            str(self.particulate_matter_1_variance), str(self.particulate_matter_2_5_variance),
            str(self.particulate_matter_10_variance), str(self.particulate_matter_wait_seconds),
            str(self.lumen_enabled), str(self.lumen_variance), str(self.lumen_wait_seconds), str(self.colour_enabled),
            str(self.red_variance), str(self.orange_variance), str(self.yellow_variance), str(self.green_variance),
            str(self.blue_variance), str(self.violet_variance), str(self.colour_wait_seconds),
            str(self.ultra_violet_enabled), str(self.ultra_violet_index_variance), str(self.ultra_violet_a_variance),
            str(self.ultra_violet_b_variance), str(self.ultra_violet_wait_seconds), str(self.accelerometer_enabled),
            str(self.accelerometer_x_variance), str(self.accelerometer_y_variance), str(self.accelerometer_z_variance),
            str(self.accelerometer_wait_seconds), str(self.magnetometer_enabled), str(self.magnetometer_x_variance),
            str(self.magnetometer_y_variance), str(self.magnetometer_z_variance), str(self.magnetometer_wait_seconds),
            str(self.gyroscope_enabled), str(self.gyroscope_x_variance), str(self.gyroscope_y_variance),
            str(self.gyroscope_z_variance), str(self.gyroscope_wait_seconds)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_trigger_variance = int(self.config_settings[0])
            self.cpu_temperature_enabled = int(self.config_settings[1])
            self.cpu_temperature_variance = float(self.config_settings[2])
            self.cpu_temperature_wait_seconds = float(self.config_settings[3])
            self.env_temperature_enabled = int(self.config_settings[4])
            self.env_temperature_variance = float(self.config_settings[5])
            self.env_temperature_wait_seconds = float(self.config_settings[6])
            self.pressure_enabled = int(self.config_settings[7])
            self.pressure_variance = float(self.config_settings[8])
            self.pressure_wait_seconds = float(self.config_settings[9])
            self.altitude_enabled = int(self.config_settings[10])
            self.altitude_variance = float(self.config_settings[11])
            self.altitude_wait_seconds = float(self.config_settings[12])
            self.humidity_enabled = int(self.config_settings[13])
            self.humidity_variance = float(self.config_settings[14])
            self.humidity_wait_seconds = float(self.config_settings[15])
            self.distance_enabled = int(self.config_settings[16])
            self.distance_variance = float(self.config_settings[17])
            self.distance_wait_seconds = float(self.config_settings[18])
            self.gas_enabled = int(self.config_settings[19])
            self.gas_resistance_index_variance = float(self.config_settings[20])
            self.gas_oxidising_variance = float(self.config_settings[21])
            self.gas_reducing_variance = float(self.config_settings[22])
            self.gas_nh3_variance = float(self.config_settings[23])
            self.gas_wait_seconds = float(self.config_settings[24])
            self.particulate_matter_enabled = int(self.config_settings[25])
            self.particulate_matter_1_variance = float(self.config_settings[26])
            self.particulate_matter_2_5_variance = float(self.config_settings[27])
            self.particulate_matter_10_variance = float(self.config_settings[28])
            self.particulate_matter_wait_seconds = float(self.config_settings[29])
            self.lumen_enabled = int(self.config_settings[30])
            self.lumen_variance = float(self.config_settings[31])
            self.lumen_wait_seconds = float(self.config_settings[32])
            self.colour_enabled = int(self.config_settings[33])
            self.red_variance = float(self.config_settings[34])
            self.orange_variance = float(self.config_settings[35])
            self.yellow_variance = float(self.config_settings[36])
            self.green_variance = float(self.config_settings[37])
            self.blue_variance = float(self.config_settings[38])
            self.violet_variance = float(self.config_settings[39])
            self.colour_wait_seconds = float(self.config_settings[40])
            self.ultra_violet_enabled = int(self.config_settings[41])
            self.ultra_violet_index_variance = float(self.config_settings[42])
            self.ultra_violet_a_variance = float(self.config_settings[43])
            self.ultra_violet_b_variance = float(self.config_settings[44])
            self.ultra_violet_wait_seconds = float(self.config_settings[45])
            self.accelerometer_enabled = int(self.config_settings[46])
            self.accelerometer_x_variance = float(self.config_settings[47])
            self.accelerometer_y_variance = float(self.config_settings[48])
            self.accelerometer_z_variance = float(self.config_settings[49])
            self.accelerometer_wait_seconds = float(self.config_settings[50])
            self.magnetometer_enabled = int(self.config_settings[51])
            self.magnetometer_x_variance = float(self.config_settings[52])
            self.magnetometer_y_variance = float(self.config_settings[53])
            self.magnetometer_z_variance = float(self.config_settings[54])
            self.magnetometer_wait_seconds = float(self.config_settings[55])
            self.gyroscope_enabled = int(self.config_settings[56])
            self.gyroscope_x_variance = float(self.config_settings[57])
            self.gyroscope_y_variance = float(self.config_settings[58])
            self.gyroscope_z_variance = float(self.config_settings[59])
            self.gyroscope_wait_seconds = float(self.config_settings[60])
        except Exception as error:
            logger.primary_logger.debug("Trigger Variance Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Trigger Variance Configuration.")
                self.save_config_to_file()
