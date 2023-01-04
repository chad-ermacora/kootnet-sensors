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
from operations_modules.app_generic_classes import CreateGeneralConfiguration
from operations_modules.app_validation_checks import get_validate_csv_emails


class CreateTriggerHighLowConfiguration(CreateGeneralConfiguration):
    """ Creates the Trigger High/Low Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        trigger_high_low_config = file_locations.trigger_high_low_config
        CreateGeneralConfiguration.__init__(self, trigger_high_low_config, load_from_file=load_from_file)
        self.config_file_header = "0 = Disabled and 1 = Enabled"
        self.config_settings_names = [
            "Enable High/Low Trigger Recording", "Enable CPU Temperature", "CPU Temperature Low Trigger",
            "CPU Temperature High Trigger", "Seconds between CPU Temperature readings",
            "Enable Environmental Temperature", "Environmental Temperature Low Trigger",
            "Environmental Temperature High Trigger", "Seconds between Env Temperature readings", "Enable Pressure",
            "Pressure Low Trigger", "Pressure High Trigger", "Seconds between Pressure readings", "Enable Altitude",
            "Altitude Low Trigger", "Altitude High Trigger", "Seconds between Altitude readings", "Enable Humidity",
            "Humidity Low Trigger", "Humidity High Trigger", "Seconds between Humidity readings", "Enable Distance",
            "Distance Low Trigger", "Distance High Trigger", "Seconds between Distance readings", "Enable Gas",
            "Gas Resistance Index Low Trigger", "Gas Resistance Index High Trigger", "Gas Oxidising Low Trigger",
            "Gas Oxidising High Trigger", "Gas Reducing Low Trigger", "Gas Reducing High Trigger",
            "Gas NH3 Low Trigger", "Gas NH3 High Trigger", "Seconds between Gas readings",
            "Enable Particulate Matter (PM)", "Particulate Matter 1 (PM1) Low Trigger",
            "Particulate Matter 1 (PM1) High Trigger", "Particulate Matter 2.5 (PM2.5) Low Trigger",
            "Particulate Matter 2.5 (PM2.5) High Trigger", "Particulate Matter 4 (PM4) Low Trigger",
            "Particulate Matter 4 (PM4) High Trigger", "Particulate Matter 10 (PM10) Low Trigger",
            "Particulate Matter 10 (PM10) High Trigger", "Seconds between PM readings", "Enable Lumen",
            "Lumen Low Trigger", "Lumen High Trigger", "Seconds between Lumen readings", "Enable Colour",
            "Red Low Trigger", "Red High Trigger", "Orange Low Trigger", "Orange High Trigger", "Yellow Low Trigger",
            "Yellow High Trigger", "Green Low Trigger", "Green High Trigger", "Blue Low Trigger", "Blue High Trigger",
            "Violet Low Trigger", "Violet High Trigger", "Seconds between Colour readings", "Enable Ultra Violet",
            "Ultra Violet Index Low Trigger", "Ultra Violet Index High Trigger", "Ultra Violet A Low Trigger",
            "Ultra Violet A High Trigger", "Ultra Violet B Low Trigger", "Ultra Violet B High Trigger",
            "Seconds between Ultra Violet readings", "Enable Accelerometer", "Accelerometer X Low Trigger",
            "Accelerometer X High Trigger", "Accelerometer Y Low Trigger", "Accelerometer Y High Trigger",
            "Accelerometer Z Low Trigger", "Accelerometer Z High Trigger", "Seconds between Accelerometer readings",
            "Enable Magnetometer", "Magnetometer X Low Trigger", "Magnetometer X High Trigger",
            "Magnetometer Y Low Trigger", "Magnetometer Y High Trigger", "Magnetometer Z Low Trigger",
            "Magnetometer Z High Trigger", "Seconds between Magnetometer readings", "Enable Gyroscope",
            "Gyroscope X Low Trigger", "Gyroscope X High Trigger", "Gyroscope Y Low Trigger",
            "Gyroscope Y High Trigger", "Gyroscope Z Low Trigger", "Gyroscope Z High Trigger",
            "Seconds between Gyroscope readings", "Enable Email Alerts", "Send Alerts to CSV Emails",
            "Enable High Alerts", "Enable Low Alerts", "Send up to 1 email every hour(s) (Set to 0 to always send)",
            "Enable returning to Normal Alerts"
        ]
        self.valid_setting_count = len(self.config_settings_names)

        self.enable_high_low_trigger_recording = 0

        self.enable_email_alerts = 0
        self.alerts_csv_emails = ""
        self.alerts_high_enabled = 0
        self.alerts_normal_enabled = 0
        self.alerts_low_enabled = 0
        # If self.alerts_resend_hourly = 0, it doesn't resend email alerts
        self.alerts_resend_emails_every_hours = 6

        self._disable_all_triggers()

        self.cpu_temperature_low = 10.0
        self.cpu_temperature_high = 75.0
        self.cpu_temperature_wait_seconds = 60.0

        self.env_temperature_low = -5.0
        self.env_temperature_high = 35.0
        self.env_temperature_wait_seconds = 60.0

        self.pressure_low = 350
        self.pressure_high = 1200
        self.pressure_wait_seconds = 60.0

        self.humidity_low = 25.0
        self.humidity_high = 80.0
        self.humidity_wait_seconds = 60.0

        self.altitude_low = 200
        self.altitude_high = 1000
        self.altitude_wait_seconds = 60.0

        self.distance_low = 1.0
        self.distance_high = 555.0
        self.distance_wait_seconds = 2

        self.lumen_low = 25.0
        self.lumen_high = 1000.0
        self.lumen_wait_seconds = 10

        self.red_low = 15.0
        self.red_high = 215.0
        self.orange_low = 15.0
        self.orange_high = 215.0
        self.yellow_low = 15.0
        self.yellow_high = 215.0
        self.green_low = 15.0
        self.green_high = 215.0
        self.blue_low = 15.0
        self.blue_high = 215.0
        self.violet_low = 15.0
        self.violet_high = 215.0
        self.colour_wait_seconds = 60.0

        self.ultra_violet_index_low = 25.0
        self.ultra_violet_index_high = 225.0
        self.ultra_violet_a_low = 21.0
        self.ultra_violet_a_high = 210.0
        self.ultra_violet_b_low = 20.0
        self.ultra_violet_b_high = 210.0
        self.ultra_violet_wait_seconds = 60.0

        self.gas_resistance_index_low = 100.0
        self.gas_resistance_index_high = 800.0
        self.gas_oxidising_low = 100.0
        self.gas_oxidising_high = 800.0
        self.gas_reducing_low = 100.0
        self.gas_reducing_high = 800.0
        self.gas_nh3_low = 100.0
        self.gas_nh3_high = 800.0
        self.gas_wait_seconds = 60.0

        self.particulate_matter_1_low = 40.0
        self.particulate_matter_1_high = 114.0
        self.particulate_matter_2_5_low = 41.0
        self.particulate_matter_2_5_high = 114.0
        self.particulate_matter_4_low = 41.0
        self.particulate_matter_4_high = 114.0
        self.particulate_matter_10_low = 41.0
        self.particulate_matter_10_high = 114.0
        self.particulate_matter_wait_seconds = 60.0

        self.accelerometer_x_low = 0.1
        self.accelerometer_x_high = 0.9
        self.accelerometer_y_low = 0.1
        self.accelerometer_y_high = 0.9
        self.accelerometer_z_low = 0.1
        self.accelerometer_z_high = 0.9
        self.accelerometer_wait_seconds = 0.3

        self.magnetometer_x_low = 40.0
        self.magnetometer_x_high = 60.0
        self.magnetometer_y_low = 40.0
        self.magnetometer_y_high = 60.0
        self.magnetometer_z_low = 40.0
        self.magnetometer_z_high = 60.0
        self.magnetometer_wait_seconds = 0.3

        self.gyroscope_x_low = 10.0
        self.gyroscope_x_high = 70.0
        self.gyroscope_y_low = 10.0
        self.gyroscope_y_high = 70.0
        self.gyroscope_z_low = 10.0
        self.gyroscope_z_high = 70.0
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
        """ Updates the High/Low Trigger configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML High/Low Triggers Update Check")

        self._disable_all_triggers()

        if html_request.form.get("checkbox_enable_high_low_trigger_recording") is not None:
            self.enable_high_low_trigger_recording = 1

        if html_request.form.get("checkbox_enable_high_low_emails") is not None:
            self.enable_email_alerts = 1

        if html_request.form.get("alerts_csv_emails") is not None:
            csv_emails = html_request.form.get("alerts_csv_emails")
            self.alerts_csv_emails = get_validate_csv_emails(csv_emails)

        if html_request.form.get("checkbox_enable_high_alert_emails") is not None:
            self.alerts_high_enabled = 1

        if html_request.form.get("checkbox_enable_normal_alert_emails") is not None:
            self.alerts_normal_enabled = 1

        if html_request.form.get("checkbox_enable_low_alert_emails") is not None:
            self.alerts_low_enabled = 1

        self.alerts_resend_emails_every_hours = float(html_request.form.get("resend_alert_email_hours"))

        if html_request.form.get("cpu_temperature") is not None:
            self.cpu_temperature_enabled = 1
        if html_request.form.get("trigger_low_cpu_temperature") is not None:
            self.cpu_temperature_low = float(html_request.form.get("trigger_low_cpu_temperature"))
        if html_request.form.get("trigger_high_cpu_temperature") is not None:
            self.cpu_temperature_high = float(html_request.form.get("trigger_high_cpu_temperature"))
        if html_request.form.get("seconds_cpu_temperature") is not None:
            self.cpu_temperature_wait_seconds = float(html_request.form.get("seconds_cpu_temperature"))

        if html_request.form.get("env_temperature") is not None:
            self.env_temperature_enabled = 1
        if html_request.form.get("trigger_low_env_temperature") is not None:
            self.env_temperature_low = float(html_request.form.get("trigger_low_env_temperature"))
        if html_request.form.get("trigger_high_env_temperature") is not None:
            self.env_temperature_high = float(html_request.form.get("trigger_high_env_temperature"))
        if html_request.form.get("seconds_env_temperature") is not None:
            self.env_temperature_wait_seconds = float(html_request.form.get("seconds_env_temperature"))

        if html_request.form.get("pressure") is not None:
            self.pressure_enabled = 1
        if html_request.form.get("trigger_low_pressure") is not None:
            self.pressure_low = float(html_request.form.get("trigger_low_pressure"))
        if html_request.form.get("trigger_high_pressure") is not None:
            self.pressure_high = float(html_request.form.get("trigger_high_pressure"))
        if html_request.form.get("seconds_pressure") is not None:
            self.pressure_wait_seconds = float(html_request.form.get("seconds_pressure"))

        if html_request.form.get("humidity") is not None:
            self.humidity_enabled = 1
        if html_request.form.get("trigger_low_humidity") is not None:
            self.humidity_low = float(html_request.form.get("trigger_low_humidity"))
        if html_request.form.get("trigger_high_humidity") is not None:
            self.humidity_high = float(html_request.form.get("trigger_high_humidity"))
        if html_request.form.get("seconds_humidity") is not None:
            self.humidity_wait_seconds = float(html_request.form.get("seconds_humidity"))

        if html_request.form.get("altitude") is not None:
            self.altitude_enabled = 1
        if html_request.form.get("trigger_low_altitude") is not None:
            self.altitude_low = float(html_request.form.get("trigger_low_altitude"))
        if html_request.form.get("trigger_high_altitude") is not None:
            self.altitude_high = float(html_request.form.get("trigger_high_altitude"))
        if html_request.form.get("seconds_altitude") is not None:
            self.altitude_wait_seconds = float(html_request.form.get("seconds_altitude"))

        if html_request.form.get("distance") is not None:
            self.distance_enabled = 1
        if html_request.form.get("trigger_low_distance") is not None:
            self.distance_low = float(html_request.form.get("trigger_low_distance"))
        if html_request.form.get("trigger_high_distance") is not None:
            self.distance_high = float(html_request.form.get("trigger_high_distance"))
        if html_request.form.get("seconds_distance") is not None:
            self.distance_wait_seconds = float(html_request.form.get("seconds_distance"))

        if html_request.form.get("lumen") is not None:
            self.lumen_enabled = 1
        if html_request.form.get("trigger_low_lumen") is not None:
            self.lumen_low = float(html_request.form.get("trigger_low_lumen"))
        if html_request.form.get("trigger_high_lumen") is not None:
            self.lumen_high = float(html_request.form.get("trigger_high_lumen"))
        if html_request.form.get("seconds_lumen") is not None:
            self.lumen_wait_seconds = float(html_request.form.get("seconds_lumen"))

        if html_request.form.get("colour") is not None:
            self.colour_enabled = 1
        if html_request.form.get("trigger_low_red") is not None:
            self.red_low = float(html_request.form.get("trigger_low_red"))
        if html_request.form.get("trigger_high_red") is not None:
            self.red_high = float(html_request.form.get("trigger_high_red"))
        if html_request.form.get("trigger_low_orange") is not None:
            self.orange_low = float(html_request.form.get("trigger_low_orange"))
        if html_request.form.get("trigger_high_orange") is not None:
            self.orange_high = float(html_request.form.get("trigger_high_orange"))
        if html_request.form.get("trigger_low_yellow") is not None:
            self.yellow_low = float(html_request.form.get("trigger_low_yellow"))
        if html_request.form.get("trigger_high_yellow") is not None:
            self.yellow_high = float(html_request.form.get("trigger_high_yellow"))
        if html_request.form.get("trigger_low_green") is not None:
            self.green_low = float(html_request.form.get("trigger_low_green"))
        if html_request.form.get("trigger_high_green") is not None:
            self.green_high = float(html_request.form.get("trigger_high_green"))
        if html_request.form.get("trigger_low_blue") is not None:
            self.blue_low = float(html_request.form.get("trigger_low_blue"))
        if html_request.form.get("trigger_high_blue") is not None:
            self.blue_high = float(html_request.form.get("trigger_high_blue"))
        if html_request.form.get("trigger_low_violet") is not None:
            self.violet_low = float(html_request.form.get("trigger_low_violet"))
        if html_request.form.get("trigger_high_violet") is not None:
            self.violet_high = float(html_request.form.get("trigger_high_violet"))
        if html_request.form.get("seconds_colour") is not None:
            self.colour_wait_seconds = float(html_request.form.get("seconds_colour"))

        if html_request.form.get("ultra_violet") is not None:
            self.ultra_violet_enabled = 1
        if html_request.form.get("trigger_low_ultra_violet_a") is not None:
            self.ultra_violet_a_low = float(html_request.form.get("trigger_low_ultra_violet_a"))
        if html_request.form.get("trigger_high_ultra_violet_a") is not None:
            self.ultra_violet_a_high = float(html_request.form.get("trigger_high_ultra_violet_a"))
        if html_request.form.get("trigger_low_ultra_violet_b") is not None:
            self.ultra_violet_b_low = float(html_request.form.get("trigger_low_ultra_violet_b"))
        if html_request.form.get("trigger_high_ultra_violet_b") is not None:
            self.ultra_violet_b_high = float(html_request.form.get("trigger_high_ultra_violet_b"))
        if html_request.form.get("seconds_ultra_violet") is not None:
            self.ultra_violet_wait_seconds = float(html_request.form.get("seconds_ultra_violet"))

        if html_request.form.get("gas") is not None:
            self.gas_enabled = 1
        if html_request.form.get("trigger_low_gas_index") is not None:
            self.gas_resistance_index_low = float(html_request.form.get("trigger_low_gas_index"))
        if html_request.form.get("trigger_high_gas_index") is not None:
            self.gas_resistance_index_high = float(html_request.form.get("trigger_high_gas_index"))
        if html_request.form.get("trigger_low_gas_oxidising") is not None:
            self.gas_oxidising_low = float(html_request.form.get("trigger_low_gas_oxidising"))
        if html_request.form.get("trigger_high_gas_oxidising") is not None:
            self.gas_oxidising_high = float(html_request.form.get("trigger_high_gas_oxidising"))
        if html_request.form.get("trigger_low_gas_reducing") is not None:
            self.gas_reducing_low = float(html_request.form.get("trigger_low_gas_reducing"))
        if html_request.form.get("trigger_high_gas_reducing") is not None:
            self.gas_reducing_high = float(html_request.form.get("trigger_high_gas_reducing"))
        if html_request.form.get("trigger_low_gas_nh3") is not None:
            self.gas_nh3_low = float(html_request.form.get("trigger_low_gas_nh3"))
        if html_request.form.get("trigger_high_gas_nh3") is not None:
            self.gas_nh3_high = float(html_request.form.get("trigger_high_gas_nh3"))
        if html_request.form.get("seconds_gas") is not None:
            self.gas_wait_seconds = float(html_request.form.get("seconds_gas"))

        if html_request.form.get("particulate_matter") is not None:
            self.particulate_matter_enabled = 1
        if html_request.form.get("trigger_low_pm1") is not None:
            self.particulate_matter_1_low = float(html_request.form.get("trigger_low_pm1"))
        if html_request.form.get("trigger_high_pm1") is not None:
            self.particulate_matter_1_high = float(html_request.form.get("trigger_high_pm1"))
        if html_request.form.get("trigger_low_pm2_5") is not None:
            self.particulate_matter_2_5_low = float(html_request.form.get("trigger_low_pm2_5"))
        if html_request.form.get("trigger_high_pm2_5") is not None:
            self.particulate_matter_2_5_high = float(html_request.form.get("trigger_high_pm2_5"))
        if html_request.form.get("trigger_low_pm4") is not None:
            self.particulate_matter_4_low = float(html_request.form.get("trigger_low_pm4"))
        if html_request.form.get("trigger_high_pm4") is not None:
            self.particulate_matter_4_high = float(html_request.form.get("trigger_high_pm4"))
        if html_request.form.get("trigger_low_pm10") is not None:
            self.particulate_matter_10_low = float(html_request.form.get("trigger_low_pm10"))
        if html_request.form.get("trigger_high_pm10") is not None:
            self.particulate_matter_10_high = float(html_request.form.get("trigger_high_pm10"))
        if html_request.form.get("seconds_pm") is not None:
            self.particulate_matter_wait_seconds = float(html_request.form.get("seconds_pm"))

        if html_request.form.get("accelerometer") is not None:
            self.accelerometer_enabled = 1
        if html_request.form.get("trigger_low_accelerometer_x") is not None:
            self.accelerometer_x_low = float(html_request.form.get("trigger_low_accelerometer_x"))
        if html_request.form.get("trigger_high_accelerometer_x") is not None:
            self.accelerometer_x_high = float(html_request.form.get("trigger_high_accelerometer_x"))
        if html_request.form.get("trigger_low_accelerometer_y") is not None:
            self.accelerometer_y_low = float(html_request.form.get("trigger_low_accelerometer_y"))
        if html_request.form.get("trigger_high_accelerometer_y") is not None:
            self.accelerometer_y_high = float(html_request.form.get("trigger_high_accelerometer_y"))
        if html_request.form.get("trigger_low_accelerometer_z") is not None:
            self.accelerometer_z_low = float(html_request.form.get("trigger_low_accelerometer_z"))
        if html_request.form.get("trigger_high_accelerometer_z") is not None:
            self.accelerometer_z_high = float(html_request.form.get("trigger_high_accelerometer_z"))
        if html_request.form.get("seconds_accelerometer") is not None:
            self.accelerometer_wait_seconds = float(html_request.form.get("seconds_accelerometer"))

        if html_request.form.get("magnetometer") is not None:
            self.magnetometer_enabled = 1
        if html_request.form.get("trigger_low_magnetometer_x") is not None:
            self.magnetometer_x_low = float(html_request.form.get("trigger_low_magnetometer_x"))
        if html_request.form.get("trigger_high_magnetometer_x") is not None:
            self.magnetometer_x_high = float(html_request.form.get("trigger_high_magnetometer_x"))
        if html_request.form.get("trigger_low_magnetometer_y") is not None:
            self.magnetometer_y_low = float(html_request.form.get("trigger_low_magnetometer_y"))
        if html_request.form.get("trigger_high_magnetometer_y") is not None:
            self.magnetometer_y_high = float(html_request.form.get("trigger_high_magnetometer_y"))
        if html_request.form.get("trigger_low_magnetometer_z") is not None:
            self.magnetometer_z_low = float(html_request.form.get("trigger_low_magnetometer_z"))
        if html_request.form.get("trigger_high_magnetometer_z") is not None:
            self.magnetometer_z_high = float(html_request.form.get("trigger_high_magnetometer_z"))
        if html_request.form.get("seconds_magnetometer") is not None:
            self.magnetometer_wait_seconds = float(html_request.form.get("seconds_magnetometer"))

        if html_request.form.get("gyroscope") is not None:
            self.gyroscope_enabled = 1
        if html_request.form.get("trigger_low_gyroscope_x") is not None:
            self.gyroscope_x_low = float(html_request.form.get("trigger_low_gyroscope_x"))
        if html_request.form.get("trigger_high_gyroscope_x") is not None:
            self.gyroscope_x_high = float(html_request.form.get("trigger_high_gyroscope_x"))
        if html_request.form.get("trigger_low_gyroscope_y") is not None:
            self.gyroscope_y_low = float(html_request.form.get("trigger_low_gyroscope_y"))
        if html_request.form.get("trigger_high_gyroscope_y") is not None:
            self.gyroscope_y_high = float(html_request.form.get("trigger_high_gyroscope_y"))
        if html_request.form.get("trigger_low_gyroscope_z") is not None:
            self.gyroscope_z_low = float(html_request.form.get("trigger_low_gyroscope_z"))
        if html_request.form.get("trigger_high_gyroscope_z") is not None:
            self.gyroscope_z_high = float(html_request.form.get("trigger_high_gyroscope_z"))
        if html_request.form.get("seconds_gyroscope") is not None:
            self.gyroscope_wait_seconds = float(html_request.form.get("seconds_gyroscope"))

        self._validate_high_low_triggers()
        self.update_configuration_settings_list()

    def _validate_high_low_triggers(self):
        if not self._validate_triggers("CPU Temp", self.cpu_temperature_low, self.cpu_temperature_high):
            self.cpu_temperature_enabled = 0

        if not self._validate_triggers("Env Temp", self.env_temperature_low, self.env_temperature_high):
            self.env_temperature_enabled = 0

        if not self._validate_triggers("Pressure", self.pressure_low, self.pressure_high):
            self.pressure_enabled = 0

        if not self._validate_triggers("Altitude", self.altitude_low, self.altitude_high):
            self.altitude_enabled = 0

        if not self._validate_triggers("Humidity", self.humidity_low, self.humidity_high):
            self.humidity_enabled = 0

        if not self._validate_triggers("Distance", self.distance_low, self.distance_high):
            self.distance_enabled = 0

        if not self._validate_triggers("Gas Index", self.gas_resistance_index_low, self.gas_resistance_index_high):
            self.gas_enabled = 0
        if not self._validate_triggers("Gas Oxidising", self.gas_oxidising_low, self.gas_oxidising_high):
            self.gas_enabled = 0
        if not self._validate_triggers("Gas Reducing", self.gas_reducing_low, self.gas_reducing_high):
            self.gas_enabled = 0
        if not self._validate_triggers("Gas NH3", self.gas_nh3_low, self.gas_nh3_high):
            self.gas_enabled = 0

        if not self._validate_triggers("PM 1", self.particulate_matter_1_low, self.particulate_matter_1_high):
            self.particulate_matter_enabled = 0
        if not self._validate_triggers("PM 2.5", self.particulate_matter_2_5_low, self.particulate_matter_2_5_high):
            self.particulate_matter_enabled = 0
        if not self._validate_triggers("PM 4", self.particulate_matter_4_low, self.particulate_matter_4_high):
            self.particulate_matter_enabled = 0
        if not self._validate_triggers("PM 10", self.particulate_matter_10_low, self.particulate_matter_10_high):
            self.particulate_matter_enabled = 0

        if not self._validate_triggers("Lumen", self.lumen_low, self.lumen_high):
            self.lumen_enabled = 0

        if not self._validate_triggers("Red", self.red_low, self.red_high):
            self.colour_enabled = 0
        if not self._validate_triggers("Orange", self.orange_low, self.orange_high):
            self.colour_enabled = 0
        if not self._validate_triggers("Yellow", self.yellow_low, self.yellow_high):
            self.colour_enabled = 0
        if not self._validate_triggers("Green", self.green_low, self.green_high):
            self.colour_enabled = 0
        if not self._validate_triggers("Blue", self.blue_low, self.blue_high):
            self.colour_enabled = 0
        if not self._validate_triggers("Violet", self.violet_low, self.violet_high):
            self.colour_enabled = 0

        # if not self._validate_triggers("UV Index", self.ultra_violet_index_low, self.ultra_violet_index_high):
        #     self.ultra_violet_enabled = 0
        if not self._validate_triggers("UV A", self.ultra_violet_a_low, self.ultra_violet_a_high):
            self.ultra_violet_enabled = 0
        if not self._validate_triggers("UV B", self.ultra_violet_b_low, self.ultra_violet_b_high):
            self.ultra_violet_enabled = 0

        if not self._validate_triggers("Acc X", self.accelerometer_x_low, self.accelerometer_x_high):
            self.accelerometer_enabled = 0
        if not self._validate_triggers("Acc Y", self.accelerometer_y_low, self.accelerometer_y_high):
            self.accelerometer_enabled = 0
        if not self._validate_triggers("Acc Z", self.accelerometer_z_low, self.accelerometer_z_high):
            self.accelerometer_enabled = 0

        if not self._validate_triggers("Mag X", self.magnetometer_x_low, self.magnetometer_x_high):
            self.magnetometer_enabled = 0
        if not self._validate_triggers("Mag Y", self.magnetometer_y_low, self.magnetometer_y_high):
            self.magnetometer_enabled = 0
        if not self._validate_triggers("Mag Z", self.magnetometer_z_low, self.magnetometer_z_high):
            self.magnetometer_enabled = 0

        if not self._validate_triggers("Gyro X", self.gyroscope_x_low, self.gyroscope_x_high):
            self.gyroscope_enabled = 0
        if not self._validate_triggers("Gyro Y", self.gyroscope_y_low, self.gyroscope_y_high):
            self.gyroscope_enabled = 0
        if not self._validate_triggers("Gyro Z", self.gyroscope_z_low, self.gyroscope_z_high):
            self.gyroscope_enabled = 0

    @staticmethod
    def _validate_triggers(sensor_name, low_trigger, high_trigger):
        """
        Takes the low and high triggers for a sensor.
        If the low trigger is lower than the high, return True else False.

        :param sensor_name: Sensor's name in text
        :param low_trigger: Number (int or float)
        :param high_trigger: Number (int or float)
        :return: True/False
        """
        if low_trigger < high_trigger:
            return True
        log_msg = f"Trigger High/Low Config: {sensor_name}'s Low Trigger is not lower than the set High Trigger"
        logger.primary_logger.warning(log_msg)
        return False

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_high_low_trigger_recording), str(self.cpu_temperature_enabled),
            str(self.cpu_temperature_low), str(self.cpu_temperature_high), str(self.cpu_temperature_wait_seconds),
            str(self.env_temperature_enabled), str(self.env_temperature_low), str(self.env_temperature_high),
            str(self.env_temperature_wait_seconds), str(self.pressure_enabled),
            str(self.pressure_low), str(self.pressure_high), str(self.pressure_wait_seconds),
            str(self.altitude_enabled), str(self.altitude_low), str(self.altitude_high),
            str(self.altitude_wait_seconds), str(self.humidity_enabled), str(self.humidity_low),
            str(self.humidity_high), str(self.humidity_wait_seconds), str(self.distance_enabled),
            str(self.distance_low), str(self.distance_high), str(self.distance_wait_seconds), str(self.gas_enabled),
            str(self.gas_resistance_index_low), str(self.gas_resistance_index_high), str(self.gas_oxidising_low),
            str(self.gas_oxidising_high), str(self.gas_reducing_low), str(self.gas_reducing_high),
            str(self.gas_nh3_low), str(self.gas_nh3_high), str(self.gas_wait_seconds),
            str(self.particulate_matter_enabled), str(self.particulate_matter_1_low),
            str(self.particulate_matter_1_high), str(self.particulate_matter_2_5_low),
            str(self.particulate_matter_2_5_high), str(self.particulate_matter_4_low),
            str(self.particulate_matter_4_high), str(self.particulate_matter_10_low),
            str(self.particulate_matter_10_high), str(self.particulate_matter_wait_seconds), str(self.lumen_enabled),
            str(self.lumen_low), str(self.lumen_high), str(self.lumen_wait_seconds), str(self.colour_enabled),
            str(self.red_low), str(self.red_high), str(self.orange_low), str(self.orange_high), str(self.yellow_low),
            str(self.yellow_high), str(self.green_low), str(self.green_high), str(self.blue_low), str(self.blue_high),
            str(self.violet_low), str(self.violet_high), str(self.colour_wait_seconds), str(self.ultra_violet_enabled),
            str(self.ultra_violet_index_low), str(self.ultra_violet_index_high), str(self.ultra_violet_a_low),
            str(self.ultra_violet_a_high), str(self.ultra_violet_b_low), str(self.ultra_violet_b_high),
            str(self.ultra_violet_wait_seconds), str(self.accelerometer_enabled), str(self.accelerometer_x_low),
            str(self.accelerometer_x_high), str(self.accelerometer_y_low), str(self.accelerometer_y_high),
            str(self.accelerometer_z_low), str(self.accelerometer_z_high), str(self.accelerometer_wait_seconds),
            str(self.magnetometer_enabled), str(self.magnetometer_x_low), str(self.magnetometer_x_high),
            str(self.magnetometer_y_low), str(self.magnetometer_y_high), str(self.magnetometer_z_low),
            str(self.magnetometer_z_high), str(self.magnetometer_wait_seconds), str(self.gyroscope_enabled),
            str(self.gyroscope_x_low), str(self.gyroscope_x_high), str(self.gyroscope_y_low),
            str(self.gyroscope_y_high), str(self.gyroscope_z_low), str(self.gyroscope_z_high),
            str(self.gyroscope_wait_seconds), str(self.enable_email_alerts), str(self.alerts_csv_emails),
            str(self.alerts_high_enabled), str(self.alerts_low_enabled), str(self.alerts_resend_emails_every_hours),
            str(self.alerts_normal_enabled)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_high_low_trigger_recording = int(self.config_settings[0])
            self.cpu_temperature_enabled = int(self.config_settings[1])
            self.cpu_temperature_low = float(self.config_settings[2])
            self.cpu_temperature_high = float(self.config_settings[3])
            self.cpu_temperature_wait_seconds = float(self.config_settings[4])
            self.env_temperature_enabled = int(self.config_settings[5])
            self.env_temperature_low = float(self.config_settings[6])
            self.env_temperature_high = float(self.config_settings[7])
            self.env_temperature_wait_seconds = float(self.config_settings[8])
            self.pressure_enabled = int(self.config_settings[9])
            self.pressure_low = float(self.config_settings[10])
            self.pressure_high = float(self.config_settings[11])
            self.pressure_wait_seconds = float(self.config_settings[12])
            self.altitude_enabled = int(self.config_settings[13])
            self.altitude_low = float(self.config_settings[14])
            self.altitude_high = float(self.config_settings[15])
            self.altitude_wait_seconds = float(self.config_settings[16])
            self.humidity_enabled = int(self.config_settings[17])
            self.humidity_low = float(self.config_settings[18])
            self.humidity_high = float(self.config_settings[19])
            self.humidity_wait_seconds = float(self.config_settings[20])
            self.distance_enabled = int(self.config_settings[21])
            self.distance_low = float(self.config_settings[22])
            self.distance_high = float(self.config_settings[23])
            self.distance_wait_seconds = float(self.config_settings[24])
            self.gas_enabled = int(self.config_settings[25])
            self.gas_resistance_index_low = float(self.config_settings[26])
            self.gas_resistance_index_high = float(self.config_settings[27])
            self.gas_oxidising_low = float(self.config_settings[28])
            self.gas_oxidising_high = float(self.config_settings[29])
            self.gas_reducing_low = float(self.config_settings[30])
            self.gas_reducing_high = float(self.config_settings[31])
            self.gas_nh3_low = float(self.config_settings[32])
            self.gas_nh3_high = float(self.config_settings[33])
            self.gas_wait_seconds = float(self.config_settings[34])
            self.particulate_matter_enabled = int(self.config_settings[35])
            self.particulate_matter_1_low = float(self.config_settings[36])
            self.particulate_matter_1_high = float(self.config_settings[37])
            self.particulate_matter_2_5_low = float(self.config_settings[38])
            self.particulate_matter_2_5_high = float(self.config_settings[39])
            self.particulate_matter_4_low = float(self.config_settings[40])
            self.particulate_matter_4_high = float(self.config_settings[41])
            self.particulate_matter_10_low = float(self.config_settings[42])
            self.particulate_matter_10_high = float(self.config_settings[43])
            self.particulate_matter_wait_seconds = float(self.config_settings[44])
            self.lumen_enabled = int(self.config_settings[45])
            self.lumen_low = float(self.config_settings[46])
            self.lumen_high = float(self.config_settings[47])
            self.lumen_wait_seconds = float(self.config_settings[48])
            self.colour_enabled = int(self.config_settings[49])
            self.red_low = float(self.config_settings[50])
            self.red_high = float(self.config_settings[51])
            self.orange_low = float(self.config_settings[52])
            self.orange_high = float(self.config_settings[53])
            self.yellow_low = float(self.config_settings[54])
            self.yellow_high = float(self.config_settings[55])
            self.green_low = float(self.config_settings[56])
            self.green_high = float(self.config_settings[57])
            self.blue_low = float(self.config_settings[58])
            self.blue_high = float(self.config_settings[59])
            self.violet_low = float(self.config_settings[60])
            self.violet_high = float(self.config_settings[61])
            self.colour_wait_seconds = float(self.config_settings[62])
            self.ultra_violet_enabled = int(self.config_settings[63])
            self.ultra_violet_index_low = float(self.config_settings[64])
            self.ultra_violet_index_high = float(self.config_settings[65])
            self.ultra_violet_a_low = float(self.config_settings[66])
            self.ultra_violet_a_high = float(self.config_settings[67])
            self.ultra_violet_b_low = float(self.config_settings[68])
            self.ultra_violet_b_high = float(self.config_settings[69])
            self.ultra_violet_wait_seconds = float(self.config_settings[70])
            self.accelerometer_enabled = int(self.config_settings[71])
            self.accelerometer_x_low = float(self.config_settings[72])
            self.accelerometer_x_high = float(self.config_settings[73])
            self.accelerometer_y_low = float(self.config_settings[74])
            self.accelerometer_y_high = float(self.config_settings[75])
            self.accelerometer_z_low = float(self.config_settings[76])
            self.accelerometer_z_high = float(self.config_settings[77])
            self.accelerometer_wait_seconds = float(self.config_settings[78])
            self.magnetometer_enabled = int(self.config_settings[79])
            self.magnetometer_x_low = float(self.config_settings[80])
            self.magnetometer_x_high = float(self.config_settings[81])
            self.magnetometer_y_low = float(self.config_settings[82])
            self.magnetometer_y_high = float(self.config_settings[83])
            self.magnetometer_z_low = float(self.config_settings[84])
            self.magnetometer_z_high = float(self.config_settings[85])
            self.magnetometer_wait_seconds = float(self.config_settings[86])
            self.gyroscope_enabled = int(self.config_settings[87])
            self.gyroscope_x_low = float(self.config_settings[88])
            self.gyroscope_x_high = float(self.config_settings[89])
            self.gyroscope_y_low = float(self.config_settings[90])
            self.gyroscope_y_high = float(self.config_settings[91])
            self.gyroscope_z_low = float(self.config_settings[92])
            self.gyroscope_z_high = float(self.config_settings[93])
            self.gyroscope_wait_seconds = float(self.config_settings[94])
            self.enable_email_alerts = int(self.config_settings[95])
            self.alerts_csv_emails = str(self.config_settings[96]).strip()
            self.alerts_high_enabled = int(self.config_settings[97])
            self.alerts_low_enabled = int(self.config_settings[98])
            self.alerts_resend_emails_every_hours = float(self.config_settings[99])
            self.alerts_normal_enabled = int(self.config_settings[100])
        except Exception as error:
            logger.primary_logger.debug("Trigger High/Low Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Trigger High/Low Configuration.")
                self.save_config_to_file()

    def _disable_all_triggers(self):
        self.enable_high_low_trigger_recording = 0
        self.enable_email_alerts = 0
        self.alerts_csv_emails = ""
        self.alerts_high_enabled = 0
        self.alerts_normal_enabled = 0
        self.alerts_low_enabled = 0
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
